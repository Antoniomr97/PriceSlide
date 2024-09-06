import requests
from app import db
from app.models import Game

def fetch_game_data():
    # Reemplaza esta URL con la URL de la API de Eneba o la URL que estés usando para scrapear
    url = 'https://api.eneba.com/games'
    response = requests.get(url)
    data = response.json()

    for item in data['games']:
        name = item['name']
        price = item['price']
        store = 'Eneba'
        # Verifica si el juego ya existe en la base de datos para evitar duplicados
        game = Game.query.filter_by(name=name).first()
        if not game:
            game = Game(name=name, price=price, store=store)
            db.session.add(game)

    db.session.commit()