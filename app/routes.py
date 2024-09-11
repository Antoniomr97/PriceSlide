from flask import render_template, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, bcrypt, login_manager
from app.models import User, Game
from app.forms import LoginForm, RegistrationForm
from app.eneba_scraper import fetch_game_data_eneba
from app.instant_gaming_scraper import fetch_game_data_instant_gaming
import pandas as pd
import matplotlib
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
        all_games = Game.query.with_entities(Game.name).distinct().all()
        game_names = [game.name for game in all_games]

        matches = process.extractBests(game_name, game_names, limit=5, scorer=fuzz.partial_ratio)
        best_match = min(matches, key=lambda x: (100 - x[1], len(x[0])))

        best_name = best_match[0]
        games_in_db = Game.query.filter_by(name=best_name).all()

        if games_in_db:
            best_price_entry = min(games_in_db, key=lambda x: x.price)
            best_match_game = {
                'name': best_name,
                'best_price': best_price_entry.price,
                'best_store': best_price_entry.store
            }

            # Obtener datos históricos de precios para el mejor juego
            historical_data = [{
                'date': game.date,
                'price': game.price,
                'store': game.store
            } for game in games_in_db]

            # Generar gráfico de evolución de precios
            if historical_data:
                df = pd.DataFrame(historical_data)
                plt.figure(figsize=(12, 6))
                for store, group in df.groupby('store'):
                    plt.plot(group['date'], group['price'], label=store)
                plt.xlabel('Fecha')
                plt.ylabel('Precio')
                plt.title(f'Evolución de Precios - {best_name}')
                plt.legend()
                plt.xticks(rotation=45)
                plt.grid(True)
                plt.tight_layout()

                img = io.BytesIO()
                plt.savefig(img, format='png')
                img.seek(0)
                plt.close()
                graph_img = base64.b64encode(img.getvalue()).decode('utf-8')

        additional_matches = []
        for match in matches:
            if match[0] != best_name:
                name = match[0]
                games_in_db = Game.query.filter_by(name=name).all()

                if games_in_db:
                    best_price_entry = min(games_in_db, key=lambda x: x.price)
                    additional_matches.append({
                        'name': name,
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