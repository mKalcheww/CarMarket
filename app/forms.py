from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange
from app.constants import CAR_BRANDS
import datetime

# Генерираме списък с години от текущата назад до 1950
current_year = datetime.datetime.now().year
YEAR_CHOICES = [(str(y), str(y)) for y in range(current_year, 1949, -1)]

class RegistrationForm(FlaskForm):
    username = StringField('Потребителско име', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Имейл', validators=[DataRequired(), Email()])
    phone_number = StringField('Телефонен номер', validators=[DataRequired()])
    password = PasswordField('Парола', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Потвърди парола', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Регистрирай се')

class LoginForm(FlaskForm):
    username = StringField('Потребителско име', validators=[DataRequired()])
    password = PasswordField('Парола', validators=[DataRequired()])
    submit = SubmitField('Вход')

class CarForm(FlaskForm):
    brand = SelectField('Марка', choices=[('', 'Изберете марка')] + [(b, b) for b in sorted(CAR_BRANDS.keys())], validators=[DataRequired()])
    model = SelectField('Модел', choices=[('', 'Първо изберете марка')], validators=[DataRequired()])
    year = SelectField('Година', choices=YEAR_CHOICES, validators=[DataRequired()])
    price = IntegerField('Цена (€)', validators=[DataRequired()])
    horsepower = IntegerField('Конски сили', validators=[DataRequired()])
    engine_size = IntegerField('Кубатура (ccm)', validators=[DataRequired()])
    fuel_type = SelectField('Гориво', choices=[('Бензин', 'Бензин'), ('Дизел', 'Дизел'), ('Електрически', 'Електрически'), ('Хибрид', 'Хибрид')], validators=[DataRequired()])
    mileage = IntegerField('Пробег (км)', validators=[DataRequired()])
    transmission = SelectField('Скоростна кутия', choices=[('Ръчна', 'Ръчна'), ('Автоматична', 'Автоматична')], validators=[DataRequired()])
    color = StringField('Цвят', validators=[DataRequired()])
    doors = SelectField('Брой врати', choices=[('2/3', '2/3'), ('4/5', '4/5')], validators=[DataRequired()])
    condition = SelectField('Състояние', choices=[('Нова', 'Нова'), ('Употребявана', 'Употребявана')], validators=[DataRequired()])
    description = TextAreaField('Описание')
    submit = SubmitField('Публикувай обявата')

class SearchForm(FlaskForm):
    brand = SelectField('Марка', choices=[('', 'Всички марки')] + [(b, b) for b in sorted(CAR_BRANDS.keys())])
    model = SelectField('Модел', choices=[('', 'Всички модели')])
    
    # Цена
    min_price = IntegerField('Мин. цена (€)')
    max_price = IntegerField('Макс. цена (€)')
    
    # Година
    min_year = SelectField('От година', choices=[('', '---')] + YEAR_CHOICES)
    max_year = SelectField('До година', choices=[('', '---')] + YEAR_CHOICES)

    # Технически характеристики
    fuel_type = SelectField('Гориво', choices=[('', 'Всички'), ('Бензин', 'Бензин'), ('Дизел', 'Дизел'), ('Електрически', 'Електрически'), ('Хибрид', 'Хибрид'), ('Газ/Бензин', 'Газ/Бензин')])
    transmission = SelectField('Трансмисия', choices=[('', 'Всички'), ('Ръчна', 'Ръчна'), ('Автоматична', 'Автоматична')])
    condition = SelectField('Състояние', choices=[('', 'Всички'), ('Нова', 'Нова'), ('Употребявана', 'Употребявана'), ('За части', 'За части')])
    
    # НОВИ ФИЛТРИ
    doors = SelectField('Врати', choices=[('', 'Всички'), ('2/3', '2/3'), ('4/5', '4/5')])
    color = StringField('Цвят')
    min_hp = IntegerField('Мин. к.с.')
    max_hp = IntegerField('Макс. к.с.')
    
    submit = SubmitField('Търси')