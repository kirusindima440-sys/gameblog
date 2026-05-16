from flask import Flask, render_template, request, redirect, url_for, flash, session
from bad_words import contains_bad_words
from flask_login import LoginManager, login_user, logout_user, login_required, current_user  # ИСПРАВЛЕНО!
from database import db, init_db
from models import Review, User, Game
from sqlalchemy.exc import IntegrityError
import os                        
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'idi-ot-syda'


UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'avatars')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 МБ

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# Подключаем базу данных
init_db(app)

# 👇 НАСТРОЙКА FLASK-LOGIN
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 
login_manager.login_message = 'Пожалуйста, войдите в систему'  


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
    """Главная страница с пагинацией и сортировкой"""
    
    # Получаем параметры из URL
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'date')  # date, rating, views
    
    # Количество обзоров на странице
    per_page = 10
    
    # Выбираем сортировку
    if sort == 'rating':
        order = Review.rating.desc()
    elif sort == 'views':
        order = Review.views.desc()
    else:  # date (по умолчанию)
        order = Review.created_at.desc()
    
    # Получаем обзоры с пагинацией и сортировкой
    pagination = Review.query.order_by(order).paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    reviews = pagination.items
    
    return render_template(
        'index.html', 
        reviews=reviews,
        pagination=pagination,
        current_sort=sort
    )



@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_review():
    if request.method == 'POST':
        game_name = request.form['game_name']
        genre = request.form['genre']
        rating = int(request.form['rating'])
        review_text = request.form['review_text']

        # 👇 ПРОВЕРКА НА МАТ
        if contains_bad_words(game_name):
            flash('Название игры содержит неприемлемые слова!', 'danger')
            return render_template('add_review.html')
        
        if contains_bad_words(review_text):
            flash('Текст обзора содержит неприемлемые слова!', 'danger')
            return render_template('add_review.html')





        
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


        # 👇 ПРОВЕРКА НА МАТ
        if contains_bad_words(game_name):
            flash('Название игры содержит неприемлемые слова!', 'danger')
            return render_template('edit_review.html', review=review)
        
        if contains_bad_words(review_text):
            flash('Текст обзора содержит неприемлемые слова!', 'danger')
            return render_template('edit_review.html', review=review)







        
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

@app.route('/admin')
@login_required
def admin_panel():
    """Админ-панель — только для админов"""
    if not current_user.is_admin:
        flash('У вас нет прав доступа к админ-панели', 'danger')
        return redirect(url_for('home'))
    
    # Получаем все обзоры (всех пользователей)
    all_reviews = Review.query.order_by(Review.created_at.desc()).all()
    all_users = User.query.all()
    all_games = Game.query.all()
    
    return render_template('admin.html', 
                         reviews=all_reviews, 
                         users=all_users, 
                         games=all_games)


@app.route('/admin/delete_review/<int:review_id>')
@login_required
def admin_delete_review(review_id):
    """Админ может удалить ЛЮБОЙ обзор"""
    if not current_user.is_admin:
        flash('У вас нет прав', 'danger')
        return redirect(url_for('home'))
    
    review = Review.query.get_or_404(review_id)
    
    # Сохраняем название игры ДО удаления
    game_title = review.game.title
    
    db.session.delete(review)
    db.session.commit()
    
    flash(f'Обзор "{game_title}" удалён админом!', 'success')
    return redirect(url_for('admin_panel'))




