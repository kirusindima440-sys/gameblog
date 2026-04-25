from database import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash



class User(db.Model, UserMixin):
    """Модель пользователя"""
    
    __tablename__ = 'users'
    
<<<<<<< HEAD
    id = db.Column(db.Integer, primary_key=True)  
=======
    id = db.Column(db.Integer, primary_key=True)  # было primaty_key
>>>>>>> 5dcdb43 (add admin panel)
    is_admin = db.Column(db.Boolean, default=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)  
    password_hash = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  

    # СВЯЗЬ: один пользователь -> много обзоров
    reviews = db.relationship('Review', backref='author', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'



    def set_password(self, password):
        """Хеширует пароль и сохраняет в password_hash"""
        self.password_hash = generate_password_hash(password)


    def check_password(self, password):
        """Проверяет, совпадает ли введённый пароль с хешем"""
        return check_password_hash(self.password_hash, password)


class Game(db.Model):  # было class = Game
    """Модель игры"""
    
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), unique=True, nullable=False)
    genre = db.Column(db.String(100), nullable=False)  # было ganre и Strong
    release_year = db.Column(db.Integer)
    
    # СВЯЗЬ: одна игра -> много обзоров
    reviews = db.relationship('Review', backref='game', lazy=True)

    def __repr__(self):
        return f'<Game {self.title}>'


class Review(db.Model):
    """Модель для обзоров игр"""
    
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    
    # ВНЕШНИЕ КЛЮЧИ
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    
    def __repr__(self):
        return f'<Review {self.game.title if hasattr(self, "game") else "No game"}>'
    
    @property
    def stars(self):
        return '⭐' * self.rating + '☆' * (5 - self.rating)
    
    @property
    def short_review(self):
        if len(self.review_text) > 50:
            return self.review_text[:50] + '...'
        return self.review_text
