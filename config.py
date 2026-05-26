import os

# =====================================================================
# POIDS DES CATÉGORIES (De 1 à 5)
# =====================================================================
CATEGORY_WEIGHTS = {
    "core_keywords": 5,
    "tools_to_watch": 5,
    "evasion_bypass": 5,
    "scientific_research": 4,
    "math_statistics": 4,
    "nlp_techniques": 3,
    "llm_specific": 3,
    "cybersecurity_forensic": 3,
    "quality_benchmarks": 2,
    "regulation_academic": 2,
    "long_tail": 2,
    "social_hashtags": 1
}

# =====================================================================
# SEUILS ET FILTRES DE PERTINENCE
# =====================================================================
MIN_RELEVANCE_SCORE = 3

def get_interest_level(score):
    if score >= 10:
        return "Fort"
    elif score >= 5:
        return "Moyen"
    else:
        return "Faible"

# Fenêtre d'analyse temporelle (en jours)
MAX_AGE_DAYS = 3

# =====================================================================
# DICTIONNAIRE DE MOTS-CLÉS
# =====================================================================
KEYWORDS = {
    "core_keywords": [
        "ai text detector", "ai content detector", "ai generated text detection",
        "ai writing detector", "llm detector", "gpt detector", "chatgpt detector",
        "generative ai detection", "synthetic text detection", "machine generated text detection",
        "ai plagiarism detector", "ai authorship detection", "ai generated document detection",
        "ai generated essay detection", "ai content authenticity", "ai detection software",
        "ai detector tool", "ai generated content classifier"
    ],
    "tools_to_watch": [
        "gptzero", "turnitin ai", "originality.ai", "copyleaks", "winston ai",
        "zerogpt", "sapling ai detector", "writer ai detector", "hive moderation",
        "crossplag ai detector", "quillbot detector", "smodin ai detector",
        "undetectable ai", "stealthwriter", "bypassgpt"
    ],
    "evasion_bypass": [
        "ai detector bypass", "ai detector evasion", "humanizer", "ai humanizer",
        "anti ai detector", "undetectable ai", "prompt obfuscation", "adversarial attack",
        "adversarial prompting", "semantic rewriting", "text paraphrasing",
        "ai text rewriting", "watermark removal", "detector jailbreak",
        "ai stealth writing", "detector resistant text"
    ],
    "scientific_research": [
        "machine generated text detection", "neural text detection", "synthetic language detection",
        "llm watermarking", "watermarked text detection", "detectgpt", "radar benchmark",
        "openai watermark", "retrieval based detection", "contrastive detection",
        "zero shot ai detection", "supervised ai detection", "unsupervised ai detection",
        "few shot detection", "ai provenance"
    ],
    "math_statistics": [
        "perplexity", "burstiness", "entropy", "cross entropy", "token entropy",
        "probabilistic detection", "statistical text analysis", "distribution analysis",
        "likelihood estimation", "classifier confidence", "sequence probability",
        "token distribution", "sampling temperature", "watermark detection",
        "cryptographic watermarking"
    ],
    "nlp_techniques": [
        "stylometry", "stylometric analysis", "computational linguistics",
        "linguistic fingerprinting", "semantic analysis", "semantic fingerprinting",
        "token probability", "entropy analysis", "text classification",
        "transformer classifier", "language model detection", "nlp forensic",
        "forensic linguistics", "text attribution", "authorship verification",
        "machine text attribution", "human vs ai text classification"
    ],
    "llm_specific": [
        "gpt generated text", "chatgpt generated content", "claude generated text",
        "gemini generated text", "llama generated text", "mistral ai text",
        "openai generated content", "llm generated essay", "llm generated document",
        "large language model detection", "foundation model detection"
    ],
    "cybersecurity_forensic": [
        "digital forensics", "content provenance", "document authenticity",
        "deepfake text", "information integrity", "misinformation detection",
        "synthetic media detection", "trust and safety ai", "ai generated misinformation",
        "content verification", "digital authenticity", "forensic ai"
    ],
    "quality_benchmarks": [
        "false positive", "false negative", "ai detector accuracy", "ai detector benchmark",
        "precision recall", "detection robustness", "classifier evaluation",
        "roc curve", "f1 score", "benchmark dataset", "evaluation framework",
        "detection reliability", "multilingual detection", "bias in ai detectors"
    ],
    "regulation_academic": [
        "academic integrity", "ai policy", "ai cheating", "ai misuse",
        "education technology", "ai in education", "ai academic fraud",
        "university ai policy", "ai regulation", "responsible ai",
        "ai ethics", "trustworthy ai", "content authenticity", "digital trust"
    ],
    "long_tail": [
        "best ai detector 2026", "most accurate ai detector", "ai detector comparison",
        "ai detector benchmark study", "how ai detectors work", "limitations of ai detectors",
        "can ai detectors detect paraphrasing", "ai detector false positives",
        "multilingual ai detection", "ai detection for education",
        "detecting chatgpt generated essays", "bypassing ai detection systems",
        "watermarking llm generated text"
    ],
    "social_hashtags": [
        "#aidetection", "#aicontentdetection", "#gptzero", "#turnitin",
        "#aiwriting", "#generativeai", "#llm", "#aiethics", "#aiplagiarism",
        "#aiforensics", "#responsibleai", "#contentauthenticity", "#syntheticmedia"
    ]
}

