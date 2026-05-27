import telebot
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from database import db
from models import Review, TelegramSubscriber, User

TOKEN = ''
bot = telebot.TeleBot(TOKEN)

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
        # 1. Проверяем, есть ли уже подписка у этого chat_id
        existing_sub = TelegramSubscriber.query.filter_by(chat_id=chat_id).first()
        if existing_sub:
            bot.reply_to(message, '✅ Вы уже подписаны на уведомления!')
            return
        
        # 2. Ищем пользователя на сайте по username из Telegram
        user = User.query.filter_by(username=telegram_username).first()
        
        # 3. Если не нашли — предлагаем варианты
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
        
        # 4. Всё хорошо — создаём подписку
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
        # Разбираем команду: /force_subscribe DIMONSTR
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
            # Проверяем, есть ли уже подписка
            existing_sub = TelegramSubscriber.query.filter_by(chat_id=chat_id).first()
            if existing_sub:
                bot.reply_to(message, '✅ Вы уже подписаны на уведомления!')
                return
            
            # Ищем пользователя по указанному логину
            user = User.query.filter_by(username=site_username).first()
            if not user:
                bot.reply_to(
                    message,
                    f'❌ Пользователь "{site_username}" не найден на сайте!\n\n'
                    f'Проверьте правильность написания или зарегистрируйтесь:\n'
                    f'https://dimonstr.pythonanywhere.com/register'
                )
                return
            
            # Создаём подписку
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
        
        result = "📝 **Последние 5 обзоров:**\n\n"
        for r in reviews:
            result += f"🎮 **{r.game.title}**\n"
            result += f"⭐ Рейтинг: {r.rating}/5\n"
            result += f"👤 Автор: {r.author.username}\n"
            result += f"🔗 /review_{r.id}\n\n"
        bot.reply_to(message, result, parse_mode='Markdown')

# ОБЗОР ПО ID
@bot.message_handler(func=lambda message: message.text.startswith('/review_'))
def send_review(message):
    try:
        review_id = int(message.text.split('_')[1])
        with app.app_context():
            review = Review.query.get(review_id)
            if review:
                text = f"🎮 **{review.game.title}**\n"
                text += f"⭐ Рейтинг: {review.rating}/5\n"
                text += f"👤 Автор: {review.author.username}\n"
                text += f"❤️ Лайков: {review.likes_count}\n"
                text += f"👁️ Просмотров: {review.views}\n\n"
                text += f"📝 {review.review_text[:200]}...\n\n"
                text += f"🔗 Читать: https://dimonstr.pythonanywhere.com/review/{review.id}"
                bot.reply_to(message, text, parse_mode='Markdown')
            else:
                bot.reply_to(message, '❌ Обзор не найден!')
    except:
        bot.reply_to(message, '❌ Ошибка!')

print('🤖 Бот запущен...')
bot.infinity_polling()
