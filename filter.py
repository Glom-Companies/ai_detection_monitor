import csv
import os
import logging
from datetime import datetime, timedelta
import email.utils
from config import KEYWORDS, CATEGORY_WEIGHTS, MIN_RELEVANCE_SCORE, MAX_AGE_DAYS, get_interest_level

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# --- DATE PARSER ROBUSTE ---
def parse_date_to_datetime(date_str):
    if not date_str:
        return datetime.now()
        
    # 1. Tentative avec RFC 2822 (courant dans les flux RSS : "Mon, 18 May 2026 09:00:00 GMT")
    try:
        dt = email.utils.parsedate_to_datetime(date_str)
        return dt.replace(tzinfo=None) # Rend naive pour comparaison facile
    except Exception:
        pass

    # 2. Tentative avec ISO format (arXiv/Reddit : "2026-05-18T10:00:00Z" ou "2026-05-18T10:00:00+02:00")
    try:
        clean_str = date_str
        if clean_str.endswith('Z'):
            clean_str = clean_str[:-1] + '+00:00'
        # Remplacements additionnels de microsecondes si présents
        dt = datetime.fromisoformat(clean_str)
        return dt.replace(tzinfo=None)
    except Exception:
        pass

    # 3. Format date brute courte (YYYY-MM-DD)
    try:
        return datetime.strptime(date_str[:10], "%Y-%m-%d")
    except Exception:
        pass

    # Fallback par défaut si illisible
    return datetime.now()

# --- CALCUL DU SCORE DE PERTINENCE ---
def score_article(title, summary):
    score = 0
    matched_categories = []
    text_to_search = f"{title} {summary}".lower()
    
    # Pour chaque catégorie, on vérifie si un de ses mots-clés est présent dans le texte
    for category, keywords in KEYWORDS.items():
        weight = CATEGORY_WEIGHTS.get(category, 0)
        for keyword in keywords:
            # Recherche exacte de sous-chaîne ou mot entier
            if keyword.lower() in text_to_search:
                score += weight
                matched_categories.append(category)
                break # Une seule occurrence par catégorie suffit pour marquer le poids
                
    return score, list(set(matched_categories))

# --- PROCESSUS DE FILTRAGE PRINCIPAL ---
def filter_articles(articles):
    logging.info("========== DÉBUT DU FILTRAGE ==========")
    filtered = []
    seen_urls = set()
    
    now = datetime.now()
    cutoff_date = now - timedelta(days=MAX_AGE_DAYS)
    
    dup_count = 0
    age_count = 0
    low_score_count = 0
    
    for article in articles:
        url = article.get("link", "").strip()
        
        # 1. Déduplication par URL
        if not url or url in seen_urls:
            dup_count += 1
            continue
            
        # 2. Filtrage par âge
        pub_date_str = article.get("published", "")
        pub_dt = parse_date_to_datetime(pub_date_str)
        
        if pub_dt < cutoff_date:
            age_count += 1
            continue
            
        # 3. Calcul de score de pertinence
        title = article.get("title", "")
        summary = article.get("summary", "")
        score, categories = score_article(title, summary)
        
        if score < MIN_RELEVANCE_SCORE:
            low_score_count += 1
            continue
            
        # Enrichissement de l'article retenu
        seen_urls.add(url)
        enriched_article = article.copy()
        enriched_article["relevance_score"] = score
        enriched_article["matched_categories"] = ",".join(categories)
        enriched_article["interest_level"] = get_interest_level(score)
        
        filtered.append(enriched_article)
        
    logging.info(f"Dédupliqués (URLs vides ou doublons) : {dup_count}")
    logging.info(f"Écartés par ancienneté (> {MAX_AGE_DAYS} jours) : {age_count}")
    logging.info(f"Écartés par score insuffisant (< {MIN_RELEVANCE_SCORE}) : {low_score_count}")
    logging.info(f"Total articles qualifiés retenus : {len(filtered)}")
    logging.info("========== FILTRAGE TERMINÉ ==========")
    
    return filtered

if __name__ == "__main__":
    # Test unitaire de validation
    test_articles = [
        {
            "title": "GPTZero releases new AI writing detection tool",
            "summary": "This new release addresses false positive rate concerns in education.",
            "link": "https://example.com/art1",
            "published": datetime.now().isoformat()
        },
        {
            "title": "Unrelated Python tutorials",
            "summary": "How to write a simple calculator using flask.",
            "link": "https://example.com/art2",
            "published": datetime.now().isoformat()
        }
    ]
    res = filter_articles(test_articles)
    print("Articles qualifiés :", res)
