from flask import Flask, render_template
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

# Prosty test uruchomienia przeglądarki i pobrania tytułu strony
def test_selenium():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    try:
        print("Uruchamianie przeglądarki Chrome...")
        driver = webdriver.Chrome(options=options)
        print("Przeglądarka uruchomiona. Przechodzenie do example.com...")
        
        driver.get("https://www.example.com")
        title = driver.title
        print(f"Tytuł strony to: {title}")
        driver.quit()
        return title
    except Exception as e:
        print(f"Błąd uruchamiania Selenium: {e}")
        return None

@app.route('/', methods=['GET'])
def index():
    print("Rozpoczynanie testu Selenium...")
    title = test_selenium()
    
    if title:
        print(f"Selenium działa poprawnie. Tytuł strony to: {title}")
    else:
        print("Błąd podczas uruchamiania Selenium.")
    
    return render_template("index.html", title=title)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
