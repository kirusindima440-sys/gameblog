import telebot
import os
from dotenv import load_dotenv
from models import TelegramSubscriber

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

def escape_html(text):
    """Экранирует специальные символы для HTML"""
    if not text:
        return ""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;'))

def send_notification_to_all(review):
    """Отправляет уведомление о новом обзоре ВСЕМ подписчикам"""
    subscribers = TelegramSubscriber.query.all()
    
    if not subscribers:
        print("Нет подписчиков для уведомления")
        return
    
    game_title = escape_html(review.game.title)
    author_name = escape_html(review.author.username)
    
    message = f"""🎮 <b>НОВЫЙ ОБЗОР!</b>

📝 <b>Игра:</b> {game_title}
👤 <b>Автор:</b> {author_name}
⭐ <b>Рейтинг:</b> {review.rating}/5
❤️ <b>Лайков:</b> {review.likes_count}

🔗 <b>Читать:</b> https://dimonstr.pythonanywhere.com/review/{review.id}"""
    
    success_count = 0
    for sub in subscribers:
        try:
            bot.send_message(sub.chat_id, message, parse_mode='HTML')
            success_count += 1
        except Exception as e:
            print(f"Ошибка отправки подписчику {sub.chat_id}: {e}")
    
    print(f"✅ Уведомление отправлено {success_count} из {len(subscribers)} подписчикам")