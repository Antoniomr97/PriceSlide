# Importamos selenium la libreria que utilizaremos para el scraping
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# Importamos time y datetime para aportar las fechas
import time
from datetime import datetime
# Importamos db de app
from app import db
from app.models import Game
# Importamos random para el tiempo entre scrolls
import random

def fetch_game_data_eneba():
    # driver que utilizaremos para acceder a chrome
    driver = webdriver.Chrome()
    # driver que abre la ventana
    driver.maximize_window()
    
    page_number = 1
    
    while True:
        # Creamos la url insertando la variable page_number
        url = f"https://www.eneba.com/es/store/games?drms[]=steam&page={page_number}&regions[]=global&regions[]=spain&types[]=game"
        driver.get(url)

        scroll_pause_time = random.uniform(1, 3)
        max_scrolls = 3

        # Scroleamos para poder cargar los juegos que cargan con el scrol
        for _ in range(max_scrolls):
            ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(scroll_pause_time)
        
        # Esperamos que los juegos carguen
        wait = WebDriverWait(driver, 10)
        # Buscamos los elementos por su css selector para obtener los bloques de juegos
        games = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".pFaGHa.WpvaUk")))
        
        # Extraemos los nombres y precios de cada juego
        if not games:
            print("No games found on this page. Ending extraction.")
            break

        for game in games:
            names = game.find_elements(By.CSS_SELECTOR, ".YLosEL")
            prices = game.find_elements(By.CSS_SELECTOR, ".L5ErLT")
        
            for name, price in zip(names, prices):
                game_name = name.text
                game_price = price.text
                store = 'Eneba'
                date = datetime.utcnow()  # Te da la fecha actual
                
                # Convertimos los precios en flotante para la comparación
                try:
                    game_price = float(game_price.replace('€', '').replace(',', '.').strip())
                except ValueError:
                    continue  # Se salta si la conversión del precio falla

                # Localiza el ultimo juego en la lista buscando el mismo nombre y ordenandolo por data en descendente y cogiendo el primero
                latest_game = Game.query.filter_by(name=game_name, store=store).order_by(Game.date.desc()).first()

                # Actualizar la base de datos si el precio es diferente del último precio registrado
                if latest_game is None or latest_game.price != game_price:
                    game_record = Game(name=game_name, price=game_price, store=store, date=date)
                    db.session.add(game_record)

        db.session.commit()
        
        # Aumentamos el numero de pagina para seguir con la paginacion
        page_number += 1
        time.sleep(3)  # Esperamos que la pagina cargue
    
    driver.quit()