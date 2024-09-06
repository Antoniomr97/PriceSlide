from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///priceSlide.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from app import routes, models

#Importar y ejecutar el scraper
from app.eneba_scraper import fetch_game_data

#Ejecutar el scraper en el contexto de la aplicación
with app.app_context():
    fetch_game_data()