@app.route('/search')
def search():
    """Страница результатов поиска"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return redirect(url_for('home'))
    
    # Ищем игры, содержащие запрос
    games = Game.query.filter(Game.title.contains(query)).all()
    game_ids = [game.id for game in games]
    
    # Находим обзоры этих игр
    reviews = Review.query.filter(Review.game_id.in_(game_ids)).order_by(
        Review.created_at.desc()
    ).all()
    
    return render_template('search.html', reviews=reviews, query=query)










@app.route('/upload_avatar', methods=['GET', 'POST'])
@login_required
def upload_avatar():
    # ========== ПОСТ (обработка отправленной формы) ==========
    if request.method == 'POST':
        # 1. Проверяем, есть ли файл в запросе
        if 'avatar' not in request.files:
            flash('Файл не выбран', 'danger')
            return redirect(url_for('profile'))
        
        file = request.files['avatar']
        
        # 2. Проверяем, выбрал ли пользователь файл (не пустое поле)
        if file.filename == '':
            flash('Файл не выбран', 'danger')
            return redirect(url_for('profile'))
        
        # 3. Проверяем расширение файла
        if not allowed_file(file.filename):
            flash('Неподдерживаемый формат. Используйте: PNG, JPG, JPEG, GIF, WEBP', 'danger')
            return redirect(url_for('profile'))
        
        # 4. Формируем безопасное имя файла
        filename = secure_filename(f"user_{current_user.id}_{file.filename}")
        
        # 5. Сохраняем файл на диск
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # 6. Удаляем старую аватарку (если она не стандартная)
        if current_user.avatar != 'default.jpg':
            old_path = os.path.join(app.config['UPLOAD_FOLDER'], current_user.avatar)
            if os.path.exists(old_path):
                os.remove(old_path)
        
        # 7. Обновляем базу данных
        current_user.avatar = filename
        db.session.commit()
        
        flash('Аватарка обновлена!', 'success')
        return redirect(url_for('profile'))
    
    # ========== GET (показ формы) ==========
    return render_template('upload_avatar.html')












@app.route('/api/reviews')
def api_reviews():
    """API: список всех обзоров в формате JSON"""
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    
    # Превращаем объекты в словари (JSON)
    reviews_list = []
    for review in reviews:
        reviews_list.append({
            'id': review.id,
            'game': review.game.title,
            'genre': review.game.genre,
            'rating': review.rating,
            'author': review.author.username,
            'text': review.review_text[:200],  # только начало
            'views': review.views,
            'created_at': review.created_at.strftime('%d.%m.%Y')
        })
    
    return reviews_list  # Flask сам превратит в JSON





@app.route('/api/review/<int:review_id>')
def api_review(review_id):
    """API: один обзор в формате JSON"""
    review = Review.query.get_or_404(review_id)
    
    return {
        'id': review.id,
        'game': review.game.title,
        'genre': review.game.genre,
        'rating': review.rating,
        'author': review.author.username,
        'text': review.review_text,
        'views': review.views,
        'created_at': review.created_at.strftime('%d.%m.%Y')
    }




@app.route('/api/games')
def api_games():
    """API: список всех игр"""
    games = Game.query.all()
    
    games_list = []
    for game in games:
        games_list.append({
            'id': game.id,
            'title': game.title,
            'genre': game.genre,
            'reviews_count': Review.query.filter_by(game_id=game.id).count()
        })
    
    return games_list






@app.route('/api/users')
def api_users():
    """API: список всех пользователей"""
    users = User.query.all()
    
    users_list = []
    for user in users:
        users_list.append({
            'id': user.id,
            'username': user.username,
            'reviews_count': len(user.reviews),
            'joined': user.created_at.strftime('%d.%m.%Y')
        })
    
    return users_list



@app.route('/api/search')
def api_search():
    """API: поиск обзоров по названию игры"""
    query = request.args.get('q', '')
    
    if not query:
        return {'error': 'Укажите параметр q'}, 400
    
    # Ищем игры, в названии которых есть query
    games = Game.query.filter(Game.title.contains(query)).all()
    game_ids = [game.id for game in games]
    
    reviews = Review.query.filter(Review.game_id.in_(game_ids)).all()
    
    results = []
    for review in reviews:
        results.append({
            'id': review.id,
            'game': review.game.title,
            'author': review.author.username,
            'rating': review.rating
        })
    
    return results



























if __name__ == '__main__':
    app.run(debug=True, port=5000)