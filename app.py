from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

app = Flask(__name__)

# Załaduj dane z pliku `.env`
load_dotenv()
username = os.getenv("EPSTRYK_LOGIN")
password = os.getenv("EPSTRYK_PASSWORD")

# Funkcja inicjująca przeglądarkę Chrome w trybie headless
def start_webdriver():
    options = Options()
    options.add_argument("--headless")  # Uruchamia Chrome w trybie headless
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    print("Inicjalizacja przeglądarki Chrome...")
    driver = webdriver.Chrome(options=options)
    print("Przeglądarka Chrome uruchomiona.")
    return driver

# Funkcja logowania do epstryk.pl
def login_to_epstryk(driver):
    print("Logowanie do epstryk.pl...")
    driver.get("https://epstryk.pl/pl/order/login.html")
    print("Strona logowania załadowana.")
    
    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, "login")))
        email_field = driver.find_element(By.NAME, "login")
        password_field = driver.find_element(By.NAME, "password")
        print("Pola logowania dostępne.")

        # Wprowadzenie danych logowania
        login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']")))
        actions = ActionChains(driver)
        actions.move_to_element(email_field).click().perform()
        email_field.send_keys(username)
        password_field.send_keys(password)
        login_button.click()
        
        print("Logowanie zakończone pomyślnie.")
        time.sleep(2)  # Oczekiwanie na pełne załadowanie strony po zalogowaniu
    except Exception as e:
        print(f"Błąd podczas logowania: {e}")

# Funkcja scrapująca dane produktu
def scrape_product_data(driver, product_url):
    print(f"Pobieranie danych z {product_url}...")
    driver.get(product_url)  # Ponowne załadowanie strony po zalogowaniu
    
    try:
        product_name = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".productCardMain__name.header.-h1.grow"))
        ).text
        print("Nazwa produktu pobrana.")
        product_code = driver.find_element(By.CSS_SELECTOR, ".productParam__value.productParam__value--normal").text
        catalog_price = driver.find_elements(By.CSS_SELECTOR, ".productParam__value.productParam__value--normal")[1].text
        your_price = driver.find_element(By.CSS_SELECTOR, ".productParam__value.-bold.productParam__value--big").text
        image_url = driver.find_element(By.CSS_SELECTOR, ".productFoto__zoom img").get_attribute("src")
        
        print("Dane produktu pobrane pomyślnie.")
    except Exception as e:
        print(f"Błąd podczas pobierania danych produktu: {e}")
        return None

    return {
        "name": product_name,
        "code": product_code,
        "catalog_price": catalog_price,
        "your_price": your_price,
        "image_url": image_url
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        product_url = request.form['product_url']
        
        # Inicjalizacja Selenium i pobieranie danych
        print("Rozpoczynanie pracy z Selenium...")
        driver = start_webdriver()
        product_data = None
        try:
            login_to_epstryk(driver)
            print("Przechodzenie do strony produktu po zalogowaniu.")
            driver.get(product_url)  # Po zalogowaniu ponownie załaduj stronę produktu
            product_data = scrape_product_data(driver, product_url)
            if product_data:
                print("Dane produktu zostały pobrane i będą przetworzone.")
        finally:
            driver.quit()

        # Generowanie kodu HTML
        if product_data:
            html_code = f"""
            <div class="product-card">
                <img src="{product_data['image_url']}" alt="{product_data['name']}">
                <h2>{product_data['name']}</h2>
                <p class="catalog-price"><s>{product_data['catalog_price']}</s></p>
                <p class="your-price" style="color: red; font-weight: bold;">{product_data['your_price']}</p>
                <button>Kup teraz</button>
            </div>
            """
            print("Kod HTML wygenerowany pomyślnie.")
            return render_template("index.html", product_data=product_data, html_code=html_code)
        else:
            print("Nie udało się pobrać danych produktu.")
            return render_template("index.html", error="Nie udało się pobrać danych produktu.")

    print("Ładowanie strony głównej...")
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
