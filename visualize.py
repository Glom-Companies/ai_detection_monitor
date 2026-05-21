import csv
import os
import logging
from datetime import datetime
import matplotlib.pyplot as plt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Palette de couleurs Premium HSL/Hex (Sleek Slate, Deep Blue, Emerald, Amber, etc.)
PREMIUM_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4', '#ec4899', '#84cc16', '#6b7280', '#1e3b8a']

def generate_charts():
    logging.info("========== DÉBUT DE LA GÉNÉRATION DES GRAPHIQUES ==========")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    date_str = datetime.now().strftime("%d_%m_%Y")
    
    trends_file = os.path.join(base_dir, "data", "trends", f"trends_{date_str}.csv")
    cats_file = os.path.join(base_dir, "data", "trends", f"categories_{date_str}.csv")
    
    visuals_dir = os.path.join(base_dir, "data", "visuals")
    os.makedirs(visuals_dir, exist_ok=True)
    
    cat_chart_path = os.path.join(visuals_dir, f"category_distribution_{date_str}.png")
    kw_chart_path = os.path.join(visuals_dir, f"keyword_trends_{date_str}.png")
    
    # --- 1. GRAPHIQUE 1 : RÉPARTITION PAR CATÉGORIE ---
    categories = []
    cat_counts = []
    
    if os.path.exists(cats_file):
        with open(cats_file, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                categories.append(row["category"])
                cat_counts.append(int(row["count"]))
                
    if categories:
        plt.figure(figsize=(8, 6))
        # Remplacement des étiquettes brutes par des libellés propres
        labels = [cat.replace("_", " ").title() for cat in categories]
        
        # Style Pie Chart Premium
        plt.pie(
            cat_counts, 
            labels=labels, 
            autopct='%1.1f%%', 
            startangle=140, 
            colors=PREMIUM_COLORS[:len(categories)],
            wedgeprops={"edgecolor": "w", 'linewidth': 1.5, 'antialiased': True}
        )
        plt.title("Répartition des Articles par Catégorie de Veille", fontsize=14, fontweight="bold", pad=20)
        plt.tight_layout()
        plt.savefig(cat_chart_path, dpi=150)
        plt.close()
        logging.info(f"✓ Graphique circulaire des catégories enregistré : {cat_chart_path}")
    else:
        logging.warning("Aucune donnée de catégorie disponible pour la visualisation.")
        
    # --- 2. GRAPHIQUE 2 : TOP 10 DES MOTS-CLÉS LES PLUS MENTIONNÉS ---
    keywords = []
    kw_counts = []
    
    if os.path.exists(trends_file):
        with open(trends_file, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                keywords.append(row["keyword"])
                kw_counts.append(int(row["mentions"]))
                
    # On ne garde que le Top 10
    top_kws = keywords[:10]
    top_counts = kw_counts[:10]
    
    if top_kws:
        plt.figure(figsize=(9, 5.5))
        
        # Inversion pour avoir le mot-clé le plus cité en haut du graphique en barres horizontales
        top_kws.reverse()
        top_counts.reverse()
        
        bars = plt.barh(top_kws, top_counts, color='#3b82f6')
        
        # Ajout des étiquettes de valeur au bout des barres
        for bar in bars:
            width = bar.get_width()
            plt.text(
                width + 0.1, 
                bar.get_y() + bar.get_height()/2, 
                f'{int(width)}', 
                ha='left', 
                va='center', 
                fontsize=10, 
                fontweight='semibold'
            )
            
        plt.title("Top 10 des Mots-Clés les plus Fréquents", fontsize=14, fontweight="bold", pad=15)
        plt.xlabel("Nombre de Mentions dans les Articles", fontsize=11, labelpad=10)
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.tight_layout()
        plt.savefig(kw_chart_path, dpi=150)
        plt.close()
        logging.info(f"✓ Graphique en barres des mots-clés enregistré : {kw_chart_path}")
    else:
        logging.warning("Aucune donnée de mot-clé disponible pour la visualisation.")
        
    logging.info("========== GÉNÉRATION DES GRAPHIQUES TERMINÉE ==========")
    return cat_chart_path, kw_chart_path

if __name__ == "__main__":
    # Test de génération (génère des graphiques vides ou basés sur les fichiers existants)
    generate_charts()
