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

# КОРИГИРАНО: Тук беше грешката. Трябва да е 'routes.login', а не 'main.login'
login_manager.login_view = 'routes.login' 
login_manager.login_message = "Моля, влезте в профила си, за да достъпите тази страница."
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Инициализация на разширенията
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Регистриране на Blueprint
    # Внимавай тук: името на blueprint-а в routes.py трябва да е bp = Blueprint('routes', __name__)
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    # Създаване на папка за снимки, ако не съществува
    with app.app_context():
        upload_path = os.path.join(app.static_folder, 'uploads', 'cars')
        if not os.path.exists(upload_path):
            os.makedirs(upload_path, exist_ok=True)

    return app