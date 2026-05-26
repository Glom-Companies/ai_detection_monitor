import os
import csv
import logging
from datetime import datetime

# Import des modules du projet
from collect import run_collection
from filter import filter_articles
from analyze import analyze_article
from trends import extract_trends
from visualize import generate_charts
from send_email import send_digest_email

# Configuration du logging principal
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def create_directory_structure(base_dir):
    """Crée tous les dossiers de stockage de données s'ils n'existent pas."""
    directories = [
        "data/raw",
        "data/filtered",
        "data/analyzed",
        "data/trends",
        "data/visuals"
    ]
    for folder in directories:
        path = os.path.join(base_dir, folder)
        os.makedirs(path, exist_ok=True)
    logging.info("Structure de répertoires 'data/' validée et prête.")

def save_to_csv(data, filepath):
    """Sauvegarde générique d'une liste de dicts en CSV."""
    if not data:
        logging.warning(f"Aucune donnée à enregistrer pour {filepath}")
        return False
        
    keys = data[0].keys()
    try:
        with open(filepath, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
        logging.info(f"✓ Données enregistrées avec succès : {filepath}")
        return True
    except Exception as e:
        logging.error(f"✗ Erreur d'écriture CSV : {filepath} ({e})")
        return False

def main():
    start_time = datetime.now()
    logging.info("=========================================================")
    logging.info("DÉMARRAGE DU PIPELINE DE VEILLE SUR LA DÉTECTION D'IA")
    logging.info("=========================================================")
    
    # 1. Préparation de l'environnement local
    base_dir = os.path.dirname(os.path.abspath(__file__))
    create_directory_structure(base_dir)
    
    date_str = datetime.now().strftime("%d_%m_%Y")
    
    # Chemins de sortie des fichiers
    raw_csv = os.path.join(base_dir, "data", "raw", f"raw_articles_{date_str}.csv")
    filtered_csv = os.path.join(base_dir, "data", "filtered", f"filtered_articles_{date_str}.csv")
    analyzed_csv = os.path.join(base_dir, "data", "analyzed", f"analyzed_articles_{date_str}.csv")
    
    # 2. COLLECTE DES SITES ET APIs
    try:
        raw_articles = run_collection()
        if not raw_articles:
            logging.warning("Aucun article récupéré. Fin du pipeline.")
            return
        save_to_csv(raw_articles, raw_csv)
    except Exception as e:
        logging.critical(f"Erreur fatale lors de la collecte : {e}")
        return
        
    # 3. FILTRAGE ET SCORING PONDÉRÉ
    try:
        filtered_articles = filter_articles(raw_articles)
        if not filtered_articles:
            logging.warning("Aucun article qualifié (score >= 3 et âge < 3 jours). Fin du pipeline.")
            return
        save_to_csv(filtered_articles, filtered_csv)
    except Exception as e:
        logging.critical(f"Erreur fatale lors du filtrage : {e}")
        return
        
    # 4. ANALYSE ET RÉSUMÉS (STATISTIQUE OU GEMINI AI)
    try:
        logging.info("Démarrage de l'analyse et de la synthèse des textes...")
        raw_analyzed = []
        for idx, art in enumerate(filtered_articles):
            logging.info(f"Analyse article {idx+1}/{len(filtered_articles)} : {art.get('title')[:40]}...")
            raw_analyzed.append(analyze_article(art))
            
        # Filtrage strict post-analyse : on ne garde que les articles identifiés comme outils/plateformes
        analyzed_articles = [art for art in raw_analyzed if art.get("is_tool")]
        logging.info(f"Filtrage sémantique : {len(analyzed_articles)}/{len(raw_analyzed)} articles qualifiés comme outils de détection.")
        
        save_to_csv(analyzed_articles, analyzed_csv)
    except Exception as e:
        logging.critical(f"Erreur fatale lors de l'analyse : {e}")
        return
        
    # 5. STATISTIQUES DE TENDANCES (Mots-clés / Catégories)
    try:
        trends_file, cats_file = extract_trends(analyzed_articles)
    except Exception as e:
        logging.critical(f"Erreur lors de l'extraction des tendances : {e}")
        return
        
    # 6. VISUALISATION ET GRAPHIQUES PNG
    try:
        cat_chart_path, kw_chart_path = generate_charts()
    except Exception as e:
        logging.critical(f"Erreur lors de la génération des graphiques : {e}")
        return
        
    # 7. ENVOI DU BULLETIN PAR EMAIL (SMTP OU APERÇU CONSOLE)
    try:
        send_digest_email(analyzed_articles, cat_chart_path, kw_chart_path)
    except Exception as e:
        logging.critical(f"Erreur lors de l'envoi de l'email : {e}")
        return
        
    end_time = datetime.now()
    duration = end_time - start_time
    logging.info("=========================================================")
    logging.info(f"PIPELINE EXÉCUTÉ AVEC SUCCÈS EN {duration.total_seconds():.1f} SECONDES")
    logging.info(f"Articles Bruts : {len(raw_articles)} | Qualifiés : {len(analyzed_articles)}")
    logging.info("=========================================================")

if __name__ == "__main__":
    main()
