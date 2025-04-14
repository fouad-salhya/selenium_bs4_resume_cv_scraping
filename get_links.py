from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import os

# Configuration du navigateur
options = webdriver.FirefoxOptions()
options.add_argument("--headless")
options.add_argument("user-agent=Mozilla/5.0")
driver = webdriver.Firefox(options=options)
wait = WebDriverWait(driver, 15)

# Fichiers
profile_file = "profile_urls.txt"
last_page_file = "last_page.txt"

# Lire la dernière page scrappée
start_page = 1
if os.path.exists(last_page_file):
    with open(last_page_file, "r") as f:
        try:
            start_page = int(f.read().strip()) + 1
        except:
            pass

print(f"✅ On démarre à la page {start_page}")

# Charger la première page
base_url = "https://www.emploi.ma/recherche-base-donnees-cv/?f%5B0%5D=im_field_candidat_metier%3A1127&f%5B1%5D=im_field_candidat_metier%3A29"
driver.get(base_url)
time.sleep(4)

def wait_for_page_button(page_number):
    try:
        wait.until(EC.presence_of_element_located((By.LINK_TEXT, str(page_number))))
        return True
    except:
        return False

def click_page(page_number):
    if wait_for_page_button(page_number):
        try:
            link = driver.find_element(By.LINK_TEXT, str(page_number))
            link.click()
            print(f"➡️ Clic sur page {page_number}")
            time.sleep(4)
            return True
        except:
            print(f"⚠️ Échec clic page {page_number}")
    return False

def extract_links():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    divs = soup.find_all('div', class_='card-block-contentx')
    links = []
    for div in divs:
        profiles = div.find_all('div', class_='card-profile')
        for profile in profiles:
            href = profile.get('data-href')
            if href:
                links.append(href)
    return links

# 💡 Scraper la page actuelle (page de démarrage) sans cliquer
links = extract_links()
print(f"✅ Page {start_page} : {len(links)} liens extraits.")

with open(profile_file, "a", encoding="utf-8") as f:
    for link in links:
        f.write(link + "\n")

with open(last_page_file, "w") as f:
    f.write(str(start_page))

# 🔁 Scraper les pages suivantes
for page in range(start_page + 1, start_page + 100):
    if click_page(page):
        time.sleep(5)
        links = extract_links()
        print(f"✅ Page {page} : {len(links)} liens extraits.")

        with open(profile_file, "a", encoding="utf-8") as f:
            for link in links:
                f.write(link + "\n")

        with open(last_page_file, "w") as f:
            f.write(str(page))
    else:
        print(f"❌ Échec chargement de la page {page}")
        break

driver.quit()
print("✅ Scraping terminé.")
