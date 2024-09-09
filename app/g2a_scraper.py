from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import random
from app.models import Game

def fetch_game_data_g2a():
    chrome_options = Options()
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
    # chrome_options.add_argument("--disable-http2")  # Uncomment if needed

    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    
    base_url = "https://www.g2a.com/es/category/games-c189?f%5Bdrm%5D%5B0%5D=1&f%5Bplatform%5D%5B0%5D=1&f%5Btype%5D%5B0%5D=10&f%5Bversions%5D%5B0%5D=8355&page="
    page_number = 1
    
    while True:
        url = f"{base_url}{page_number}"
        print(f"Fetching URL: {url}")
        
        try:
            driver.get(url)
            time.sleep(random.uniform(3, 5))  # Allow some time for the page to load
        except Exception as e:
            print(f"Error al acceder a la URL {url}: {e}")
            time.sleep(random.uniform(10, 20))  # Wait before retrying
            continue  # Retry the same page

        # Scroll down the page to load more games if needed
        scroll_pause_time = random.uniform(1, 3)
        max_scrolls = 4
        last_height = driver.execute_script("return document.body.scrollHeight")

        for _ in range(max_scrolls):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        # Wait for games to load
        wait = WebDriverWait(driver, 20)
        try:
            games = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".sc-gIvpjk.kgKIqe.indexes__StyledProductBox-wklrsw-122.beGIwZ.productCard")))
        except Exception as e:
            print(f"Error al esperar los elementos: {e}")
            time.sleep(random.uniform(10, 20))  # Wait before retrying
            continue  # Retry the same page

        # Extract and print game names and prices
        if not games:
            print("No games found on this page. Moving to next page.")
            page_number += 1
            time.sleep(random.uniform(5, 10))  # Wait before loading the next page
            continue

        for game in games:
            try:
                # Extract the game name from the <a> tag inside <h3>
                name_element = game.find_element(By.CSS_SELECTOR, "h3 a")
                game_name = name_element.text

                # Extract the price using the correct class selector for the price span
                price_element = game.find_element(By.CSS_SELECTOR, ".sc-iqAclL.sc-crzoAE.dJFpVb.eqnGHx.sc-bqGGPW.gjCrxq")
                game_price = price_element.text

                store = 'G2A'
                date = datetime.utcnow()  # The current date and time in UTC

                # Convert price to float for comparison
                try:
                    game_price = float(game_price.replace('€', '').replace(',', '.').strip())
                except ValueError:
                    continue  # Skip if price conversion fails

                # Check the latest record for the game in the same store
                latest_game = Game.query.filter_by(name=game_name, store=store).order_by(Game.date.desc()).first()

                # Instead of adding to the DB, print what would have been added
                if latest_game is None or latest_game.price != game_price:
                    print(f"Would add to DB: Name: {game_name}, Price: {game_price}, Store: {store}, Date: {date}")
                    # Commenting out the DB insert
                    # game_record = Game(name=game_name, price=game_price, store=store, date=date)
                    # db.session.add(game_record)

            except Exception as e:
                print(f"Error extracting game data: {e}")
                continue
        
        # Comment out the commit statement
        # db.session.commit()

        # Move to the next page
        page_number += 1
        time.sleep(random.uniform(5, 10))  # Wait for the page to load
    
    driver.quit()