# 🎮 GameBlog — Игровой блог на Flask

**Живой демо-сайт:** https://dimonstr.pythonanywhere.com  
**Telegram-бот:** @GameBlogSuper_bot

---

## 📝 О проекте

GameBlog — это полноценный веб-сайт для публикации обзоров на игры.  
Пользователи могут регистрироваться, писать обзоры, оставлять комментарии, ставить лайки и загружать аватарки.

---

## 🛠️ Использованные технологии

- **Backend:** Python 3, Flask, Flask-Login, Flask-SQLAlchemy
- **Database:** SQLite (локально), SQLite (на сервере)
- **Frontend:** HTML5, CSS3, Bootstrap
- **Deployment:** PythonAnywhere, Git, GitHub
- **Integrations:** Telegram Bot API

---

## ✨ Основные возможности

| Функция | Описание |
|---------|----------|
| 🔐 **Регистрация и вход** | Пользователи могут создавать аккаунты и входить в систему |
| 👑 **Админ-панель** | Управление обзорами и пользователями |
| ✍️ **CRUD обзоров** | Создание, чтение, редактирование, удаление обзоров |
| 🖼️ **Аватарки** | Загрузка и отображение аватарок пользователей |
| 💬 **Комментарии** | Комментарии к обзорам с возможностью удаления |
| ❤️ **Лайки** | Пользователи могут ставить лайки на обзоры |
| 👁️ **Счётчик просмотров** | Отслеживание популярности обзоров |
| 🔍 **Поиск** | Поиск обзоров по названию игры |
| 📄 **Пагинация** | Разбиение списка обзоров на страницы |
| 📊 **Сортировка** | По дате, рейтингу, просмотрам, лайкам |
| 📱 **Адаптивный дизайн** | Сайт удобно смотреть с телефона |
| 🤖 **Telegram-бот** | Уведомления о новых обзорах, команды `/latest`, `/subscribe` |
| 🚫 **Мат-фильтр** | Защита от нецензурной лексики |



📸 Скриншоты
Главная страница
<img width="1920" height="1037" alt="home" src="https://github.com/user-attachments/assets/04cd67e1-d660-49cc-843f-4666f28f3688" />


Страница обзора
<img width="1920" height="1038" alt="review" src="https://github.com/user-attachments/assets/f2ac705b-be20-44b9-bab7-74ee17635393" />

Профиль пользователя
<img width="1920" height="1037" alt="profile" src="https://github.com/user-attachments/assets/c0ff0eda-4149-47e8-a787-4c3408f84275" />


Админ-панель
<img width="1920" height="1036" alt="admin" src="https://github.com/user-attachments/assets/ac2768d0-06fc-491f-9879-9db49f25965d" />


Добавление обзора
<img width="1920" height="1037" alt="add_review" src="https://github.com/user-attachments/assets/33888ac9-c293-4bdb-abd7-457f65625950" />





## 🚀 Как запустить локально

```bash
git clone https://github.com/kirusindima440-sys/gameblog.git
cd gameblog
pip install -r requirements.txt
python app.py