# =====================================================================
# SOURCES RSS ET CONFIGURATION DES APIS
# =====================================================================
RSS_FEEDS = [
    # Blogs d'éditeurs de détecteurs
    {"name": "Copyleaks Blog", "url": "https://copyleaks.com/blog/feed"},
    {"name": "Winston AI Blog", "url": "https://gowinston.ai/blog/feed/"},
    {"name": "GPTZero News", "url": "https://gptzero.me/news/rss"},

    # Blogs scientifiques & NLP
    {"name": "Hugging Face Blog", "url": "https://huggingface.co/blog/feed.xml"},
    {"name": "Google Research Blog", "url": "https://research.google/blog/feed/"},
    {"name": "Lil'Log (Lilian Weng)", "url": "https://lilianweng.github.io/lil-log/feed.xml"},
    {"name": "Meta Engineering", "url": "https://engineering.fb.com/feed/"},
    {"name": "Meta Research", "url": "https://research.facebook.com/feed/"},

    # Médias Tech & Éducatifs
    {"name": "Wired AI", "url": "https://www.wired.com/feed/category/gear/latest/rss"},
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/"},
    {"name": "Inside Higher Ed", "url": "https://www.insidehighered.com/feed"}
]

# Blogs sans RSS (Scraping)
HTML_BLOGS_TO_SCRAPE = [
    {"name": "Originality.ai Blog", "url": "https://originality.ai/blog", "base_url": "https://originality.ai"},
    {"name": "Turnitin Blog", "url": "https://www.turnitin.com/blog", "base_url": "https://www.turnitin.com"},
    {"name": "Compilatio Blog", "url": "https://www.compilatio.net/fr/blog", "base_url": "https://www.compilatio.net"}
]

# Subreddits (JSON API)
REDDIT_SUBREDDITS = [
    {"subreddit": "ChatGPT", "query": "AI text detection OR AI detector"},
    {"subreddit": "LocalLLaMA", "query": "watermarking OR AI text detection"},
    {"subreddit": "education", "query": "AI detector OR AI plagiarism"}
]

# Requête arXiv (APIcs.AI & cs.CL)
ARXIV_QUERY = 'all:"AI text detection" OR all:"LLM watermarking" OR all:"machine generated text"'

