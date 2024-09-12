# Importamos Flask para manejar el acceso de datos de solicitudes y la generación Urls y diversos usos
from flask import render_template, redirect, url_for, request
# Importamos Flask-Login para la gestion de la autentificación y sesiones de usuario
from flask_login import login_user, logout_user, current_user, login_required
# Importamos todo lo necesario de app
from app import app, db, bcrypt, login_manager
from app.models import User, Game
from app.forms import LoginForm, RegistrationForm
from app.eneba_scraper import fetch_game_data_eneba
from app.instant_gaming_scraper import fetch_game_data_instant_gaming
# Importando pandas para el análisis de datos
import pandas as pd
# Importamos matplotlib para la generación de graficos
import matplotlib
# Utilizamos Agg para usar el backend sin interfaz, es util para generar graficos en entornos sin interfaz grafica como un servidor
matplotlib.use('Agg')
# Proporciona una interfaz para crear gráficos
import matplotlib.pyplot as plt
# Un modulo que proporciona herramientas para trabajar con flujos de entrada y salida(se utiliza para crear graficos)
import io
import base64
# Para realizar busquedas aproximadas
from fuzzywuzzy import process, fuzz

# Esta ruta carga al usuario cargando su id de la base de datos
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Esta routa hace que el programa empiece en login
@app.route('/')
def index():
    return redirect(url_for('login'))

# Esta ruta realiza el registro hasheando la contraseña y devuelve al login
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

# Esta ruta genera el login y confirma que está registrado en la base de datos
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html', form=form)

# En esta ruta está toda la logica para la llamada del producto
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    # Generamos las variables que vamos a usar
    best_match_game = None
    additional_matches = []
    historical_data = []
    graph_img = None
    game_name = request.args.get('game_name')

    # Comprobamos que hay juego
    if game_name:
        # Obtienes los juegos
        all_games = Game.query.with_entities(Game.name).distinct().all()
        # Obtienes los nombres de los juegos
        game_names = [game.name for game in all_games]

        # Extrae las mejores coincidencias con extractBests marcandole los parametros
        matches = process.extractBests(game_name, game_names, limit=5, scorer=fuzz.partial_ratio)
        # Utilizado para conseguir la coincidencia más parecida
        best_match = min(matches, key=lambda x: (100 - x[1], len(x[0])))

        # Elige el primer elemento de los mejores match
        best_name = best_match[0]

        # Busca los juegos en la base de datos
        games_in_db = Game.query.filter_by(name=best_name).all()

        if games_in_db:
            # Compara los precios de la busqueda y pone el de menor precio
            best_price_entry = min(games_in_db, key=lambda x: x.price)

            # Registramos el mejor juego
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
                # Agrupamos los datos por tienda, traza la linea para cada tienda, mostrando la evolución de los precios a lo largo del tiempo
                for store, group in df.groupby('store'):
                    plt.plot(group['date'], group['price'], label=store)
                
                # Aplicamos los datos que apareceran en Date y Price
                plt.xlabel('Date')
                plt.ylabel('Price')
                plt.title(f'Price Evolution - {best_name}')
                plt.legend()
                plt.xticks(rotation=45)
                plt.grid(True)
                plt.tight_layout()

                img = io.BytesIO()
                plt.savefig(img, format='png')
                img.seek(0)
                plt.close()
                graph_img = base64.b64encode(img.getvalue()).decode('utf-8')

        # Generamos las coincidencias extras
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

# Utiliza el logout para cerrar sesion y volver al login 
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Inicia el scraper en otra pagina del navegador
@app.route('/update_games_eneba', methods=['POST'])
@login_required
def update_games_eneba():
    fetch_game_data_eneba()
    return redirect(url_for('home'))

# Inicia el scraper en otra pagina del navegador
@app.route('/update_games_instant_gaming', methods=['POST'])
@login_required
def update_games_instant_gaming():
    fetch_game_data_instant_gaming()
    return redirect(url_for('home'))