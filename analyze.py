import re
import requests
import os
import logging
from config import KEYWORDS, GEMINI_API_KEY

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# --- NETTOYEUR HTML ---
def clean_html(raw_html):
    if not raw_html:
        return ""
    # Enlever les tags HTML
    clean_text = re.sub(r"<[^>]+>", " ", raw_html)
    # Remplacer les entités d'espaces multiples par un seul espace
    clean_text = re.sub(r"\s+", " ", clean_text)
    return clean_text.strip()

# --- GÉNÉRATEUR DE RÉSUMÉ AVEC GEMINI (REQUÊTE DIRECTE) ---
def generate_gemini_summary(title, summary):
    import time
    if not GEMINI_API_KEY:
        logging.warning("GEMINI_API_KEY est vide dans l'environnement. Utilisation du résumeur local.")
        return None
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = (
        "Tu es un expert en veille technologique sur l'IA.\n"
        "Rédige un résumé très court (2 à 3 phrases maximum), neutre, clair et entièrement en français "
        "de l'actualité suivante en te basant sur son titre et sa description.\n"
        "Mets en valeur l'aspect lié à la détection de texte IA, au watermarking ou aux faux positifs s'ils sont mentionnés.\n\n"
        f"Titre : {title}\n"
        f"Description : {summary}\n\n"
        "Résumé (en français) :"
    )
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 180
        }
    }
    
    headers = {"Content-Type": "application/json"}
    
    max_retries = 3
    backoff = 4
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=12)
            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    text_content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    if text_content:
                        return text_content.strip()
                logging.warning("Format de réponse Gemini inattendu.")
                break
            elif response.status_code == 429:
                logging.warning(f"Rate limit Gemini atteint (429). Tentative {attempt+1}/{max_retries}. Attente de {backoff}s...")
                time.sleep(backoff)
                backoff *= 2
            else:
                logging.warning(f"L'appel à l'API Gemini a échoué (Status code: {response.status_code})")
                break
        except Exception as e:
            logging.error(f"Erreur d'appel API Gemini (tentative {attempt+1}) : {e}")
            time.sleep(backoff)
            backoff *= 2
            
    return None

# --- GÉNÉRATEUR DE RÉSUMÉ DE REPLI (FALLBACK LOCAL STATISTIQUE) ---
def generate_local_summary(title, summary):
    text = f"{title}. {summary}"
    # Extraction des phrases
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Mise à plat de tous les mots-clés du dictionnaire
    all_kws = [kw.lower() for sublist in KEYWORDS.values() for kw in sublist]
    
    scored_sentences = []
    for sentence in sentences:
        clean_sentence = sentence.strip()
        if not clean_sentence or len(clean_sentence) < 15:
            continue
            
        # Comptage des occurrences de mots-clés
        score = 0
        for kw in all_kws:
            if kw in clean_sentence.lower():
                score += 1
                
        scored_sentences.append((clean_sentence, score))
        
    # Tri par score décroissant
    scored_sentences.sort(key=lambda x: x[1], reverse=True)
    
    # Récupérer les 2 meilleures phrases ayant au moins 1 mot-clé
    selected = [s[0] for s in scored_sentences[:2] if s[1] > 0]
    
    if not selected:
        # Fallback si aucune phrase ne contient de mot-clé : on prend les deux premières phrases lisibles
        selected = [s[0] for s in scored_sentences[:2]]
        
    if not selected:
        # Fallback ultime
        return f"{title} - {summary[:150]}..."
        
    return " ".join(selected)

# --- POINT D'ENTRÉE ANALYSE ---
def analyze_article(article):
    import time
    title = clean_html(article.get("title", ""))
    raw_summary = article.get("summary", "")
    clean_summary = clean_html(raw_summary)
    
    # Essayer le résumé intelligent par l'API Gemini
    summary_fr = generate_gemini_summary(title, clean_summary)
    
    # Si on utilise Gemini, on met un petit délai de 4 secondes pour respecter le rate limit de 15 RPM
    if GEMINI_API_KEY and summary_fr:
        time.sleep(4)
        
    # Sinon, utiliser le résumeur statistique local
    if not summary_fr:
        summary_fr = generate_local_summary(title, clean_summary)
        
    analyzed = article.copy()
    analyzed["title"] = title
    analyzed["summary"] = clean_summary
    # Ajout du résumé narratif final
    analyzed["narrative_summary"] = summary_fr
    
    return analyzed

if __name__ == "__main__":
    test_article = {
        "title": "GPTZero adds detection for stealth-writer bypassing <b>mechanisms</b>",
        "summary": "This update helps professors identify students using AI humanizers like BypassGPT. The false positive rate remains under 1%.",
        "link": "https://example.com/test"
    }
    print("Article traité :", analyze_article(test_article))
