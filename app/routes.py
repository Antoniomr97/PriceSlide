import io
import base64
import matplotlib.pyplot as plt
from flask import render_template, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, bcrypt, login_manager
from app.models import User, Game
from app.forms import LoginForm, RegistrationForm
from app.eneba_scraper import fetch_game_data_eneba
from app.g2a_scraper import fetch_game_data_g2a
from app.instant_gaming_scraper import fetch_game_data_instant_gaming

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Redirigir a la página de login desde la ruta principal
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html', form=form)

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/plot')
@login_required
def plot():
    # Consultar precios y fechas desde la base de datos
    games = Game.query.all()
    dates = [game.date_added for game in games]
    prices = [game.price for game in games]

    # Crear el gráfico
    plt.figure(figsize=(10, 6))
    plt.plot(dates, prices, marker='o', linestyle='-')
    plt.title('Precio del Juego a lo Largo del Tiempo')
    plt.xlabel('Fecha')
    plt.ylabel('Precio')
    plt.grid(True)

    # Guardar la imagen en un buffer
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    # Codificar la imagen en base64 para integrarla en HTML
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    return render_template('plot.html', img_data=img_base64)

@app.route('/update_games_eneba')
@login_required
def update_games_eneba():
    fetch_game_data_eneba()  # Llama a la función para actualizar los datos de los juegos

# @app.route('/update_games_g2a')
# @login_required
# def update_games_g2a():
#     fetch_game_data_g2a()

@app.route('/update_games_instant_gaming')
@login_required
def update_games_instant_gaming():
    fetch_game_data_instant_gaming()