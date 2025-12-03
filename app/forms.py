from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, FloatField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange
from flask_wtf.file import FileAllowed

class RegisterForm(FlaskForm):
    username = StringField('Потребителско име', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Имейл', validators=[DataRequired(), Email()])
    password = PasswordField('Парола', validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField('Повтори парола', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Регистрация')

class LoginForm(FlaskForm):
    username = StringField('Потребител', validators=[DataRequired()])
    password = PasswordField('Парола', validators=[DataRequired()])
    submit = SubmitField('Вход')

class CarForm(FlaskForm):
    brand = StringField('Марка', validators=[DataRequired()])
    model = StringField('Модел', validators=[DataRequired()])
    year = IntegerField('Година', validators=[DataRequired(), NumberRange(min=1900, max=2026)])
    price = IntegerField('Цена (лв.)', validators=[DataRequired(), NumberRange(min=100)])
    horsepower = IntegerField('Конски сили', validators=[DataRequired(), NumberRange(min=30, max=2000)])
    fuel = SelectField('Гориво', choices=[
        ('Бензин', 'Бензин'),
        ('Дизел', 'Дизел'),
        ('Електрически', 'Електрически'),
        ('Хибрид', 'Хибрид'),
        ('Пропан-бутан', 'LPG')
    ], validators=[DataRequired()])
    mileage = IntegerField('Пробег (км)', validators=[DataRequired(), NumberRange(min=0, max=999999)])
    engine_size = IntegerField('Кубатура (ccm)', validators=[DataRequired(), NumberRange(min=500, max=8000)])
    transmission = SelectField('Скоростна кутия', choices=[
        ('Ръчна', 'Ръчна'),
        ('Автоматична', 'Автоматична')
    ], validators=[DataRequired()])
    color = StringField('Цвят', validators=[DataRequired()])
    doors = SelectField('Брой врати', choices=[(3, '2/3'), (5, '4/5')], validators=[DataRequired()])
    condition = SelectField('Състояние', choices=[
        ('Нова', 'Нова'),
        ('Употребявана', 'Употребявана'),
        ('За части', 'За части')
    ], validators=[DataRequired()])
    description = TextAreaField('Описание')
    submit = SubmitField('Публикувай обявата')