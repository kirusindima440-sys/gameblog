import telebot
from database import db
from models import TelegramSubscriber

TOKEN = '8915543382:AAHiXCm6MkTbti4xsaJ5h4d3LGBmbs7Lgeo'
bot = telebot.TeleBot(TOKEN)

def send_notification_to_all(review):
    """Отправляет уведомление о новом обзоре ВСЕМ подписчикам"""
    # НЕ НУЖНО with app.app_context() - мы уже внутри контекста!
    subscribers = TelegramSubscriber.query.all()
    
    if not subscribers:
        print("Нет подписчиков для уведомления")
        return
    
    message = f"""🎮 **НОВЫЙ ОБЗОР!**

📝 **Игра:** {review.game.title}
👤 **Автор:** {review.author.username}
⭐ **Рейтинг:** {review.rating}/5
❤️ **Лайков:** {review.likes_count}

🔗 **Читать:** https://dimonstr.pythonanywhere.com/review/{review.id}
    """
    
    success_count = 0
    for sub in subscribers:
        try:
            bot.send_message(sub.chat_id, message, parse_mode='Markdown')
            success_count += 1
        except Exception as e:
            print(f"Ошибка отправки подписчику {sub.chat_id}: {e}")
    
    print(f"✅ Уведомление отправлено {success_count} из {len(subscribers)} подписчикам")