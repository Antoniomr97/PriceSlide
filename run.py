from app import app
# from app.eneba_scraper import fetch_game_data_eneba
# from app.g2a_scraper import fetch_game_data_g2a
from app.instant_gaming_scraper import fetch_game_data_instant_gaming


if __name__ == "__main__":
    with app.app_context():
         fetch_game_data_instant_gaming()  # Llama al scraper dentro del contexto de la aplicación
    app.run(debug=True)