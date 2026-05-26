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

# --- RENDU DE LA CARTE D'UN OUTIL ---
def render_tool_card(item, lang="en"):
    is_new = item.get("is_new_tool", False)
    level = item.get("interest_level", "Faible")
    badge_class = "score-fort" if level == "Fort" else ("score-moyen" if level == "Moyen" else "score-faible")
    
    if lang == "en":
        title = item.get("update_title_en", item.get("title", ""))
        desc = item.get("description_en", item.get("summary", ""))
        perf = item.get("performance_en", "N/A")
        price = item.get("pricing_en", "N/A")
        cta_text = "Try Tool"
        interest_label = f"Interest: {level}"
        new_badge_html = '<span class="badge-new">NEW TOOL</span>' if is_new else ''
    else:
        title = item.get("update_title_fr", item.get("narrative_summary", ""))
        desc = item.get("description_fr", item.get("narrative_summary", ""))
        perf = item.get("performance_fr", "N/A")
        price = item.get("pricing_fr", "N/A")
        cta_text = "Essayer l'outil"
        interest_label = f"Intérêt : {level}"
        new_badge_html = '<span class="badge-new" style="background-color: #10b981;">NOUVEL OUTIL</span>' if is_new else ''
        
    try_link = item.get("try_link", "#")
    if not try_link or try_link == "N/A":
        try_link = "#"
        
    cta_button_html = ""
    if try_link and try_link != "#":
        cta_button_html = f'<div style="margin-top: 15px;"><a href="{try_link}" class="cta-button" target="_blank">{cta_text} &rarr;</a></div>'
        
    html = f"""
    <div class="item">
        <div class="meta-row">
            <span class="tool-name-badge">{item.get('tool_name', 'Unknown Tool')}</span>
            {new_badge_html}
            <span class="source-badge">{item.get('source', 'Inconnue')}</span>
            <span class="score-badge {badge_class}">{interest_label}</span>
        </div>
        <div class="item-title">{title}</div>
        <div class="summary-text">
            {desc}
        </div>
        <div class="details-row">
            <div class="detail-item"><strong>Performance :</strong> {perf}</div>
            <div class="detail-item"><strong>Pricing / Tarif :</strong> {price}</div>
        </div>
        {cta_button_html}
    </div>
    """
    return html

