import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

# Инициализация на обектите
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# Настройка на LoginManager
login_manager.login_view = 'main.login'  # Пренасочва тук, ако страницата изисква вход
login_manager.login_message = "Моля, влезте в профила си, за да достъпите тази страница."
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    # Импортираме User тук, за да избегнем Circular Import
    from app.models import User
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Инициализация на разширенията с контекста на приложението
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Регистриране на Blueprint
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    # Създаване на папка за снимки, ако не съществува
    with app.app_context():
        upload_path = os.path.join(app.static_folder, 'uploads', 'cars')
        if not os.path.exists(upload_path):
            os.makedirs(upload_path, exist_ok=True)
            print(f"Създадена директория за снимки: {upload_path}")

    return app