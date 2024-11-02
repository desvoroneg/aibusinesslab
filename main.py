import os
import telebot
import logging
import socket
import dns.resolver

# Настройка DNS
dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8', '8.8.4.4']

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
ADMIN_ID = os.getenv('ADMIN_ID')

# Настройка для работы за прокси
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

socket.getaddrinfo = custom_resolver

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(TOKEN, state_storage=state_storage)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
👋 Привет! Я бот канала AI Business Lab.

Через меня вы можете получить чек-лист "20 процессов в вашем бизнесе, которые можно автоматизировать прямо сейчас с помощью AI"

Чтобы получить чек-лист:
1. Подпишитесь на канал @AIBusinessLab
2. Отправьте команду /checklist

🎁 Желаю продуктивной автоматизации!
    """
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['checklist'])
def handle_checklist_request(message):
    user_id = message.from_user.id
    username = message.from_user.username
    
    try:
        user_channel_status = bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        is_subscribed = user_channel_status.status in ['member', 'administrator', 'creator']
        
        if is_subscribed:
            with open('checklist.pdf', 'rb') as checklist:
                bot.send_document(
                    message.chat.id,
                    checklist,
                    caption="Спасибо за подписку! Вот ваш чек-лист по автоматизации бизнес-процессов 🎁"
                )
            # Уведомление админу
            bot.send_message(
                ADMIN_ID,
                f"Новая выдача чек-листа!\nUser: @{username}\nID: {user_id}"
            )
        else:
            bot.reply_to(
                message,
                f"Для получения чек-листа подпишитесь на канал @AIBusinessLab и попробуйте снова!"
            )
    except Exception as e:
        logger.error(f"Error: {e}")
        bot.reply_to(
            message,
            "Произошла ошибка. Пожалуйста, попробуйте позже или напишите в поддержку."
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
    try:
        logger.info("Testing DNS resolution...")
        test_ip = socket.gethostbyname('api.telegram.org')
        logger.info(f"DNS resolution successful: {test_ip}")
        bot.infinity_polling()
    except Exception as e:
        logger.error(f"Startup error: {e}")
