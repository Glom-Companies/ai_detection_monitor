import csv
import os
import logging
from collections import Counter
from datetime import datetime
from config import KEYWORDS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def extract_trends(articles):
    logging.info("========== DÉBUT DE L'EXTRACTION DES TENDANCES ==========")
    
    # 1. Compteurs
    category_counter = Counter()
    keyword_counter = Counter()
    
    for article in articles:
        # Récupère les catégories associées de l'article
        cats_str = article.get("matched_categories", "")
        if cats_str:
            for cat in cats_str.split(","):
                category_counter[cat] += 1
                
        # Analyse textuelle complète pour compter les occurrences de chaque mot-clé individuel
        text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        
        for category, keywords in KEYWORDS.items():
            for kw in keywords:
                # Si le mot-clé est mentionné dans le texte
                if kw.lower() in text:
                    keyword_counter[kw] += 1
                    
    # 2. Préparation des répertoires
    base_dir = os.path.dirname(os.path.abspath(__file__))
    trends_dir = os.path.join(base_dir, "data", "trends")
    os.makedirs(trends_dir, exist_ok=True)
    
    date_str = datetime.now().strftime("%d_%m_%Y")
    
    # Sauvegarde des mots-clés les plus mentionnés
    trends_filepath = os.path.join(trends_dir, f"trends_{date_str}.csv")
    with open(trends_filepath, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["keyword", "mentions"])
        for kw, count in keyword_counter.most_common():
            writer.writerow([kw, count])
            
    # Sauvegarde de la répartition par catégorie
    cats_filepath = os.path.join(trends_dir, f"categories_{date_str}.csv")
    with open(cats_filepath, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["category", "count"])
        for cat, count in category_counter.most_common():
            writer.writerow([cat, count])
            
    logging.info(f"✓ Fichiers de tendances sauvegardés dans {trends_dir}")
    logging.info("========== EXTRACTION DES TENDANCES TERMINÉE ==========")
    
    return trends_filepath, cats_filepath

if __name__ == "__main__":
    test_articles = [
        {"title": "GPTZero and Copyleaks battle AI plagiarism", "matched_categories": "core_keywords,tools_to_watch"},
        {"title": "Understanding perplexity and burstiness in LLMs", "matched_categories": "math_statistics"}
    ]
    extract_trends(test_articles)
