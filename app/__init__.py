import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate          # ← ДОБАВЕНО
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()                         # ← ДОБАВЕНО
login_manager = LoginManager()
login_manager.login_view = 'routes.login'
login_manager.login_message_category = "info"

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Създаване на папка за снимки
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Инициализация
    db.init_app(app)
    migrate.init_app(app, db)               # ← ТОВА Е КЛЮЧЪТ!
    login_manager.init_app(app)

    # Импорт на модели и руутове
    from .models import User
    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Създаване на таблици + админ
    with app.app_context():
        db.create_all()
        if not User.query.first():
            from werkzeug.security import generate_password_hash
            admin = User(
                username='admin',
                email='admin@carmarket.bg',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            print("СЪЗДАДЕН Е АДМИН: admin / admin123")

    return app