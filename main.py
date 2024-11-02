import os
import telebot
import logging
import requests
import time
from flask import Flask
from threading import Thread

# Настройка Flask
app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot is running'

def run_flask():
    app.run(host='0.0.0.0', port=8000)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

bot = telebot.TeleBot(TOKEN)

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

# Запуск бота
if __name__ == '__main__':
    logger.info("Bot started")
    # Запускаем Flask в отдельном потоке
    Thread(target=run_flask).start()
    # Запускаем бота
    bot.infinity_polling()
