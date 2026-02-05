from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange
from app.constants import CAR_BRANDS
import datetime

# Генерираме списък с години от текущата назад до 1950
current_year = datetime.datetime.now().year
YEAR_CHOICES = [(str(y), str(y)) for y in range(current_year, 1949, -1)]

class RegistrationForm(FlaskForm):
    username = StringField('Потребителско име', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Парола', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Потвърди Парола', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Регистрация')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Парола', validators=[DataRequired()])
    submit = SubmitField('Вход')

class CarForm(FlaskForm):
    # Марка - зарежда се от constants.py
    brand = SelectField('Марка', 
                        choices=[('', 'Изберете марка')] + [(b, b) for b in sorted(CAR_BRANDS.keys())], 
                        validators=[DataRequired()])
    
    # Модел - ще се пълни динамично чрез JS, но дефинираме начално състояние
    model = SelectField('Модел', choices=[('', 'Първо изберете марка')], validators=[DataRequired()])
    
    year = SelectField('Година на производство', choices=YEAR_CHOICES, validators=[DataRequired()])
    
    price = IntegerField('Цена (в лв.)', validators=[DataRequired(), NumberRange(min=1)])
    
    mileage = IntegerField('Пробег (км)', validators=[DataRequired(), NumberRange(min=0)])
    
    engine_size = IntegerField('Двигател (куб. см)', validators=[DataRequired(), NumberRange(min=500)])
    
    fuel_type = SelectField('Тип гориво', choices=[
        ('Бензин', 'Бензин'),
        ('Дизел', 'Дизел'),
        ('Газ/Бензин', 'Газ/Бензин'),
        ('Хибрид', 'Хибрид'),
        ('Електричество', 'Електричество')
    ], validators=[DataRequired()])
    
    transmission = SelectField('Скоростна кутия', choices=[
        ('Ръчна', 'Ръчна'),
        ('Автоматична', 'Автоматична')
    ], validators=[DataRequired()])
    
    condition = SelectField('Състояние', choices=[
        ('Употребяван', 'Употребяван'),
        ('Нов', 'Нов'),
        ('За части', 'За части')
    ], validators=[DataRequired()])
    
    description = TextAreaField('Допълнителна информация', validators=[Length(max=1000)])
    
    submit = SubmitField('Публикувай обявата')

class SearchForm(FlaskForm):
    brand = SelectField('Марка', choices=[('', 'Всички марки')] + [(b, b) for b in sorted(CAR_BRANDS.keys())])
    model = SelectField('Модел', choices=[('', 'Всички модели')])
    
    min_price = IntegerField('Мин. цена')
    max_price = IntegerField('Макс. цена')
    
    condition = SelectField('Състояние', choices=[
        ('', 'Всички'),
        ('Употребяван', 'Употребяван'),
        ('Нов', 'Нов')
    ])
    
    submit = SubmitField('Търси')