from flask_login import UserMixin
from . import db
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False) # Ново поле
    is_admin = db.Column(db.Boolean, default=False)
    cars = db.relationship('Car', backref='author', lazy=True)
class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    horsepower = db.Column(db.Integer, nullable=False)
    fuel = db.Column(db.String(30), nullable=False)  # Бензин, Дизел, Електро, Хибрид, LPG
    mileage = db.Column(db.Integer, nullable=False)  # пробег в км
    engine_size = db.Column(db.Integer, nullable=False)  # кубатура в ccm
    transmission = db.Column(db.String(20), nullable=False)  # Ръчна / Автоматична
    color = db.Column(db.String(30), nullable=False)
    euro_standard = db.Column(db.String(10))  # Euro 1–6, не е задължително
    doors = db.Column(db.Integer, nullable=False)  # 2/3, 4/5
    condition = db.Column(db.String(20), nullable=False, default="Употребявана")  # Нова, Употребявана, За части
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Множество снимки
    images = db.relationship('CarImage', backref='car', lazy=True, cascade="all, delete-orphan")

class CarImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    is_main = db.Column(db.Boolean, default=False)  # главна снимка