import smtplib
import os
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path
from datetime import datetime
from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, EMAIL_TO, FROM_EMAIL, FROM_NAME

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# --- CSS ET FORMATAGE DE L'EMAIL HTML ---
def build_html_body(articles, date_str):
    # En-tête HTML de base avec style premium CSS en ligne
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #0f172a;
                background-color: #f1f5f9;
                padding: 20px;
            }}
            .container {{
                max-width: 680px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            }}
            .header {{
                background: #0f172a;
                color: #ffffff;
                padding: 40px 32px;
                text-align: center;
            }}
            .header h1 {{
                font-size: 26px;
                font-weight: 700;
                letter-spacing: -0.5px;
                margin-bottom: 8px;
            }}
            .header p {{
                font-size: 14px;
                color: #94a3b8;
                font-weight: 400;
            }}
            .content {{
                padding: 32px;
            }}
            .section-title {{
                font-size: 18px;
                font-weight: 700;
                color: #0f172a;
                margin-bottom: 16px;
                padding-bottom: 8px;
                border-bottom: 2px solid #cbd5e1;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .summary-box {{
                background: #f8fafc;
                border-left: 4px solid #3b82f6;
                border-radius: 0 8px 8px 0;
                padding: 20px;
                margin-bottom: 32px;
            }}
            .summary-box h3 {{
                font-size: 15px;
                font-weight: 600;
                color: #1e3a8a;
                margin-bottom: 8px;
            }}
            .summary-box p {{
                font-size: 14.5px;
                color: #334155;
                font-style: italic;
            }}
            .category-block {{
                margin-bottom: 32px;
            }}
            .category-header {{
                font-size: 15px;
                font-weight: 600;
                color: #475569;
                background: #e2e8f0;
                padding: 6px 12px;
                border-radius: 4px;
                margin-bottom: 16px;
                display: inline-block;
            }}
            .item {{
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 16px;
                transition: transform 0.2s;
            }}
            .item-title {{
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 8px;
            }}
            .item-title a {{
                color: #1e293b;
                text-decoration: none;
            }}
            .item-title a:hover {{
                color: #3b82f6;
            }}
            .meta-row {{
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 12px;
                flex-wrap: wrap;
            }}
            .source-badge {{
                font-size: 12px;
                font-weight: 500;
                color: #64748b;
                background: #f1f5f9;
                padding: 2px 8px;
                border-radius: 9999px;
            }}
            .score-badge {{
                font-size: 12px;
                font-weight: 600;
                padding: 2px 8px;
                border-radius: 4px;
            }}
            .score-fort {{
                background: #fee2e2;
                color: #b91c1c;
            }}
            .score-moyen {{
                background: #dbeafe;
                color: #1d4ed8;
            }}
            .score-faible {{
                background: #f1f5f9;
                color: #475569;
            }}
            .summary-text {{
                font-size: 14px;
                color: #334155;
                margin-bottom: 12px;
            }}
            .narrative-text {{
                font-size: 14px;
                color: #0f172a;
                background: #f0f9ff;
                border: 1px solid #bae6fd;
                border-radius: 6px;
                padding: 12px;
                font-weight: 500;
            }}
            .visuals-section {{
                margin-top: 32px;
                text-align: center;
            }}
            .chart-img {{
                max-width: 100%;
                height: auto;
                margin-bottom: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px 0 rgba(0,0,0,0.05);
            }}
            .footer {{
                background: #f8fafc;
                padding: 24px 32px;
                text-align: center;
                border-top: 1px solid #e2e8f0;
            }}
            .footer p {{
                font-size: 12px;
                color: #94a3b8;
                margin: 4px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Détection de Contenus Générés par IA</h1>
                <p>Veille Technologique & Analyse du {date_str}</p>
            </div>
            <div class="content">
    """
    
    # 1. Ajout de la boîte Synthèse IA globale au début de l'email
    html += """
                <div class="section-title">Synthèse de la Période</div>
                <div class="summary-box">
                    <h3>💡 Principaux enseignements</h3>
    """
    
    # Compilation d'un résumé global en combinant les résumés narratifs des articles d'importance "Fort"
    forts = [a for a in articles if a.get("interest_level") == "Fort"]
    moyennes = [a for a in articles if a.get("interest_level") == "Moyen"]
    
    if forts:
        summary_paragraphs = "<p>" + "</p><p>".join([a["narrative_summary"] for a in forts[:3]]) + "</p>"
    elif moyennes:
        summary_paragraphs = "<p>" + "</p><p>".join([a["narrative_summary"] for a in moyennes[:2]]) + "</p>"
    else:
        summary_paragraphs = "<p>Aucun article majeur détecté sur les 3 derniers jours. Le volume global reste stable.</p>"
        
    html += f"{summary_paragraphs}</div>"
    
    # 2. Ajout des articles groupés par thématique/catégorie
    html += """
                <div class="section-title">Articles de Veille Récents</div>
    """
    
    # Regrouper par catégorie
    grouped = {}
    for article in articles:
        cats = article.get("matched_categories", "autre").split(",")
        # Assigne au premier match principal
        primary_cat = cats[0] if cats else "autre"
        grouped.setdefault(primary_cat, []).append(article)
        
    for category, cat_articles in grouped.items():
        cat_title = category.replace("_", " ").upper()
        html += f"""
                <div class="category-block">
                    <span class="category-header">{cat_title}</span>
        """
        
        # Tri des articles de la catégorie par score de pertinence décroissant
        cat_articles.sort(key=lambda x: int(x.get("relevance_score", 0)), reverse=True)
        
        for item in cat_articles:
            level = item.get("interest_level", "Faible")
            badge_class = "score-fort" if level == "Fort" else ("score-moyen" if level == "Moyen" else "score-faible")
            
            html += f"""
                    <div class="item">
                        <div class="item-title"><a href="{item.get('link', '#')}">{item.get('title', 'Sans titre')}</a></div>
                        <div class="meta-row">
                            <span class="source-badge">{item.get('source', 'Inconnue')}</span>
                            <span class="score-badge {badge_class}">Intérêt {level} (Score: {item.get('relevance_score', 0)})</span>
                        </div>
                        <div class="summary-text">{item.get('summary', '')[:250]}...</div>
                        <div class="narrative-text">📢 {item.get('narrative_summary', '')}</div>
                    </div>
            """
        html += "</div>"
        
    # 3. Ajout des statistiques graphiques (Inline avec CID)
    html += """
                <div class="section-title">Analyse Statistique</div>
                <div class="visuals-section">
                    <img class="chart-img" src="cid:cat_chart" alt="Répartition par Catégorie">
                    <img class="chart-img" src="cid:kw_chart" alt="Mots-Clés Dominants">
                </div>
            </div>
            <div class="footer">
                <p>Ce bulletin de veille technologique a été généré automatiquement.</p>
                <p>Équipe Veille LRSIA | Plateforme de Monitoring des IA Génératives</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def safe_print(text):
    import sys
    try:
        print(text)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or 'utf-8'
        try:
            print(text.encode(encoding, errors='replace').decode(encoding))
        except Exception:
            print(text.encode('ascii', errors='replace').decode('ascii'))

# --- ENVOI DE L'EMAIL ---
def send_digest_email(articles, cat_chart_path, kw_chart_path):
    date_str = datetime.now().strftime("%d/%m/%Y")
    
    # 1. Vérification de la configuration
    if not all([SMTP_USER, SMTP_PASSWORD, EMAIL_TO]):
        status_msg = f"SMTP_USER='{SMTP_USER or 'vide'}', SMTP_PASSWORD='{'détecté (***)' if SMTP_PASSWORD else 'vide'}', EMAIL_TO='{EMAIL_TO or 'vide'}'"
        logging.error(f"Configuration SMTP ou destinataires EMAIL_TO manquante ({status_msg}). Envoi annulé.")
        logging.warning("--- APERÇU DE LA NEWSLETTER DANS LA CONSOLE ---")
        for idx, art in enumerate(articles[:5]):
            safe_print(f"[{idx+1}] [{art['interest_level']}] {art['title']}")
            safe_print(f"    [Resume] : {art['narrative_summary']}")
            safe_print(f"    Lien : {art['link']}\n")
        return False
        
    logging.info(f"Préparation de l'envoi de l'email à : {EMAIL_TO}")
    
    # 2. Création de la structure MIME avec images intégrées (MIMEMultipart 'related')
    msg = MIMEMultipart("related")
    msg["Subject"] = f"🔍 Veille Détection IA & Documents - {date_str}"
    msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"] = EMAIL_TO
    
    # Partie alternative pour le texte brut et le HTML
    msg_alt = MIMEMultipart("alternative")
    msg.attach(msg_alt)
    
    # Texte brut en fallback
    text_fallback = f"Veille Détection IA du {date_str}\n\n"
    for art in articles[:10]:
        text_fallback += f"- [{art.get('interest_level')}] {art.get('title')}\n  URL: {art.get('link')}\n  Résumé: {art.get('narrative_summary')}\n\n"
        
    msg_alt.attach(MIMEText(text_fallback, "plain", "utf-8"))
    
    # Génération du HTML
    html_content = build_html_body(articles, date_str)
    msg_alt.attach(MIMEText(html_content, "html", "utf-8"))
    
    # 3. Pièces jointes graphiques avec CID pour l'affichage en ligne
    for img_path, cid in [(cat_chart_path, "cat_chart"), (kw_chart_path, "kw_chart")]:
        if img_path and os.path.exists(img_path):
            try:
                with open(img_path, "rb") as f:
                    img_data = f.read()
                mime_img = MIMEImage(img_data)
                mime_img.add_header("Content-ID", f"<{cid}>")
                mime_img.add_header("Content-Disposition", "inline", filename=os.path.basename(img_path))
                msg.attach(mime_img)
                logging.info(f"✓ Image jointe avec succès : {img_path} (CID: {cid})")
            except Exception as e:
                logging.error(f"✗ Impossible de joindre l'image {img_path} : {e}")
                
    # 4. Envoi SMTP
    try:
        destinataires = [d.strip() for d in EMAIL_TO.split(",")]
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, destinataires, msg.as_string())
            
        logging.info(f"✓ Email de veille envoyé avec succès à {len(destinataires)} destinataires.")
        return True
    except Exception as e:
        logging.error(f"✗ Erreur lors de l'envoi de l'email : {e}")
        return False
