from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import random
from app import db
from app.models import Game

def fetch_game_data_instant_gaming():
    driver = webdriver.Chrome()
    driver.maximize_window()
    
    base_url = "https://www.instant-gaming.com/es/busquedas/?platform%5B0%5D=1&type%5B0%5D=&sort_by=&min_reviewsavg=10&max_reviewsavg=100&noreviews=1&min_price=0&max_price=200&noprice=1&gametype=all&search_tags=0&query=&page=1&_gl=1*sdcct*_up*MQ..&gclid=CjwKCAjwufq2BhAmEiwAnZqw8mYQhIXR7gILYmMr2VtDYW7lsH_nR49IKyXDdWNWkZ8G8ZP71OD18hoCt6MQAvD_BwE"
    page_number = 1
    
    while True:
        url = f"https://www.instant-gaming.com/es/busquedas/?platform%5B0%5D=1&type%5B0%5D=&sort_by=&min_reviewsavg=10&max_reviewsavg=100&noreviews=1&min_price=0&max_price=200&noprice=1&gametype=all&search_tags=0&query=&page={page_number}&_gl=1*sdcct*_up*MQ..&gclid=CjwKCAjwufq2BhAmEiwAnZqw8mYQhIXR7gILYmMr2VtDYW7lsH_nR49IKyXDdWNWkZ8G8ZP71OD18hoCt6MQAvD_BwE"
        driver.get(url)

        scroll_pause_time = random.uniform(1, 3)
        max_scrolls = 7
        # Scroll down the page to load more games if needed
        for _ in range(max_scrolls):
            ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(scroll_pause_time)
        
        # Wait for games to load
        wait = WebDriverWait(driver, 10)
        games = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".item.force-badge")))
        
        # Extract and store game names and prices
        if not games:
            print("No games found on this page. Ending extraction.")
            break

        for game in games:
            names = game.find_elements(By.CSS_SELECTOR, ".title")
            prices = game.find_elements(By.CSS_SELECTOR, ".price")
        
            for name, price in zip(names, prices):
                game_name = name.text
                game_price = price.text
                store = 'Instant Gaming'
                date = datetime.utcnow()  # The current date and time in UTC
                
                # Convert price to float for comparison
                try:
                    game_price = float(game_price.replace('€', '').replace(',', '.').strip())
                except ValueError:
                    continue  # Skip if price conversion fails

                # Check the latest record for the game in the same store
                latest_game = Game.query.filter_by(name=game_name, store=store).order_by(Game.date.desc()).first()
                if latest_game is None or latest_game.price != game_price:
                    game_record = Game(name=game_name, price=game_price, store=store, date=date)
                    db.session.add(game_record)

        # Commit the changes to the database
        db.session.commit()

        # Move to the next page
        page_number += 1
        time.sleep(3)  # Wait for the page to load
    
    driver.quit()