# =====================================================================
# BASE DE DONNÉES DE RÉFÉRENCE DES OUTILS DE DÉTECTION D'IA
# =====================================================================
KNOWN_TOOLS = {
    "gptzero": {
        "name": "GPTZero",
        "url": "https://gptzero.me",
        "pricing_en": "Freemium (10k words/mo; Premium from $10-20/mo)",
        "pricing_fr": "Freemium (10k mots/mois ; Premium à partir de 10-20 $/mois)",
        "access_en": "Web App, API, LMS Integration, Chrome Extension",
        "access_fr": "Web App, API, Intégration LMS, Extension Chrome",
        "benchmarks_en": "99.3% accuracy, 0.24% FPR. Highly robust on GPT-5 (100%) and o3 (96.3%). Includes Writing Replay.",
        "benchmarks_fr": "Précision de 99,3 %, 0,24 % de faux positifs. Très robuste sur GPT-5 (100 %) et o3 (96,3 %). Inclut l'historique d'écriture.",
    },
    "pangram labs": {
        "name": "Pangram Labs",
        "url": "https://pangram.com",
        "pricing_en": "5 free credits/day; Pro from $20/mo; API at $0.05/request",
        "pricing_fr": "5 crédits gratuits/jour ; Pro à partir de 20 $/mois ; API à 0,05 $/requête",
        "access_en": "Web App, API, Enterprise Integration",
        "access_fr": "Web App, API, Intégration entreprise",
        "benchmarks_en": "99.8% accuracy, 0.004% FPR (highest protection). Detects AI assistance and identifies source model.",
        "benchmarks_fr": "Précision de 99,8 %, 0,004 % de faux positifs (sécurité maximale). Détecte l'assistance et identifie le modèle source.",
    },
    "turnitin": {
        "name": "Turnitin",
        "url": "https://turnitin.com",
        "pricing_en": "Custom institutional pricing",
        "pricing_fr": "Sur devis institutionnel uniquement",
        "access_en": "LMS Integration (Canvas, Blackboard, Moodle)",
        "access_fr": "Intégration native LMS (Canvas, Blackboard, Moodle)",
        "benchmarks_en": "82.5% - 92.0% accuracy, 0.51% - 1.28% FPR. Conservative approach favoring human authors.",
        "benchmarks_fr": "Précision de 82,5 % - 92,0 %, 0,51 % - 1,28 % de faux positifs. Approche prudente protégeant les auteurs.",
    },
    "copyleaks": {
        "name": "Copyleaks",
        "url": "https://copyleaks.com",
        "pricing_en": "Personal from $13.99/mo; Pro from $74.99/mo",
        "pricing_fr": "Personnel à partir de 13,99 $/mois ; Pro à partir de 74,99 $/mois",
        "access_en": "Web App, API, LMS Integration, Chrome Extension",
        "access_fr": "Web App, API, Intégration LMS, Extension Chrome",
        "benchmarks_en": "90.7% - 94.0% accuracy, 4.0% - 5.26% FPR. Strong in code and multilingual detection.",
        "benchmarks_fr": "Précision de 90,7 % - 94,0 %, 4,0 % - 5,26 % de faux positifs. Fort en multilingue et détection de code.",
    },
    "originality.ai": {
        "name": "Originality.ai",
        "url": "https://originality.ai",
        "pricing_en": "Pay-as-you-go from $30 (3k credits); Pro from $14.95/mo",
        "pricing_fr": "À la demande dès 30 $ (3k crédits) ; Pro dès 14,95 $/mois",
        "access_en": "Web App, API, Chrome Extension, WordPress Plugin",
        "access_fr": "Web App, API, Extension Chrome, Plugin WordPress",
        "benchmarks_en": "83% accuracy (drops to 31% on GPT-5, 7.6% on o3). High FPR (4.79% - 5.7%). High detection of humanized content.",
        "benchmarks_fr": "Précision de 83 % (chute à 31 % sur GPT-5, 7,6 % sur o3). FPR élevé (4,79 % - 5,7 %). Très fort contre le texte humanisé.",
    },
    "compilatio": {
        "name": "Compilatio",
        "url": "https://compilatio.net",
        "pricing_en": "Institutional subscription quote (Magister, Studium)",
        "pricing_fr": "Sur devis institutionnel (Magister, Studium)",
        "access_en": "Web App, LMS Integration",
        "access_fr": "Web App, Intégration LMS",
        "benchmarks_en": "94.0% - 99.0% accuracy, <1.0% FPR. Multilingual (24 languages) with granular highlight of suspect segments.",
        "benchmarks_fr": "Précision de 94,0 % - 99,0 %, faux positifs < 1,0 %. Multilingue (24 langues) avec surlignage granulaire des passages suspectés.",
    },
    "hive moderation": {
        "name": "Hive Moderation",
        "url": "https://hivemoderation.com",
        "pricing_en": "Pay-per-use API; Enterprise custom pricing",
        "pricing_fr": "API facturée à l'usage ; Formules Enterprise sur devis",
        "access_en": "REST API, Enterprise Dashboard",
        "access_fr": "API REST, Console Enterprise",
        "benchmarks_en": "Multimodal (Text, Audio, Video, Image, CSAM). Vulnerable to controlnet/inpainting.",
        "benchmarks_fr": "Multimodal (Texte, Audio, Vidéo, Image, CSAM). Vulnérable aux retouches avancées d'images (ControlNet).",
    },
    "winston ai": {
        "name": "Winston AI",
        "url": "https://gowinston.ai",
        "pricing_en": "From $18/mo for 80k words",
        "pricing_fr": "À partir de 18 $/mois pour 80k mots",
        "access_en": "Web App, Chrome Extension",
        "access_fr": "Web App, Extension navigateur",
        "benchmarks_en": "High publisher claimed accuracy (~99.98%). Features OCR extraction from images.",
        "benchmarks_fr": "Haute précision revendiquée par l'éditeur (~99,98 %). Intègre l'extraction OCR depuis les images.",
    },
    "zerogpt": {
        "name": "ZeroGPT",
        "url": "https://zerogpt.com",
        "pricing_en": "Free base tier; Premium subscription available",
        "pricing_fr": "Gratuit de base ; Abonnements Premium disponibles",
        "access_en": "Web App, API",
        "access_fr": "Web App, API",
        "benchmarks_en": "70.0% - 73.75% accuracy. Very high False Positive Rate (20.51% - 33.0%). Not recommended for academic use.",
        "benchmarks_fr": "Précision de 70,0 % - 73,75 %. Taux de faux positifs critique (20,51 % - 33,0 %). Fortement déconseillé pour l'académique.",
    },
    "undetectable ai": {
        "name": "Undetectable AI",
        "url": "https://undetectable.ai",
        "pricing_en": "From $19/mo",
        "pricing_fr": "À partir de 19 $/mois",
        "access_en": "Web App",
        "access_fr": "Web App",
        "benchmarks_en": "Hybrid tool (detector + aggressive humanizer). Detection accuracy is around 85% - 90% (without FPR).",
        "benchmarks_fr": "Outil hybride (détecteur + humaniseur agressif). Précision en détection pure d'environ 85 % - 90 %.",
    }
}

# =====================================================================
# CONFIGURATION EMAIL SMTP (Chargée depuis l'environnement)
# =====================================================================
SMTP_HOST = os.environ.get("SMTP_HOST") or "smtp.gmail.com"
SMTP_PORT_env = os.environ.get("SMTP_PORT")
SMTP_PORT = int(SMTP_PORT_env) if SMTP_PORT_env and SMTP_PORT_env.isdigit() else 587
SMTP_USER = os.environ.get("SMTP_USER") or ""
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD") or ""
EMAIL_TO = os.environ.get("EMAIL_TO") or "stoniot005@gmail.com, adanlienclounonprecieux877@gmail.com"
FROM_EMAIL = os.environ.get("FROM_EMAIL") or SMTP_USER
FROM_NAME = os.environ.get("FROM_NAME") or "Veille Détection IA"

# Clé API Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
