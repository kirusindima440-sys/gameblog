from database import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash



class User(db.Model, UserMixin):
    """Модель пользователя"""
    
    __tablename__ = 'users'
    

    


    id = db.Column(db.Integer, primary_key=True)  

    avatar = db.Column(db.String(200), default='default.jpg')

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
    
    # 👇 ДОБАВЬ ЭТИ МЕТОДЫ
    @property
    def likes_count(self):
        return Like.query.filter_by(review_id=self.id).count()
    
    def user_liked(self, user_id):
        return Like.query.filter_by(review_id=self.id, user_id=user_id).first() is not None


class Comment(db.Model):
    """Модель комментария к обзору"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Внешние ключи
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), nullable=False)
    
    # Связи
    author = db.relationship('User', backref='comments', lazy=True)
    review = db.relationship('Review', backref='comments', lazy=True)
    
    def __repr__(self):
        return f'<Comment by {self.author.username} on review {self.review_id}>'
    
    @property
    def short_text(self):
        if len(self.text) > 100:
            return self.text[:100] + '...'
        return self.text



class Like(db.Model):
    """Модель лайка к обзору"""
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Уникальность: один пользователь → один лайк на один обзор
    __table_args__ = (db.UniqueConstraint('user_id', 'review_id', name='unique_like'),)
    
    # Связи
    user = db.relationship('User', backref='user_likes')
    review = db.relationship('Review', backref='review_likes')








class TelegramSubscriber(db.Model):
    """Модель подписчика на Telegram-уведомления"""
    __tablename__ = 'telegram_subscribers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    chat_id = db.Column(db.BigInteger, nullable=False, unique=True)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связь с пользователем
    user = db.relationship('User', backref='telegram_subscription')
    
    def __repr__(self):
        return f'<Subscriber {self.user.username}>'