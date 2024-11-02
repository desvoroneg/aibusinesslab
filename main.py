import os
import telebot
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import socket
import dns.resolver

# Настройка DNS
dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8', '8.8.4.4']  # Google DNS

# Переопределяем функцию разрешения имен
def custom_resolver(host):
    try:
        return socket.gethostbyname(host)
    except:
        try:
            answers = dns.resolver.resolve(host, 'A')
            return answers[0].address
        except Exception as e:
            logger.error(f"DNS resolution failed: {e}")
            raise

socket.getaddrinfo = lambda *args: [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (custom_resolver(args[0]), args[1]))]

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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

def test_dns():
    try:
        ip = custom_resolver('api.telegram.org')
        logger.info(f"Successfully resolved api.telegram.org to {ip}")
        return True
    except Exception as e:
        logger.error(f"DNS test failed: {e}")
        return False

if __name__ == '__main__':
    logger.info("Bot starting...")
    try:
        # Проверяем DNS
        if not test_dns():
            logger.error("DNS resolution test failed")
            exit(1)
            
        # Запускаем health check сервер в отдельном потоке
        health_thread = Thread(target=run_health_server, daemon=True)
        health_thread.start()
        logger.info("Health check server thread started")
        
        # Запускаем бота
        logger.info("Starting bot polling...")
        bot.infinity_polling()
    except Exception as e:
        logger.error(f"Error during startup: {e}")
