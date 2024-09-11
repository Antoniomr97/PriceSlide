from flask import render_template, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, bcrypt, login_manager
from app.models import User, Game
from app.forms import LoginForm, RegistrationForm
from app.eneba_scraper import fetch_game_data_eneba
from app.instant_gaming_scraper import fetch_game_data_instant_gaming
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from fuzzywuzzy import process, fuzz  # Para coincidencias parciales

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    min_price = None
    min_price_store = None
    graph_img = None
    matched_games = []  # Lista de juegos coincidentes

    # Si se envía el formulario de búsqueda
    if request.method == 'GET':  # Cambiado para manejar GET
        game_name = request.args.get('game_name')  # Obtener el nombre del juego desde el formulario

        if game_name:
            # Obtener todos los nombres de juegos de la base de datos
            all_games = Game.query.with_entities(Game.name).distinct().all()
            game_names = [game.name for game in all_games]

            # Encontrar las mejores coincidencias (similitud parcial)
            matches = process.extractBests(game_name, game_names, limit=5, scorer=fuzz.partial_ratio)

            # Buscar los juegos coincidentes en la base de datos
            for match in matches:
                name = match[0]
                game = Game.query.filter_by(name=name).first()
                if game:
                    matched_games.append({
                        'name': game.name,
                        'min_price': game.price,
                        'store': game.store,
                        'date': game.date
                    })

    # Mostrar resultados si hay coincidencias
    if matched_games:
        # Solo mostrar gráfico del primer juego coincidente como ejemplo
        game_data = Game.query.filter_by(name=matched_games[0]['name']).all()
        if game_data:
            df = pd.DataFrame({
                'date': [game.date for game in game_data],
                'price': [game.price for game in game_data],
                'store': [game.store for game in game_data]
            })

            current_prices = df[df['date'] == df['date'].max()]
            min_price_row = current_prices.loc[current_prices['price'].idxmin()]
            min_price = min_price_row['price']
            min_price_store = min_price_row['store']

            grouped = df.groupby('store')

            plt.figure(figsize=(10, 6))
            colors = {'Instant Gaming': 'orange', 'Eneba': 'purple'}
            for store, group in grouped:
                plt.plot(group['date'], group['price'], label=store, color=colors.get(store, 'blue'))

            plt.xlabel('Fecha')
            plt.ylabel('Precio')
            plt.title(f'Evolución del Precio - {matched_games[0]["name"]}')
            plt.legend()
            plt.xticks(rotation=45)
            plt.grid(True)

            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            plt.close()

            img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
            graph_img = img_base64

    return render_template('home.html', min_price=min_price, min_price_store=min_price_store, graph_img=graph_img, games=matched_games)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/update_games_eneba', methods=['POST'])
@login_required
def update_games_eneba():
    fetch_game_data_eneba()
    return redirect(url_for('home'))

@app.route('/update_games_instant_gaming', methods=['POST'])
@login_required
def update_games_instant_gaming():
    fetch_game_data_instant_gaming()
    return redirect(url_for('home'))