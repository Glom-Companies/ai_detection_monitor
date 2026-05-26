import re
import requests
import os
import logging
from config import KEYWORDS, GEMINI_API_KEY, KNOWN_TOOLS
import json

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

def clean_json_string(text):
    """Nettoie le texte renvoyé par l'IA pour s'assurer qu'il s'agit d'un JSON valide."""
    if not text:
        return ""
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text, flags=re.IGNORECASE)
    return text.strip()

# --- GÉNÉRATEUR DE RÉSUMÉ AVEC GEMINI (REQUÊTE DIRECTE - SORTIE JSON) ---
def generate_gemini_summary(title, summary):
    import time
    if not GEMINI_API_KEY:
        logging.warning("GEMINI_API_KEY est vide dans l'environnement. Utilisation du résumeur local.")
        return None
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = (
        "Tu es un expert en veille technologique sur l'IA et la détection de texte.\n"
        "Analyse l'article suivant (titre et description/contenu) et extrait les informations de manière très structurée sous forme d'un objet JSON.\n\n"
        f"Titre : {title}\n"
        f"Contenu : {summary}\n\n"
        "Le JSON doit STRICTEMENT suivre ce schéma et n'avoir AUCUN texte en dehors du JSON :\n"
        "{\n"
        "  \"is_tool\": true, // booléen: true si l'article parle d'un outil/plateforme/logiciel de détection d'IA spécifique, ou d'une mise à jour de performance/benchmark de cet outil. false sinon.\n"
        "  \"tool_name\": \"Nom de l'outil\", // chaîne: nom de l'outil (ex: GPTZero, Turnitin, Pangram Labs...) ou \"N/A\" si non applicable.\n"
        "  \"update_title_en\": \"Short title of the update in English\", // max 80 chars\n"
        "  \"update_title_fr\": \"Titre court de la nouveauté en français\", // max 80 chars\n"
        "  \"description_en\": \"Brief English description of the update/tool (1-2 sentences)\",\n"
        "  \"description_fr\": \"Brève description de la nouveauté/outil en français (1-2 phrases)\",\n"
        "  \"performance_en\": \"English performance metrics/benchmarks mentioned in the text (e.g. accuracy, false positives). If none, put 'N/A'\",\n"
        "  \"performance_fr\": \"Métriques de performance/benchmarks en français mentionnés (ex: taux de précision, faux positifs). Si aucun, mettre 'N/A'\",\n"
        "  \"pricing_en\": \"Pricing model in English (e.g. Free, Freemium, Paid). If none, put 'N/A'\",\n"
        "  \"pricing_fr\": \"Modèle de tarification en français (ex: Gratuit, Freemium, Payant). Si aucun, mettre 'N/A'\",\n"
        "  \"try_link\": \"URL mentioned in the text for trying the tool. If none, put 'N/A'\"\n"
        "}\n\n"
        "Important : Ne génère rien d'autre que du JSON valide."
    )
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.1,
            "maxOutputTokens": 450
        }
    }
    
    headers = {"Content-Type": "application/json"}
    
    max_retries = 3
    backoff = 4
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    text_content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    if text_content:
                        clean_text = clean_json_string(text_content)
                        try:
                            parsed_json = json.loads(clean_text)
                            return parsed_json
                        except json.JSONDecodeError as je:
                            logging.error(f"Erreur de décodage JSON de la réponse Gemini : {je}. Texte brut : {clean_text}")
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

# --- GÉNÉRATEUR DE RÉSUMÉ DE REPLI (FALLBACK LOCAL STATISTIQUE AVEC DB) ---
def generate_local_summary(title, summary):
    """
    Fallback local statistique si Gemini échoue.
    Recherche si un outil connu est cité dans le texte.
    """
    text = f"{title}. {summary}"
    text_lower = text.lower()
    
    matched_tool_key = None
    for key in KNOWN_TOOLS.keys():
        if re.search(r'\b' + re.escape(key) + r'\b', text_lower):
            matched_tool_key = key
            break
            
    if not matched_tool_key:
        for key in KNOWN_TOOLS.keys():
            if key in text_lower:
                matched_tool_key = key
                break
                
    if matched_tool_key:
        tool = KNOWN_TOOLS[matched_tool_key]
        return {
            "is_tool": True,
            "tool_name": tool["name"],
            "update_title_en": f"Update: {title}",
            "update_title_fr": f"Mise à jour : {title}",
            "description_en": summary[:200] + ("..." if len(summary) > 200 else ""),
            "description_fr": summary[:200] + ("..." if len(summary) > 200 else ""),
            "performance_en": tool["benchmarks_en"],
            "performance_fr": tool["benchmarks_fr"],
            "pricing_en": tool["pricing_en"],
            "pricing_fr": tool["pricing_fr"],
            "try_link": tool["url"]
        }
        
    is_about_detection = any(kw in text_lower for kw in ["detector", "detect", "plagiarism", "watermark", "authenticity"])
    
    if is_about_detection:
        words = title.split()
        guessed_name = words[0] if words else "Unknown Tool"
        return {
            "is_tool": True,
            "tool_name": guessed_name,
            "update_title_en": title,
            "update_title_fr": title,
            "description_en": summary[:200] + ("..." if len(summary) > 200 else ""),
            "description_fr": summary[:200] + ("..." if len(summary) > 200 else ""),
            "performance_en": "N/A",
            "performance_fr": "N/A",
            "pricing_en": "N/A",
            "pricing_fr": "N/A",
            "try_link": "N/A"
        }
        
    return {
        "is_tool": False,
        "tool_name": "N/A",
        "update_title_en": title,
        "update_title_fr": title,
        "description_en": summary[:200] + ("..." if len(summary) > 200 else ""),
        "description_fr": summary[:200] + ("..." if len(summary) > 200 else ""),
        "performance_en": "N/A",
        "performance_fr": "N/A",
        "pricing_en": "N/A",
        "pricing_fr": "N/A",
        "try_link": "N/A"
    }

