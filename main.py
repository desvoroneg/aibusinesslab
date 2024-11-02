import os
import telebot
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

bot = telebot.TeleBot(TOKEN)

# Простой HTTP сервер для health checks
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
    
    def log_message(self, format, *args):
        pass

def run_health_server():
    server = HTTPServer(('0.0.0.0', 8000), HealthCheckHandler)
    logger.info("Health check server started on port 8000")
    server.serve_forever()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
👋 Привет! Я бот канала AI Business Lab.

Через меня вы можете получить чек-лист "20 процессов в вашем бизнесе, которые можно автоматизировать прямо сейчас с помощью AI"

Чтобы получить чек-лист, отправьте команду /checklist

🎁 Желаю продуктивной автоматизации!
    """
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['checklist'])
def handle_checklist_request(message):
    user_id = message.from_user.id
    username = message.from_user.username
    
    try:
        with open('checklist.pdf', 'rb') as checklist:
            bot.send_document(
                message.chat.id,
                checklist,
                caption="Вот ваш чек-лист по автоматизации бизнес-процессов 🎁\n\nПодписывайтесь на наш канал @AIBusinessLab для получения новых материалов!"
            )
        # Уведомление админу
        bot.send_message(
            ADMIN_ID,
            f"Новая выдача чек-листа!\nUser: @{username}\nID: {user_id}"
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        bot.reply_to(
            message,
            "Произошла ошибка. Пожалуйста, попробуйте позже или напишите в поддержку @desvoroneg"
        )

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
🤖 Как пользоваться ботом:

/start - начать работу с ботом
/checklist - получить чек-лист
/help - показать это сообщение

При проблемах пишите: @desvoroneg
    """
    bot.reply_to(message, help_text)

if __name__ == '__main__':
    logger.info("Bot starting...")
    try:
        # Запускаем health check сервер в отдельном потоке
        health_thread = Thread(target=run_health_server, daemon=True)
        health_thread.start()
        logger.info("Health check server thread started")
        
        # Запускаем бота
        logger.info("Starting bot polling...")
        bot.infinity_polling()
    except Exception as e:
        logger.error(f"Error during startup: {e}")
