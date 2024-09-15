from flask import render_template, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, bcrypt, login_manager
from app.models import User, Game
from app.forms import LoginForm, RegistrationForm
from app.eneba_scraper import fetch_game_data_eneba
from app.instant_gaming_scraper import fetch_game_data_instant_gaming
import pandas as pd
import matplotlib
import matplotlib.dates as mdates
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from fuzzywuzzy import process, fuzz

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
    best_match_game = None
    additional_matches = []
    historical_data = []
    graph_img = None
    game_name = request.args.get('game_name')

    if game_name:
        # Obtener todos los nombres de juegos en la base de datos
        all_games = Game.query.with_entities(Game.name).distinct().all()
        game_names = [game.name.lower() for game in all_games]

        # Buscar coincidencia exacta (respetar mayúsculas y minúsculas)
        exact_match = Game.query.filter(Game.name.ilike(f'%{game_name}%')).all()
        
        if exact_match:
            # Obtener el mejor precio actual
            best_price_entry = min(exact_match, key=lambda x: x.price)
            best_match_game = {
                'name': best_price_entry.name.title(),
                'best_price': best_price_entry.price,
                'best_store': best_price_entry.store
            }

            # Obtener datos históricos de precios para el mejor juego
            historical_data = [ {
                'date': game.date,
                'price': game.price,
                'store': game.store
            } for game in exact_match]

            # Filtrar datos históricos para mostrar solo las fechas con cambios de precio
            filtered_historical_data = []
            for store, group in pd.DataFrame(historical_data).groupby('store'):
                group = group.sort_values(by='date')  # Ordenar por fecha
                previous_price = None
                for _, row in group.iterrows():
                    if previous_price is None or row['price'] != previous_price:
                        filtered_historical_data.append(row)
                    previous_price = row['price']

            # Generar gráfico de evolución de precios solo con los cambios de precio
            if filtered_historical_data:
                df = pd.DataFrame(filtered_historical_data)
                plt.figure(figsize=(12, 6))

                # Agrupar por tienda y trazar los puntos donde hubo cambios de precio
                for store, group in df.groupby('store'):
                    plt.plot(group['date'], group['price'], label=store, marker='o')

                plt.xlabel('Date')
                plt.ylabel('Price')
                plt.title(f'Price Evolution - {best_price_entry.name.title()}')
                plt.legend()

                # Formatear las fechas correctamente en el eje X
                plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
                plt.xticks(rotation=45)
                plt.grid(True)
                plt.tight_layout()

                # Guardar la imagen como base64 para mostrarla en HTML
                img = io.BytesIO()
                plt.savefig(img, format='png')
                img.seek(0)
                plt.close()
                graph_img = base64.b64encode(img.getvalue()).decode('utf-8')

        else:
            # Buscar coincidencias aproximadas si no hay coincidencia exacta
            matches = process.extractBests(game_name, game_names, limit=5, scorer=fuzz.partial_ratio)
            best_matches = [match for match in matches if match[1] >= 80]  # Ajustar el umbral según sea necesario

            for match in best_matches:
                name = match[0]
                games_in_db = Game.query.filter(Game.name.ilike(f'%{name}%')).all()
                if games_in_db:
                    best_price_entry = min(games_in_db, key=lambda x: x.price)
                    additional_matches.append({
                        'name': name.title(),
                        'best_price': best_price_entry.price,
                        'best_store': best_price_entry.store
                    })

    return render_template('home.html', best_match_game=best_match_game, additional_matches=additional_matches, graph_img=graph_img)

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