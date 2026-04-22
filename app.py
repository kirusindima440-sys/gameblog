from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user  # ИСПРАВЛЕНО!
from database import db, init_db
from models import Review, User, Game
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'idi-ot-syda'

# Подключаем базу данных
init_db(app)

# 👇 НАСТРОЙКА FLASK-LOGIN
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 
login_manager.login_message = 'Пожалуйста, войдите в систему'  # ИСПРАВЛЕНО!


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login вызывает эту функцию, чтобы получить пользователя по ID"""
    return User.query.get(int(user_id))


# Вспомогательная функция для поиска или создания игры
def get_or_create_game(title, genre):
    """Находит игру по названию или создаёт новую"""
    game = Game.query.filter_by(title=title).first()
    if not game:
        game = Game(title=title, genre=genre)
        db.session.add(game)
        db.session.commit()
    return game


@app.route('/')
def home():
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('index.html', reviews=reviews)




@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_review():
    if request.method == 'POST':
        game_name = request.form['game_name']
        genre = request.form['genre']
        rating = int(request.form['rating'])
        review_text = request.form['review_text']
        
        # Находим или создаём игру
        game = get_or_create_game(game_name, genre)
        
        new_review = Review(
            rating=rating,
            review_text=review_text,
            user_id=current_user.id,
            game_id=game.id
        )
        
        db.session.add(new_review)
        db.session.commit()
        
        flash('Обзор добавлен!', 'success')
        return redirect(url_for('home'))
    
    return render_template('add_review.html')


@app.route('/review/<int:review_id>')
@login_required 
def show_review(review_id):
    review = Review.query.get_or_404(review_id)

    # Создаём ключ для этого обзора в сессии
    viewed_key = f'viewed_review_{review_id}'
    
    # Если пользователь ещё не смотрел этот обзор
    if not session.get(viewed_key):
        review.views += 1
        db.session.commit()
        session[viewed_key] = True  # Запоминаем, что смотрел
    
    return render_template('review.html', review=review)
@app.route('/games')
@login_required
def games_list():
    """Список всех игр"""
    games = Game.query.all()
    # Для каждой игры считаем количество обзоров
    for game in games:
        game.reviews_count = Review.query.filter_by(game_id=game.id).count()
    return render_template('games.html', games=games)


@app.route('/game/<int:game_id>')
@login_required
def show_game(game_id):
    """Страница одной игры со всеми обзорами"""
    game = Game.query.get_or_404(game_id)
    reviews = Review.query.filter_by(game_id=game_id).order_by(Review.created_at.desc()).all()
    return render_template('game_detail.html', game=game, reviews=reviews)




@app.route('/users')
@login_required
def users_list():
    """Список всех авторов"""
    users = User.query.all()
    return render_template('users.html', users=users)


@app.route('/user/<int:user_id>')
@login_required
def show_user(user_id):
    """Страница одного автора со всеми его обзорами"""
    user = User.query.get_or_404(user_id)
    reviews = Review.query.filter_by(user_id=user_id).order_by(Review.created_at.desc()).all()
    return render_template('user_detail.html', user=user, reviews=reviews)






@app.route('/edit/<int:review_id>', methods=['GET', 'POST'])
@login_required  # Только залогиненные могут редактировать
def edit_review(review_id):
    review = Review.query.get_or_404(review_id)
    
    # Проверка: только автор может редактировать свой обзор
    if review.user_id != current_user.id:
        flash('Вы можете редактировать только свои обзоры!', 'danger')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        game_name = request.form['game_name']
        genre = request.form['genre']
        rating = int(request.form['rating'])
        review_text = request.form['review_text']
        
        # Находим или создаём игру
        game = get_or_create_game(game_name, genre)
        
        # Обновляем обзор
        review.rating = rating
        review.review_text = review_text
        review.game_id = game.id
        
        db.session.commit()
        flash('Обзор обновлён!', 'success')
        return redirect(url_for('show_review', review_id=review.id))
    
    return render_template('edit_review.html', review=review)


@app.route('/delete/<int:review_id>')
@login_required  # Только залогиненные могут удалять
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    
    # Проверка: только автор может удалить свой обзор
    if review.user_id != current_user.id:
        flash('Вы можете удалять только свои обзоры!', 'danger')
        return redirect(url_for('home'))
    
    db.session.delete(review)
    db.session.commit()
    flash('Обзор удалён!', 'success')
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        if not username or not email or not password:
            flash('Все поля обязательны для заполнения', 'danger')
            return render_template('register.html')
        
        if password != password_confirm:
            flash('Пароли не совпадают', 'danger')
            return render_template('register.html')
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Пользователь с таким именем уже существует', 'danger')
            return render_template('register.html')
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Пользователь с таким email уже существует', 'danger')
            return render_template('register.html')
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Регистрация успешна! Теперь войдите в систему', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f'Добро пожаловать, {user.username}!', 'success')
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('home'))
        else:
            flash('Неверное имя пользователя или пароль', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('home'))


@app.route('/profile')
@login_required
def profile():
    # Получаем все обзоры текущего пользователя
    user_reviews = Review.query.filter_by(user_id=current_user.id).order_by(Review.created_at.desc()).all()
    return render_template('profile.html', user=current_user, reviews=user_reviews)


@app.route('/setup')
def setup():
    db.drop_all()
    db.create_all()
    
    # Создаём пользователя для примера
    user = User(username='dimon', email='dimon@mail.ru')
    user.set_password('12345')
    db.session.add(user)
    
    # Создаём игру для примера
    game = Game(title='The Witcher 3', genre='RPG')
    db.session.add(game)
    db.session.commit()
    
    return "База данных готова! <a href='/'>На главную</a>"


if __name__ == '__main__':
    app.run(debug=True, port=5000)