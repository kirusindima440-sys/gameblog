from app import app
from database import db
from models import User

with app.app_context():
    user = User.query.filter_by(username='DIMONSTR').first()
    if user:
        user.is_admin = True
        db.session.commit()
        print(f"{user.username} теперь админ!")
    else:
        print("Пользователь не найден")