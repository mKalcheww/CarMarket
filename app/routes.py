# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app, jsonify, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Car, CarImage, db
from .forms import RegistrationForm, LoginForm, CarForm, SearchForm
from werkzeug.utils import secure_filename
import os
import time
from sqlalchemy.orm import joinedload
from werkzeug.security import generate_password_hash, check_password_hash # Явен импорт на security функциите
from functools import wraps
from app.constants import CAR_BRANDS
import os 
import google.generativeai as genai

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, 'is_admin', False):
            abort(403) # Forbidden
        return f(*args, **kwargs)
    return decorated_function

bp = Blueprint('routes', __name__)

# Начало – всички коли (N+1 fix)
@bp.route('/')
def index():
    # Използваме joinedload за да вземем снимките с една заявка
    cars = Car.query.options(joinedload(Car.images)).order_by(Car.created_at.desc()).all()
    return render_template('index.html', cars=cars)

@bp.route('/api/models/<brand>')
def get_models_api(brand):
    models = CAR_BRANDS.get(brand, [])
    return jsonify(models)

# Регистрация
@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # ПРОВЕРКА: Съществува ли вече такъв потребител?
        existing_user = User.query.filter_by(username=form.username.data).first()
        existing_email = User.query.filter_by(email=form.email.data).first()
        
        if existing_user:
            flash('Потребителското име вече е заето. Изберете друго.', 'danger')
            return render_template('register.html', form=form)
            
        if existing_email:
            flash('Този имейл вече е регистриран.', 'danger')
            return render_template('register.html', form=form)

        # Ако всичко е наред, създаваме потребителя
        user = User(
            username=form.username.data,
            email=form.email.data,
            phone_number=form.phone_number.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        try:
            db.session.commit()
            flash('Регистрацията е успешна! Вече можете да влезете.', 'success')
            return redirect(url_for('routes.login'))
        except Exception as e:
            db.session.rollback()
            flash('Възникна грешка при запис в базата данни.', 'danger')
            
    return render_template('register.html', form=form)

@bp.route('/get_models/<brand>')
def get_models(brand):
    models = db.session.query(Car.model).filter(Car.brand == brand).distinct().all()
    model_list = [m[0] for m in models]
    return jsonify(model_list)

# Вход
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
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

# Добавяне на кола – всеки регистриран потребител (WTF Validation fix)
@bp.route('/add_car', methods=['GET', 'POST'])
@login_required
def add_car():
    form = CarForm()
    
    # ВАЖНО: Преди validate_on_submit, трябва да попълним choices за модела,
    # за да не гърми формата с "Not a valid choice"
    if request.method == 'POST':
        selected_brand = request.form.get('brand')
        if selected_brand in CAR_BRANDS:
            # Попълваме choices динамично спрямо изпратената марка
            form.model.choices = [(m, m) for m in CAR_BRANDS[selected_brand]]

    if form.validate_on_submit():
        # Твоята логика за създаване на колата (примерна според твоите полета):
        car = Car(
            brand=form.brand.data,
            model=form.model.data,
            year=form.year.data,
            price=form.price.data,
            horsepower=form.horsepower.data,
            engine_size=form.engine_size.data,
            fuel=form.fuel_type.data, # Провери дали името съвпада с модела ти
            mileage=form.mileage.data,
            transmission=form.transmission.data,
            doors=form.doors.data,
            condition=form.condition.data,
            description=form.description.data,
            user_id=current_user.id
        )
        
        db.session.add(car)
        db.session.commit()
        
        # Ако е AJAX заявка (от твоя JS), връщаме JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'car_id': car.id}), 200
            
        flash('Обявата беше създадена успешно!', 'success')
        return redirect(url_for('main.index'))
    
    # Ако има грешки при AJAX заявка
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'errors': form.errors}), 400

    return render_template('add_car.html', form=form)


@bp.route('/upload_image/<int:car_id>', methods=['POST'])
@login_required
def upload_image(car_id):
    car = Car.query.get_or_404(car_id)
    if car.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Нямате право!'}), 403

    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'Няма файл'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Празно име'}), 400

    if not file.filename.lower().endswith(('jpg', 'jpeg', 'png', 'webp', 'gif')):
        return jsonify({'success': False, 'error': 'Невалиден формат'}), 400

    # Първата снимка става главна
    is_main = CarImage.query.filter_by(car_id=car_id).count() == 0

    filename = secure_filename(f"{car_id}_{int(time.time())}_{file.filename}")
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    file = request.files['file']
    # Ограничение до 5MB
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    if file_length > 5 * 1024 * 1024:
        return jsonify({'success': False, 'error': 'Файлът е твърде голям (макс. 5MB)'}), 400
    file.seek(0)

    image = CarImage(filename=filename, car_id=car_id, is_main=is_main)
    db.session.add(image)
    db.session.commit()

    return jsonify({
        'success': True,
        'url': url_for('static', filename=f'uploads/cars/{filename}'),
        'is_main': is_main
    })

# Моите обяви
@bp.route('/my_cars')
@login_required
def my_cars():
    # Използваме joinedload за да вземем снимките с една заявка
    cars = Car.query.filter_by(user_id=current_user.id).options(joinedload(Car.images)).order_by(Car.created_at.desc()).all()
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

# --- Добави това в app/routes.py ---

# 1. Логика за редактиране
# app/routes.py