# --- POINT D'ENTRÉE ANALYSE ---
def analyze_article(article):
    import time
    title = clean_html(article.get("title", ""))
    raw_summary = article.get("summary", "")
    clean_summary = clean_html(raw_summary)
    
    analysis = None
    if GEMINI_API_KEY:
        analysis = generate_gemini_summary(title, clean_summary)
        # Respect rate limits
        time.sleep(4)
        
    if not analysis:
        if GEMINI_API_KEY:
            logging.info(f"Utilisation du résumeur de repli local pour : '{title[:40]}...'")
        analysis = generate_local_summary(title, clean_summary)
        
    analyzed = article.copy()
    analyzed["title"] = title
    analyzed["summary"] = clean_summary
    
    for k, v in analysis.items():
        analyzed[k] = v
        
    # Enrichissement avec KNOWN_TOOLS
    if analyzed.get("is_tool"):
        tool_name = analyzed.get("tool_name", "").strip()
        tool_key = tool_name.lower()
        
        matched_key = None
        for key in KNOWN_TOOLS.keys():
            if key == tool_key or key in tool_key or tool_key in key:
                matched_key = key
                break
                
        if matched_key:
            ref_tool = KNOWN_TOOLS[matched_key]
            if not analyzed.get("try_link") or analyzed["try_link"] == "N/A" or not analyzed["try_link"].startswith("http"):
                analyzed["try_link"] = ref_tool["url"]
                
            if not analyzed.get("pricing_en") or analyzed["pricing_en"] == "N/A":
                analyzed["pricing_en"] = ref_tool["pricing_en"]
            if not analyzed.get("pricing_fr") or analyzed["pricing_fr"] == "N/A":
                analyzed["pricing_fr"] = ref_tool["pricing_fr"]
                
            if not analyzed.get("performance_en") or analyzed["performance_en"] == "N/A":
                analyzed["performance_en"] = ref_tool["benchmarks_en"]
            if not analyzed.get("performance_fr") or analyzed["performance_fr"] == "N/A":
                analyzed["performance_fr"] = ref_tool["benchmarks_fr"]
                
            analyzed["tool_name"] = ref_tool["name"]
            analyzed["is_new_tool"] = False
        else:
            # Nouvel outil détecté
            analyzed["is_new_tool"] = True
            if not analyzed.get("try_link") or analyzed["try_link"] == "N/A" or not analyzed["try_link"].startswith("http"):
                analyzed["try_link"] = article.get("link", "N/A")
            if not analyzed.get("pricing_en") or analyzed["pricing_en"] == "N/A":
                analyzed["pricing_en"] = "N/A"
            if not analyzed.get("pricing_fr") or analyzed["pricing_fr"] == "N/A":
                analyzed["pricing_fr"] = "N/A"
            if not analyzed.get("performance_en") or analyzed["performance_en"] == "N/A":
                analyzed["performance_en"] = "N/A"
            if not analyzed.get("performance_fr") or analyzed["performance_fr"] == "N/A":
                analyzed["performance_fr"] = "N/A"
    else:
        analyzed["is_new_tool"] = False
        
    # Compatibilité avec le script original (pour ne pas casser d'autres parties)
    analyzed["narrative_summary"] = analyzed.get("description_fr", clean_summary[:200])
    
    return analyzed

if __name__ == "__main__":
    test_article = {
        "title": "GPTZero adds detection for stealth-writer bypassing <b>mechanisms</b>",
        "summary": "This update helps professors identify students using AI humanizers like BypassGPT. The false positive rate remains under 1%.",
        "link": "https://example.com/test"
    }
    print("Article traité :", analyze_article(test_article))
