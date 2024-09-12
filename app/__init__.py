from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# Importamos LoginManager para realizar el Login con sus recursos
from flask_login import LoginManager
# Bcrypt para control de contraseñas
from flask_bcrypt import Bcrypt

# Crea una instancia de la aplicación Flask
app = Flask(__name__)
# Establece una clave secreta para manejar la seguridad
app.config['SECRET_KEY'] = '8c41f37e9ad2a73b229df6255e571d4b65347c6c4119dc29'
# Configura la ubicación y el tipo de base de datos que se usará con SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///priceSlide.db'

# Crea una instancia y la asocia con la aplicación app. Así puede interactuar con la base de datos en la variable db
db = SQLAlchemy(app)
# Crea una instancia Bcrypt que nos permite utilizar hashing de contraseñas
bcrypt = Bcrypt(app)
# Creamos instancia de LoginManager como login_manager para poder manejar la gestión de sesiones de usuario
login_manager = LoginManager(app)
# Establece a donde va cuando no estas logeado
login_manager.login_view = 'login'

from app import routes, models