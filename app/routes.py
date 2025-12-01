# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Car, CarImage, db
from .forms import RegisterForm, LoginForm, CarForm
from werkzeug.utils import secure_filename
import os

bp = Blueprint('routes', __name__)

# Начало – всички коли
@bp.route('/')
def index():
    cars = Car.query.order_by(Car.created_at.desc()).all()
    return render_template('index.html', cars=cars)

# Регистрация
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        from werkzeug.security import generate_password_hash
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        flash('Регистрацията е успешна! Влез в профила си.', 'success')
        return redirect(url_for('routes.login'))
    return render_template('register.html', form=form)

# Вход
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        from werkzeug.security import check_password_hash
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Добре дошъл обратно!', 'success')
            return redirect(url_for('routes.index'))
        flash('Грешно потребителско име или парола', 'danger')
    return render_template('login.html', form=form)

# Изход
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Успешно излязохте от профила си', 'info')
    return redirect(url_for('routes.index'))

# Добавяне на кола – всеки регистриран потребител
import time
from werkzeug.utils import secure_filename

@bp.route('/add_car', methods=['GET', 'POST'])
@login_required
def add_car():
    form = CarForm()
    if form.validate_on_submit():
        car = Car(
            brand=form.brand.data,
            model=form.model.data,
            year=form.year.data,
            price=form.price.data,
            horsepower=form.horsepower.data,
            fuel=form.fuel.data or "Неизвестно",
            description=form.description.data,
            user_id=current_user.id
        )
        db.session.add(car)
        db.session.commit()
        return jsonify({'car_id': car.id})

    return render_template('add_car.html', form=form)


@bp.route('/upload_image/<int:car_id>', methods=['POST'])
@login_required
def upload_image(car_id):
    car = Car.query.get_or_404(car_id)
    if car.user_id != current_user.id:
        return jsonify(error="Нямате право"), 403

    if 'file' not in request.files:
        return jsonify(error="Няма файл"), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify(error="Празен файл"), 400

    # Първата снимка е главна
    is_main = CarImage.query.filter_by(car_id=car_id).count() == 0

    filename = secure_filename(f"{car_id}_{int(time.time())}_{file.filename}")
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(path)

    img = CarImage(filename=filename, car_id=car_id, is_main=is_main)
    db.session.add(img)
    db.session.commit()

    return jsonify({
        'success': True,
        'url': url_for('static', filename='uploads/cars/' + filename),
        'is_main': is_main
    })

# Моите обяви
@bp.route('/my_cars')
@login_required
def my_cars():
    cars = Car.query.filter_by(user_id=current_user.id).order_by(Car.created_at.desc()).all()
    return render_template('my_cars.html', cars=cars)

# Детайлен изглед на кола
@bp.route('/car/<int:id>')
def car_detail(id):
    car = Car.query.get_or_404(id)
    main_image = next((img for img in car.images if img.is_main), None)
    if not main_image and car.images:
        main_image = car.images[0]
    other_images = [img for img in car.images if img != main_image]
    return render_template('car_detail.html', car=car, main_image=main_image, other_images=other_images)

# Изтриване на обява (само собственик или админ)
@bp.route('/delete_car/<int:id>')
@login_required
def delete_car(id):
    car = Car.query.get_or_404(id)
    
    if car.user_id != current_user.id and not current_user.is_admin:
        flash('Нямате право да изтриете тази обява!', 'danger')
        return redirect(url_for('routes.index'))

    # Изтриваме снимките от диска
    for img in car.images:
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], img.filename)
        if os.path.exists(path):
            os.remove(path)

    db.session.delete(car)
    db.session.commit()
    flash('Обявата е изтрита успешно', 'success')
    return redirect(url_for('routes.my_cars') if car.user_id == current_user.id else url_for('routes.index'))