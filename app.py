from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

app = Flask(__name__)

# Załaduj dane z pliku `.env`
load_dotenv()
username = os.getenv("EPSTRYK_LOGIN")
password = os.getenv("EPSTRYK_PASSWORD")

# Funkcja inicjująca przeglądarkę Chrome w trybie headless
def start_webdriver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Uruchamia Chrome w trybie headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")  # Zwiększa stabilność w trybie headless
    chrome_options.add_argument("--remote-debugging-port=9222")  # DevTools dla stabilności

    # Inicjalizacja Chrome w trybie headless
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Funkcja logowania do epstryk.pl
def login_to_epstryk(driver):
    driver.get("https://epstryk.pl/pl/login")
    time.sleep(2)
    
    # Wprowadzenie danych logowania
    driver.find_element(By.ID, "login_field").send_keys(username)
    driver.find_element(By.ID, "password_field").send_keys(password)
    driver.find_element(By.NAME, "commit").click()
    time.sleep(2)  # Oczekiwanie na zalogowanie

# Funkcja scrapująca dane produktu z epstryk.pl
def scrape_product_data(driver, product_url):
    driver.get(product_url)
    time.sleep(2)
    
    # Pobieranie danych produktu
    product_name = driver.find_element(By.CSS_SELECTOR, ".productCardMain__name.header.-h1.grow").text
    product_code = driver.find_element(By.CSS_SELECTOR, ".productParam__value.productParam__value--normal").text
    catalog_price = driver.find_elements(By.CSS_SELECTOR, ".productParam__value.productParam__value--normal")[1].text
    your_price = driver.find_element(By.CSS_SELECTOR, ".productParam__value.-bold.productParam__value--big").text
    image_url = driver.find_element(By.CSS_SELECTOR, ".productFoto__zoom img").get_attribute("src")

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
        driver = start_webdriver()
        try:
            login_to_epstryk(driver)
            product_data = scrape_product_data(driver, product_url)
        finally:
            driver.quit()

        # Generowanie kodu HTML
        html_code = f"""
        <div class="product-card">
            <img src="{product_data['image_url']}" alt="{product_data['name']}">
            <h2>{product_data['name']}</h2>
            <p class="catalog-price"><s>{product_data['catalog_price']}</s></p>
            <p class="your-price" style="color: red; font-weight: bold;">{product_data['your_price']}</p>
            <button>Kup teraz</button>
        </div>
        """
        
        return render_template("index.html", product_data=product_data, html_code=html_code)
    
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
