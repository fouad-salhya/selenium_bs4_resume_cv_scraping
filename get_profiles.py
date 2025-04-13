import os
import threading
import keyboard
from selenium import webdriver
from bs4 import BeautifulSoup
import time

# === Config Firefox ===
options = webdriver.FirefoxOptions()
options.add_argument("--headless")
options.add_argument("user-agent=Mozilla/5.0")

driver = webdriver.Firefox(options=options)

# === Dossier de sortie ===
output_dir = "hi"
os.makedirs(output_dir, exist_ok=True)

# === Pause/Reprise avec touche Entrée ===
pause_event = threading.Event()
pause_event.set()

def pause_resume():
    while True:
        keyboard.wait("enter")
        if pause_event.is_set():
            print("\n⏸️ Pause activée. Appuyez sur Entrée pour reprendre.")
            pause_event.clear()
        else:
            print("\n▶️ Reprise du scraping.")
            pause_event.set()

threading.Thread(target=pause_resume, daemon=True).start()

# === Sauvegarde et reprise automatique ===
def get_last_scraped():
    if os.path.exists("last_scraped.txt"):
        with open("last_scraped.txt", "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content.isdigit():
                return int(content)
    return 0

def save_last_scraped(index):
    with open("last_scraped.txt", "w", encoding="utf-8") as f:
        f.write(str(index))

# === Chargement des URLs ===
with open("profile_urls.txt", "r", encoding="utf-8") as f:
    profile_urls = [line.strip() for line in f.readlines() if line.strip()]

start_index = get_last_scraped()

# === Scraping principal ===
for index, url in enumerate(profile_urls[start_index:], start=start_index + 1):
    print(f"\n🔍 Scraping profil {index} : {url}")

    try:
        driver.get(url)
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        page_content = soup.find('div', class_='page-content')

        if page_content:
            container = page_content.find('div', class_='container container-grid')
            if container:
                cards = container.find_all('div', class_='card card-block')
                if len(cards) >= 2:
                    div_content = cards[1].find("div", class_="card-block-content")
                    if div_content:
                        text = div_content.get_text("\n", strip=True)
                        file_path = os.path.join(output_dir, f"{index}.txt")
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(text)
                        print(f" Profil {index} sauvegardé.")

                        # ➤ Sauvegarde ici SEULEMENT si scraping réussi :
                        save_last_scraped(index)
                    else:
                        print(f" Aucune donnée trouvée pour le profil {index}.")
                else:
                    print(f" Carte manquante pour le profil {index}.")
            else:
                print(f"Container non trouvé pour le profil {index}.")
        else:
            print(f" Contenu non trouvé pour le profil {index}.")

    except Exception as e:
        print(f" Erreur pour le profil {index} : {e}")

    # Attente si pause
    while not pause_event.is_set():
        time.sleep(1)

    time.sleep(10)

# === Fin ===
driver.quit()
print("\n🎉 Tous les profils ont été traités.")
