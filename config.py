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
# CONFIGURATION EMAIL SMTP (Chargée depuis l'environnement)
# =====================================================================
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
EMAIL_TO = os.environ.get("EMAIL_TO", "stoniot005@gmail.com, adanlienclounonprecieux877@gmail.com")
FROM_EMAIL = os.environ.get("FROM_EMAIL", SMTP_USER)
FROM_NAME = os.environ.get("FROM_NAME", "Veille Détection IA")

# Clé API Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
