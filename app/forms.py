from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, FloatField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length
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
    year = IntegerField('Година', validators=[DataRequired()])
    price = FloatField('Цена (лв)', validators=[DataRequired()])
    horsepower = IntegerField('Конски сили')
    fuel = SelectField('Гориво', choices=[('Бензин', 'Бензин'), ('Дизел', 'Дизел'), ('Електричество', 'Електричество'), ('Хибрид', 'Хибрид')])
    description = TextAreaField('Описание')
    submit = SubmitField('Публикувай обявата')