# --- CSS ET FORMATAGE DE L'EMAIL HTML ---
def build_html_body(articles, date_str):
    # Séparation des niveaux d'intérêt
    forts = [a for a in articles if a.get("interest_level") == "Fort"]
    moyennes = [a for a in articles if a.get("interest_level") == "Moyen"]
    
    # 1. Compilation des résumés globaux
    if forts:
        summary_en = "<p>" + "</p><p>".join([a.get("description_en", "") for a in forts[:3]]) + "</p>"
        summary_fr = "<p>" + "</p><p>".join([a.get("description_fr", "") for a in forts[:3]]) + "</p>"
    elif moyennes:
        summary_en = "<p>" + "</p><p>".join([a.get("description_en", "") for a in moyennes[:2]]) + "</p>"
        summary_fr = "<p>" + "</p><p>".join([a.get("description_fr", "") for a in moyennes[:2]]) + "</p>"
    else:
        summary_en = "<p>No major AI detection tool updates detected over the last 3 days.</p>"
        summary_fr = "<p>Aucune mise à jour majeure d'outils de détection d'IA détectée sur les 3 derniers jours.</p>"

    # Tri des articles par pertinence
    articles_sorted = sorted(articles, key=lambda x: int(x.get("relevance_score", 0)), reverse=True)
    
    # Génération du HTML pour chaque langue
    en_cards = ""
    fr_cards = ""
    for art in articles_sorted:
        en_cards += render_tool_card(art, lang="en")
        fr_cards += render_tool_card(art, lang="fr")
        
    if not articles_sorted:
        en_cards = "<p style='color: #64748b; font-style: italic;'>No tool updates found in this period.</p>"
        fr_cards = "<p style='color: #64748b; font-style: italic;'>Aucune mise à jour d'outil trouvée sur cette période.</p>"

    html = f"""<!DOCTYPE html>
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
            font-size: 24px;
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
            margin-top: 24px;
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
            margin-bottom: 24px;
        }}
        .summary-box h3 {{
            font-size: 15px;
            font-weight: 600;
            color: #1e3a8a;
            margin-bottom: 8px;
        }}
        .summary-box p {{
            font-size: 14px;
            color: #334155;
            font-style: italic;
            margin-bottom: 8px;
        }}
        .summary-box p:last-child {{
            margin-bottom: 0;
        }}
        .item {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 16px;
        }}
        .item-title {{
            font-size: 16px;
            font-weight: 700;
            color: #1e293b;
            margin: 10px 0;
        }}
        .meta-row {{
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }}
        .tool-name-badge {{
            font-size: 11px;
            font-weight: 700;
            color: #ffffff;
            background: #0f172a;
            padding: 3px 10px;
            border-radius: 4px;
            text-transform: uppercase;
        }}
        .badge-new {{
            font-size: 11px;
            font-weight: 700;
            color: #ffffff;
            background: #10b981;
            padding: 3px 8px;
            border-radius: 4px;
            text-transform: uppercase;
        }}
        .source-badge {{
            font-size: 11px;
            font-weight: 500;
            color: #64748b;
            background: #f1f5f9;
            padding: 3px 8px;
            border-radius: 4px;
        }}
        .score-badge {{
            font-size: 11px;
            font-weight: 600;
            padding: 3px 8px;
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
        .details-row {{
            background: #f8fafc;
            border-left: 3px solid #cbd5e1;
            padding: 10px 15px;
            border-radius: 0 6px 6px 0;
            margin-top: 10px;
        }}
        .detail-item {{
            font-size: 13px;
            color: #475569;
            margin-bottom: 4px;
        }}
        .detail-item:last-child {{
            margin-bottom: 0;
        }}
        .cta-button {{
            background: #2563eb;
            color: #ffffff !important;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            display: inline-block;
        }}
        .cta-button:hover {{
            background: #1d4ed8;
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
        <!-- HEADER -->
        <div class="header">
            <h1>AI Text Detection Monitor</h1>
            <p>Veille Technologique & Outils IA - {date_str}</p>
        </div>
        
        <div class="content">
            <!-- ==================== ENGLISH SECTION ==================== -->
            <div class="section-title">AI Detectors Watch (EN)</div>
            <div class="summary-box">
                <h3>💡 Key Lessons & Summaries</h3>
                {summary_en}
            </div>
            {en_cards}
            
            <!-- BILINGUAL DIVIDER -->
            <div style="text-align: center; margin: 50px 0; position: relative;">
                <hr style="border: 0; border-top: 2px dashed #cbd5e1; margin: 0;">
                <span style="background: #ffffff; padding: 0 15px; color: #64748b; font-size: 12px; font-weight: 700; position: absolute; top: -10px; left: 50%; transform: translateX(-50%); text-transform: uppercase; letter-spacing: 1px;">
                    Version Française
                </span>
            </div>
            
            <!-- ==================== FRENCH SECTION ==================== -->
            <div class="section-title">Veille Détecteurs d'IA (FR)</div>
            <div class="summary-box">
                <h3>💡 Principaux enseignements</h3>
                {summary_fr}
            </div>
            {fr_cards}
            
            <!-- STATS GRAPHICS (Shared at bottom) -->
            <div class="section-title">Statistical Trends / Tendances Statistiques</div>
            <div class="visuals-section">
                <img class="chart-img" src="cid:cat_chart" alt="Category Distribution">
                <img class="chart-img" src="cid:kw_chart" alt="Dominant Keywords">
            </div>
        </div>
        
        <!-- FOOTER -->
        <div class="footer">
            <p>This automated tech watch digest was compiled by LRSIA.</p>
            <p>Ce bulletin de veille automatisé a été compilé par le LRSIA.</p>
            <p>&copy; {datetime.now().year} LRSIA | IFRI-UAC | <a href="https://lrsia.ifri-uac.bj/" style="color: #475569;">https://lrsia.ifri-uac.bj/</a></p>
        </div>
    </div>
</body>
</html>"""
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
    
    # 1. Vérification de la configuration SMTP
    if not all([SMTP_USER, SMTP_PASSWORD, EMAIL_TO]):
        status_msg = f"SMTP_USER='{SMTP_USER or 'vide'}', SMTP_PASSWORD='{'détecté (***)' if SMTP_PASSWORD else 'vide'}', EMAIL_TO='{EMAIL_TO or 'vide'}'"
        logging.error(f"Configuration SMTP ou destinataires EMAIL_TO manquante ({status_msg}). Envoi annulé.")
        logging.warning("--- APERÇU DE LA NEWSLETTER DANS LA CONSOLE (BILINGUE) ---")
        for idx, art in enumerate(articles[:5]):
            safe_print(f"[{idx+1}] Tool: {art.get('tool_name')} | New: {art.get('is_new_tool')}")
            safe_print(f"    [EN] : {art.get('update_title_en')}")
            safe_print(f"           {art.get('description_en')}")
            safe_print(f"           Perf: {art.get('performance_en')} | Pricing: {art.get('pricing_en')}")
            safe_print(f"    [FR] : {art.get('update_title_fr')}")
            safe_print(f"           {art.get('description_fr')}")
            safe_print(f"           Perf: {art.get('performance_fr')} | Pricing: {art.get('pricing_fr')}")
            safe_print(f"    Link : {art.get('try_link')}\n")
        return False
        
    logging.info(f"Préparation de l'envoi de l'email à : {EMAIL_TO}")
    
    # 2. Création du message MIME
    msg = MIMEMultipart("related")
    msg["Subject"] = f"🔍 AI Detection Monitor: Tools & Platforms / Veille Outils IA - {date_str}"
    msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"] = EMAIL_TO
    
    # Alternative text/html
    msg_alt = MIMEMultipart("alternative")
    msg.attach(msg_alt)
    
    # Fallback texte brut
    text_fallback = f"AI Detection Monitor / Veille Outils IA du {date_str}\n\n"
    for art in articles[:10]:
        text_fallback += f"Tool: {art.get('tool_name')}\n"
        text_fallback += f"  [EN] Title: {art.get('update_title_en')}\n"
        text_fallback += f"       Summary: {art.get('description_en')}\n"
        text_fallback += f"  [FR] Titre: {art.get('update_title_fr')}\n"
        text_fallback += f"       Résumé: {art.get('description_fr')}\n"
        text_fallback += f"  Link: {art.get('try_link')}\n\n"
        
    msg_alt.attach(MIMEText(text_fallback, "plain", "utf-8"))
    
    # HTML
    html_content = build_html_body(articles, date_str)
    msg_alt.attach(MIMEText(html_content, "html", "utf-8"))
    
    # 3. Pièces jointes graphiques avec CID
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
            
        logging.info(f"✓ Email de veille bilingue envoyé avec succès à {len(destinataires)} destinataires.")
        return True
    except Exception as e:
        logging.error(f"✗ Erreur lors de l'envoi de l'email : {e}")
        return False