@bp.route('/edit_car/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_car(id):
    car = Car.query.get_or_404(id)
    
    if car.user_id != current_user.id and not getattr(current_user, 'is_admin', False):
        flash('Нямате право да редактирате тази обява!', 'danger')
        return redirect(url_for('routes.index'))

    form = CarForm(obj=car)
    form.model.choices = [(m, m) for m in CAR_BRANDS.get(car.brand, [])]

    if form.validate_on_submit():
        # --- НОВО: ОБРАБОТКА НА СНИМКИТЕ ПРИ ЗАПАЗВАНЕ ---
        
        # 1. Изтриване на маркираните снимки
        deleted_ids_str = request.form.get('deleted_image_ids')
        if deleted_ids_str:
            # Превръщаме текста "5,8" в списък от числа [5, 8]
            deleted_ids = [int(img_id) for img_id in deleted_ids_str.split(',') if img_id.strip().isdigit()]
            for img_id in deleted_ids:
                img_to_delete = CarImage.query.get(img_id)
                # Проверяваме дали снимката съществува и дали наистина принадлежи на тази кола (защита)
                if img_to_delete and img_to_delete.car_id == car.id:
                    # Трием файла от папката
                    file_path = os.path.join(current_app.root_path, 'static/uploads/cars', img_to_delete.filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    # Трием от базата
                    db.session.delete(img_to_delete)

        # 2. Задаване на нова главна снимка
        main_image_id_str = request.form.get('main_image_id')
        if main_image_id_str and main_image_id_str.isdigit():
            main_image_id = int(main_image_id_str)
            img_to_make_main = CarImage.query.get(main_image_id)
            # Проверяваме дали избраната снимка е на тази кола
            if img_to_make_main and img_to_make_main.car_id == car.id:
                # Махаме флага 'is_main' от всички снимки на колата
                CarImage.query.filter_by(car_id=car.id).update({'is_main': False})
                # Задаваме го само на новата
                img_to_make_main.is_main = True
                
        # --- КРАЙ НА НОВАТА ОБРАБОТКА ---

        # Обновяваме останалите текстови полета
        car.brand = form.brand.data
        car.model = form.model.data
        car.year = form.year.data
        car.price = form.price.data
        car.horsepower = form.horsepower.data
        car.engine_size = form.engine_size.data
        car.fuel = form.fuel_type.data
        car.mileage = form.mileage.data
        car.transmission = form.transmission.data
        car.doors = form.doors.data
        car.condition = form.condition.data
        car.description = form.description.data
        
        # Запазваме всичко (и текстовете, и промените по снимките) накуп!
        db.session.commit()
        flash('Обявата беше обновена успешно!', 'success')
        return redirect(url_for('routes.car_detail', id=car.id))
    
    if request.method == 'GET':
        form.fuel_type.data = car.fuel 

    return render_template('edit_car.html', form=form, car=car)

# 2. Логика за изтриване
@bp.route('/delete_car/<int:id>') # Махнахме POST за по-лесно връзване с линк бутон
@login_required
def delete_car(id):
    car = Car.query.get_or_404(id)

    # Проверка: Само собственикът или Админ могат да трият
    if car.author != current_user and not getattr(current_user, 'is_admin', False):
        flash('Нямате право да изтриете тази обява.', 'danger')
        return redirect(url_for('routes.my_cars'))

    # Изтриване на картинките (по желание, тук само записа в базата)
    db.session.delete(car)
    db.session.commit()
    flash('Обявата беше изтрита.', 'success')
    
    # Ако е админ и трие чужда кола, го връщаме в общия списък, иначе в "Моите обяви"
    if request.referrer and 'car_detail' in request.referrer:
        return redirect(url_for('routes.index'))
        
    return redirect(url_for('routes.my_cars'))

@bp.route('/search')
def search():
    form = SearchForm(request.args)
    
    # Динамично зареждане на моделите, ако има избрана марка
    if form.brand.data:
        form.model.choices = [('', 'Всички модели')] + [(m, m) for m in CAR_BRANDS.get(form.brand.data, [])]

    query = Car.query.options(joinedload(Car.images))

    # ПРИЛАГАНЕ НА ВСИЧКИ ФИЛТРИ
    if form.brand.data:
        query = query.filter(Car.brand == form.brand.data)
    if form.model.data:
        query = query.filter(Car.model == form.model.data)
    if form.min_price.data:
        query = query.filter(Car.price >= form.min_price.data)
    if form.max_price.data:
        query = query.filter(Car.price <= form.max_price.data)
    if form.min_year.data:
        query = query.filter(Car.year >= int(form.min_year.data))
    if form.max_year.data:
        query = query.filter(Car.year <= int(form.max_year.data))
    if form.fuel_type.data:
        query = query.filter(Car.fuel == form.fuel_type.data)
    if form.transmission.data:
        query = query.filter(Car.transmission == form.transmission.data)
    if form.condition.data:
        query = query.filter(Car.condition == form.condition.data)
    if form.doors.data:
        query = query.filter(Car.doors == form.doors.data)
    if form.min_hp.data:
        query = query.filter(Car.horsepower >= form.min_hp.data)
    if form.max_hp.data:
        query = query.filter(Car.horsepower <= form.max_hp.data)

    cars = query.all()
    return render_template('search.html', cars=cars, form=form)

@bp.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({'error': 'Няма съобщение'}), 400

    try:
        # 1. Принтираме всички достъпни модели в терминала (за дебъгване)
        print("--- ДОСТЪПНИ GEMINI МОДЕЛИ ЗА ТОЗИ КЛЮЧ ---")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
        print("-------------------------------------------")

        # 2. Използваме най-стабилния и универсален модел
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"Ти си AI асистент на име AutoMind в сайт за обяви за коли на име CarMarket. Отговаряй кратко, точно и любезно на български език. Потребител: {user_message}"
        
        response = model.generate_content(prompt)
        return jsonify({'response': response.text})
    except Exception as e:
        print(f"Gemini Error: {e}")
        # Връщаме самата грешка към фронтенда, за да я видим в чата
        return jsonify({'error': str(e)}), 500