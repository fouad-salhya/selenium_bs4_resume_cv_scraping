import os
import csv

# Dossier contenant les CVs au format .txt
dossier_cv = "./data/"

# Fichier CSV de sortie
fichier_csv = "./clean_cv/data.csv"

# Liste des mots-clés qui définissent les sections
mots_cles = [
    "Types de métiers recherchés",
    "Expérience professionnelle",
    "Compétences",
    "Formation",
    "Compétences clés",
    "Langues",
    "Plus d'informations",
]

# Fonction pour extraire les informations d'un fichier CV
def extraire_infos(fichier_path):
    with open(fichier_path, "r", encoding="utf-8") as fichier:
        lignes = fichier.readlines()

    data = {key: "" for key in mots_cles}  # Dictionnaire pour stocker les infos
    current_key = None

    for ligne in lignes:
        ligne = ligne.strip()  # Supprimer les espaces inutiles

        if ligne in mots_cles:
            current_key = ligne  # Mettre à jour la clé actuelle
        elif current_key:
            data[current_key] += " " + ligne  # Ajouter le contenu sous la bonne colonne

    return data

# Liste pour stocker toutes les données
donnees_csv = []

# Lire tous les fichiers CV et extraire les données
for fichier in os.listdir(dossier_cv):
    if fichier.endswith(".txt"):
        chemin_fichier = os.path.join(dossier_cv, fichier)
        data_cv = extraire_infos(chemin_fichier)
        donnees_csv.append(data_cv)

# Écriture des données dans le fichier CSV
with open(fichier_csv, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=mots_cles)
    writer.writeheader()
    writer.writerows(donnees_csv)

print(f"Fichier CSV généré : {fichier_csv}")
