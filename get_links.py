import os
import threading
import keyboard
from selenium import webdriver
from bs4 import BeautifulSoup
import time

# Configuration de Selenium avec Firefox
options = webdriver.FirefoxOptions()
options.add_argument("--headless")  # Mode sans affichage
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

driver = webdriver.Firefox(options=options)

# Création du dossier 'data' s'il n'existe pas
output_dir = "result"
os.makedirs(output_dir, exist_ok=True)

# Variable de contrôle pour la pause
pause_event = threading.Event()
pause_event.set()

def pause_resume():
    global pause_event
    while True:
        keyboard.wait("enter")  # Attendre que l'utilisateur appuie sur "Entrée"
        if pause_event.is_set():
            print("Pause activée. Appuyez sur Entrée pour reprendre.")
            pause_event.clear()
        else:
            print("Reprise du programme.")
            pause_event.set()

# Lancer le thread de contrôle de pause
threading.Thread(target=pause_resume, daemon=True).start()

# Fonction pour extraire et sauvegarder le contenu des profils
def extract_and_save_profile(profile_url, file_index):
    driver.get(profile_url)
    time.sleep(2)  # Attendre le chargement
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    page_content = soup.find('div', class_='page-content')
    
    if page_content:
        container = page_content.find('div', class_='container container-grid')
        if container:
            cards = container.find_all('div', class_='card card-block')
            if len(cards) >= 2:
                second_card = cards[1]  # Récupérer la 2e div
                div_content = second_card.find("div", class_="card-block-content")
                
                if div_content:
                    text_content = div_content.get_text("\n", strip=True)  # Garde les retours à la ligne
                    
                    file_name = os.path.join(output_dir, f"{file_index}.txt")
                    with open(file_name, "w", encoding="utf-8") as file:
                        file.write(text_content)
                    print(f"Profil {file_index} sauvegardé dans {file_name}")
                else:
                    print(f"Erreur : Contenu de la carte introuvable pour {profile_url}")
            else:
                print(f"Erreur : Pas assez de cartes pour {profile_url}")
        else:
            print(f"Erreur : Conteneur introuvable pour {profile_url}")
    else:
        print(f"Erreur : Contenu de la page introuvable pour {profile_url}")

# Fonction pour obtenir le dernier profil scrappé
def get_last_scraped():
    if os.path.exists("last_scraped.txt"):
        with open("last_scraped.txt", "r") as f:
            return int(f.read().strip())
    return 0  # Si le fichier n'existe pas, commencer à partir de la première ligne

# Fonction pour sauvegarder la dernière ligne scrappée
def save_last_scraped(line_index):
    with open("last_scraped.txt", "w") as f:
        f.write(str(line_index))

# Charger les URLs depuis le fichier texte
with open("profile_urls.txt", "r", encoding="utf-8") as file:
    profile_urls = file.readlines()

# Obtenir la dernière ligne scrappée
start_index = get_last_scraped()

# Extraire et sauvegarder les profils
for index, profile_url in enumerate(profile_urls[start_index:], start=start_index + 1):
    profile_url = profile_url.strip()  # Supprimer les espaces et retours à la ligne
    print(f"Scraping le profil {index}: {profile_url}")
    
    # Scraper et sauvegarder
    extract_and_save_profile(profile_url, index)
    
    # Sauvegarder l'index de la ligne après chaque scraping réussi
    save_last_scraped(index)
    
    print("Appuyez sur Entrée pour mettre en pause/reprendre.")
    while not pause_event.is_set():  # Attendre la reprise si le programme est mis en pause
        time.sleep(1)  # Attendre la reprise
    
    time.sleep(10)  # Attendre avant de passer à la page suivante

# Fermer le navigateur
driver.quit()

print("\nExtraction des profils terminée !")
