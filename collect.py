import urllib.parse
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
import feedparser
import logging
from datetime import datetime
import json
import os
from config import RSS_FEEDS, HTML_BLOGS_TO_SCRAPE, REDDIT_SUBREDDITS, ARXIV_QUERY

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# En-têtes standards pour contourner les blocages HTTP simples
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# --- 1. COLLECTE RSS ---
def collect_rss_feeds():
    logging.info("Début de la collecte des flux RSS...")
    articles = []
    
    for feed_info in RSS_FEEDS:
        name = feed_info["name"]
        url = feed_info["url"]
        logging.info(f"Requête RSS : {name} ({url})")
        
        try:
            feed = feedparser.parse(url)
            count = 0
            for entry in feed.entries:
                # Normalisation de la date
                pub_date = entry.get("published", entry.get("updated", ""))
                
                articles.append({
                    "title": entry.get("title", "Sans titre"),
                    "summary": entry.get("summary", ""),
                    "link": entry.get("link", ""),
                    "published": pub_date,
                    "source": name,
                    "collected_at": datetime.now().isoformat()
                })
                count += 1
            logging.info(f"✓ {count} articles collectés depuis {name}")
        except Exception as e:
            logging.error(f"✗ Erreur lors de la lecture du flux RSS {name} : {e}")
            
    return articles

# --- 2. SCRAPING HTML DES BLOGS SANS FLUX RSS ---
def scrape_blogs():
    logging.info("Début du scraping des blogs HTML...")
    articles = []
    
    for blog in HTML_BLOGS_TO_SCRAPE:
        name = blog["name"]
        url = blog["url"]
        base_url = blog["base_url"]
        logging.info(f"Scraping blog : {name} ({url})")
        
        try:
            response = requests.get(url, headers=DEFAULT_HEADERS, timeout=15)
            if response.status_code != 200:
                logging.warning(f"[!] Échec du scraping pour {name} (Status code: {response.status_code})")
                continue
                
            soup = BeautifulSoup(response.text, "html.parser")
            seen_links = set()
            count = 0
            
            # Recherche générique des liens dans le HTML
            for a in soup.find_all("a", href=True):
                href = a["href"]
                # Cible les structures d'articles
                if ("/blog/" in href or "/news/" in href or "/resource/" in href or "/communique-" in href) and href not in ("/blog/", "/blog", "/news/"):
                    full_url = href if href.startswith("http") else base_url.rstrip("/") + "/" + href.lstrip("/")
                    title = a.get_text(strip=True)
                    
                    if full_url not in seen_links and len(title) > 15:
                        seen_links.add(full_url)
                        articles.append({
                            "title": title,
                            "summary": "Consulter le site officiel pour lire l'intégralité de l'article.",
                            "link": full_url,
                            "published": datetime.now().isoformat(),  # Date de scraping par défaut
                            "source": name,
                            "collected_at": datetime.now().isoformat()
                        })
                        count += 1
            logging.info(f"✓ {count} articles extraits par scraping pour {name}")
        except Exception as e:
            logging.error(f"✗ Erreur lors du scraping de {name} : {e}")
            
    return articles

# --- 3. REQUÊTES REDDIT API JSON ---
def collect_reddit():
    logging.info("Début de la collecte des subreddits...")
    posts = []
    
    # Reddit exige un User-Agent spécifique sous peine d'erreur 429
    reddit_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AI-Detection-Watch-Bot/1.0"
    }
    
    for sub in REDDIT_SUBREDDITS:
        subreddit = sub["subreddit"]
        query = sub["query"]
        logging.info(f"Recherche Reddit : r/{subreddit} (Requête: '{query}')")
        
        search_url = f"https://www.reddit.com/r/{subreddit}/search.json"
        params = {
            "q": query,
            "restrict_sr": 1,
            "sort": "new",
            "limit": 15
        }
        
        try:
            response = requests.get(search_url, params=params, headers=reddit_headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                children = data.get("data", {}).get("children", [])
                count = 0
                for child in children:
                    p = child["data"]
                    # Convertit timestamp Reddit (UTC) en ISO format
                    created_utc = p.get("created_utc")
                    pub_date = datetime.utcfromtimestamp(created_utc).isoformat() if created_utc else ""
                    
                    posts.append({
                        "title": p.get("title", ""),
                        "summary": p.get("selftext", "")[:300] + "..." if p.get("selftext") else "Discussion Reddit",
                        "link": f"https://www.reddit.com{p.get('permalink')}",
                        "published": pub_date,
                        "source": f"Reddit r/{subreddit}",
                        "collected_at": datetime.now().isoformat()
                    })
                    count += 1
                logging.info(f"✓ {count} posts récupérés pour r/{subreddit}")
            else:
                logging.warning(f"[!] Échec Reddit pour r/{subreddit} (Code: {response.status_code})")
        except Exception as e:
            logging.error(f"✗ Erreur sur Reddit r/{subreddit} : {e}")
            
    return posts

# --- 4. REQUÊTES ARXIV API ---
def collect_arxiv():
    logging.info("Début de la collecte d'arXiv...")
    papers = []
    
    query_encoded = urllib.parse.quote(ARXIV_QUERY)
    url = f"http://export.arxiv.org/api/query?search_query={query_encoded}&max_results=20&sortBy=submittedDate&sortOrder=descending"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            count = 0
            
            for entry in root.findall('atom:entry', ns):
                title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
                link = entry.find("atom:link[@rel='alternate']", ns).attrib['href']
                published = entry.find('atom:published', ns).text
                summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ') if entry.find('atom:summary', ns) is not None else ""
                
                papers.append({
                    "title": title,
                    "summary": summary[:400] + "...",
                    "link": link,
                    "published": published,
                    "source": "arXiv Academic API",
                    "collected_at": datetime.now().isoformat()
                })
                count += 1
            logging.info(f"✓ {count} articles scientifiques importés depuis arXiv")
        else:
            logging.warning(f"[!] Échec de requête arXiv (Code: {response.status_code})")
    except Exception as e:
        logging.error(f"✗ Erreur lors de la requête arXiv : {e}")
        
    return papers

# --- EXÉCUTION COMMUNE ---
def run_collection():
    logging.info("========== DÉBUT DE LA COLLECTE MULTI-SOURCES ==========")
    all_articles = []
    
    # Exécution séquentielle de chaque collecteur
    all_articles.extend(collect_rss_feeds())
    all_articles.extend(scrape_blogs())
    all_articles.extend(collect_reddit())
    all_articles.extend(collect_arxiv())
    
    logging.info(f"========== COLLECTE TERMINÉE : {len(all_articles)} ARTICLES RÉCUPÉRÉS ==========")
    return all_articles

if __name__ == "__main__":
    articles = run_collection()
    # Sauvegarde de démo pour tests unitaires directs
    import csv
    raw_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    filepath = os.path.join(raw_dir, f"raw_articles_{datetime.now().strftime('%d_%m_%Y')}.csv")
    
    if articles:
        with open(filepath, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=articles[0].keys())
            writer.writeheader()
            writer.writerows(articles)
        print(f"[DEBUG] Fichier brut généré : {filepath}")
