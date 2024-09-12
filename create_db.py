# Importamos la aplicación de Flask, la base de datos definida y los modelos de esta misma
from app import app, db
from app.models import User, Game

# Se inicia el contexto para que todo se realice dentro del entorno correcto
with app.app_context():
    #Este es un metodo de SQLAlchemy que va a crear todas las bases de datos segun los modelos definidos
    db.create_all()