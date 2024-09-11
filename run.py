from app import app
# from app.eneba_scraper import fetch_game_data_eneba
from app.instant_gaming_scraper import fetch_game_data_instant_gaming


if __name__ == "__main__":
    with app.app_context():
     #     fetch_game_data_eneba() # Llama al scraper de eneba dentro del contexto de la aplicación
        #  fetch_game_data_instant_gaming()  # Llama al scraper de instant gaming dentro del contexto de la aplicación
        app.run(debug=True)