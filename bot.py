import telebot
import sys
import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')

# Проверка, что токен загрузился
if not TOKEN:
    print("❌ ОШИБКА: BOT_TOKEN не найден в .env файле!")
    sys.exit(1)

bot = telebot.TeleBot(TOKEN)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from database import db
from models import Review, TelegramSubscriber, User


bot = telebot.TeleBot(TOKEN)

# Функция для экранирования HTML-символов
def escape_html(text):
    """Экранирует специальные символы для HTML"""
    if not text:
        return ""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;'))


# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 
        '🎮 Привет! Я бот игрового блога GameBlog!\n\n'
        '📝 Команды:\n'
        '/subscribe — подписаться на новые обзоры\n'
        '/unsubscribe — отписаться\n'
        '/latest — последние 5 обзоров\n'
        '/review_<id> — обзор по ID'
    )

# ПОДПИСКА
@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    chat_id = message.chat.id
    telegram_username = message.from_user.username
    
    with app.app_context():
        existing_sub = TelegramSubscriber.query.filter_by(chat_id=chat_id).first()
        if existing_sub:
            bot.reply_to(message, '✅ Вы уже подписаны на уведомления!')
            return
        
        user = User.query.filter_by(username=telegram_username).first()
        
        if not user:
            bot.reply_to(
                message,
                f'❌ Пользователь с именем "{telegram_username}" не найден на сайте.\n\n'
                f'Возможные действия:\n'
                f'1️⃣ Зарегистрируйтесь на сайте: https://dimonstr.pythonanywhere.com/register\n'
                f'2️⃣ Убедитесь, что ваш username в Telegram совпадает с username на сайте\n'
                f'3️⃣ Используйте команду /force_subscribe ВАШ_ЛОГИН_НА_САЙТЕ\n\n'
                f'Пример: /force_subscribe DIMONCHK'
            )
            return
        
        new_sub = TelegramSubscriber(user_id=user.id, chat_id=chat_id)
        db.session.add(new_sub)
        db.session.commit()
        
        bot.reply_to(
            message,
            f'✅ Вы подписаны на уведомления, {user.username}!\n\n'
            f'Теперь вы будете получать сообщения о новых обзорах.'
        )

@bot.message_handler(commands=['force_subscribe'])
def force_subscribe(message):
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(
                message,
                '❌ Неправильный формат!\n'
                'Используйте: /force_subscribe ВАШ_ЛОГИН_НА_САЙТЕ\n\n'
                'Пример: /force_subscribe DIMONSTR'
            )
            return
        
        site_username = parts[1]
        chat_id = message.chat.id
        
        with app.app_context():
            existing_sub = TelegramSubscriber.query.filter_by(chat_id=chat_id).first()
            if existing_sub:
                bot.reply_to(message, '✅ Вы уже подписаны на уведомления!')
                return
            
            user = User.query.filter_by(username=site_username).first()
            if not user:
                bot.reply_to(
                    message,
                    f'❌ Пользователь "{site_username}" не найден на сайте!\n\n'
                    f'Проверьте правильность написания или зарегистрируйтесь:\n'
                    f'https://dimonstr.pythonanywhere.com/register'
                )
                return
            
            new_sub = TelegramSubscriber(user_id=user.id, chat_id=chat_id)
            db.session.add(new_sub)
            db.session.commit()
            
            bot.reply_to(
                message,
                f'✅ Вы успешно подписаны на уведомления как {user.username}!'
            )
    except Exception as e:
        bot.reply_to(message, f'❌ Произошла ошибка: {str(e)}')

# ОТПИСКА
@bot.message_handler(commands=['unsubscribe'])
def unsubscribe(message):
    chat_id = message.chat.id
    
    with app.app_context():
        subscriber = TelegramSubscriber.query.filter_by(chat_id=chat_id).first()
        if subscriber:
            db.session.delete(subscriber)
            db.session.commit()
            bot.reply_to(message, '✅ Вы отписались от уведомлений')
        else:
            bot.reply_to(message, '❌ Вы не были подписаны')

# ПОСЛЕДНИЕ ОБЗОРЫ
@bot.message_handler(commands=['latest'])
def send_latest_reviews(message):
    with app.app_context():
        reviews = Review.query.order_by(Review.created_at.desc()).limit(5).all()
        if not reviews:
            bot.reply_to(message, '😢 Пока нет обзоров!')
            return
        
        result = "📝 <b>Последние 5 обзоров:</b>\n\n"
        for r in reviews:
            game_title = escape_html(r.game.title)
            author_name = escape_html(r.author.username)
            
            result += f"🎮 <b>{game_title}</b>\n"
            result += f"⭐ Рейтинг: {r.rating}/5\n"
            result += f"👤 Автор: {author_name}\n"
            result += f"🔗 /review_{r.id}\n\n"
        
        bot.reply_to(message, result, parse_mode='HTML')

# ОБЗОР ПО ID
@bot.message_handler(func=lambda message: message.text.startswith('/review_'))
def send_review(message):
    try:
        review_id = int(message.text.split('_')[1])
        with app.app_context():
            review = Review.query.get(review_id)
            if review:
                game_title = escape_html(review.game.title)
                author_name = escape_html(review.author.username)
                review_text = escape_html(review.review_text[:200])
                
                text = f"🎮 <b>{game_title}</b>\n"
                text += f"⭐ Рейтинг: {review.rating}/5\n"
                text += f"👤 Автор: {author_name}\n"
                text += f"❤️ Лайков: {review.likes_count}\n"
                text += f"👁️ Просмотров: {review.views}\n\n"
                text += f"📝 {review_text}...\n\n"
                text += f"🔗 Читать: https://dimonstr.pythonanywhere.com/review/{review.id}"
                
                bot.reply_to(message, text, parse_mode='HTML')
            else:
                bot.reply_to(message, '❌ Обзор не найден!')
    except:
        bot.reply_to(message, '❌ Ошибка!')

print('🤖 Бот запущен...')
bot.infinity_polling()
