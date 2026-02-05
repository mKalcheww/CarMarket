import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

# Инициализация на разширенията извън фабриката
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message = "Моля, влезте в профила си, за да достъпите тази страница."
login_manager.login_message_category = "info"
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Инициализиране на разширенията с app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Регистрация на Blueprints
    from app.routes import bp
    app.register_blueprint(bp)

    with app.app_context():
        # СТРИКТНО ПРЕМАХВАМЕ db.create_all() тук.
        # Структурата ще се управлява само от Flask-Migrate.

        # Автоматично създаване на администраторски акаунт
        from app.models import User
        from werkzeug.security import generate_password_hash
        
        try:
            # Проверяваме дали таблицата User съществува, преди да търсим в нея
            # Това предотвратява грешки по време на 'flask db migrate'
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@carmarket.bg',
                    password_hash=generate_password_hash('admin123'),
                    is_admin=True
                )
                db.session.add(admin)
                db.session.commit()
                print("СЪЗДАДЕН Е АДМИН: admin / admin123")
        except Exception:
            # Ако таблиците не съществуват (при първи run), просто не правим нищо
            db.session.rollback()
            print("Базата все още няма таблици. Админ ще бъде създаден след 'flask db upgrade'.")

    return app