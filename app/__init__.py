from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = '8c41f37e9ad2a73b229df6255e571d4b65347c6c4119dc29'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///priceSlide.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from app import routes, models