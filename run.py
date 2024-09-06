from app import app
from app.eneba_scraper import fetch_game_data

if __name__ == "__main__":
    with app.app_context():
         fetch_game_data()  # Llama al scraper dentro del contexto de la aplicación
    app.run(debug=True)