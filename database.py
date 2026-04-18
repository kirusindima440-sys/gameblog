from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Создаем объект для работы с БД
db = SQLAlchemy()

# Функция для подключения БД к приложению
def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gameblog.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    # Создаем таблицы (если их нет)
    with app.app_context():
        db.create_all()
        print("✅ База данных готова!")