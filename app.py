"""
🍽️ SARAH'MIAM - Assistant Culinaire Bi-culturel France-Maroc
Version: 3.0 FINALE
Auteur: Abdel
Date: 28 Décembre 2025

FONCTIONNALITÉS COMPLÈTES:
- 40 recettes ultra-détaillées (20 FR + 20 MA)
- Génération IA illimitée via Groq
- Géolocalisation automatique (HTML5 + IP + Manuel)
- Météo contextualisée avec suggestions
- Gestion allergies
- Vérification ingrédients
- Mode groupe (multiplication portions)
- Suggestions intelligentes (budget/temps/niveau)
- Détection stress vocal
- Scan frigo photo (Groq Vision)
- Timer cuisine
- Conversions automatiques
- Code-switching FR/Darija naturel
- Vocal main-libre (Whisper + TTS)
- Mode cuisine pas-à-pas
- Comparateur prix 5 enseignes
- GPS enseignes
"""

# =============================================================================
# IMPORTS
# =============================================================================

import streamlit as st
import os
import json
import re
import base64
from datetime import datetime
from groq import Groq
from audio_recorder_streamlit import audio_recorder
import tempfile
import requests

# Charger .env automatiquement
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# =============================================================================
# CONFIGURATION PAGE STREAMLIT (DOIT ÊTRE EN PREMIER)
# =============================================================================

st.set_page_config(
    page_title="Sarah'Miam - Chef Personnel",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# META TAGS PWA - Pour installation sur téléphone avec le bon nom
# =============================================================================

st.markdown("""
<!-- PWA Meta Tags pour installation mobile -->
<meta name="application-name" content="Sarah'Miam">
<meta name="apple-mobile-web-app-title" content="Sarah'Miam">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="mobile-web-app-capable" content="yes">
<meta name="theme-color" content="#FF6B35">
<meta name="msapplication-TileColor" content="#FF6B35">
<meta name="msapplication-navbutton-color" content="#FF6B35">

<!-- Open Graph pour partage réseaux sociaux -->
<meta property="og:title" content="Sarah'Miam - Assistant Culinaire">
<meta property="og:description" content="Ton chef personnel bi-culturel France-Maroc">
<meta property="og:type" content="website">

<!-- Manifest PWA inline -->
<link rel="manifest" href="data:application/json,{
    'name': 'Sarah\\'Miam',
    'short_name': 'Sarah\\'Miam',
    'description': 'Assistant culinaire bi-culturel France-Maroc',
    'start_url': '.',
    'display': 'standalone',
    'background_color': '#FFFFFF',
    'theme_color': '#FF6B35',
    'icons': [{
        'src': 'https://em-content.zobj.net/source/apple/391/pot-of-food_1f372.png',
        'sizes': '120x120',
        'type': 'image/png'
    }]
}">

<style>
    /* Fix pour que le nom apparaisse bien sur mobile */
    @media (display-mode: standalone) {
        header[data-testid="stHeader"] {
            display: none;
        }
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# CONFIGURATION API
# =============================================================================

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    OPENWEATHER_API_KEY = st.secrets.get("OPENWEATHER_API_KEY", "")
except:
    # Fallback pour développement local
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

if not GROQ_API_KEY:
    st.error("⚠️ GROQ_API_KEY manquant! Crée le fichier .streamlit/secrets.toml")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# =============================================================================
# CONSTANTES
# =============================================================================

BUDGET_MAX_PAR_ASSIETTE = 5.0  # euros

# Liste des allergènes courants
ALLERGENES = {
    "gluten": ["farine", "pates", "pain", "couscous", "semoule", "blé"],
    "lactose": ["lait", "creme", "beurre", "fromage", "yaourt"],
    "arachides": ["cacahuete", "arachide"],
    "fruits_a_coque": ["amande", "noix", "noisette", "pistache"],
    "oeufs": ["oeuf", "jaune_oeuf"],
    "poisson": ["saumon", "cabillaud", "thon", "sardine", "anchois", "poisson"],
    "crustaces": ["crevette", "crabe", "homard"],
    "soja": ["soja", "tofu"],
    "celeri": ["celeri"],
    "moutarde": ["moutarde"],
    "sesame": ["sesame"],
    "sulfites": ["vin", "vinaigre"]
}

# Dictionnaire Darija
DICTIONNAIRE_DARIJA = {
    "tomate": "matecha", "oignon": "besla", "carotte": "khizou",
    "pomme de terre": "batata", "poulet": "djaj", "viande": "l7em",
    "poisson": "hout", "agneau": "ghanem", "cumin": "kamoun",
    "cannelle": "karfa", "safran": "zafran", "gingembre": "skinjbir",
    "farine": "dqiq", "huile": "zit", "sel": "mel7a", "poivre": "ibzar"
}

EXPRESSIONS_DARIJA = {
    "bienvenue": "Marhaba bik!",
    "bon_appetit": "Bsaha!",
    "delicieux": "Benin bezzaf!",
    "commence": "Yallah, nwellou!",
    "regarde": "Chouf!",
    "facile": "Sahel!",
    "excellent": "Mezyan bezzaf!",
    "bravo": "Tbarkallah!",
    "courage": "Allah y3awnek!"
}

# Conversions culinaires
CONVERSIONS = {
    "tasse_ml": 250,
    "cuillere_soupe_ml": 15,
    "cuillere_cafe_ml": 5,
    "tasse_farine_g": 125,
    "tasse_sucre_g": 200,
    "tasse_riz_g": 185,
    "oz_g": 28.35,
    "lb_kg": 0.453592
}

# Prix enseignes pour comparateur
PRIX_ENSEIGNES = {
    "Lidl": {
        "poulet_kg": 4.80, "boeuf_kg": 11.20, "viande_mouton_kg": 12.50, "merguez_kg": 8.90,
        "viande_hachee_kg": 9.20, "agneau_kg": 13.50, "porc_kg": 7.80,
        "tomates_kg": 2.10, "oignons_kg": 0.95, "oignon_kg": 0.95, "poivrons_kg": 2.40,
        "courgettes_kg": 1.80, "aubergines_kg": 2.20, "carottes_kg": 1.10, "pommes_de_terre_kg": 1.50,
        "tomates_cerises_kg": 3.20, "salade_kg": 1.80, "celeri_kg": 2.50, "haricots_verts_kg": 3.50,
        "lentilles_kg": 2.80, "pois_chiches_kg": 2.90, "riz_kg": 1.80, "pates_kg": 1.50,
        "farine_kg": 0.90, "couscous_kg": 2.20, "semoule_kg": 1.90,
        "coriandre_kg": 8.50, "persil_kg": 8.00, "menthe_kg": 9.00, "basilic_kg": 10.50,
        "oeufs_unite": 0.25, "fromage_kg": 12.50, "creme_fraiche_kg": 4.80, "beurre_kg": 8.90,
        "lait_litre": 0.95, "yaourt_unite": 0.40,
        "saumon_kg": 16.50, "cabillaud_kg": 12.80, "sardines_kg": 6.50,
        "huile_litre": 4.20, "olives_kg": 6.80, "citrons_kg": 2.50
    },
    "Aldi": {
        "poulet_kg": 4.90, "boeuf_kg": 11.50, "viande_mouton_kg": 12.80, "merguez_kg": 9.20,
        "viande_hachee_kg": 9.50, "agneau_kg": 13.80, "porc_kg": 8.10,
        "tomates_kg": 2.20, "oignons_kg": 0.99, "oignon_kg": 0.99, "poivrons_kg": 2.50,
        "courgettes_kg": 1.90, "aubergines_kg": 2.30, "carottes_kg": 1.15, "pommes_de_terre_kg": 1.55,
        "tomates_cerises_kg": 3.30, "salade_kg": 1.85, "celeri_kg": 2.60, "haricots_verts_kg": 3.60,
        "lentilles_kg": 2.90, "pois_chiches_kg": 3.00, "riz_kg": 1.85, "pates_kg": 1.55,
        "farine_kg": 0.95, "couscous_kg": 2.30, "semoule_kg": 1.95,
        "coriandre_kg": 8.80, "persil_kg": 8.30, "menthe_kg": 9.30, "basilic_kg": 10.80,
        "oeufs_unite": 0.26, "fromage_kg": 12.80, "creme_fraiche_kg": 4.90, "beurre_kg": 9.10,
        "lait_litre": 0.98, "yaourt_unite": 0.42,
        "saumon_kg": 16.90, "cabillaud_kg": 13.10, "sardines_kg": 6.70,
        "huile_litre": 4.30, "olives_kg": 7.00, "citrons_kg": 2.60
    },
    "Leclerc": {
        "poulet_kg": 5.50, "boeuf_kg": 12.90, "viande_mouton_kg": 14.20, "merguez_kg": 10.50,
        "viande_hachee_kg": 10.80, "agneau_kg": 15.20, "porc_kg": 9.20,
        "tomates_kg": 2.80, "oignons_kg": 1.20, "oignon_kg": 1.20, "poivrons_kg": 3.10,
        "courgettes_kg": 2.40, "aubergines_kg": 2.90, "carottes_kg": 1.45, "pommes_de_terre_kg": 1.85,
        "tomates_cerises_kg": 4.10, "salade_kg": 2.30, "celeri_kg": 3.20, "haricots_verts_kg": 4.30,
        "lentilles_kg": 3.50, "pois_chiches_kg": 3.60, "riz_kg": 2.30, "pates_kg": 1.90,
        "farine_kg": 1.20, "couscous_kg": 2.80, "semoule_kg": 2.40,
        "coriandre_kg": 10.50, "persil_kg": 10.00, "menthe_kg": 11.00, "basilic_kg": 12.80,
        "oeufs_unite": 0.32, "fromage_kg": 14.50, "creme_fraiche_kg": 5.80, "beurre_kg": 10.50,
        "lait_litre": 1.15, "yaourt_unite": 0.50,
        "saumon_kg": 19.50, "cabillaud_kg": 15.20, "sardines_kg": 7.80,
        "huile_litre": 5.10, "olives_kg": 8.50, "citrons_kg": 3.10
    },
    "Auchan": {
        "poulet_kg": 5.80, "boeuf_kg": 12.80, "viande_mouton_kg": 14.50, "merguez_kg": 10.80,
        "viande_hachee_kg": 11.00, "agneau_kg": 15.50, "porc_kg": 9.50,
        "tomates_kg": 2.90, "oignons_kg": 1.30, "oignon_kg": 1.30, "poivrons_kg": 3.20,
        "courgettes_kg": 2.50, "aubergines_kg": 3.00, "carottes_kg": 1.50, "pommes_de_terre_kg": 1.90,
        "tomates_cerises_kg": 4.20, "salade_kg": 2.40, "celeri_kg": 3.30, "haricots_verts_kg": 4.40,
        "lentilles_kg": 3.60, "pois_chiches_kg": 3.70, "riz_kg": 2.40, "pates_kg": 1.95,
        "farine_kg": 1.25, "couscous_kg": 2.90, "semoule_kg": 2.50,
        "coriandre_kg": 10.80, "persil_kg": 10.30, "menthe_kg": 11.30, "basilic_kg": 13.00,
        "oeufs_unite": 0.33, "fromage_kg": 14.80, "creme_fraiche_kg": 5.90, "beurre_kg": 10.80,
        "lait_litre": 1.18, "yaourt_unite": 0.52,
        "saumon_kg": 19.80, "cabillaud_kg": 15.50, "sardines_kg": 8.00,
        "huile_litre": 5.20, "olives_kg": 8.80, "citrons_kg": 3.20
    },
    "Carrefour": {
        "poulet_kg": 6.20, "boeuf_kg": 13.50, "viande_mouton_kg": 15.00, "merguez_kg": 11.20,
        "viande_hachee_kg": 11.50, "agneau_kg": 16.00, "porc_kg": 9.80,
        "tomates_kg": 3.10, "oignons_kg": 1.50, "oignon_kg": 1.50, "poivrons_kg": 3.50,
        "courgettes_kg": 2.70, "aubergines_kg": 3.20, "carottes_kg": 1.60, "pommes_de_terre_kg": 2.10,
        "tomates_cerises_kg": 4.50, "salade_kg": 2.60, "celeri_kg": 3.50, "haricots_verts_kg": 4.70,
        "lentilles_kg": 3.80, "pois_chiches_kg": 3.90, "riz_kg": 2.60, "pates_kg": 2.10,
        "farine_kg": 1.35, "couscous_kg": 3.10, "semoule_kg": 2.70,
        "coriandre_kg": 11.50, "persil_kg": 11.00, "menthe_kg": 12.00, "basilic_kg": 13.80,
        "oeufs_unite": 0.35, "fromage_kg": 15.50, "creme_fraiche_kg": 6.20, "beurre_kg": 11.50,
        "lait_litre": 1.25, "yaourt_unite": 0.55,
        "saumon_kg": 21.00, "cabillaud_kg": 16.50, "sardines_kg": 8.50,
        "huile_litre": 5.50, "olives_kg": 9.50, "citrons_kg": 3.50
    }
}

# Liens GPS enseignes
LIENS_ENSEIGNES = {
    "Leclerc": {"gps": "https://www.google.com/maps/search/Leclerc+{ville}"},
    "Carrefour": {"gps": "https://www.google.com/maps/search/Carrefour+{ville}"},
    "Auchan": {"gps": "https://www.google.com/maps/search/Auchan+{ville}"},
    "Aldi": {"gps": "https://www.google.com/maps/search/Aldi+{ville}"},
    "Lidl": {"gps": "https://www.google.com/maps/search/Lidl+{ville}"}
}

# =============================================================================
# BASE DE DONNÉES - 40 RECETTES ULTRA-DÉTAILLÉES
# =============================================================================

RECETTES_DETAILLEES = {
    # ========== RECETTES MAROCAINES (20) ==========
    "Harira": {
        "pays": "🇲🇦 Maroc",
        "categorie": "Soupe",
        "budget_assiette": 1.20,
        "duree_min": 60,
        "difficulte": "Moyen",
        "saison": "Hiver",
        "darija": "الحريرة - Had l-harira, katskhon f ramadan!",
        "ingredients": {
            "viande_mouton_kg": 0.3,
            "tomates_kg": 0.5,
            "oignon_kg": 0.2,
            "lentilles_kg": 0.15,
            "pois_chiches_kg": 0.15,
            "farine_kg": 0.05,
            "celeri_kg": 0.1,
            "coriandre_kg": 0.05
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🔥 Préparation de la base (10 min)",
                "description": "Faire revenir la viande coupée en petits morceaux avec l'oignon émincé dans une grande marmite avec 2 cuillères d'huile d'olive. Remuer constamment jusqu'à ce que la viande soit bien dorée.",
                "temperature": "Feu moyen-vif",
                "duree": "10 minutes",
                "astuce": "Walli ghir tqelbi mezyan bach ma ta7reqch! (Remue bien pour ne pas brûler!)"
            },
            {
                "num": 2,
                "titre": "🍅 Ajout des tomates et épices (5 min)",
                "description": "Ajouter les tomates pelées et coupées, le céleri haché, sel, poivre, curcuma, gingembre et un peu de safran. Laisser mijoter en remuant.",
                "temperature": "Feu moyen",
                "duree": "5 minutes",
                "astuce": "Les épices doivent bien se mélanger avec la viande avant d'ajouter l'eau"
            },
            {
                "num": 3,
                "titre": "💧 Cuisson principale (30 min)",
                "description": "Ajouter 2 litres d'eau, les lentilles et les pois chiches (trempés la veille). Porter à ébullition puis réduire le feu. Couvrir et laisser mijoter.",
                "temperature": "Feu doux",
                "duree": "30 minutes",
                "astuce": "Safi, khelli-ha tta tsali! (Laisse mijoter tranquillement!)"
            },
            {
                "num": 4,
                "titre": "🌾 Préparation du Tedouira (5 min)",
                "description": "Dans un bol, mélanger la farine avec un peu d'eau froide pour faire une pâte liquide sans grumeaux. Ajouter la coriandre fraîche ciselée.",
                "temperature": "Température ambiante",
                "duree": "5 minutes",
                "astuce": "Le tedouira donne l'onctuosité typique de la harira"
            },
            {
                "num": 5,
                "titre": "🥄 Liaison finale (10 min)",
                "description": "Ajouter le tedouira progressivement en remuant constamment. Continuer la cuisson en remuant pour éviter les grumeaux.",
                "temperature": "Feu doux",
                "duree": "10 minutes",
                "astuce": "Walli ma twaqfch men tqelib! (Ne t'arrête pas de remuer!)"
            },
            {
                "num": 6,
                "titre": "✨ Finitions",
                "description": "Goûter et ajuster l'assaisonnement. Ajouter un filet de citron et plus de coriandre fraîche.",
                "temperature": "Éteindre le feu",
                "duree": "2 minutes",
                "astuce": "Le citron réveille tous les arômes!"
            },
            {
                "num": 7,
                "titre": "🍽️ Service",
                "description": "Servir bien chaud avec des dattes, des œufs durs et des chebakia pendant Ramadan, ou simplement avec du pain.",
                "temperature": "Très chaud",
                "duree": "Immédiat",
                "astuce": "Besaha w raha! (Bon appétit et santé!)"
            }
        ],
        "anecdote": "La harira est LA soupe du Ramadan au Maroc. Chaque famille a sa recette secrète transmise de génération en génération!"
    },
    
    "Tajine Poulet Citron": {
        "pays": "🇲🇦 Maroc",
        "categorie": "Plat principal",
        "budget_assiette": 2.80,
        "duree_min": 75,
        "difficulte": "Facile",
        "saison": "Toute",
        "darija": "طاجين دجاج بالحامض - Tajine dial djaj b l7amed!",
        "ingredients": {
            "poulet_kg": 1.0,
            "citron_confit_kg": 0.15,
            "oignon_kg": 0.2,
            "olives_kg": 0.1,
            "citron_frais_kg": 0.1,
            "huile_olive_kg": 0.05
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🔪 Préparation du poulet (10 min)",
                "description": "Nettoyer le poulet et le découper en 8 morceaux. Frotter chaque morceau avec sel, poivre, curcuma, gingembre et un peu d'ail écrasé.",
                "temperature": "Température ambiante",
                "duree": "10 minutes",
                "astuce": "Walli khelli t3teq l7wayej mezyan f l7am! (Fais bien pénétrer les épices!)"
            },
            {
                "num": 2,
                "titre": "🧅 Faire revenir (15 min)",
                "description": "Dans le tajine ou une cocotte, faire chauffer l'huile d'olive et faire dorer le poulet de tous côtés avec l'oignon émincé.",
                "temperature": "Feu moyen-vif",
                "duree": "15 minutes",
                "astuce": "Il faut que le poulet soit bien doré pour avoir du goût!"
            },
            {
                "num": 3,
                "titre": "💧 Cuisson mijotée (40 min)",
                "description": "Ajouter un demi-verre d'eau, le citron confit coupé en quartiers, quelques branches de coriandre. Couvrir et laisser mijoter à feu doux.",
                "temperature": "Feu très doux",
                "duree": "40 minutes",
                "astuce": "Safi, khelli-ha tchettah bchwiya bchwiya! (Laisse mijoter doucement!)"
            },
            {
                "num": 4,
                "titre": "🫒 Ajout des olives (10 min)",
                "description": "Ajouter les olives vertes dénoyautées et le jus d'un citron frais. Poursuivre la cuisson à découvert.",
                "temperature": "Feu doux",
                "duree": "10 minutes",
                "astuce": "Les olives doivent juste chauffer, pas trop cuire"
            },
            {
                "num": 5,
                "titre": "✨ Finitions",
                "description": "Vérifier l'assaisonnement. La sauce doit être onctueuse et bien réduite. Ajouter de la coriandre fraîche ciselée.",
                "temperature": "Éteindre le feu",
                "duree": "2 minutes",
                "astuce": "La sauce ne doit pas être trop liquide!"
            },
            {
                "num": 6,
                "titre": "🍽️ Présentation",
                "description": "Disposer le poulet au centre, les citrons confits et olives autour. Napper de sauce et parsemer de coriandre.",
                "temperature": "Chaud",
                "duree": "3 minutes",
                "astuce": "Présente-le directement dans le tajine, c'est plus beau!"
            },
            {
                "num": 7,
                "titre": "🥖 Service",
                "description": "Servir avec du pain marocain bien chaud (khobz) ou du riz blanc.",
                "temperature": "Très chaud",
                "duree": "Immédiat",
                "astuce": "Besaha! (Bon appétit!)"
            }
        ],
        "anecdote": "Le tajine aux citrons confits est un classique marocain. Le secret? Les vrais citrons confits maison qui ont macéré au moins 1 mois!"
    },
    
    "Couscous Royal": {
        "pays": "🇲🇦 Maroc",
        "categorie": "Plat principal",
        "budget_assiette": 3.50,
        "duree_min": 120,
        "difficulte": "Difficile",
        "saison": "Toute",
        "darija": "كسكس - Seksu dyalna, a khoya!",
        "ingredients": {
            "viande_mouton_kg": 0.4,
            "poulet_kg": 0.4,
            "merguez_kg": 0.3,
            "semoule_couscous_kg": 0.5,
            "legumes_kg": 1.5,
            "pois_chiches_kg": 0.2,
            "oignon_kg": 0.2
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🥘 Préparation du bouillon (20 min)",
                "description": "Dans un grand couscoussier, faire revenir la viande et le poulet avec l'oignon, ail, épices (ras el hanout, curcuma, gingembre, poivre). Ajouter 3 litres d'eau.",
                "temperature": "Feu vif puis moyen",
                "duree": "20 minutes",
                "astuce": "Hadi asas seksu! (C'est la base du couscous!)"
            },
            {
                "num": 2,
                "titre": "🥕 Préparation des légumes (15 min)",
                "description": "Éplucher et couper en gros morceaux: carottes, navets, courgettes, courge, tomates. Ajouter au bouillon avec les pois chiches trempés.",
                "temperature": "Feu moyen",
                "duree": "15 minutes",
                "astuce": "Coupe gros sinon ça va se défaire!"
            },
            {
                "num": 3,
                "titre": "🌾 Premier roulage de la semoule (10 min)",
                "description": "Mettre la semoule dans un grand plat. Arroser d'eau salée, malaxer avec les mains pour séparer les grains. Ajouter un filet d'huile.",
                "temperature": "Température ambiante",
                "duree": "10 minutes",
                "astuce": "Khelli kulshi mtfarreq mezyan! (Bien séparer tous les grains!)"
            },
            {
                "num": 4,
                "titre": "💨 Première cuisson vapeur (20 min)",
                "description": "Mettre la semoule dans le panier du couscoussier au-dessus du bouillon qui bout. Ne pas couvrir. Laisser la vapeur monter.",
                "temperature": "Vapeur forte",
                "duree": "20 minutes",
                "astuce": "Quand la vapeur sort partout, c'est bon!"
            },
            {
                "num": 5,
                "titre": "🌾 Deuxième roulage (10 min)",
                "description": "Reverser la semoule dans le plat. Casser les grumeaux avec les mains mouillées. Ajouter eau salée et huile. Rouler à nouveau.",
                "temperature": "Température ambiante",
                "duree": "10 minutes",
                "astuce": "Walli khdem b sbabek! (Travaille avec tes doigts!)"
            },
            {
                "num": 6,
                "titre": "💨 Deuxième cuisson vapeur (20 min)",
                "description": "Remettre au-dessus du bouillon. Laisser cuire à nouveau. Cette fois on peut couvrir légèrement.",
                "temperature": "Vapeur moyenne",
                "duree": "20 minutes",
                "astuce": "Les grains doivent être bien gonflés et aérés"
            },
            {
                "num": 7,
                "titre": "🌶️ Cuisson merguez (15 min)",
                "description": "Dans une poêle, griller les merguez à feu moyen. Les piquer avec une fourchette pour évacuer la graisse.",
                "temperature": "Feu moyen",
                "duree": "15 minutes",
                "astuce": "N'ajoute pas d'huile, elles en ont déjà!"
            },
            {
                "num": 8,
                "titre": "✨ Dernier roulage et beurrage (5 min)",
                "description": "Reverser la semoule une dernière fois. Ajouter le beurre et malaxer délicatement pour séparer les grains.",
                "temperature": "Tiède",
                "duree": "5 minutes",
                "astuce": "Le beurre rend le couscous fondant!"
            },
            {
                "num": 9,
                "titre": "🍽️ Montage et service",
                "description": "Former une montagne de semoule. Disposer viandes, poulet, merguez et légumes autour. Napper de bouillon. Servir le reste du bouillon à part.",
                "temperature": "Très chaud",
                "duree": "5 minutes",
                "astuce": "Besaha w raha! C'est le plat du vendredi!"
            }
        ],
        "anecdote": "Le couscous royal est servi chaque vendredi dans les familles marocaines. C'est un moment de partage et de convivialité!"
    },
    
    "Kefta": {
        "pays": "🇲🇦 Maroc",
        "categorie": "Plat principal",
        "budget_assiette": 1.80,
        "duree_min": 30,
        "difficulte": "Facile",
        "saison": "Toute",
        "darija": "كفتة - Kefta dial mama!",
        "ingredients": {
            "viande_hachee_kg": 0.6,
            "oignon_kg": 0.15,
            "persil_kg": 0.05,
            "coriandre_kg": 0.05
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🔪 Préparation du mélange (10 min)",
                "description": "Hacher finement persil, coriandre et oignon. Mélanger avec la viande hachée, sel, poivre, paprika, cumin et un peu de piment.",
                "temperature": "Température ambiante",
                "duree": "10 minutes",
                "astuce": "Khelli l7wayej yetmellku mezyan! (Mélange bien les épices!)"
            },
            {
                "num": 2,
                "titre": "✋ Façonnage des brochettes (10 min)",
                "description": "Mouiller les mains. Prendre une boule de viande et l'allonger autour d'une brochette en pressant bien.",
                "temperature": "Température ambiante",
                "duree": "10 minutes",
                "astuce": "Mains mouillées = la viande ne colle pas!"
            },
            {
                "num": 3,
                "titre": "🔥 Cuisson au grill (10 min)",
                "description": "Faire griller les keftas à feu vif en les retournant régulièrement. Elles doivent être bien dorées à l'extérieur.",
                "temperature": "Feu vif",
                "duree": "10 minutes",
                "astuce": "Qelleb-hom bezzaf! (Retourne-les souvent!)"
            },
            {
                "num": 4,
                "titre": "🍽️ Service",
                "description": "Servir avec du pain, de la salade et de la harissa.",
                "temperature": "Très chaud",
                "duree": "Immédiat",
                "astuce": "Besaha!"
            }
        ],
        "anecdote": "Les keftas se mangent dans la rue au Maroc, c'est du fast-food marocain!"
    },
    
    "Zaalouk": {
        "pays": "🇲🇦 Maroc",
        "categorie": "Salade",
        "budget_assiette": 0.90,
        "duree_min": 40,
        "difficulte": "Facile",
        "saison": "Été",
        "darija": "زعلوك - Zaalouk bnaynin!",
        "ingredients": {
            "aubergine_kg": 0.8,
            "tomate_kg": 0.5,
            "ail_kg": 0.05,
            "huile_olive_kg": 0.08
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🔥 Griller les aubergines (15 min)",
                "description": "Piquer les aubergines avec une fourchette. Les griller directement sur le feu ou au four jusqu'à ce que la peau soit complètement noircie.",
                "temperature": "Feu vif / Four 220°C",
                "duree": "15 minutes",
                "astuce": "Khelli-ha ta t7req kulha! (Laisse-la brûler complètement!)"
            },
            {
                "num": 2,
                "titre": "🥄 Éplucher et écraser (10 min)",
                "description": "Laisser tiédir puis éplucher. Écraser la chair à la fourchette avec l'ail écrasé.",
                "temperature": "Tiède",
                "duree": "10 minutes",
                "astuce": "La chair doit être comme une purée"
            },
            {
                "num": 3,
                "titre": "🍅 Cuisson avec tomates (15 min)",
                "description": "Dans une poêle, faire revenir les tomates râpées avec l'aubergine écrasée, huile d'olive, paprika, cumin, sel. Faire mijoter.",
                "temperature": "Feu moyen",
                "duree": "15 minutes",
                "astuce": "Qelleb mezyan! (Remue bien!)"
            },
            {
                "num": 4,
                "titre": "🍽️ Service",
                "description": "Servir froid avec du pain ou en salade d'accompagnement.",
                "temperature": "Froid",
                "duree": "Après refroidissement",
                "astuce": "Meilleur le lendemain!"
            }
        ],
        "anecdote": "Le zaalouk est incontournable dans les tables marocaines, c'est une salade cuite aux aubergines grillées!"
    },
    
    "Pastilla": {
        "pays": "🇲🇦 Maroc",
        "categorie": "Plat festif",
        "budget_assiette": 4.50,
        "duree_min": 120,
        "difficulte": "Difficile",
        "saison": "Toute",
        "darija": "بسطيلة - Bstila dial l3reyess!",
        "ingredients": {
            "feuilles_brick_kg": 0.4,
            "pigeon_ou_poulet_kg": 1.0,
            "amandes_kg": 0.3,
            "oeufs_kg": 0.3,
            "oignon_kg": 0.3,
            "beurre_kg": 0.2,
            "sucre_kg": 0.1,
            "cannelle_kg": 0.02
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🍖 Cuisson de la viande (45 min)",
                "description": "Faire revenir le pigeon ou poulet avec oignon, épices (safran, gingembre, cannelle), beurre. Ajouter eau et laisser mijoter jusqu'à ce que la viande se détache.",
                "temperature": "Feu doux",
                "duree": "45 minutes",
                "astuce": "La viande doit être ultra fondante!"
            },
            {
                "num": 2,
                "titre": "🥚 Préparation des œufs (10 min)",
                "description": "Retirer la viande. Dans le bouillon restant, ajouter les œufs battus et cuire en remuant jusqu'à obtenir des œufs brouillés. Égoutter.",
                "temperature": "Feu doux",
                "duree": "10 minutes",
                "astuce": "Les œufs doivent être bien secs"
            },
            {
                "num": 3,
                "titre": "🔥 Torréfaction des amandes (10 min)",
                "description": "Faire dorer les amandes à sec dans une poêle. Les concasser grossièrement et mélanger avec sucre et cannelle.",
                "temperature": "Feu moyen",
                "duree": "10 minutes",
                "astuce": "Ne les brûle pas!"
            },
            {
                "num": 4,
                "titre": "🍖 Effilocher la viande (10 min)",
                "description": "Effilocher la viande en enlevant os et peau. Mélanger avec un peu de bouillon réduit et épices.",
                "temperature": "Température ambiante",
                "duree": "10 minutes",
                "astuce": "La viande doit être en fins morceaux"
            },
            {
                "num": 5,
                "titre": "📋 Montage de la pastilla (20 min)",
                "description": "Beurrer un moule rond. Disposer les feuilles de brick beurrées en rosace. Alterner couches: œufs, viande, amandes, viande, œufs. Replier les feuilles.",
                "temperature": "Température ambiante",
                "duree": "20 minutes",
                "astuce": "Chaque couche doit être bien répartie!"
            },
            {
                "num": 6,
                "titre": "🔥 Cuisson finale (25 min)",
                "description": "Badigeonner le dessus de beurre. Cuire au four jusqu'à ce que le dessus soit bien doré et croustillant.",
                "temperature": "Four 180°C",
                "duree": "25 minutes",
                "astuce": "Elle doit être dorée comme de l'or!"
            },
            {
                "num": 7,
                "titre": "✨ Décoration et service",
                "description": "Saupoudrer de sucre glace et tracer des lignes de cannelle. Servir chaud ou tiède.",
                "temperature": "Chaud/Tiède",
                "duree": "5 minutes",
                "astuce": "Le mélange sucré-salé est typique!"
            }
        ],
        "anecdote": "La pastilla est LE plat festif marocain par excellence, servi lors des grandes occasions. C'est un chef-d'œuvre culinaire!"
    },
    
    "Bissara": {
        "pays": "🇲🇦 Maroc",
        "categorie": "Soupe",
        "budget_assiette": 0.60,
        "duree_min": 50,
        "difficulte": "Facile",
        "saison": "Hiver",
        "darija": "بيصارة - Bissara dyal sbah!",
        "ingredients": {
            "feves_seches_kg": 0.5,
            "ail_kg": 0.08,
            "huile_olive_kg": 0.08,
            "cumin_kg": 0.02,
            "paprika_kg": 0.02
        },
        "etapes": [
            {
                "num": 1,
                "titre": "💧 Cuisson des fèves (40 min)",
                "description": "Faire cuire les fèves sèches (épluchées) avec l'ail dans beaucoup d'eau salée jusqu'à ce qu'elles soient très tendres.",
                "temperature": "Feu moyen",
                "duree": "40 minutes",
                "astuce": "Elles doivent se défaire facilement!"
            },
            {
                "num": 2,
                "titre": "🥄 Mixage (5 min)",
                "description": "Mixer le tout jusqu'à obtenir une purée lisse et onctueuse. Ajouter de l'eau de cuisson si trop épais.",
                "temperature": "Chaud",
                "duree": "5 minutes",
                "astuce": "Consistance crémeuse parfaite!"
            },
            {
                "num": 3,
                "titre": "🌶️ Assaisonnement (5 min)",
                "description": "Verser dans des bols. Faire un puits au centre, y verser l'huile d'olive. Saupoudrer de cumin et paprika.",
                "temperature": "Très chaud",
                "duree": "5 minutes",
                "astuce": "L'huile d'olive au centre, c'est traditionnel!"
            },
            {
                "num": 4,
                "titre": "🍽️ Service",
                "description": "Servir bien chaud avec du pain marocain (khobz) pour tremper.",
                "temperature": "Très chaud",
                "duree": "Immédiat",
                "astuce": "Parfait pour le petit-déjeuner d'hiver!"
            }
        ],
        "anecdote": "La bissara est le petit-déjeuner traditionnel des travailleurs marocains en hiver. Nourrissante et économique!"
    },
    
    "Rfissa": {
        "pays": "🇲🇦 Maroc",
        "categorie": "Plat principal",
        "budget_assiette": 2.50,
        "duree_min": 90,
        "difficulte": "Moyen",
        "saison": "Hiver",
        "darija": "رفيسة - Rfissa dial les mamans!",
        "ingredients": {
            "poulet_kg": 1.2,
            "msemmen_ou_crepes_kg": 0.4,
            "lentilles_kg": 0.2,
            "oignon_kg": 0.25,
            "fenugrec_kg": 0.05,
            "smen_beurre_kg": 0.15
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🍖 Cuisson du poulet (50 min)",
                "description": "Dans une marmite, faire cuire le poulet avec oignon, ail, smen (beurre rance), safran, gingembre, ras el hanout, fenugrec et lentilles. Couvrir d'eau.",
                "temperature": "Feu moyen",
                "duree": "50 minutes",
                "astuce": "Le fenugrec donne le goût unique!"
            },
            {
                "num": 2,
                "titre": "🥞 Préparation des msemmen (20 min si fait maison)",
                "description": "Si tu fais les msemmen maison, prépare-les et fais-les cuire. Sinon utilise des crêpes ou achète des msemmen tout faits.",
                "temperature": "Feu moyen",
                "duree": "20 minutes",
                "astuce": "Les msemmen du commerce font l'affaire!"
            },
            {
                "num": 3,
                "titre": "💧 Réduction de la sauce (10 min)",
                "description": "Retirer le poulet cuit. Faire réduire le bouillon avec les lentilles jusqu'à obtenir une sauce épaisse et onctueuse.",
                "temperature": "Feu vif",
                "duree": "10 minutes",
                "astuce": "La sauce doit napper la cuillère!"
            },
            {
                "num": 4,
                "titre": "🥞 Trempage des msemmen (5 min)",
                "description": "Déchirer les msemmen en morceaux. Les tremper dans la sauce chaude pour qu'ils s'imprègnent bien.",
                "temperature": "Chaud",
                "duree": "5 minutes",
                "astuce": "Ils doivent être bien imbibés!"
            },
            {
                "num": 5,
                "titre": "🍽️ Montage et service (5 min)",
                "description": "Dans un plat de service, disposer les msemmen trempés. Disposer le poulet dessus. Arroser du reste de sauce. Garnir de lentilles.",
                "temperature": "Très chaud",
                "duree": "5 minutes",
                "astuce": "Se mange avec les mains traditionnellement!"
            }
        ],
        "anecdote": "La rfissa est LE plat traditionnel servi aux jeunes mamans après l'accouchement au Maroc. Très nourrissant!"
    },
    
    "Tangia": {
        "pays": "🇲🇦 Maroc",
        "categorie": "Plat principal",
        "budget_assiette": 3.20,
        "duree_min": 240,
        "difficulte": "Moyen",
        "saison": "Toute",
        "darija": "طانجية - Tangia dial Marrakech!",
        "ingredients": {
            "viande_mouton_kg": 1.0,
            "ail_kg": 0.1,
            "huile_kg": 0.1,
            "smen_kg": 0.05,
            "citron_confit_kg": 0.1
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🏺 Préparation dans la jarre (15 min)",
                "description": "Dans une jarre en terre cuite (tangia), mettre la viande coupée en gros morceaux avec ail écrasé, huile, smen, cumin, safran, sel, poivre et citron confit.",
                "temperature": "Température ambiante",
                "duree": "15 minutes",
                "astuce": "Pas d'eau! Cuisson à l'étouffée!"
            },
            {
                "num": 2,
                "titre": "🔥 Cuisson traditionnelle (4h)",
                "description": "Fermer hermétiquement avec du papier d'alu et ficelle. Mettre dans les braises du hammam (bain maure) ou au four très doux.",
                "temperature": "Four 110°C",
                "duree": "4 heures",
                "astuce": "Traditionnellement cuit dans les braises du hammam!"
            },
            {
                "num": 3,
                "titre": "🍽️ Service",
                "description": "Ouvrir la jarre devant les convives. La viande doit être ultra fondante et se défaire toute seule.",
                "temperature": "Très chaud",
                "duree": "Immédiat",
                "astuce": "L'ouverture de la tangia est un moment!"
            }
        ],
        "anecdote": "La tangia est LE plat des hommes à Marrakech! Traditionnellement préparé par les hommes et cuit au hammam pendant qu'ils se lavent!"
    },
    
    "Briouates": {
        "pays": "🇲🇦 Maroc",
        "categorie": "Entrée",
        "budget_assiette": 1.40,
        "duree_min": 45,
        "difficulte": "Moyen",
        "saison": "Toute",
        "darija": "بريوات - Briouates dial Ramadan!",
        "ingredients": {
            "feuilles_brick_kg": 0.25,
            "viande_hachee_kg": 0.4,
            "oignon_kg": 0.1,
            "persil_kg": 0.05,
            "huile_friture_kg": 0.5
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🍳 Préparation de la farce (20 min)",
                "description": "Faire revenir la viande hachée avec oignon émincé, persil, coriandre, sel, poivre, cumin, paprika. Cuire jusqu'à évaporation complète de l'eau.",
                "temperature": "Feu moyen",
                "duree": "20 minutes",
                "astuce": "La farce doit être sèche, pas de jus!"
            },
            {
                "num": 2,
                "titre": "📐 Pliage en triangles (15 min)",
                "description": "Couper les feuilles de brick en bandes. Mettre une cuillère de farce au bout. Plier en triangle comme un drapeau. Coller le bout avec un peu d'œuf battu.",
                "temperature": "Température ambiante",
                "duree": "15 minutes",
                "astuce": "Plie comme un drapeau américain!"
            },
            {
                "num": 3,
                "titre": "🔥 Friture (10 min)",
                "description": "Faire chauffer l'huile. Frire les briouates jusqu'à ce qu'elles soient bien dorées et croustillantes. Égoutter sur papier absorbant.",
                "temperature": "Huile 180°C",
                "duree": "10 minutes",
                "astuce": "Feu moyen pour qu'elles dorent sans brûler!"
            },
            {
                "num": 4,
                "titre": "🍽️ Service",
                "description": "Servir chaud ou tiède en entrée ou à l'heure du thé.",
                "temperature": "Chaud/Tiède",
                "duree": "Immédiat",
                "astuce": "Parfait pour le ftour du Ramadan!"
            }
        ],
        "anecdote": "Les briouates sont incontournables pendant le Ramadan. Chaque famille a sa farce préférée: viande, poulet, fromage ou amandes!"
    },
    
    "Taktouka": {
        "pays": "🇲🇦 Maroc",
        "categorie": "Salade",
        "budget_assiette": 0.80,
        "duree_min": 35,
        "difficulte": "Facile",
        "saison": "Été",
        "darija": "تكتوكة - Taktouka dial sif!",
        "ingredients": {
            "poivron_kg": 0.6,
            "tomate_kg": 0.5,
            "ail_kg": 0.04,
            "huile_olive_kg": 0.06
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🔥 Griller les poivrons (15 min)",
                "description": "Griller les poivrons directement sur le feu ou au four jusqu'à ce que la peau soit noircie. Les mettre dans un sac plastique fermé 5 min.",
                "temperature": "Feu vif / Four 220°C",
                "duree": "15 minutes",
                "astuce": "Le sac facilite l'épluchage!"
            },
            {
                "num": 2,
                "titre": "✋ Éplucher et couper (5 min)",
                "description": "Éplucher les poivrons sous l'eau. Retirer graines et membranes. Couper en lanières.",
                "temperature": "Tiède",
                "duree": "5 minutes",
                "astuce": "Enlève bien toutes les peaux!"
            },
            {
                "num": 3,
                "titre": "🍅 Cuisson finale (15 min)",
                "description": "Dans une poêle, faire revenir ail, tomates concassées, poivrons, huile d'olive, paprika, cumin, sel. Faire mijoter jusqu'à épaississement.",
                "temperature": "Feu moyen",
                "duree": "15 minutes",
                "astuce": "La sauce doit être épaisse!"
            },
            {
                "num": 4,
                "titre": "🍽️ Service",
                "description": "Servir froid avec du pain ou en accompagnement d'un tajine.",
                "temperature": "Froid",
                "duree": "Après refroidissement",
                "astuce": "Meilleur le lendemain!"
            }
        ],
        "anecdote": "La taktouka est la salade d'été par excellence au Maroc. Fraîche et savoureuse!"
    },
    
    "Seffa": {
        "pays": "🇲🇦 Maroc",
        "categorie": "Dessert/Plat sucré",
        "budget_assiette": 1.20,
        "duree_min": 40,
        "difficulte": "Facile",
        "saison": "Toute",
        "darija": "سفة - Seffa dial l3id!",
        "ingredients": {
            "vermicelles_kg": 0.5,
            "amandes_kg": 0.15,
            "sucre_kg": 0.15,
            "cannelle_kg": 0.02,
            "beurre_kg": 0.1,
            "raisins_secs_kg": 0.08
        },
        "etapes": [
            {
                "num": 1,
                "titre": "💨 Cuisson vapeur des vermicelles (20 min)",
                "description": "Faire cuire les vermicelles à la vapeur dans un couscoussier. Ils doivent être tendres et bien gonflés.",
                "temperature": "Vapeur forte",
                "duree": "20 minutes",
                "astuce": "Ne pas les faire bouillir dans l'eau!"
            },
            {
                "num": 2,
                "titre": "🧈 Beurrage (5 min)",
                "description": "Verser les vermicelles dans un plat. Ajouter le beurre fondu et mélanger délicatement pour bien les séparer.",
                "temperature": "Chaud",
                "duree": "5 minutes",
                "astuce": "Le beurre les rend brillants!"
            },
            {
                "num": 3,
                "titre": "🥜 Préparation garniture (10 min)",
                "description": "Faire griller les amandes. Les concasser grossièrement. Mélanger avec sucre et cannelle. Faire gonfler les raisins secs dans eau tiède.",
                "temperature": "Feu moyen",
                "duree": "10 minutes",
                "astuce": "Amandes bien dorées = plus de goût!"
            },
            {
                "num": 4,
                "titre": "🏔️ Montage (5 min)",
                "description": "Former une montagne de vermicelles. Décorer le sommet avec le mélange amandes-sucre-cannelle. Parsemer de raisins secs autour.",
                "temperature": "Chaud",
                "duree": "5 minutes",
                "astuce": "La présentation en montagne est traditionnelle!"
            },
            {
                "num": 5,
                "titre": "🍽️ Service",
                "description": "Servir chaud ou tiède. Chacun se sert en creusant dans la montagne.",
                "temperature": "Chaud/Tiède",
                "duree": "Immédiat",
                "astuce": "Servi lors des fêtes et célébrations!"
            }
        ],
        "anecdote": "La seffa est servie lors des grandes occasions: mariages, Aid, naissances. C'est un plat de fête!"
    },
    
    "Msemmen": {
        "pays": "🇲🇦 Maroc",
        "categorie": "Pain/Crêpe",
        "budget_assiette": 0.50,
        "duree_min": 60,
        "difficulte": "Difficile",
        "saison": "Toute",
        "darija": "مسمن - Msemmen dial sbah!",
        "ingredients": {
            "farine_kg": 0.5,
            "semoule_fine_kg": 0.15,
            "huile_kg": 0.1,
            "beurre_kg": 0.08,
            "sel_kg": 0.01
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🥄 Préparation de la pâte (15 min)",
                "description": "Mélanger farine, semoule fine, sel. Ajouter eau tiède progressivement et pétrir jusqu'à obtenir une pâte lisse et élastique. Laisser reposer 10 min.",
                "temperature": "Température ambiante",
                "duree": "15 minutes",
                "astuce": "La pâte doit être souple!"
            },
            {
                "num": 2,
                "titre": "🔵 Façonnage des boules (10 min)",
                "description": "Diviser la pâte en boules de la taille d'une noix. Les huiler légèrement. Laisser reposer 20 min.",
                "temperature": "Température ambiante",
                "duree": "10 minutes + 20 min repos",
                "astuce": "L'huile permet l'étalement!"
            },
            {
                "num": 3,
                "titre": "📏 Étalement et pliage (15 min)",
                "description": "Sur une surface huilée, étaler chaque boule très finement au maximum. Badigeonner de beurre fondu. Plier en carré en 2 fois.",
                "temperature": "Température ambiante",
                "duree": "15 minutes",
                "astuce": "Plus c'est fin, plus c'est feuilleté!"
            },
            {
                "num": 4,
                "titre": "🔥 Cuisson (20 min)",
                "description": "Faire cuire chaque msemmen dans une poêle ou sur une plaque chaude sans matière grasse. Retourner quand des bulles se forment. Doit être doré des 2 côtés.",
                "temperature": "Feu moyen",
                "duree": "20 minutes (2-3 min/pièce)",
                "astuce": "Pas d'huile dans la poêle!"
            },
            {
                "num": 5,
                "titre": "🍽️ Service",
                "description": "Servir chaud avec du miel, de la confiture ou du fromage. Ou nature avec du thé à la menthe.",
                "temperature": "Chaud",
                "duree": "Immédiat",
                "astuce": "Parfait pour le petit-déjeuner!"
            }
        ],
        "anecdote": "Les msemmen sont les crêpes feuilletées marocaines. C'est l'art du pliage qui fait leur texture unique!"
    },
    
    "Chebakia": {
        "pays": "🇲🇦 Maroc",
        "categorie": "Pâtisserie",
        "budget_assiette": 1.80,
        "duree_min": 90,
        "difficulte": "Difficile",
        "saison": "Ramadan",
        "darija": "شباكية - Chebakia dial Ramadan!",
        "ingredients": {
            "farine_kg": 0.5,
            "amandes_kg": 0.1,
            "sesame_kg": 0.15,
            "miel_kg": 0.3,
            "huile_friture_kg": 1.0,
            "oeuf_kg": 0.1,
            "levure_kg": 0.02
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🥄 Préparation de la pâte (20 min)",
                "description": "Mélanger farine, amandes concassées, graines de sésame grillées, épices (cannelle, anis, gomme arabique), levure. Ajouter œufs, huile, eau de fleur d'oranger. Pétrir. Repos 30 min.",
                "temperature": "Température ambiante",
                "duree": "20 min + 30 min repos",
                "astuce": "La pâte doit être ferme!"
            },
            {
                "num": 2,
                "titre": "📏 Étalement et découpe (25 min)",
                "description": "Étaler finement. Découper en rectangles. Faire 4 fentes longitudinales. Tresser en passant une extrémité dans les fentes pour former une fleur.",
                "temperature": "Température ambiante",
                "duree": "25 minutes",
                "astuce": "Le tressage demande de la pratique!"
            },
            {
                "num": 3,
                "titre": "🔥 Friture (20 min)",
                "description": "Faire chauffer l'huile. Frire les chebakia jusqu'à ce qu'elles soient bien dorées. Égoutter sur papier absorbant.",
                "temperature": "Huile 170°C",
                "duree": "20 minutes",
                "astuce": "Feu moyen pour cuisson uniforme!"
            },
            {
                "num": 4,
                "titre": "🍯 Trempage dans le miel (15 min)",
                "description": "Faire chauffer le miel avec un peu d'eau de fleur d'oranger. Y tremper les chebakia encore chaudes. Les retirer et les rouler dans du sésame grillé.",
                "temperature": "Miel tiède",
                "duree": "15 minutes",
                "astuce": "Le miel doit être liquide mais pas trop chaud!"
            },
            {
                "num": 5,
                "titre": "🍽️ Séchage et service (10 min)",
                "description": "Disposer sur une grille pour laisser égoutter le surplus de miel. Laisser durcir légèrement.",
                "temperature": "Température ambiante",
                "duree": "10 minutes",
                "astuce": "Elles se conservent plusieurs semaines!"
            }
        ],
        "anecdote": "Les chebakia sont LA pâtisserie du Ramadan! Servies au ftour avec la harira. Leur forme en fleur tressée est emblématique!"
    },
    
    "Maakouda": {
        "pays": "🇲🇦 Maroc",
        "categorie": "Entrée/Snack",
        "budget_assiette": 0.70,
        "duree_min": 35,
        "difficulte": "Facile",
        "saison": "Toute",
        "darija": "معقودة - Maakouda dial lil!",
        "ingredients": {
            "pomme_terre_kg": 0.8,
            "persil_kg": 0.05,
            "ail_kg": 0.03,
            "oeuf_kg": 0.1,
            "huile_friture_kg": 0.5
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🥔 Cuisson des pommes de terre (20 min)",
                "description": "Éplucher et couper les pommes de terre en morceaux. Les faire bouillir dans l'eau salée jusqu'à ce qu'elles soient bien tendres.",
                "temperature": "Eau bouillante",
                "duree": "20 minutes",
                "astuce": "Elles doivent être très tendres!"
            },
            {
                "num": 2,
                "titre": "🥄 Préparation de la purée (5 min)",
                "description": "Égoutter et écraser en purée. Ajouter persil haché, ail écrasé, sel, poivre, cumin, paprika. Incorporer l'œuf battu. Bien mélanger.",
                "temperature": "Chaud",
                "duree": "5 minutes",
                "astuce": "La purée doit être homogène!"
            },
            {
                "num": 3,
                "titre": "✋ Façonnage (5 min)",
                "description": "Former des boulettes aplaties avec les mains mouillées. Les passer dans la farine.",
                "temperature": "Température ambiante",
                "duree": "5 minutes",
                "astuce": "Pas trop épaisses!"
            },
            {
                "num": 4,
                "titre": "🔥 Friture (5 min)",
                "description": "Faire chauffer l'huile. Frire les maakouda jusqu'à ce qu'elles soient bien dorées et croustillantes.",
                "temperature": "Huile 180°C",
                "duree": "5 minutes",
                "astuce": "Feu vif pour qu'elles soient croustillantes!"
            },
            {
                "num": 5,
                "titre": "🍽️ Service",
                "description": "Égoutter et servir chaud avec de la harissa ou dans du pain.",
                "temperature": "Très chaud",
                "duree": "Immédiat",
                "astuce": "Parfait en sandwich!"
            }
        ],
        "anecdote": "Les maakouda sont le street-food marocain par excellence! On les trouve partout, surtout le soir!"
    },
    
    "Sellou": {
        "pays": "🇲🇦 Maroc",
        "categorie": "Pâtisserie sèche",
        "budget_assiette": 2.20,
        "duree_min": 60,
        "difficulte": "Moyen",
        "saison": "Ramadan/Fêtes",
        "darija": "سلو - Sellou dial Ramadan!",
        "ingredients": {
            "farine_kg": 0.5,
            "amandes_kg": 0.3,
            "sesame_kg": 0.15,
            "miel_kg": 0.2,
            "beurre_kg": 0.25,
            "sucre_kg": 0.15
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🔥 Torréfaction de la farine (25 min)",
                "description": "Faire griller la farine à sec dans une grande poêle en remuant constamment jusqu'à ce qu'elle soit bien dorée et dégage une odeur de noisette.",
                "temperature": "Feu moyen-doux",
                "duree": "25 minutes",
                "astuce": "Remue tout le temps sinon elle brûle!"
            },
            {
                "num": 2,
                "titre": "🥜 Torréfaction amandes et sésame (15 min)",
                "description": "Griller séparément les amandes et le sésame. Laisser refroidir puis moudre finement les amandes.",
                "temperature": "Feu moyen",
                "duree": "15 minutes",
                "astuce": "Les amandes doivent être bien dorées!"
            },
            {
                "num": 3,
                "titre": "🥄 Mélange à sec (5 min)",
                "description": "Dans un grand récipient, mélanger la farine torréfiée, les amandes moulues, le sésame, le sucre et les épices (cannelle, anis).",
                "temperature": "Température ambiante",
                "duree": "5 minutes",
                "astuce": "Bien mélanger pour homogénéiser!"
            },
            {
                "num": 4,
                "titre": "🧈 Ajout du gras (10 min)",
                "description": "Faire fondre le beurre. L'ajouter progressivement au mélange en pétrissant. Ajouter le miel. Mélanger jusqu'à obtenir une pâte sableuse.",
                "temperature": "Beurre fondu tiède",
                "duree": "10 minutes",
                "astuce": "La texture doit être sableuse, pas trop compacte!"
            },
            {
                "num": 5,
                "titre": "🏔️ Façonnage (5 min)",
                "description": "Tasser le sellou dans un plat. Former une montagne ou des dômes. Décorer avec des amandes entières.",
                "temperature": "Température ambiante",
                "duree": "5 minutes",
                "astuce": "Se déguste à la cuillère!"
            }
        ],
        "anecdote": "Le sellou est une pâtisserie énergétique servie aux jeunes mamans et pendant le Ramadan. Très nutritif!"
    },
    
    "Baghrir": {
        "pays": "🇲🇦 Maroc",
        "categorie": "Crêpe",
        "budget_assiette": 0.60,
        "duree_min": 40,
        "difficulte": "Moyen",
        "saison": "Toute",
        "darija": "بغرير - Baghrir dial sbah!",
        "ingredients": {
            "semoule_fine_kg": 0.25,
            "farine_kg": 0.15,
            "levure_kg": 0.02,
            "oeuf_kg": 0.05,
            "sucre_kg": 0.02,
            "sel_kg": 0.005,
            "beurre_miel_kg": 0.15
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🥄 Préparation de la pâte (10 min)",
                "description": "Mixer semoule fine, farine, levure, sucre, sel, œuf et eau tiède jusqu'à obtenir une pâte liquide homogène. Laisser reposer 15 min.",
                "temperature": "Température ambiante",
                "duree": "10 min + 15 min repos",
                "astuce": "La pâte doit être liquide comme une crêpe!"
            },
            {
                "num": 2,
                "titre": "💨 Activation de la levure (15 min)",
                "description": "Pendant le repos, la pâte va faire des bulles et gonfler. C'est normal! Ne pas remuer après le repos.",
                "temperature": "Température ambiante",
                "duree": "15 minutes",
                "astuce": "Les bulles sont essentielles!"
            },
            {
                "num": 3,
                "titre": "🔥 Cuisson (15 min)",
                "description": "Chauffer une poêle antiadhésive sans matière grasse. Verser une louche de pâte. Cuire SEULEMENT d'un côté jusqu'à apparition de mille trous et surface sèche.",
                "temperature": "Feu moyen",
                "duree": "15 minutes (2 min/pièce)",
                "astuce": "Ne JAMAIS retourner! Un seul côté!"
            },
            {
                "num": 4,
                "titre": "🍯 Préparation beurre-miel",
                "description": "Faire fondre du beurre avec du miel à feu doux. Mélanger bien.",
                "temperature": "Feu doux",
                "duree": "5 minutes",
                "astuce": "Mélange moitié-moitié!"
            },
            {
                "num": 5,
                "titre": "🍽️ Service",
                "description": "Empiler les baghrir côté troué vers le haut. Verser généreusement le mélange beurre-miel qui va s'infiltrer dans tous les trous.",
                "temperature": "Chaud",
                "duree": "Immédiat",
                "astuce": "Les mille trous absorbent le beurre-miel!"
            }
        ],
        "anecdote": "Les baghrir sont appelés 'crêpes aux mille trous'. Leur texture alvéolée unique absorbe le beurre fondu au miel!"
    },
    
    "Khobz": {
        "pays": "🇲🇦 Maroc",
        "categorie": "Pain",
        "budget_assiette": 0.30,
        "duree_min": 90,
        "difficulte": "Facile",
        "saison": "Toute",
        "darija": "خبز - Khobz dial darna!",
        "ingredients": {
            "farine_kg": 1.0,
            "semoule_fine_kg": 0.1,
            "levure_kg": 0.02,
            "sel_kg": 0.02,
            "huile_kg": 0.03
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🥄 Préparation de la pâte (15 min)",
                "description": "Mélanger farine, semoule, sel. Diluer la levure dans eau tiède avec une pincée de sucre. Ajouter à la farine. Pétrir 10 min en ajoutant eau tiède progressivement.",
                "temperature": "Température ambiante",
                "duree": "15 minutes",
                "astuce": "Pétris bien pour avoir du moelleux!"
            },
            {
                "num": 2,
                "titre": "💨 Première levée (45 min)",
                "description": "Former une boule. Huiler légèrement. Couvrir d'un torchon humide. Laisser lever dans un endroit chaud jusqu'à doubler de volume.",
                "temperature": "Endroit chaud 25-30°C",
                "duree": "45 minutes",
                "astuce": "Près du radiateur ou four éteint!"
            },
            {
                "num": 3,
                "titre": "✋ Façonnage (5 min)",
                "description": "Dégazer la pâte. Former des boules aplaties de 15cm de diamètre. Saupoudrer de semoule fine.",
                "temperature": "Température ambiante",
                "duree": "5 minutes",
                "astuce": "Pas trop fin sinon pas moelleux!"
            },
            {
                "num": 4,
                "titre": "💨 Seconde levée (15 min)",
                "description": "Laisser reposer les pains formés encore 15 min sous un torchon.",
                "temperature": "Température ambiante",
                "duree": "15 minutes",
                "astuce": "Cette levée donne le moelleux!"
            },
            {
                "num": 5,
                "titre": "🔥 Cuisson (10 min)",
                "description": "Préchauffer le four à 240°C. Cuire les pains sur plaque huilée jusqu'à ce qu'ils soient dorés et gonflés.",
                "temperature": "Four 240°C",
                "duree": "10 minutes",
                "astuce": "Four très chaud = beau gonflement!"
            },
            {
                "num": 6,
                "titre": "🍽️ Service",
                "description": "Laisser tiédir sous un torchon pour garder moelleux. Servir tiède.",
                "temperature": "Tiède",
                "duree": "Après refroidissement",
                "astuce": "Rien de meilleur que le pain maison!"
            }
        ],
        "anecdote": "Le khobz marocain est rond et plat. Dans chaque quartier, il y a un four communautaire (ferran) où on apporte sa pâte à cuire!"
    },
    
    "Zaazaa": {
        "pays": "🇲🇦 Maroc",
        "categorie": "Dessert",
        "budget_assiette": 1.50,
        "duree_min": 35,
        "difficulte": "Facile",
        "saison": "Toute",
        "darija": "زعزع - Zaazaa dyal bent!",
        "ingredients": {
            "lait_kg": 1.0,
            "semoule_fine_kg": 0.15,
            "sucre_kg": 0.12,
            "eau_fleur_oranger_kg": 0.03,
            "amandes_kg": 0.08
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🥛 Chauffer le lait (5 min)",
                "description": "Faire chauffer le lait avec le sucre dans une casserole. Ne pas faire bouillir.",
                "temperature": "Feu moyen",
                "duree": "5 minutes",
                "astuce": "Surveille bien!"
            },
            {
                "num": 2,
                "titre": "🌾 Ajout semoule (15 min)",
                "description": "Saupoudrer la semoule fine en pluie tout en remuant constamment. Cuire en remuant jusqu'à épaississement.",
                "temperature": "Feu doux",
                "duree": "15 minutes",
                "astuce": "Remue sans arrêt pour éviter grumeaux!"
            },
            {
                "num": 3,
                "titre": "✨ Parfumage (5 min)",
                "description": "Retirer du feu. Ajouter l'eau de fleur d'oranger. Bien mélanger.",
                "temperature": "Hors feu",
                "duree": "5 minutes",
                "astuce": "L'eau de fleur d'oranger parfume délicatement!"
            },
            {
                "num": 4,
                "titre": "🥜 Préparation amandes (10 min)",
                "description": "Faire griller les amandes effilées. Les réserver pour la décoration.",
                "temperature": "Feu moyen",
                "duree": "10 minutes",
                "astuce": "Amandes bien dorées!"
            },
            {
                "num": 5,
                "titre":"🍽️ Service",
                "description": "Verser dans des coupelles individuelles. Décorer d'amandes grillées. Servir tiède ou froid.",
                "temperature": "Tiède/Froid",
                "duree": "Immédiat ou après refroidissement",
                "astuce": "Parfait pour finir un repas!"
            }
        ],
        "anecdote": "Le zaazaa est un dessert lacté traditionnel marocain, réconfortant et parfumé à la fleur d'oranger!"
    },
    
    # ========== RECETTES FRANÇAISES (20) ==========
    
    "Dinde de Noël": {
        "pays": "🇫🇷 France",
        "categorie": "Plat festif",
        "budget_assiette": 4.50,
        "duree_min": 180,
        "difficulte": "Moyen",
        "saison": "Hiver",
        "ingredients": {
            "dinde_kg": 3.0,
            "marron_kg": 0.5,
            "beurre_kg": 0.15,
            "oignon_kg": 0.2,
            "chair_saucisse_kg": 0.3
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🥄 Préparation de la farce (30 min)",
                "description": "Faire revenir oignons émincés dans du beurre. Ajouter la chair à saucisse et les marrons émiettés. Assaisonner avec sel, poivre, thym, persil. Laisser refroidir.",
                "temperature": "Feu moyen",
                "duree": "30 minutes",
                "astuce": "La farce doit être froide avant de farcir!"
            },
            {
                "num": 2,
                "titre": "🦃 Farcir la dinde (15 min)",
                "description": "Saler et poivrer l'intérieur de la dinde. Remplir avec la farce sans trop tasser. Coudre ou brider l'ouverture.",
                "temperature": "Température ambiante",
                "duree": "15 minutes",
                "astuce": "Ne pas trop tasser la farce!"
            },
            {
                "num": 3,
                "titre": "🧈 Beurrer et assaisonner (10 min)",
                "description": "Badigeonner généreusement la dinde de beurre ramolli. Saler et poivrer l'extérieur. Ajouter thym et laurier.",
                "temperature": "Température ambiante",
                "duree": "10 minutes",
                "astuce": "Le beurre donne une belle peau dorée!"
            },
            {
                "num": 4,
                "titre": "🔥 Cuisson au four (2h30)",
                "description": "Enfourner à 180°C. Arroser régulièrement (toutes les 30 min) avec le jus de cuisson. Couvrir d'alu si elle dore trop vite.",
                "temperature": "Four 180°C",
                "duree": "2h30",
                "astuce": "Compter 45 min par kg!"
            },
            {
                "num": 5,
                "titre": "✨ Préparation de la sauce (15 min)",
                "description": "Récupérer le jus de cuisson. Dégraisser. Faire réduire avec un peu de vin blanc. Filtrer.",
                "temperature": "Feu vif",
                "duree": "15 minutes",
                "astuce": "La sauce doit napper la cuillère!"
            },
            {
                "num": 6,
                "titre": "🍽️ Découpe et service",
                "description": "Laisser reposer 15 min avant de découper. Servir avec la farce et la sauce à part.",
                "temperature": "Chaud",
                "duree": "15 min repos",
                "astuce": "Le repos permet au jus de se répartir!"
            }
        ],
        "anecdote": "La dinde farcie aux marrons est LE plat traditionnel du réveillon de Noël en France depuis le 19ème siècle!"
    },
    
    "Bûche de Noël": {
        "pays": "🇫🇷 France",
        "categorie": "Dessert",
        "budget_assiette": 2.80,
        "duree_min": 90,
        "difficulte": "Difficile",
        "saison": "Hiver",
        "ingredients": {
            "oeuf_kg": 0.25,
            "sucre_kg": 0.2,
            "farine_kg": 0.12,
            "cacao_kg": 0.05,
            "creme_kg": 0.5,
            "chocolat_kg": 0.3
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🥚 Préparation de la génoise (20 min)",
                "description": "Battre les œufs avec le sucre au fouet électrique jusqu'à ce que le mélange blanchisse et triple de volume. Incorporer délicatement farine et cacao tamisés.",
                "temperature": "Température ambiante",
                "duree": "20 minutes",
                "astuce": "Le mélange doit faire un ruban!"
            },
            {
                "num": 2,
                "titre": "🔥 Cuisson de la génoise (12 min)",
                "description": "Étaler sur une plaque recouverte de papier cuisson. Enfourner à 180°C. La génoise doit être cuite mais souple.",
                "temperature": "Four 180°C",
                "duree": "12 minutes",
                "astuce": "Ne pas trop cuire sinon elle cassera au roulage!"
            },
            {
                "num": 3,
                "titre": "🌀 Roulage (10 min)",
                "description": "Démouler sur un torchon humide saupoudré de sucre. Rouler la génoise encore chaude avec le torchon. Laisser refroidir roulée.",
                "temperature": "Tiède",
                "duree": "10 minutes",
                "astuce": "Rouler tant que c'est chaud!"
            },
            {
                "num": 4,
                "titre": "🍫 Ganache montée (25 min)",
                "description": "Faire fondre le chocolat dans la crème chaude. Laisser refroidir puis mettre au frais 2h. Fouetter jusqu'à obtenir une texture mousseuse.",
                "temperature": "Froid puis température ambiante",
                "duree": "25 min + 2h repos",
                "astuce": "La ganache doit être bien froide pour monter!"
            },
            {
                "num": 5,
                "titre": "🌰 Montage (15 min)",
                "description": "Dérouler délicatement la génoise. Tartiner de ganache. Rerouler sans le torchon. Couper une extrémité en biais pour faire une branche.",
                "temperature": "Température ambiante",
                "duree": "15 minutes",
                "astuce": "Serrer bien en roulant!"
            },
            {
                "num": 6,
                "titre": "✨ Décoration (20 min)",
                "description": "Masquer toute la bûche de ganache. Strier avec une fourchette pour imiter l'écorce. Décorer avec champignons en meringue, houx en pâte d'amande.",
                "temperature": "Température ambiante",
                "duree": "20 minutes",
                "astuce": "Les stries donnent l'effet bois!"
            },
            {
                "num": 7,
                "titre": "🍽️ Service",
                "description": "Mettre au frais au moins 2h avant de servir. Saupoudrer de sucre glace au moment de servir.",
                "temperature": "Froid",
                "duree": "Après 2h au frais",
                "astuce": "Sortir 10 min avant de servir!"
            }
        ],
        "anecdote": "La bûche de Noël rappelle la tradition de la bûche brûlée dans la cheminée pendant les fêtes. C'est le dessert incontournable du réveillon!"
    },
    
    "Blanquette de Veau": {
        "pays": "🇫🇷 France",
        "categorie": "Plat principal",
        "budget_assiette": 3.20,
        "duree_min": 120,
        "difficulte": "Moyen",
        "saison": "Hiver",
        "ingredients": {
            "veau_kg": 1.0,
            "carotte_kg": 0.3,
            "oignon_kg": 0.2,
            "champignon_kg": 0.25,
            "creme_kg": 0.2,
            "jaune_oeuf_kg": 0.06,
            "beurre_kg": 0.05,
            "farine_kg": 0.04
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🥘 Cuisson de la viande (90 min)",
                "description": "Mettre le veau en morceaux dans l'eau froide. Porter à ébullition et écumer. Ajouter carottes, oignons piqués de clous de girofle, bouquet garni. Saler. Mijoter à couvert.",
                "temperature": "Feu doux",
                "duree": "90 minutes",
                "astuce": "L'eau froide permet de bien départ partir les impuretés!"
            },
            {
                "num": 2,
                "titre": "🍄 Cuisson des champignons (10 min)",
                "description": "Nettoyer et émincer les champignons. Les faire revenir dans du beurre avec un filet de citron.",
                "temperature": "Feu vif",
                "duree": "10 minutes",
                "astuce": "Le citron garde les champignons blancs!"
            },
            {
                "num": 3,
                "titre": "🧈 Préparation du roux (10 min)",
                "description": "Faire fondre le beurre. Ajouter la farine et mélanger au fouet 2 min sans colorer. Ajouter progressivement 50cl de bouillon de cuisson en fouettant.",
                "temperature": "Feu moyen",
                "duree": "10 minutes",
                "astuce": "Le roux ne doit pas colorer pour la blanquette!"
            },
            {
                "num": 4,
                "titre": "✨ Liaison finale (10 min)",
                "description": "Battre la crème avec les jaunes d'œufs. Ajouter une louche de sauce chaude en fouettant. Verser dans la sauce en remuant. Ne plus faire bouillir!",
                "temperature": "Feu très doux",
                "duree": "10 minutes",
                "astuce": "Ne JAMAIS faire bouillir après les œufs!"
            },
            {
                "num": 5,
                "titre": "🥕 Assemblage",
                "description": "Égoutter la viande et les légumes. Les disposer dans un plat. Ajouter les champignons. Napper de sauce. Vérifier l'assaisonnement.",
                "temperature": "Chaud",
                "duree": "5 minutes",
                "astuce": "La sauce doit être onctueuse!"
            },
            {
                "num": 6,
                "titre": "🍽️ Service",
                "description": "Servir bien chaud avec du riz basmati ou des pommes vapeur. Parsemer de persil frais ciselé.",
                "temperature": "Très chaud",
                "duree": "Immédiat",
                "astuce": "Un classique de la cuisine bourgeoise française!"
            }
        ],
        "anecdote": "La blanquette de veau est un grand classique de la cuisine française. Le secret: une sauce blanche veloutée sans coloration!"
    },
    
    "Ratatouille": {
        "pays": "🇫🇷 France",
        "categorie": "Plat légumes",
        "budget_assiette": 1.80,
        "duree_min": 60,
        "difficulte": "Facile",
        "saison": "Été",
        "ingredients": {
            "aubergine_kg": 0.4,
            "courgette_kg": 0.4,
            "poivron_kg": 0.4,
            "tomate_kg": 0.6,
            "oignon_kg": 0.2,
            "ail_kg": 0.05,
            "huile_olive_kg": 0.1
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🔪 Préparation des légumes (15 min)",
                "description": "Laver et couper tous les légumes en dés réguliers d'environ 2cm. Garder chaque légume séparé.",
                "temperature": "Température ambiante",
                "duree": "15 minutes",
                "astuce": "Des dés réguliers = cuisson homogène!"
            },
            {
                "num": 2,
                "titre": "🍆 Cuisson des aubergines (10 min)",
                "description": "Faire revenir les aubergines dans l'huile d'olive jusqu'à ce qu'elles soient tendres et légèrement dorées. Réserver.",
                "temperature": "Feu vif",
                "duree": "10 minutes",
                "astuce": "Les aubergines absorbent beaucoup d'huile!"
            },
            {
                "num": 3,
                "titre": "🥒 Cuisson des courgettes (8 min)",
                "description": "Dans la même poêle, faire revenir les courgettes jusqu'à ce qu'elles soient tendres. Réserver.",
                "temperature": "Feu vif",
                "duree": "8 minutes",
                "astuce": "Ne pas trop cuire, elles doivent rester fermes!"
            },
            {
                "num": 4,
                "titre": "🫑 Cuisson des poivrons (10 min)",
                "description": "Faire revenir les poivrons jusqu'à ce qu'ils soient tendres. Réserver.",
                "temperature": "Feu moyen",
                "duree": "10 minutes",
                "astuce": "Ils doivent être fondants!"
            },
            {
                "num": 5,
                "titre": "🍅 Sauce tomate (15 min)",
                "description": "Faire revenir oignons et ail. Ajouter les tomates concassées, thym, laurier, sel, poivre. Laisser mijoter jusqu'à épaississement.",
                "temperature": "Feu moyen",
                "duree": "15 minutes",
                "astuce": "La sauce doit être bien réduite!"
            },
            {
                "num": 6,
                "titre": "🥘 Mijotage final (10 min)",
                "description": "Remettre tous les légumes dans la sauce tomate. Mélanger délicatement. Laisser mijoter ensemble quelques minutes.",
                "temperature": "Feu doux",
                "duree": "10 minutes",
                "astuce": "Les saveurs se mélangent!"
            },
            {
                "num": 7,
                "titre": "🍽️ Service",
                "description": "Servir chaud ou tiède avec du riz, des pâtes ou du pain. Parsemer de basilic frais.",
                "temperature": "Chaud/Tiède",
                "duree": "Immédiat",
                "astuce": "Meilleure le lendemain!"
            }
        ],
        "anecdote": "La ratatouille est LE plat provençal par excellence! Chaque légume est cuit séparément pour garder sa texture et son goût."
    },
    
    "Gratin Dauphinois": {
        "pays": "🇫🇷 France",
        "categorie": "Accompagnement",
        "budget_assiette": 1.20,
        "duree_min": 90,
        "difficulte": "Facile",
        "saison": "Toute",
        "ingredients": {
            "pomme_terre_kg": 1.5,
            "creme_kg": 0.5,
            "lait_kg": 0.3,
            "ail_kg": 0.03,
            "beurre_kg": 0.03,
            "muscade_kg": 0.002
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🔪 Préparation des pommes de terre (15 min)",
                "description": "Éplucher les pommes de terre. Les laver et les sécher. Les couper en rondelles fines (2-3mm) à la mandoline ou au couteau. NE PAS les rincer après découpe!",
                "temperature": "Température ambiante",
                "duree": "15 minutes",
                "astuce": "L'amidon des pommes de terre lie le gratin!"
            },
            {
                "num": 2,
                "titre": "🧄 Préparation du plat (5 min)",
                "description": "Frotter énergiquement le plat à gratin avec une gousse d'ail coupée. Beurrer généreusement le fond et les parois.",
                "temperature": "Température ambiante",
                "duree": "5 minutes",
                "astuce": "L'ail parfume subtilement!"
            },
            {
                "num": 3,
                "titre": "📋 Montage (10 min)",
                "description": "Disposer les pommes de terre en couches régulières. Saler, poivrer et râper un peu de muscade entre chaque couche.",
                "temperature": "Température ambiante",
                "duree": "10 minutes",
                "astuce": "Bien chevaucher les rondelles!"
            },
            {
                "num": 4,
                "titre": "🥛 Préparation de l'appareil (5 min)",
                "description": "Mélanger la crème et le lait. Saler, poivrer, ajouter muscade. Verser sur les pommes de terre jusqu'à les recouvrir aux 3/4.",
                "temperature": "Température ambiante",
                "duree": "5 minutes",
                "astuce": "Ne pas totalement recouvrir!"
            },
            {
                "num": 5,
                "titre": "🔥 Première cuisson (45 min)",
                "description": "Enfourner à 160°C. Cuire jusqu'à ce que les pommes de terre soient tendres (vérifier avec un couteau).",
                "temperature": "Four 160°C",
                "duree": "45 minutes",
                "astuce": "Cuisson douce pour éviter que la crème tranche!"
            },
            {
                "num": 6,
                "titre": "🔥 Gratinage (10 min)",
                "description": "Monter le four à 200°C pour faire dorer le dessus. Le gratin doit être bien doré et croustillant.",
                "temperature": "Four 200°C",
                "duree": "10 minutes",
                "astuce": "Surveiller pour ne pas brûler!"
            },
            {
                "num": 7,
                "titre": "🍽️ Service",
                "description": "Laisser reposer 10 min avant de servir. Le gratin sera plus facile à découper.",
                "temperature": "Chaud",
                "duree": "Après 10 min repos",
                "astuce": "Parfait avec une viande rôtie!"
            }
        ],
        "anecdote": "Le VRAI gratin dauphinois ne contient PAS de fromage! C'est l'amidon des pommes de terre qui lie la crème."
    },
    
    "Quiche Lorraine": {
        "pays": "🇫🇷 France",
        "categorie": "Tarte salée",
        "budget_assiette": 1.60,
        "duree_min": 60,
        "difficulte": "Facile",
        "saison": "Toute",
        "ingredients": {
            "pate_brisee_kg": 0.25,
            "lardons_kg": 0.2,
            "creme_kg": 0.3,
            "oeuf_kg": 0.15,
            "lait_kg": 0.1,
            "muscade_kg": 0.002
        },
        "etapes": [
            {
                "num": 1,
                "titre": "📋 Préparation de la pâte (10 min)",
                "description": "Étaler la pâte brisée. Foncer un moule à tarte beurré. Piquer le fond avec une fourchette. Mettre au frais 15 min.",
                "temperature": "Froid 4°C",
                "duree": "10 min + 15 min repos",
                "astuce": "Piquer évite que la pâte gonfle!"
            },
            {
                "num": 2,
                "titre": "🥓 Cuisson des lardons (8 min)",
                "description": "Faire revenir les lardons à sec dans une poêle jusqu'à ce qu'ils soient dorés. Pas besoin d'ajouter de matière grasse. Égoutter sur papier absorbant.",
                "temperature": "Feu vif",
                "duree": "8 minutes",
                "astuce": "Bien les faire dorer!"
            },
            {
                "num": 3,
                "titre": "🥚 Préparation de l'appareil (5 min)",
                "description": "Battre les œufs en omelette. Ajouter la crème et le lait. Saler légèrement (les lardons sont déjà salés), poivrer, muscader. Bien mélanger.",
                "temperature": "Température ambiante",
                "duree": "5 minutes",
                "astuce": "Attention au sel!"
            },
            {
                "num": 4,
                "titre": "📋 Montage (5 min)",
                "description": "Répartir les lardons sur le fond de tarte. Verser l'appareil à quiche dessus délicatement.",
                "temperature": "Température ambiante",
                "duree": "5 minutes",
                "astuce": "Remplir jusqu'à 1cm du bord!"
            },
            {
                "num": 5,
                "titre": "🔥 Cuisson (30 min)",
                "description": "Enfourner à 180°C. Cuire jusqu'à ce que l'appareil soit pris et le dessus légèrement doré. La quiche doit juste trembler au centre.",
                "temperature": "Four 180°C",
                "duree": "30 minutes",
                "astuce": "Ne pas trop cuire sinon elle devient sèche!"
            },
            {
                "num": 6,
                "titre": "🍽️ Service",
                "description": "Laisser tiédir 10 min avant de démouler et servir. Délicieuse chaude ou tiède avec une salade verte.",
                "temperature": "Tiède",
                "duree": "Après 10 min repos",
                "astuce": "La vraie quiche lorraine n'a pas de fromage!"
            }
        ],
        "anecdote": "La quiche lorraine authentique ne contient PAS de fromage ni d'oignon! Juste lardons, œufs et crème."
    },
    
    "Pot-au-Feu": {
        "pays": "🇫🇷 France",
        "categorie": "Plat mijoté",
        "budget_assiette": 2.80,
        "duree_min": 180,
        "difficulte": "Facile",
        "saison": "Hiver",
        "ingredients": {
            "boeuf_kg": 1.2,
            "os_moelle_kg": 0.4,
            "carotte_kg": 0.6,
            "navet_kg": 0.4,
            "poireau_kg": 0.4,
            "oignon_kg": 0.2,
            "celeri_kg": 0.2
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🥘 Démarrage à l'eau froide (15 min)",
                "description": "Mettre la viande dans une grande marmite d'eau froide. Porter doucement à ébullition. Écumer soigneusement toutes les impuretés qui remontent.",
                "temperature": "Feu moyen puis doux",
                "duree": "15 minutes",
                "astuce": "L'eau froide permet de bien écumer!"
            },
            {
                "num": 2,
                "titre": "🧅 Ajout aromates (5 min)",
                "description": "Ajouter l'oignon piqué de clous de girofle, le bouquet garni, sel, poivre en grains. Couvrir partiellement.",
                "temperature": "Feu doux",
                "duree": "5 minutes",
                "astuce": "Le clou de girofle parfume subtilement!"
            },
            {
                "num": 3,
                "titre": "💧 Cuisson de la viande (2h)",
                "description": "Laisser mijoter très doucement. L'eau doit à peine frémir. Écumer régulièrement. La viande doit être fondante.",
                "temperature": "Feu très doux (frémissement)",
                "duree": "2 heures",
                "astuce": "Plus c'est doux, plus c'est tendre!"
            },
            {
                "num": 4,
                "titre": "🥕 Ajout des légumes (45 min)",
                "description": "Ajouter carottes, navets, poireaux ficelés, céleri. Continuer la cuisson jusqu'à ce que les légumes soient tendres.",
                "temperature": "Feu doux",
                "duree": "45 minutes",
                "astuce": "Ficeler les poireaux pour qu'ils ne se défassent pas!"
            },
            {
                "num": 5,
                "titre": "🦴 Cuisson des os à moelle (15 min)",
                "description": "30 minutes avant la fin, ajouter les os à moelle ficelés dans un linge. Ils doivent juste chauffer sans que la moelle fonde.",
                "temperature": "Feu doux",
                "duree": "15 minutes",
                "astuce": "La moelle est le trésor du pot-au-feu!"
            },
            {
                "num": 6,
                "titre": "🍽️ Service traditionnel",
                "description": "Servir en 2 temps: d'abord le bouillon avec vermicelles, puis la viande et légumes avec cornichons, moutarde et gros sel. Tartiner la moelle sur du pain grillé.",
                "temperature": "Très chaud",
                "duree": "Immédiat",
                "astuce": "C'est LE plat familial dominical français!"
            }
        ],
        "anecdote": "Le pot-au-feu est considéré comme le plat national français. Henri IV voulait que chaque famille puisse en manger le dimanche!"
    },
    
    "Hachis Parmentier": {
        "pays": "🇫🇷 France",
        "categorie": "Plat principal",
        "budget_assiette": 1.40,
        "duree_min": 60,
        "difficulte": "Facile",
        "saison": "Toute",
        "ingredients": {
            "viande_hachee_kg": 0.6,
            "pomme_terre_kg": 1.0,
            "oignon_kg": 0.15,
            "beurre_kg": 0.08,
            "lait_kg": 0.15,
            "fromage_rape_kg": 0.08
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🥔 Cuisson pommes de terre (25 min)",
                "description": "Éplucher et couper les pommes de terre. Les cuire dans l'eau salée jusqu'à ce qu'elles soient tendres.",
                "temperature": "Eau bouillante",
                "duree": "25 minutes",
                "astuce": "Bien tendres pour une purée lisse!"
            },
            {
                "num": 2,
                "titre": "🥄 Purée (10 min)",
                "description": "Égoutter les pommes de terre. Les écraser au presse-purée. Ajouter beurre et lait chaud. Saler, poivrer, muscader. Battre énergiquement.",
                "temperature": "Chaud",
                "duree": "10 minutes",
                "astuce": "Ne jamais mixer, ça rend la purée collante!"
            },
            {
                "num": 3,
                "titre": "🍖 Cuisson de la viande (15 min)",
                "description": "Faire revenir l'oignon émincé. Ajouter la viande hachée. Faire cuire en émiettant bien. Saler, poivrer. Ajouter concentré de tomate et herbes.",
                "temperature": "Feu vif",
                "duree": "15 minutes",
                "astuce": "La viande doit être bien cuite et sèche!"
            },
            {
                "num": 4,
                "titre": "📋 Montage (5 min)",
                "description": "Dans un plat à gratin beurré, étaler la viande. Recouvrir de purée en lissant bien. Parsemer de fromage râpé. Faire des stries avec une fourchette.",
                "temperature": "Température ambiante",
                "duree": "5 minutes",
                "astuce": "Les stries donnent un beau gratiné!"
            },
            {
                "num": 5,
                "titre": "🔥 Gratinage (25 min)",
                "description": "Enfourner à 200°C jusqu'à ce que le dessus soit bien doré et croustillant.",
                "temperature": "Four 200°C",
                "duree": "25 minutes",
                "astuce": "Le gratiné doit être doré!"
            },
            {
                "num": 6,
                "titre": "🍽️ Service",
                "description": "Laisser reposer 5 min. Servir bien chaud avec une salade verte.",
                "temperature": "Très chaud",
                "duree": "Après 5 min repos",
                "astuce": "Parfait pour recycler un reste de pot-au-feu!"
            }
        ],
        "anecdote": "Le hachis Parmentier est nommé d'après Antoine Parmentier qui a popularisé la pomme de terre en France au 18ème siècle!"
    },
    
    "Poulet Rôti": {
        "pays": "🇫🇷 France",
        "categorie": "Plat principal",
        "budget_assiette": 2.20,
        "duree_min": 75,
        "difficulte": "Facile",
        "saison": "Toute",
        "ingredients": {
            "poulet_kg": 1.5,
            "beurre_kg": 0.08,
            "citron_kg": 0.1,
            "thym_kg": 0.01,
            "ail_kg": 0.05
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🧄 Préparation du poulet (10 min)",
                "description": "Retirer le poulet du frigo 30 min avant. Glisser beurre, ail et thym sous la peau. Mettre citron coupé et herbes dans la cavité. Brider les cuisses.",
                "temperature": "Température ambiante",
                "duree": "10 minutes",
                "astuce": "Le beurre sous la peau = peau ultra croustillante!"
            },
            {
                "num": 2,
                "titre": "🧈 Assaisonnement extérieur (5 min)",
                "description": "Badigeonner le poulet de beurre fondu. Saler généreusement la peau. Poivrer. Parsemer de thym.",
                "temperature": "Température ambiante",
                "duree": "5 minutes",
                "astuce": "Bien saler la peau pour qu'elle soit croustillante!"
            },
            {
                "num": 3,
                "titre": "🔥 Cuisson four chaud (60 min)",
                "description": "Enfourner à 220°C pendant 15 min puis baisser à 180°C. Arroser toutes les 15 min avec le jus de cuisson. Total: 20 min par 500g + 20 min.",
                "temperature": "Four 220°C puis 180°C",
                "duree": "60 minutes",
                "astuce": "Arroser régulièrement = viande juteuse!"
            },
            {
                "num": 4,
                "titre": "✅ Vérification cuisson",
                "description": "Piquer entre cuisse et blanc: le jus doit être clair, pas rosé. La température à cœur doit être 75°C.",
                "temperature": "Chaud",
                "duree": "2 minutes",
                "astuce": "Jus clair = poulet cuit!"
            },
            {
                "num": 5,
                "titre": "💤 Repos (15 min)",
                "description": "Sortir le poulet du four. Le couvrir de papier alu. Laisser reposer 15 min. Le jus va se répartir dans la viande.",
                "temperature": "Chaud",
                "duree": "15 minutes",
                "astuce": "Le repos est ESSENTIEL!"
            },
            {
                "num": 6,
                "titre": "🍽️ Découpe et service",
                "description": "Découper: séparer cuisses, ailes, puis trancher les blancs en biais. Servir avec le jus de cuisson dégraissé.",
                "temperature": "Chaud",
                "duree": "5 minutes",
                "astuce": "Le poulet rôti dominical français!"
            }
        ],
        "anecdote": "Le poulet rôti du dimanche est une institution en France! Servi traditionnellement avec des frites ou des haricots verts."
    },
    
    "Bœuf Bourguignon": {
        "pays": "🇫🇷 France",
        "categorie": "Plat mijoté",
        "budget_assiette": 3.40,
        "duree_min": 180,
        "difficulte": "Moyen",
        "saison": "Hiver",
        "ingredients": {
            "boeuf_kg": 1.2,
            "lardons_kg": 0.2,
            "carotte_kg": 0.3,
            "oignon_kg": 0.3,
            "champignon_kg": 0.3,
            "vin_rouge_kg": 0.75,
            "farine_kg": 0.04,
            "beurre_kg": 0.05
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🥓 Cuisson des lardons (10 min)",
                "description": "Faire revenir les lardons dans une cocotte jusqu'à ce qu'ils soient bien dorés. Les retirer et réserver.",
                "temperature": "Feu vif",
                "duree": "10 minutes",
                "astuce": "Bien les faire dorer!"
            },
            {
                "num": 2,
                "titre": "🥩 Saisie de la viande (15 min)",
                "description": "Couper le bœuf en gros cubes. Les saisir dans la graisse des lardons par petites quantités jusqu'à belle coloration. Réserver.",
                "temperature": "Feu très vif",
                "duree": "15 minutes",
                "astuce": "Ne pas surcharger la cocotte!"
            },
            {
                "num": 3,
                "titre": "🧅 Cuisson des légumes (10 min)",
                "description": "Faire revenir oignons et carottes coupés en gros morceaux dans la cocotte. Saupoudrer de farine et remuer 2 min.",
                "temperature": "Feu moyen",
                "duree": "10 minutes",
                "astuce": "La farine va lier la sauce!"
            },
            {
                "num": 4,
                "titre": "🍷 Mouillage au vin (5 min)",
                "description": "Remettre viande et lardons. Verser le vin rouge (de Bourgogne idéalement). Ajouter bouquet garni, ail. Porter à ébullition.",
                "temperature": "Feu vif",
                "duree": "5 minutes",
                "astuce": "Le vin doit recouvrir la viande!"
            },
            {
                "num": 5,
                "titre": "💧 Mijotage (2h30)",
                "description": "Couvrir et enfourner à 150°C ou laisser mijoter à feu très doux. La viande doit être fondante.",
                "temperature": "Four 150°C ou feu très doux",
                "duree": "2h30",
                "astuce": "Plus c'est long, plus c'est bon!"
            },
            {
                "num": 6,
                "titre": "🍄 Cuisson des champignons (10 min)",
                "description": "45 min avant la fin, faire revenir les champignons dans du beurre et les ajouter au plat.",
                "temperature": "Feu vif",
                "duree": "10 minutes",
                "astuce": "Les champignons à la fin pour garder leur texture!"
            },
            {
                "num": 7,
                "titre": "🍽️ Service",
                "description": "Servir bien chaud avec des pommes vapeur, des pâtes fraîches ou du pain. Meilleur réchauffé le lendemain!",
                "temperature": "Très chaud",
                "duree": "Immédiat",
                "astuce": "Grand classique de la cuisine bourguignonne!"
            }
        ],
        "anecdote": "Le bœuf bourguignon est un des plats les plus emblématiques de la cuisine française. Julia Child l'a rendu célèbre aux USA!"
    },
    
    "Croque-Monsieur": {
        "pays": "🇫🇷 France",
        "categorie": "Sandwich chaud",
        "budget_assiette": 1.30,
        "duree_min": 20,
        "difficulte": "Facile",
        "saison": "Toute",
        "ingredients": {
            "pain_mie_kg": 0.2,
            "jambon_kg": 0.15,
            "gruyere_kg": 0.15,
            "beurre_kg": 0.04,
            "lait_kg": 0.1,
            "farine_kg": 0.02
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🧈 Béchamel express (8 min)",
                "description": "Faire fondre le beurre. Ajouter la farine, mélanger 2 min. Ajouter le lait progressivement en fouettant. Cuire jusqu'à épaississement. Saler, poivrer, muscader.",
                "temperature": "Feu moyen",
                "duree": "8 minutes",
                "astuce": "La béchamel doit napper la cuillère!"
            },
            {
                "num": 2,
                "titre": "🥪 Montage des sandwiches (5 min)",
                "description": "Beurrer légèrement les tranches de pain. Sur une tranche: béchamel, jambon, gruyère râpé. Recouvrir de la 2ème tranche.",
                "temperature": "Température ambiante",
                "duree": "5 minutes",
                "astuce": "Le beurre empêche le pain de ramollir!"
            },
            {
                "num": 3,
                "titre": "✨ Nappage (2 min)",
                "description": "Tartiner le dessus de béchamel. Parsemer généreusement de gruyère râpé.",
                "temperature": "Température ambiante",
                "duree": "2 minutes",
                "astuce": "Beaucoup de fromage = beau gratiné!"
            },
            {
                "num": 4,
                "titre": "🔥 Gratinage (7 min)",
                "description": "Enfourner à 220°C position grill jusqu'à ce que le dessus soit bien doré et gratinéet que le fromage bouillonne.",
                "temperature": "Four 220°C grill",
                "duree": "7 minutes",
                "astuce": "Surveiller pour ne pas brûler!"
            },
            {
                "num": 5,
                "titre": "🍽️ Service",
                "description": "Servir immédiatement bien chaud avec une salade verte. Avec un œuf au plat dessus, c'est un Croque-Madame!",
                "temperature": "Très chaud",
                "duree": "Immédiat",
                "astuce": "L'incontournable des bistrots parisiens!"
            }
        ],
        "anecdote": "Le croque-monsieur est né dans un café parisien en 1910. Son nom viendrait du croustillant du pain grillé!"
    },
    
    "Omelette": {
        "pays": "🇫🇷 France",
        "categorie": "Plat rapide",
        "budget_assiette": 0.80,
        "duree_min": 10,
        "difficulte": "Moyen",
        "saison": "Toute",
        "ingredients": {
            "oeuf_kg": 0.18,
            "beurre_kg": 0.02,
            "creme_kg": 0.02,
            "fines_herbes_kg": 0.01
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🥚 Préparation des œufs (2 min)",
                "description": "Casser 3 œufs par personne dans un bol. Battre légèrement à la fourchette avec une cuillère de crème. Saler, poivrer.",
                "temperature": "Température ambiante",
                "duree": "2 minutes",
                "astuce": "Ne pas trop battre!"
            },
            {
                "num": 2,
                "titre": "🧈 Cuisson au beurre (5 min)",
                "description": "Faire chauffer le beurre dans une poêle antiadhésive. Quand il mousse, verser les œufs. Remuer vivement avec une spatule.",
                "temperature": "Feu vif",
                "duree": "5 minutes",
                "astuce": "Le beurre ne doit pas brunir!"
            },
            {
                "num": 3,
                "titre": "🌀 Technique du roulage (2 min)",
                "description": "Quand les œufs sont encore baveux dessus, arrêter de remuer. Laisser prendre 30 secondes. Plier l'omelette en trois avec la spatule.",
                "temperature": "Feu vif",
                "duree": "2 minutes",
                "astuce": "L'intérieur doit rester baveux!"
            },
            {
                "num": 4,
                "titre": "✨ Finition (1 min)",
                "description": "Parsemer de fines herbes ciselées (persil, ciboulette, cerfeuil, estragon). Glisser sur l'assiette.",
                "temperature": "Chaud",
                "duree": "1 minute",
                "astuce": "Les herbes au dernier moment!"
            },
            {
                "num": 5,
                "titre": "🍽️ Service",
                "description": "Servir immédiatement. L'omelette ne supporte pas l'attente! Avec une salade, c'est parfait.",
                "temperature": "Très chaud",
                "duree": "Immédiat",
                "astuce": "L'omelette française est baveuse!"
            }
        ],
        "anecdote": "La vraie omelette française doit être baveuse à l'intérieur! C'est l'art du timing qui fait la différence."
    },
    
    "Salade Niçoise": {
        "pays": "🇫🇷 France",
        "categorie": "Salade",
        "budget_assiette": 2.40,
        "duree_min": 30,
        "difficulte": "Facile",
        "saison": "Été",
        "ingredients": {
            "tomate_kg": 0.5,
            "oeuf_dur_kg": 0.12,
            "thon_kg": 0.15,
            "olive_kg": 0.08,
            "anchois_kg": 0.05,
            "poivron_kg": 0.15,
            "oignon_kg": 0.08,
            "huile_olive_kg": 0.06
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🥚 Cuisson des œufs (12 min)",
                "description": "Faire bouillir les œufs 10 min pour qu'ils soient durs. Les rafraîchir à l'eau froide. Écaler et couper en quartiers.",
                "temperature": "Eau bouillante",
                "duree": "12 minutes",
                "astuce": "10 min = jaune parfait!"
            },
            {
                "num": 2,
                "titre": "🔪 Préparation des légumes (10 min)",
                "description": "Laver et couper les tomates en quartiers. Couper le poivron en lanières. Émincer finement l'oignon. Tout doit être cru!",
                "temperature": "Température ambiante",
                "duree": "10 minutes",
                "astuce": "La salade niçoise est 100% crue!"
            },
            {
                "num": 3,
                "titre": "🥗 Assaisonnement (5 min)",
                "description": "Dans un bol, mélanger huile d'olive, vinaigre, sel, poivre, ail écrasé pour faire la vinaigrette.",
                "temperature": "Température ambiante",
                "duree": "5 minutes",
                "astuce": "3 parts d'huile pour 1 part de vinaigre!"
            },
            {
                "num": 4,
                "titre": "🍽️ Montage (5 min)",
                "description": "Disposer joliment les tomates, œufs, thon émietté, olives noires, anchois, poivrons, oignon. Arroser de vinaigrette. Parsemer de basilic frais.",
                "temperature": "Frais",
                "duree": "5 minutes",
                "astuce": "Chaque ingrédient visible!"
            },
            {
                "num": 5,
                "titre": "🍽️ Service",
                "description": "Servir frais mais pas glacé. Accompagner de pain de campagne.",
                "temperature": "Frais",
                "duree": "Immédiat",
                "astuce": "L'authentique n'a PAS de pommes de terre ni haricots verts!"
            }
        ],
        "anecdote": "La vraie salade niçoise de Nice ne contient JAMAIS de pommes de terre ni de haricots verts! Seulement des légumes crus."
    },
    
    "Coq au Vin": {
        "pays": "🇫🇷 France",
        "categorie": "Plat mijoté",
        "budget_assiette": 3.60,
        "duree_min": 150,
        "difficulte": "Moyen",
        "saison": "Hiver",
        "ingredients": {
            "poulet_kg": 1.5,
            "vin_rouge_kg": 0.75,
            "lardons_kg": 0.2,
            "oignon_grelot_kg": 0.25,
            "champignon_kg": 0.3,
            "ail_kg": 0.05,
            "beurre_kg": 0.05,
            "farine_kg": 0.03
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🍷 Marinade (24h recommandé)",
                "description": "Faire mariner les morceaux de poulet dans le vin rouge avec carottes, oignon, ail, bouquet garni. Couvrir et mettre au frais 12-24h.",
                "temperature": "Froid 4°C",
                "duree": "12-24 heures",
                "astuce": "La marinade attendrit et parfume!"
            },
            {
                "num": 2,
                "titre": "🥓 Cuisson des lardons (10 min)",
                "description": "Égoutter le poulet (garder la marinade). Faire revenir les lardons jusqu'à ce qu'ils soient dorés. Réserver.",
                "temperature": "Feu vif",
                "duree": "10 minutes",
                "astuce": "Bien les faire dorer!"
            },
            {
                "num": 3,
                "titre": "🍗 Cuisson du poulet (20 min)",
                "description": "Sécher le poulet. Le faire dorer de tous côtés dans la graisse des lardons. Saupoudrer de farine, remuer 2 min.",
                "temperature": "Feu vif",
                "duree": "20 minutes",
                "astuce": "Bien colorer pour le goût!"
            },
            {
                "num": 4,
                "titre": "🍷 Flambage et mijotage (90 min)",
                "description": "Flamber au cognac. Ajouter la marinade filtrée, lardons, ail. Porter à ébullition puis couvrir et laisser mijoter à feu très doux.",
                "temperature": "Feu très doux",
                "duree": "90 minutes",
                "astuce": "Mijotage doux = viande fondante!"
            },
            {
                "num": 5,
                "titre": "🍄 Garniture (20 min)",
                "description": "Faire glacer les oignons grelots au beurre avec sucre. Faire sauter les champignons. Ajouter au plat 15 min avant la fin.",
                "temperature": "Feu moyen",
                "duree": "20 minutes",
                "astuce": "Les oignons grelots entiers c'est traditionnel!"
            },
            {
                "num": 6,
                "titre": "✨ Liaison finale (10 min)",
                "description": "Sortir le poulet. Faire réduire la sauce si besoin. Vérifier l'assaisonnement. Remettre le poulet.",
                "temperature": "Feu vif",
                "duree": "10 minutes",
                "astuce": "La sauce doit napper!"
            },
            {
                "num": 7,
                "titre": "🍽️ Service",
                "description": "Servir bien chaud dans la cocotte avec des pommes vapeur, pâtes fraîches ou riz. Parsemer de persil.",
                "temperature": "Très chaud",
                "duree": "Immédiat",
                "astuce": "Grand classique bourguignon!"
            }
        ],
        "anecdote": "Le coq au vin est un plat paysan qui utilisait les vieux coqs devenus trop durs. Le vin et le mijotage les attendrissaient!"
    },
    
    "Soupe de Légumes": {
        "pays": "🇫🇷 France",
        "categorie": "Soupe",
        "budget_assiette": 0.90,
        "duree_min": 50,
        "difficulte": "Facile",
        "saison": "Toute",
        "ingredients": {
            "legumes_kg": 1.2,
            "pomme_terre_kg": 0.4,
            "oignon_kg": 0.15,
            "huile_olive_kg": 0.03,
            "beurre_kg": 0.02
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🔪 Préparation des légumes (15 min)",
                "description": "Éplucher et couper tous les légumes en morceaux moyens: carottes, poireaux, céleri, pommes de terre, courgettes selon saison.",
                "temperature": "Température ambiante",
                "duree": "15 minutes",
                "astuce": "Morceaux réguliers = cuisson homogène!"
            },
            {
                "num": 2,
                "titre": "🧅 Faire suer les légumes (10 min)",
                "description": "Faire revenir l'oignon dans beurre et huile. Ajouter les légumes durs (carottes, céleri, navets). Faire suer 5 min à couvert.",
                "temperature": "Feu doux",
                "duree": "10 minutes",
                "astuce": "Faire suer développe les saveurs!"
            },
            {
                "num": 3,
                "titre": "💧 Cuisson (30 min)",
                "description": "Ajouter pommes de terre et légumes tendres. Couvrir d'eau. Saler. Porter à ébullition puis laisser mijoter jusqu'à ce que tout soit tendre.",
                "temperature": "Feu moyen puis doux",
                "duree": "30 minutes",
                "astuce": "Les légumes doivent se défaire facilement!"
            },
            {
                "num": 4,
                "titre": "🥄 Mixer ou moulinette (5 min)",
                "description": "Passer au mixer plongeant pour une soupe veloutée, ou au moulin à légumes pour une texture plus rustique. Ou laisser en morceaux.",
                "temperature": "Chaud",
                "duree": "5 minutes",
                "astuce": "Ajuster la consistance avec le bouillon!"
            },
            {
                "num": 5,
                "titre": "✨ Finitions",
                "description": "Vérifier l'assaisonnement. Ajouter une noisette de beurre ou un filet de crème pour plus d'onctuosité.",
                "temperature": "Chaud",
                "duree": "2 minutes",
                "astuce": "Le beurre final = touche du chef!"
            },
            {
                "num": 6,
                "titre": "🍽️ Service",
                "description": "Servir bien chaud avec des croûtons, du pain grillé ou du fromage râpé.",
                "temperature": "Très chaud",
                "duree": "Immédiat",
                "astuce": "La soupe de grand-mère française!"
            }
        ],
        "anecdote": "La soupe de légumes est le plat familial par excellence en France. Chaque région a sa variante selon les légumes locaux!"
    },
    
    "Poisson Vapeur": {
        "pays": "🇫🇷 France",
        "categorie": "Plat léger",
        "budget_assiette": 3.80,
        "duree_min": 25,
        "difficulte": "Facile",
        "saison": "Toute",
        "ingredients": {
            "poisson_blanc_kg": 0.6,
            "citron_kg": 0.1,
            "beurre_kg": 0.05,
            "herbes_kg": 0.02,
            "legumes_kg": 0.4
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🔪 Préparation du poisson (5 min)",
                "description": "Rincer le poisson (cabillaud, lieu, dorade). Sécher. Saler, poivrer. Arroser de jus de citron.",
                "temperature": "Température ambiante",
                "duree": "5 minutes",
                "astuce": "Poisson bien sec = meilleure cuisson!"
            },
            {
                "num": 2,
                "titre": "🥕 Préparation des légumes (8 min)",
                "description": "Éplucher et tailler les légumes (carottes, courgettes, brocolis) en julienne ou petits morceaux.",
                "temperature": "Température ambiante",
                "duree": "8 minutes",
                "astuce": "Taille fine pour cuisson rapide!"
            },
            {
                "num": 3,
                "titre": "💨 Cuisson vapeur (12 min)",
                "description": "Dans un cuiseur vapeur, disposer d'abord les légumes, puis le poisson dessus. Parsemer de rondelles de citron et d'herbes (aneth, cerfeuil). Cuire à la vapeur.",
                "temperature": "Vapeur 100°C",
                "duree": "12 minutes",
                "astuce": "Le poisson est cuit quand la chair est opaque!"
            },
            {
                "num": 4,
                "titre": "🧈 Sauce légère (5 min)",
                "description": "Faire fondre le beurre avec jus de citron et herbes ciselées. Ou préparer une sauce au yaourt-citron-aneth.",
                "temperature": "Feu doux",
                "duree": "5 minutes",
                "astuce": "Sauce légère pour rester diététique!"
            },
            {
                "num": 5,
                "titre": "🍽️ Service",
                "description": "Dresser le poisson sur les légumes. Napper de sauce légère. Décorer de rondelles de citron et herbes fraîches.",
                "temperature": "Chaud",
                "duree": "Immédiat",
                "astuce": "Plat sain et léger parfait!"
            }
        ],
        "anecdote": "La cuisson vapeur préserve tous les nutriments et la texture délicate du poisson. C'est la cuisson santé par excellence!"
    },
    
    # ========== 5 RECETTES SUPPLÉMENTAIRES ==========
    
    "Tajine Kefta aux Œufs": {
        "pays": "🇲🇦 Maroc",
        "categorie": "Plat principal",
        "budget_assiette": 2.20,
        "duree_min": 35,
        "difficulte": "Facile",
        "saison": "Toute",
        "darija": "طاجين كفتة بالبيض - Tajine kefta b lbid!",
        "ingredients": {
            "viande_hachee_kg": 0.5,
            "tomates_kg": 0.4,
            "oignon_kg": 0.15,
            "oeuf_kg": 0.2,
            "persil_kg": 0.03,
            "cumin_kg": 0.01
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🥩 Préparation des boulettes (10 min)",
                "description": "Mélanger la viande hachée avec oignon râpé, persil haché, cumin, paprika, sel et poivre. Former des boulettes de la taille d'une noix.",
                "temperature": "Température ambiante",
                "duree": "10 minutes",
                "astuce": "Des petites boulettes cuisent plus vite!"
            },
            {
                "num": 2,
                "titre": "🍅 Préparation de la sauce (10 min)",
                "description": "Dans le tajine ou une poêle, faire revenir l'oignon émincé. Ajouter les tomates pelées concassées, sel, poivre, cumin, paprika. Laisser mijoter.",
                "temperature": "Feu moyen",
                "duree": "10 minutes",
                "astuce": "La sauce doit épaissir!"
            },
            {
                "num": 3,
                "titre": "🥘 Cuisson des keftas (10 min)",
                "description": "Déposer les boulettes dans la sauce tomate. Couvrir et laisser cuire à feu doux.",
                "temperature": "Feu doux",
                "duree": "10 minutes",
                "astuce": "Ne pas trop remuer pour garder les boulettes entières!"
            },
            {
                "num": 4,
                "titre": "🥚 Ajout des œufs (5 min)",
                "description": "Créer des petits puits dans la sauce. Casser un œuf dans chaque puits. Couvrir et cuire jusqu'à ce que les blancs soient pris mais les jaunes encore coulants.",
                "temperature": "Feu doux",
                "duree": "5 minutes",
                "astuce": "Jaunes coulants, c'est meilleur!"
            },
            {
                "num": 5,
                "titre": "🍽️ Service",
                "description": "Servir directement dans le tajine avec du pain marocain pour saucer.",
                "temperature": "Très chaud",
                "duree": "Immédiat",
                "astuce": "On trempe le pain dans le jaune, un délice!"
            }
        ],
        "anecdote": "Ce tajine est un classique du dîner familial marocain. Simple, rapide et tout le monde l'adore!"
    },
    
    "Crêpes Suzette": {
        "pays": "🇫🇷 France",
        "categorie": "Dessert",
        "budget_assiette": 2.00,
        "duree_min": 40,
        "difficulte": "Moyen",
        "saison": "Toute",
        "ingredients": {
            "farine_kg": 0.125,
            "oeuf_kg": 0.1,
            "lait_kg": 0.25,
            "beurre_kg": 0.1,
            "sucre_kg": 0.08,
            "orange_kg": 0.3
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🥣 Pâte à crêpes (10 min + repos)",
                "description": "Mélanger farine, œufs, lait et une pincée de sel. Laisser reposer 30 min minimum.",
                "temperature": "Température ambiante",
                "duree": "10 minutes + repos",
                "astuce": "Pâte sans grumeaux = crêpes fines!"
            },
            {
                "num": 2,
                "titre": "🍳 Cuisson des crêpes (15 min)",
                "description": "Dans une poêle beurrée bien chaude, verser une louche de pâte. Cuire 1-2 min de chaque côté.",
                "temperature": "Feu vif",
                "duree": "15 minutes",
                "astuce": "Crêpes fines et dorées!"
            },
            {
                "num": 3,
                "titre": "🍊 Beurre d'orange (5 min)",
                "description": "Faire fondre le beurre avec le sucre. Ajouter le zeste et le jus des oranges. Faire caraméliser légèrement.",
                "temperature": "Feu moyen",
                "duree": "5 minutes",
                "astuce": "Le beurre doit mousser et devenir ambré!"
            },
            {
                "num": 4,
                "titre": "🔥 Flambage (2 min)",
                "description": "Plier les crêpes en quatre, les disposer dans la sauce. Ajouter un peu de Grand Marnier et flamber.",
                "temperature": "Feu vif",
                "duree": "2 minutes",
                "astuce": "Attention aux flammes! Spectaculaire!"
            },
            {
                "num": 5,
                "titre": "🍽️ Service",
                "description": "Servir immédiatement 2 crêpes par personne, nappées de sauce à l'orange.",
                "temperature": "Chaud",
                "duree": "Immédiat",
                "astuce": "Un dessert de restaurant à la maison!"
            }
        ],
        "anecdote": "Les Crêpes Suzette auraient été inventées par accident en 1895 au Café de Paris à Monte-Carlo, pour le Prince de Galles!"
    },
    
    "Mhancha aux Amandes": {
        "pays": "🇲🇦 Maroc",
        "categorie": "Dessert",
        "budget_assiette": 2.80,
        "duree_min": 60,
        "difficulte": "Difficile",
        "saison": "Toute",
        "darija": "المحنشة - Mhancha dial les fêtes!",
        "ingredients": {
            "amandes_kg": 0.3,
            "sucre_kg": 0.15,
            "feuilles_brick_kg": 0.2,
            "beurre_kg": 0.1,
            "miel_kg": 0.1,
            "eau_fleur_oranger_kg": 0.02
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🥜 Pâte d'amandes (15 min)",
                "description": "Mixer les amandes avec le sucre, l'eau de fleur d'oranger et un peu de beurre fondu jusqu'à obtenir une pâte.",
                "temperature": "Température ambiante",
                "duree": "15 minutes",
                "astuce": "Pas trop fine, garder du croquant!"
            },
            {
                "num": 2,
                "titre": "📜 Montage des boudins (15 min)",
                "description": "Étaler la pâte d'amandes en boudin sur chaque feuille de brick beurrée. Rouler serré pour former des cigares.",
                "temperature": "Température ambiante",
                "duree": "15 minutes",
                "astuce": "Bien serrer pour que ça tienne!"
            },
            {
                "num": 3,
                "titre": "🐍 Formation du serpent (10 min)",
                "description": "Dans un plat rond beurré, enrouler le premier cigare en spirale au centre, puis ajouter les autres bout à bout pour former un serpent enroulé.",
                "temperature": "Température ambiante",
                "duree": "10 minutes",
                "astuce": "C'est cette forme qui donne le nom mhancha (serpent)!"
            },
            {
                "num": 4,
                "titre": "🔥 Cuisson (25 min)",
                "description": "Badigeonner de beurre fondu et jaune d'œuf. Enfourner jusqu'à ce que ce soit bien doré.",
                "temperature": "Four 180°C",
                "duree": "25 minutes",
                "astuce": "Surveiller la coloration!"
            },
            {
                "num": 5,
                "titre": "🍯 Finition au miel (5 min)",
                "description": "À la sortie du four, arroser généreusement de miel chaud. Décorer d'amandes effilées.",
                "temperature": "Chaud",
                "duree": "5 minutes",
                "astuce": "Le miel doit être chaud pour bien pénétrer!"
            },
            {
                "num": 6,
                "titre": "🍽️ Service",
                "description": "Laisser tiédir et couper en parts. Servir avec du thé à la menthe.",
                "temperature": "Tiède",
                "duree": "Immédiat",
                "astuce": "Indispensable aux fêtes marocaines!"
            }
        ],
        "anecdote": "La mhancha (serpent en arabe) est le gâteau des grandes occasions au Maroc: mariages, baptêmes, fêtes religieuses!"
    },
    
    "Soupe à l'Oignon": {
        "pays": "🇫🇷 France",
        "categorie": "Soupe",
        "budget_assiette": 1.50,
        "duree_min": 50,
        "difficulte": "Facile",
        "saison": "Hiver",
        "ingredients": {
            "oignon_kg": 0.6,
            "beurre_kg": 0.05,
            "farine_kg": 0.03,
            "vin_rouge_kg": 0.1,
            "fromage_rape_kg": 0.1,
            "pain_kg": 0.1
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🧅 Caramélisation des oignons (30 min)",
                "description": "Émincer finement les oignons. Les faire revenir dans le beurre à feu doux jusqu'à ce qu'ils soient bien dorés et caramélisés.",
                "temperature": "Feu doux",
                "duree": "30 minutes",
                "astuce": "Patience! C'est la caramélisation qui fait tout!"
            },
            {
                "num": 2,
                "titre": "🍷 Déglaçage (5 min)",
                "description": "Saupoudrer de farine, mélanger. Déglacer au vin blanc ou rouge. Ajouter 1.5L de bouillon de bœuf ou d'eau. Saler, poivrer, thym, laurier.",
                "temperature": "Feu moyen",
                "duree": "5 minutes",
                "astuce": "Bien gratter les sucs de cuisson!"
            },
            {
                "num": 3,
                "titre": "💧 Cuisson (15 min)",
                "description": "Laisser mijoter à feu doux pour que les saveurs se développent.",
                "temperature": "Feu doux",
                "duree": "15 minutes",
                "astuce": "Plus ça mijote, meilleur c'est!"
            },
            {
                "num": 4,
                "titre": "🧀 Gratinage (5 min)",
                "description": "Verser la soupe dans des bols allant au four. Ajouter des croûtons de pain. Couvrir généreusement de gruyère râpé. Gratiner sous le gril.",
                "temperature": "Gril du four",
                "duree": "5 minutes",
                "astuce": "Le fromage doit être bien doré et filant!"
            },
            {
                "num": 5,
                "titre": "🍽️ Service",
                "description": "Servir immédiatement, attention c'est très chaud!",
                "temperature": "Brûlant",
                "duree": "Immédiat",
                "astuce": "La soupe des nuits parisiennes!"
            }
        ],
        "anecdote": "La soupe à l'oignon gratinée était servie aux Halles de Paris aux travailleurs de nuit. Un classique réconfortant!"
    },
    
    "Cornes de Gazelle": {
        "pays": "🇲🇦 Maroc",
        "categorie": "Dessert",
        "budget_assiette": 2.50,
        "duree_min": 75,
        "difficulte": "Difficile",
        "saison": "Toute",
        "darija": "كعب الغزال - Kaab lghzal, le must!",
        "ingredients": {
            "farine_kg": 0.25,
            "amandes_kg": 0.25,
            "sucre_kg": 0.15,
            "beurre_kg": 0.1,
            "eau_fleur_oranger_kg": 0.03
        },
        "etapes": [
            {
                "num": 1,
                "titre": "🥜 Pâte d'amandes (20 min)",
                "description": "Mixer les amandes mondées avec le sucre glace, l'eau de fleur d'oranger et un peu de beurre fondu jusqu'à obtenir une pâte souple.",
                "temperature": "Température ambiante",
                "duree": "20 minutes",
                "astuce": "La pâte doit être malléable mais pas collante!"
            },
            {
                "num": 2,
                "titre": "🥟 Pâte extérieure (15 min)",
                "description": "Mélanger farine, beurre fondu, eau de fleur d'oranger et un peu d'eau. Pétrir jusqu'à obtenir une pâte élastique. Laisser reposer.",
                "temperature": "Température ambiante",
                "duree": "15 minutes",
                "astuce": "Pâte très fine et élastique!"
            },
            {
                "num": 3,
                "titre": "🌙 Façonnage (25 min)",
                "description": "Former des petits boudins de pâte d'amandes. Étaler finement la pâte, y déposer les boudins, replier et former des croissants en pinçant les bords.",
                "temperature": "Température ambiante",
                "duree": "25 minutes",
                "astuce": "La forme doit évoquer une corne de gazelle!"
            },
            {
                "num": 4,
                "titre": "🔥 Cuisson (15 min)",
                "description": "Disposer sur une plaque beurrée. Piquer avec une aiguille pour éviter qu'ils éclatent. Enfourner jusqu'à légère coloration.",
                "temperature": "Four 180°C",
                "duree": "15 minutes",
                "astuce": "Ils ne doivent PAS dorer, juste cuire!"
            },
            {
                "num": 5,
                "titre": "✨ Finition",
                "description": "À la sortie du four, saupoudrer légèrement de sucre glace.",
                "temperature": "Tiède",
                "duree": "5 minutes",
                "astuce": "Délicats et fondants en bouche!"
            },
            {
                "num": 6,
                "titre": "🍽️ Service",
                "description": "Servir avec du thé à la menthe. Se conservent plusieurs jours dans une boîte hermétique.",
                "temperature": "Température ambiante",
                "duree": "Immédiat",
                "astuce": "Le roi des gâteaux marocains!"
            }
        ],
        "anecdote": "Les cornes de gazelle (kaab lghzal) sont considérées comme le summum de la pâtisserie marocaine. Leur finesse est un signe de maîtrise!"
    }
}

# =============================================================================
# PRIX INGRÉDIENTS (référence)
# =============================================================================

PRIX_INGREDIENTS = {
    "viande_mouton_kg": 12.50, "viande_hachee_kg": 8.90, "poulet_kg": 6.50,
    "merguez_kg": 9.50, "dinde_kg": 7.80, "veau_kg": 18.00, "boeuf_kg": 15.00,
    "lardons_kg": 10.00, "jambon_kg": 12.00, "chair_saucisse_kg": 8.50,
    "pigeon_ou_poulet_kg": 8.00, "thon_kg": 20.00, "anchois_kg": 35.00,
    "poisson_blanc_kg": 16.00, "tomates_kg": 2.80, "oignon_kg": 1.50,
    "carotte_kg": 1.20, "courgette_kg": 2.50, "aubergine_kg": 3.00,
    "poivron_kg": 4.00, "pomme_terre_kg": 1.30, "legumes_kg": 2.50,
    "navet_kg": 1.80, "poireau_kg": 2.20, "celeri_kg": 2.00,
    "champignon_kg": 7.00, "oignon_grelot_kg": 3.50, "lentilles_kg": 3.50,
    "pois_chiches_kg": 3.20, "feves_seches_kg": 4.00, "farine_kg": 1.20,
    "semoule_couscous_kg": 2.00, "semoule_fine_kg": 1.80, "vermicelles_kg": 2.50,
    "pain_mie_kg": 2.50, "pate_brisee_kg": 3.50, "feuilles_brick_kg": 8.00,
    "msemmen_ou_crepes_kg": 5.00, "coriandre_kg": 8.00, "persil_kg": 8.00,
    "ail_kg": 6.00, "thym_kg": 20.00, "herbes_kg": 15.00, "fines_herbes_kg": 20.00,
    "creme_kg": 5.00, "lait_kg": 1.10, "beurre_kg": 10.00, "smen_beurre_kg": 15.00,
    "fromage_rape_kg": 12.00, "gruyere_kg": 14.00, "jaune_oeuf_kg": 8.00,
    "oeuf_kg": 3.50, "oeuf_dur_kg": 3.50, "citron_kg": 3.50,
    "citron_confit_kg": 12.00, "citron_frais_kg": 3.50, "marron_kg": 18.00,
    "olives_kg": 8.00, "olive_kg": 8.00, "huile_olive_kg": 8.00, "huile_kg": 5.00,
    "huile_friture_kg": 4.00, "sucre_kg": 1.50, "miel_kg": 15.00,
    "chocolat_kg": 12.00, "cacao_kg": 8.00, "amandes_kg": 18.00,
    "sesame_kg": 10.00, "raisins_secs_kg": 8.00, "cannelle_kg": 25.00,
    "muscade_kg": 30.00, "cumin_kg": 15.00, "paprika_kg": 12.00,
    "fenugrec_kg": 10.00, "levure_kg": 8.00, "sel_kg": 1.00,
    "vin_rouge_kg": 8.00, "eau_fleur_oranger_kg": 12.00, "os_moelle_kg": 5.00,
    "orange_kg": 2.50, "pain_kg": 2.00
}

# =============================================================================
# INITIALISATION SESSION STATE
# =============================================================================

def init_session_state():
    """Initialise toutes les variables de session"""
    defaults = {
        'profil': {
            'nom': '',
            'ville': '',
            'allergies': [],
            'preferences': [],
            'niveau': 'debutant'
        },
        'historique': [],
        'recette_en_cours': None,
        'mode_cuisine': False,
        'etape_cuisine': 0,
        'last_audio_hash': None,
        'ville_utilisateur': '',
        'bienvenue_jouee': False,
        'nb_personnes': 4,
        'ingredients_disponibles': [],
        'timers': [],
        'meteo_cache': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# =============================================================================
# FONCTIONS GÉOLOCALISATION (CORRIGÉES)
# =============================================================================

def obtenir_ville_via_ip():
    """Géolocalisation via IP - Plusieurs APIs en fallback"""
    apis = [
        ('https://ipapi.co/json/', lambda d: d.get('city', '')),
        ('https://ip-api.com/json/', lambda d: d.get('city', '')),
        ('https://ipinfo.io/json', lambda d: d.get('city', ''))
    ]
    
    for url, extractor in apis:
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                data = response.json()
                ville = extractor(data)
                if ville and ville != 'undefined':
                    return ville
        except:
            continue
    
    return ""

def obtenir_geolocalisation_html5():
    """Géolocalisation HTML5 pour navigateur - FORCE GPS SUR MOBILE"""
    return """
    <script>
    (function() {
        // Détecter si mobile
        var isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        
        // Vérifier si déjà une ville GPS (pas IP) dans l'URL
        var urlParams = new URLSearchParams(window.location.search);
        var villeExistante = urlParams.get('ville_gps');
        var sourceGPS = urlParams.get('source_gps');
        
        // Liste des villes "fausses" (serveurs cloud)
        var villesFausses = ['The Dalles', 'Dalles', 'Council Bluffs', 'Ashburn', 'San Francisco', 'undefined', 'null', 'France', ''];
        
        // Sur mobile: toujours redemander si la ville semble fausse ou si pas de source GPS
        if (isMobile) {
            var estFausse = villesFausses.some(function(v) { 
                return villeExistante && villeExistante.toLowerCase().indexOf(v.toLowerCase()) !== -1; 
            });
            
            if (!sourceGPS || sourceGPS !== 'gps' || estFausse) {
                console.log('Mobile détecté, demande GPS...');
                demanderGPS();
                return;
            }
        }
        
        // Sur PC: ne pas redemander si ville existe
        if (villeExistante && villeExistante.length > 2 && sourceGPS === 'gps') {
            console.log('Ville GPS déjà définie:', villeExistante);
            return;
        }
        
        // Éviter boucle infinie
        if (window.geoRequestedV5) return;
        window.geoRequestedV5 = true;
        
        demanderGPS();
        
        function demanderGPS() {
            if (!navigator.geolocation) {
                console.log('Géolocalisation non supportée');
                return;
            }
            
            console.log('Demande géolocalisation GPS...');
            
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    var lat = position.coords.latitude;
                    var lon = position.coords.longitude;
                    console.log('Position GPS obtenue:', lat, lon);
                    
                    // Reverse geocoding avec Nominatim
                    var url = 'https://nominatim.openstreetmap.org/reverse?lat=' + lat + '&lon=' + lon + '&format=json&accept-language=fr&zoom=12';
                    
                    fetch(url, {
                        headers: {'User-Agent': 'SarahMiam/3.0'}
                    })
                    .then(function(r) { return r.json(); })
                    .then(function(data) {
                        var addr = data.address || {};
                        console.log('Adresse complète:', addr);
                        
                        // Priorité: city > town > village > municipality > county
                        var ville = addr.city || addr.town || addr.village || addr.municipality || addr.county || addr.state_district || '';
                        
                        console.log('Ville extraite:', ville);
                        
                        if (ville && ville.length > 1) {
                            var params = new URLSearchParams(window.location.search);
                            params.set('ville_gps', ville);
                            params.set('source_gps', 'gps');  // Marquer comme venant du GPS
                            window.location.replace(window.location.pathname + '?' + params.toString());
                        }
                    })
                    .catch(function(err) { 
                        console.log('Erreur geocoding:', err); 
                    });
                },
                function(error) {
                    console.log('Erreur GPS:', error.code, error.message);
                    // Afficher un message à l'utilisateur
                    if (error.code === 1) {
                        console.log('Permission refusée - utiliser bouton Changer ville');
                    }
                },
                {
                    enableHighAccuracy: true,
                    timeout: 20000,
                    maximumAge: 0  // Pas de cache, toujours frais
                }
            );
        }
    })();
    </script>
    """

# =============================================================================
# FONCTION MÉTÉO (CORRIGÉE)
# =============================================================================

def obtenir_meteo():
    """Récupère météo OpenWeather - avec cache"""
    if not OPENWEATHER_API_KEY:
        return None
    
    ville = st.session_state.ville_utilisateur
    if not ville or ville == "France":
        return None
    
    # Cache de 10 minutes
    if st.session_state.meteo_cache:
        cache = st.session_state.meteo_cache
        if cache.get('ville') == ville:
            age = (datetime.now() - cache.get('timestamp', datetime.min)).seconds
            if age < 600:
                return cache.get('data')
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={ville},FR&appid={OPENWEATHER_API_KEY}&units=metric&lang=fr"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            meteo = {
                'temp': round(data['main']['temp'], 1),
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'ville': ville
            }
            # Mettre en cache
            st.session_state.meteo_cache = {
                'ville': ville,
                'data': meteo,
                'timestamp': datetime.now()
            }
            return meteo
    except Exception as e:
        pass
    
    return None

def suggestion_meteo(meteo):
    """Suggère des recettes selon la météo"""
    if not meteo:
        return []
    
    temp = meteo['temp']
    desc = meteo['description'].lower()
    suggestions = []
    
    # Selon température
    if temp < 10:
        suggestions = ["Harira", "Pot-au-Feu", "Soupe à l'Oignon", "Couscous Royal", "Blanquette de Veau"]
    elif temp < 18:
        suggestions = ["Tajine Poulet Citron", "Bœuf Bourguignon", "Rfissa", "Gratin Dauphinois"]
    else:
        suggestions = ["Salade Niçoise", "Ratatouille", "Zaalouk", "Poisson Vapeur"]
    
    # Selon description
    if 'pluie' in desc or 'nuage' in desc:
        suggestions = ["Harira", "Bissara", "Soupe à l'Oignon", "Blanquette de Veau"]
    
    return suggestions[:3]

# =============================================================================
# FONCTIONS ALLERGIES (NOUVELLE)
# =============================================================================

def verifier_allergenes(recette_nom, allergies_utilisateur):
    """Vérifie si une recette contient des allergènes de l'utilisateur"""
    if not allergies_utilisateur:
        return True, []
    
    recette = RECETTES_DETAILLEES.get(recette_nom)
    if not recette:
        return True, []
    
    allergenes_trouves = []
    ingredients = list(recette.get('ingredients', {}).keys())
    
    for allergie in allergies_utilisateur:
        if allergie.lower() in ALLERGENES:
            for ingredient_allergie in ALLERGENES[allergie.lower()]:
                for ing in ingredients:
                    if ingredient_allergie in ing.lower():
                        allergenes_trouves.append(f"{allergie}: {ing}")
    
    return len(allergenes_trouves) == 0, allergenes_trouves

def filtrer_recettes_allergies(allergies):
    """Retourne les recettes sans les allergènes spécifiés"""
    recettes_ok = []
    for nom in RECETTES_DETAILLEES.keys():
        ok, _ = verifier_allergenes(nom, allergies)
        if ok:
            recettes_ok.append(nom)
    return recettes_ok

def detecter_allergies(texte):
    """Détecte les allergies mentionnées dans un texte"""
    texte_lower = texte.lower()
    allergies_detectees = []
    
    mots_cles = {
        "gluten": ["gluten", "blé", "céréales"],
        "lactose": ["lactose", "lait", "produits laitiers"],
        "arachides": ["arachide", "cacahuète"],
        "fruits_a_coque": ["noix", "amande", "noisette", "fruits à coque"],
        "oeufs": ["oeuf", "œuf"],
        "poisson": ["poisson"],
        "crustaces": ["crustacé", "crevette", "crabe"],
        "soja": ["soja"],
        "celeri": ["céleri"],
        "sesame": ["sésame"]
    }
    
    for allergie, mots in mots_cles.items():
        for mot in mots:
            if mot in texte_lower:
                if allergie not in allergies_detectees:
                    allergies_detectees.append(allergie)
    
    return allergies_detectees

# =============================================================================
# FONCTIONS INGRÉDIENTS (NOUVELLE)
# =============================================================================

def verifier_ingredients(recette_nom, ingredients_disponibles):
    """Vérifie quels ingrédients manquent pour une recette"""
    recette = RECETTES_DETAILLEES.get(recette_nom)
    if not recette:
        return [], []
    
    ingredients_recette = list(recette.get('ingredients', {}).keys())
    disponibles = [i.lower().replace(' ', '_') for i in ingredients_disponibles]
    
    manquants = []
    presents = []
    
    for ing in ingredients_recette:
        ing_clean = ing.lower().replace('_kg', '').replace('_litre', '').replace('_unite', '')
        trouve = False
        for dispo in disponibles:
            if ing_clean in dispo or dispo in ing_clean:
                trouve = True
                break
        
        if trouve:
            presents.append(ing)
        else:
            manquants.append(ing)
    
    return presents, manquants

def generer_liste_courses(recette_nom, nb_personnes=4):
    """Génère une liste de courses pour une recette"""
    recette = RECETTES_DETAILLEES.get(recette_nom)
    if not recette:
        return []
    
    multiplicateur = nb_personnes / 4  # Recettes de base pour 4
    liste = []
    
    for ing, quantite in recette.get('ingredients', {}).items():
        ing_clean = ing.replace('_kg', '').replace('_litre', '').replace('_unite', '').replace('_', ' ')
        qte_ajustee = round(quantite * multiplicateur, 2)
        
        if '_kg' in ing:
            unite = 'kg'
        elif '_litre' in ing:
            unite = 'L'
        else:
            unite = 'unité(s)'
        
        liste.append({
            'ingredient': ing_clean.capitalize(),
            'quantite': qte_ajustee,
            'unite': unite
        })
    
    return liste

# =============================================================================
# FONCTIONS MODE GROUPE (NOUVELLE)
# =============================================================================

def multiplier_recette(recette_nom, nb_personnes):
    """Multiplie les quantités d'une recette selon le nombre de personnes"""
    recette = RECETTES_DETAILLEES.get(recette_nom)
    if not recette:
        return None
    
    multiplicateur = nb_personnes / 4
    
    ingredients_ajustes = {}
    for ing, qte in recette.get('ingredients', {}).items():
        ingredients_ajustes[ing] = round(qte * multiplicateur, 2)
    
    budget_ajuste = round(recette.get('budget_assiette', 0) * nb_personnes, 2)
    
    return {
        'ingredients': ingredients_ajustes,
        'budget_total': budget_ajuste,
        'nb_personnes': nb_personnes
    }

# =============================================================================
# FONCTIONS SUGGESTIONS INTELLIGENTES (NOUVELLE)
# =============================================================================

def suggerer_recettes(budget_max=None, temps_max=None, difficulte=None, saison=None):
    """Suggère des recettes selon les critères"""
    suggestions = []
    
    for nom, recette in RECETTES_DETAILLEES.items():
        score = 0
        
        # Filtre budget
        if budget_max and recette.get('budget_assiette', 0) <= budget_max:
            score += 1
        elif budget_max:
            continue
        
        # Filtre temps
        if temps_max and recette.get('duree_min', 0) <= temps_max:
            score += 1
        elif temps_max:
            continue
        
        # Filtre difficulté
        if difficulte:
            diff_recette = recette.get('difficulte', '').lower()
            if difficulte.lower() == diff_recette:
                score += 1
            elif difficulte.lower() == 'facile' and diff_recette != 'facile':
                continue
        
        # Filtre saison
        if saison:
            saison_recette = recette.get('saison', 'Toute').lower()
            if saison.lower() in saison_recette or saison_recette == 'toute':
                score += 1
        
        suggestions.append((nom, score, recette))
    
    # Trier par score décroissant
    suggestions.sort(key=lambda x: x[1], reverse=True)
    
    return [(s[0], s[2]) for s in suggestions[:6]]

# =============================================================================
# FONCTION DÉTECTION STRESS (NOUVELLE)
# =============================================================================

def detecter_stress(texte):
    """Détecte le stress dans le message de l'utilisateur"""
    texte_lower = texte.lower()
    
    mots_stress = [
        "pressé", "vite", "rapide", "urgent", "pas le temps",
        "fatigué", "épuisé", "crevé", "stressé", "stress",
        "simple", "facile", "compliqué", "dur", "difficile",
        "aide", "help", "sos", "panique"
    ]
    
    score_stress = 0
    for mot in mots_stress:
        if mot in texte_lower:
            score_stress += 1
    
    return score_stress >= 2

def detecter_recette_dans_message(texte):
    """
    Détecte si l'utilisateur mentionne une recette et veut la préparer.
    Retourne le nom de la recette si trouvée, None sinon.
    """
    texte_lower = texte.lower()
    
    # Mots qui indiquent une intention de cuisiner
    mots_action = [
        "préparer", "preparer", "faire", "cuisiner", "guide", "guidez",
        "oui", "ok", "d'accord", "daccord", "allons-y", "go", "commence",
        "je veux", "j'aimerais", "montre", "aide", "aidez", "aider"
    ]
    
    # Vérifier si c'est une demande d'action
    est_demande_action = any(mot in texte_lower for mot in mots_action)
    
    # Chercher une recette mentionnée
    recette_trouvee = None
    meilleur_score = 0
    
    for nom_recette in RECETTES_DETAILLEES.keys():
        nom_lower = nom_recette.lower()
        
        # Correspondance exacte ou partielle
        if nom_lower in texte_lower:
            score = len(nom_lower)
            if score > meilleur_score:
                meilleur_score = score
                recette_trouvee = nom_recette
        else:
            # Chercher les mots clés de la recette
            mots_recette = nom_lower.split()
            for mot in mots_recette:
                if len(mot) > 3 and mot in texte_lower:
                    score = len(mot)
                    if score > meilleur_score:
                        meilleur_score = score
                        recette_trouvee = nom_recette
    
    # Si on a trouvé une recette ET c'est une demande d'action, lancer
    if recette_trouvee and est_demande_action:
        return recette_trouvee
    
    # Si le message est juste "oui" ou confirmation, vérifier l'historique
    if texte_lower.strip() in ["oui", "ok", "oui.", "ok.", "d'accord", "yes", "yep", "ouais", "go", "allons-y", "oui ?"]:
        # Chercher la dernière recette mentionnée dans l'historique
        for entry in reversed(st.session_state.historique[-6:]):
            if entry['role'] == 'assistant':
                for nom_recette in RECETTES_DETAILLEES.keys():
                    if nom_recette.lower() in entry['content'].lower():
                        return nom_recette
    
    return recette_trouvee if est_demande_action else None

def lancer_mode_cuisine(nom_recette):
    """Lance le mode cuisine pour une recette donnée"""
    if nom_recette in RECETTES_DETAILLEES:
        st.session_state.recette_en_cours = nom_recette
        st.session_state.mode_cuisine = True
        st.session_state.etape_cuisine = 0
        return True
    return False

def recettes_anti_stress():
    """Retourne des recettes simples et rapides pour les moments de stress"""
    recettes = []
    for nom, recette in RECETTES_DETAILLEES.items():
        if recette.get('difficulte') == 'Facile' and recette.get('duree_min', 999) <= 30:
            recettes.append(nom)
    return recettes[:5]

# =============================================================================
# FONCTIONS AUDIO
# =============================================================================

def transcribe_audio_whisper(audio_bytes):
    """Transcription Whisper via Groq"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        with open(tmp_path, 'rb') as audio_file:
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3",
                language="fr",
                response_format="text"
            )
        
        os.unlink(tmp_path)
        return transcription.strip()
    except Exception as e:
        return None

def lire_texte_vocal(texte):
    """Synthèse vocale via JavaScript"""
    if not texte or len(texte) < 3:
        return
    
    # Nettoyer le texte - supprimer emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F1E0-\U0001F1FF"
        "\U0001F300-\U0001F5FF"
        "\U0001F600-\U0001F64F"
        "\U0001F680-\U0001F6FF"
        "\U0001F700-\U0001F77F"
        "\U0001F780-\U0001F7FF"
        "\U0001F800-\U0001F8FF"
        "\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FA6F"
        "\U0001FA70-\U0001FAFF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    texte_clean = emoji_pattern.sub(' ', texte)
    texte_clean = texte_clean.replace("'", "'").replace('"', ' ').replace('\n', ' ').replace('`', ' ')
    texte_clean = re.sub(r'\s+', ' ', texte_clean).strip()[:300]
    
    unique_id = abs(hash(texte_clean + str(datetime.now().timestamp()))) % 100000
    
    html = f"""
    <div id="speech-{unique_id}"></div>
    <script>
    (function() {{
        try {{
            if (window.speechSynthesis) {{
                window.speechSynthesis.cancel();
            }}
            
            function speak() {{
                try {{
                    const text = `{texte_clean}`;
                    const utterance = new SpeechSynthesisUtterance(text);
                    utterance.lang = 'fr-FR';
                    utterance.rate = 0.9;
                    utterance.pitch = 1.0;
                    utterance.volume = 1.0;
                    
                    const voices = window.speechSynthesis.getVoices();
                    const frVoice = voices.find(v => v.lang.startsWith('fr'));
                    if (frVoice) utterance.voice = frVoice;
                    
                    window.speechSynthesis.speak(utterance);
                }} catch(e) {{}}
            }}
            
            if (window.speechSynthesis.getVoices().length === 0) {{
                window.speechSynthesis.onvoiceschanged = function() {{
                    speak();
                    window.speechSynthesis.onvoiceschanged = null;
                }};
            }} else {{
                setTimeout(speak, 300);
            }}
        }} catch(error) {{}}
    }})();
    </script>
    """
    st.components.v1.html(html, height=0)

# =============================================================================
# FONCTIONS COMPARATEUR ET GPS
# =============================================================================

def comparer_prix(ingredients):
    """Compare les prix entre enseignes"""
    comparaison = {}
    details = {}
    
    for enseigne, prix in PRIX_ENSEIGNES.items():
        total = 0
        detail_enseigne = {}
        for ing, qte in ingredients.items():
            prix_ing = prix.get(ing, PRIX_INGREDIENTS.get(ing, 0))
            cout = prix_ing * qte
            total += cout
            detail_enseigne[ing] = round(cout, 2)
        
        comparaison[enseigne] = round(total, 2)
        details[enseigne] = detail_enseigne
    
    # Trier par prix croissant
    comparaison = dict(sorted(comparaison.items(), key=lambda x: x[1]))
    
    return comparaison, details

# =============================================================================
# FONCTIONS CONVERSION
# =============================================================================

def convertir_mesure(valeur, de_unite, vers_unite):
    """Convertit les mesures culinaires"""
    conversions = {
        ('g', 'tasse_farine'): lambda v: v / 125,
        ('tasse_farine', 'g'): lambda v: v * 125,
        ('g', 'tasse_sucre'): lambda v: v / 200,
        ('tasse_sucre', 'g'): lambda v: v * 200,
        ('ml', 'tasse'): lambda v: v / 250,
        ('tasse', 'ml'): lambda v: v * 250,
        ('ml', 'cuillere_soupe'): lambda v: v / 15,
        ('cuillere_soupe', 'ml'): lambda v: v * 15,
        ('celsius', 'fahrenheit'): lambda v: (v * 9/5) + 32,
        ('fahrenheit', 'celsius'): lambda v: (v - 32) * 5/9,
        ('g', 'oz'): lambda v: v / 28.35,
        ('oz', 'g'): lambda v: v * 28.35,
        ('kg', 'lb'): lambda v: v * 2.205,
        ('lb', 'kg'): lambda v: v / 2.205
    }
    
    key = (de_unite.lower(), vers_unite.lower())
    if key in conversions:
        return round(conversions[key](valeur), 2)
    
    return None

# =============================================================================
# FONCTION TIMER
# =============================================================================

def creer_timer_html(duree_minutes, nom_timer):
    """Crée un timer JavaScript"""
    duree_secondes = duree_minutes * 60
    
    html = f"""
    <div id="timer-{nom_timer}" style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin: 10px 0;
    ">
        <div style="font-size: 16px; margin-bottom: 10px;">⏱️ {nom_timer}</div>
        <div id="display-{nom_timer}" style="font-size: 36px; font-weight: bold;">
            {duree_minutes:02d}:00
        </div>
    </div>
    
    <script>
    (function() {{
        let seconds = {duree_secondes};
        const display = document.getElementById('display-{nom_timer}');
        
        const timer = setInterval(function() {{
            seconds--;
            const mins = Math.floor(seconds / 60);
            const secs = seconds % 60;
            display.textContent = String(mins).padStart(2, '0') + ':' + String(secs).padStart(2, '0');
            
            if (seconds <= 0) {{
                clearInterval(timer);
                display.textContent = "TERMINÉ!";
                display.parentElement.style.background = 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
                
                // Alerte vocale
                if (window.speechSynthesis) {{
                    const msg = new SpeechSynthesisUtterance("C'est prêt pour {nom_timer}!");
                    msg.lang = 'fr-FR';
                    window.speechSynthesis.speak(msg);
                }}
                
                // Son d'alerte
                try {{
                    const ctx = new (window.AudioContext || window.webkitAudioContext)();
                    const osc = ctx.createOscillator();
                    osc.connect(ctx.destination);
                    osc.frequency.value = 800;
                    osc.start();
                    setTimeout(() => osc.stop(), 500);
                }} catch(e) {{}}
            }}
        }}, 1000);
    }})();
    </script>
    """
    return html

# =============================================================================
# FONCTION IA - SARAH
# =============================================================================

def demander_sarah(user_input, contexte="conversation"):
    """Appelle Groq pour obtenir une réponse de Sarah"""
    
    # Récupérer infos contextuelles
    meteo = obtenir_meteo()
    profil = st.session_state.profil
    
    # Construire le contexte
    contexte_info = f"""
PROFIL UTILISATEUR:
- Prénom: {profil.get('nom', 'Ami')}
- Ville: {st.session_state.ville_utilisateur or 'Non renseignée'}
- Allergies: {', '.join(profil.get('allergies', [])) or 'Aucune'}
- Nombre de personnes: {st.session_state.nb_personnes}
"""
    
    # Météo en info secondaire seulement
    meteo_info = ""
    if meteo:
        meteo_info = f"(Info: il fait {meteo['temp']}°C dehors)"

    # Liste des recettes disponibles
    recettes_ma = [n for n, r in RECETTES_DETAILLEES.items() if '🇲🇦' in r['pays']]
    recettes_fr = [n for n, r in RECETTES_DETAILLEES.items() if '🇫🇷' in r['pays']]
    
    system_prompt = f"""Tu es Sarah, assistante culinaire PROFESSIONNELLE bi-culturelle France-Maroc.

{contexte_info}
{meteo_info}

RECETTES DISPONIBLES (40 au total):
🇲🇦 Marocaines: {', '.join(recettes_ma)}
🇫🇷 Françaises: {', '.join(recettes_fr)}

RÈGLE CRITIQUE - RESPECTE LA DEMANDE DE L'UTILISATEUR:
- Si l'utilisateur demande une recette SPÉCIFIQUE (ex: "Pastilla", "Couscous", "Blanquette"), 
  tu DOIS parler de CETTE recette, PAS d'une autre!
- Ne propose JAMAIS une autre recette si l'utilisateur en a déjà choisi une
- La météo est une INFO SECONDAIRE, elle ne doit PAS changer le choix de l'utilisateur

AUTRES RÈGLES:
1. Utilise UNIQUEMENT le prénom (jamais "chéri", "BOBO", "ma belle")
2. Tutoiement simple et professionnel
3. Réponses COURTES (2-3 phrases MAX)
4. Si recette demandée pas dans ta liste → propose des alternatives VARIÉES
5. UNIQUEMENT si l'utilisateur n'a PAS de choix précis, tu peux suggérer selon la météo

DARIJA (pour recettes marocaines uniquement):
- Expressions naturelles: Bsaha, Yallah, Mezyan, Sahel
- Ne traduis jamais les noms des plats traditionnels

EXEMPLES CORRECTS:
User: "Je veux faire une Pastilla"
Sarah: "Super choix! La Pastilla, Mezyan! Je te guide pour la préparer?"

User: "Et ça me convient" (après avoir choisi Pastilla)
Sarah: "Parfait! On commence la Pastilla. Voici les ingrédients..."

User: "Qu'est-ce que je pourrais faire?"
Sarah: "Hmm, il fait frais... Un bon Tajine ou une Blanquette te réchaufferait!"

EXEMPLE INTERDIT:
User: "Je veux une Pastilla"
Sarah: "Par ce froid, je te recommande la Harira..." ❌ NON! L'utilisateur a choisi Pastilla!
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return completion.choices[0].message.content
    except Exception as e:
        return "Désolée, j'ai un petit souci technique. Réessaie dans un instant!"

def generer_recette_ia(description):
    """Génère une recette complète via IA"""
    
    system_prompt = """Tu es un chef cuisinier expert bi-culturel France-Maroc.
Génère une recette COMPLÈTE au format JSON VALIDE avec cette structure:

{
  "nom": "Nom de la recette",
  "pays": "🇫🇷 France" ou "🇲🇦 Maroc",
  "categorie": "Plat principal/Dessert/Entrée/Soupe",
  "budget_assiette": 2.50,
  "duree_min": 45,
  "difficulte": "Facile/Moyen/Difficile",
  "saison": "Hiver/Été/Toute",
  "ingredients": {"ingredient_kg": 0.5},
  "etapes": [{"num": 1, "titre": "Titre", "description": "Description", "temperature": "Feu moyen", "duree": "10 min", "astuce": "Conseil"}],
  "anecdote": "Histoire culturelle"
}

IMPORTANT: Retourne UNIQUEMENT le JSON, rien d'autre."""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Crée une recette pour: {description}"}
            ],
            temperature=0.8,
            max_tokens=1500
        )
        
        response = completion.choices[0].message.content
        
        # Extraire le JSON
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            recette = json.loads(json_match.group())
            return recette
        
        return None
    except Exception as e:
        return None

# =============================================================================
# FONCTION SCAN FRIGO (GROQ VISION)
# =============================================================================

def analyser_photo_frigo(image_bytes):
    """Analyse une photo du frigo avec Groq Vision"""
    try:
        # Encoder en base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        completion = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyse cette photo de frigo/ingrédients. 
Liste UNIQUEMENT les ingrédients que tu vois clairement, un par ligne.
Format: ingredient1, ingredient2, ingredient3
Ne mets rien d'autre que la liste."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        ingredients_texte = completion.choices[0].message.content
        # Parser la liste
        ingredients = [i.strip() for i in ingredients_texte.replace('\n', ',').split(',') if i.strip()]
        return ingredients
        
    except Exception as e:
        return []

def suggerer_recettes_ingredients(ingredients_disponibles):
    """Suggère des recettes basées sur les ingrédients disponibles"""
    if not ingredients_disponibles:
        return []
    
    suggestions = []
    ingredients_lower = [i.lower() for i in ingredients_disponibles]
    
    for nom, recette in RECETTES_DETAILLEES.items():
        ingredients_recette = list(recette.get('ingredients', {}).keys())
        
        # Compter combien d'ingrédients correspondent
        matches = 0
        for ing_recette in ingredients_recette:
            ing_clean = ing_recette.lower().replace('_kg', '').replace('_', ' ')
            for ing_dispo in ingredients_lower:
                if ing_clean in ing_dispo or ing_dispo in ing_clean:
                    matches += 1
                    break
        
        if matches > 0:
            pourcentage = (matches / len(ingredients_recette)) * 100
            suggestions.append((nom, pourcentage, recette))
    
    # Trier par pourcentage décroissant
    suggestions.sort(key=lambda x: x[1], reverse=True)
    
    return [(s[0], s[1], s[2]) for s in suggestions[:5]]


# =============================================================================
# FONCTION AFFICHAGE ÉTAPES CUISINE
# =============================================================================

def afficher_etape_cuisine():
    """Affiche l'étape actuelle de la recette en cours"""
    if not st.session_state.recette_en_cours or not st.session_state.mode_cuisine:
        return
    
    recette = RECETTES_DETAILLEES.get(st.session_state.recette_en_cours)
    if not recette:
        return
    
    etapes = recette.get('etapes', [])
    if not etapes:
        return
    
    idx = st.session_state.etape_cuisine
    if idx >= len(etapes):
        idx = len(etapes) - 1
        st.session_state.etape_cuisine = idx
    
    etape = etapes[idx]
    
    # Affichage de l'étape
    st.markdown(f"""
    <div class="etape-box">
        <h2>{etape.get('titre', f'Étape {idx + 1}')}</h2>
        <p style="font-size: 20px; line-height: 1.6; margin: 20px 0;">
            {etape.get('description', '')}
        </p>
        <div style="display: flex; justify-content: center; gap: 30px; margin-top: 20px;">
            <div style="background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 10px;">
                🌡️ {etape.get('temperature', 'N/A')}
            </div>
            <div style="background: rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 10px;">
                ⏱️ {etape.get('duree', 'N/A')}
            </div>
        </div>
        <div style="background: rgba(255,200,55,0.3); padding: 15px; border-radius: 10px; margin-top: 20px;">
            💡 <strong>Astuce:</strong> {etape.get('astuce', '')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Lire l'étape à voix haute
    texte_vocal = f"{etape.get('titre', '')}. {etape.get('description', '')}. Astuce: {etape.get('astuce', '')}"
    lire_texte_vocal(texte_vocal)

# =============================================================================
# CSS PROFESSIONNEL
# =============================================================================

def get_professional_css():
    """CSS Design Professionnel"""
    return """
    <style>
    /* VARIABLES */
    :root {
        --orange: #FF6B35;
        --orange-light: #F7931E;
        --yellow: #FFC837;
        --purple: #667eea;
        --purple-dark: #764ba2;
        --green: #11998e;
        --pink: #f093fb;
    }
    
    /* GRADIENTS */
    .gradient-header {
        background: linear-gradient(135deg, var(--orange) 0%, var(--orange-light) 50%, var(--yellow) 100%);
        padding: 25px;
        border-radius: 20px;
        margin-bottom: 25px;
        box-shadow: 0 10px 40px rgba(255, 107, 53, 0.3);
    }
    
    /* CARDS */
    .card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-3px);
    }
    
    /* MÉTÉO */
    .weather-card {
        background: linear-gradient(135deg, var(--purple) 0%, var(--purple-dark) 100%);
        color: white;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    .weather-temp {
        font-size: 48px;
        font-weight: bold;
        margin: 10px 0;
    }
    
    /* SARAH */
    .sarah-welcome {
        background: linear-gradient(135deg, var(--pink) 0%, #f5576c 100%);
        color: white;
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(240, 147, 251, 0.3);
    }
    
    .sarah-avatar {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 40px;
        margin: 0 auto 15px;
    }
    
    .sarah-message {
        font-size: 22px;
        font-weight: 500;
        text-align: center;
        line-height: 1.5;
    }
    
    /* COMPARATEUR */
    .comparateur-card {
        background: linear-gradient(135deg, var(--green) 0%, #38ef7d 100%);
        color: white;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
    }
    
    .prix-badge {
        background: white;
        color: var(--green);
        padding: 8px 15px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    
    /* GPS BUTTON */
    .gps-button {
        background: linear-gradient(135deg, var(--pink) 0%, #f5576c 100%);
        color: white;
        padding: 12px 25px;
        border-radius: 25px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        margin-top: 10px;
    }
    
    /* MICRO */
    .micro-container {
        background: linear-gradient(135deg, var(--orange) 0%, var(--orange-light) 100%);
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        margin-top: 20px;
    }
    
    .micro-title {
        color: white;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    /* ÉTAPES */
    .etape-box {
        background: linear-gradient(135deg, var(--purple) 0%, var(--purple-dark) 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .etape-box h2 {
        color: white !important;
        font-size: 26px;
        margin-bottom: 15px;
    }
    
    /* MESSAGES */
    .message-user {
        background: linear-gradient(135deg, var(--purple) 0%, var(--purple-dark) 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 20px 20px 5px 20px;
        margin: 10px 0;
        max-width: 80%;
        float: right;
        clear: both;
    }
    
    .message-assistant {
        background: linear-gradient(135deg, var(--orange) 0%, var(--orange-light) 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px 0;
        max-width: 80%;
        float: left;
        clear: both;
    }
    
    /* ANIMATIONS */
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-slide {
        animation: slideIn 0.5s ease-out;
    }
    
    /* RESPONSIVE */
    @media (max-width: 768px) {
        .weather-temp { font-size: 36px; }
        .sarah-message { font-size: 18px; }
        .etape-box h2 { font-size: 22px; }
        .etape-box p { font-size: 16px; }
    }
    
    /* ALLERGIE WARNING */
    .allergie-warning {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    /* SUGGESTION CARD */
    .suggestion-card {
        background: linear-gradient(135deg, #a8e6cf 0%, #88d8b0 100%);
        color: #2d5a3d;
        padding: 15px;
        border-radius: 10px;
        margin: 5px 0;
        cursor: pointer;
    }
    
    .suggestion-card:hover {
        transform: scale(1.02);
    }
    </style>
    """

# =============================================================================
# FONCTION PRINCIPALE
# =============================================================================

def main():
    """Fonction principale de l'application"""
    
    # CSS
    st.markdown(get_professional_css(), unsafe_allow_html=True)
    
    # Géolocalisation HTML5 (prioritaire, fonctionne sur mobile)
    st.markdown(obtenir_geolocalisation_html5(), unsafe_allow_html=True)
    
    # Récupérer ville depuis URL si disponible (set par HTML5/GPS)
    try:
        ville_gps = st.query_params.get('ville_gps', None)
        source_gps = st.query_params.get('source_gps', None)
        
        # Liste des villes de serveurs cloud à ignorer
        villes_serveurs = ['the dalles', 'dalles', 'council bluffs', 'ashburn', 'san francisco', 'boardman']
        
        if ville_gps and ville_gps.lower() not in villes_serveurs:
            if ville_gps not in ['', 'null', 'undefined', 'France']:
                if ville_gps != st.session_state.ville_utilisateur:
                    st.session_state.ville_utilisateur = ville_gps
                    st.session_state.profil['ville'] = ville_gps
                    st.session_state.meteo_cache = None
    except:
        pass
    
    # Si pas de ville valide, essayer via IP (mais filtrer les villes US)
    if not st.session_state.ville_utilisateur or st.session_state.ville_utilisateur in ['', 'France']:
        ville_ip = obtenir_ville_via_ip()
        villes_serveurs = ['the dalles', 'dalles', 'council bluffs', 'ashburn', 'san francisco', 'boardman']
        if ville_ip and ville_ip.lower() not in villes_serveurs and ville_ip not in ['', 'France', 'undefined']:
            st.session_state.ville_utilisateur = ville_ip
            st.session_state.profil['ville'] = ville_ip
    
    # HEADER
    st.markdown("""
    <div class="gradient-header">
        <h1 style="color: white; text-align: center; font-size: 42px; margin: 0;">
            🍽️ SARAH'MIAM
        </h1>
        <p style="color: white; text-align: center; font-size: 18px; margin-top: 10px; opacity: 0.9;">
            Ton chef personnel France-Maroc 🇫🇷 🇲🇦
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # MÉTÉO + DATE
    ville = st.session_state.ville_utilisateur or "France"
    meteo = obtenir_meteo()
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if meteo:
            st.markdown(f"""
            <div class="weather-card animate-slide">
                <div style="font-size: 18px; font-weight: bold;">📍 {meteo['ville']}</div>
                <div class="weather-temp">{meteo['temp']}°C</div>
                <div>{meteo['description']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="weather-card animate-slide">
                <div style="font-size: 18px; font-weight: bold;">📍 {ville}</div>
                <div style="font-size: 14px; margin-top: 10px;">Bienvenue!</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        now = datetime.now()
        st.markdown(f"""
        <div class="card animate-slide">
            <div style="text-align: center;">
                <div style="font-size: 22px; color: #FF6B35; font-weight: bold;">
                    📅 {now.strftime('%d %B %Y')}
                </div>
                <div style="font-size: 18px; color: #666; margin-top: 5px;">
                    ⏰ {now.strftime('%H:%M')}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("📍 Changer ville", use_container_width=True):
            st.session_state.show_ville = not st.session_state.get('show_ville', False)
    
    # Champ pour changer de ville
    if st.session_state.get('show_ville', False):
        nouvelle_ville = st.text_input("Ta ville:", key="input_ville")
        if st.button("✅ Valider") and nouvelle_ville:
            st.session_state.ville_utilisateur = nouvelle_ville
            st.session_state.profil['ville'] = nouvelle_ville
            st.session_state.show_ville = False
            st.session_state.meteo_cache = None  # Reset cache météo
            st.rerun()
    
    # Suggestions météo
    if meteo:
        suggestions_meteo = suggestion_meteo(meteo)
        if suggestions_meteo:
            st.markdown(f"""
            <div class="suggestion-card">
                🌤️ <strong>Suggestions du jour:</strong> {', '.join(suggestions_meteo)}
            </div>
            """, unsafe_allow_html=True)
    
    # MESSAGE BIENVENUE
    if len(st.session_state.historique) == 0:
        prenom = st.session_state.profil.get('nom', '')
        if prenom:
            msg = f"Marhaba {prenom}! Qu'est-ce qui te ferait plaisir aujourd'hui?"
        else:
            msg = "Marhaba! Je suis Sarah, ton chef personnel France-Maroc! Qu'est-ce qui te ferait plaisir?"
        
        st.markdown(f"""
        <div class="sarah-welcome animate-slide">
            <div class="sarah-avatar">👩‍🍳</div>
            <div class="sarah-message">{msg}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.get('bienvenue_jouee', False):
            lire_texte_vocal(msg)
            st.session_state.bienvenue_jouee = True
    
    # SIDEBAR
    with st.sidebar:
        st.markdown("### 👤 Mon Profil")
        
        # Prénom
        nom = st.text_input("Prénom:", value=st.session_state.profil.get('nom', ''), key="input_nom")
        if nom != st.session_state.profil.get('nom'):
            st.session_state.profil['nom'] = nom
        
        # Nombre de personnes
        st.session_state.nb_personnes = st.number_input(
            "Nombre de personnes:", 
            min_value=1, 
            max_value=20, 
            value=st.session_state.nb_personnes,
            key="input_nb_pers"
        )
        
        # Allergies
        st.markdown("#### ⚠️ Allergies")
        allergies_options = list(ALLERGENES.keys())
        allergies_selectionnees = st.multiselect(
            "Sélectionne tes allergies:",
            allergies_options,
            default=st.session_state.profil.get('allergies', []),
            key="input_allergies"
        )
        st.session_state.profil['allergies'] = allergies_selectionnees
        
        st.markdown("---")
        
        # COMPARATEUR
        st.markdown("### 🛒 Comparateur Prix")
        
        recettes_list = list(RECETTES_DETAILLEES.keys())
        rec_comp = st.selectbox("Choisir une recette:", [""] + recettes_list, key="select_comp")
        
        if rec_comp and st.button("💰 Comparer les prix", key="btn_comp"):
            recette = RECETTES_DETAILLEES[rec_comp]
            comp, _ = comparer_prix(recette['ingredients'])
            
            meilleur = list(comp.keys())[0]
            
            st.markdown(f"""
            <div class="comparateur-card">
                <div style="font-size: 18px; font-weight: bold; margin-bottom: 10px;">
                    🏆 Meilleur: {meilleur}
                </div>
                <div class="prix-badge">{comp[meilleur]}€</div>
            </div>
            """, unsafe_allow_html=True)
            
            for ens, px in comp.items():
                st.write(f"• {ens}: {px}€")
            
            # Lien GPS
            if ville and meilleur in LIENS_ENSEIGNES:
                lien = LIENS_ENSEIGNES[meilleur]['gps'].format(ville=ville)
                st.markdown(f'<a href="{lien}" target="_blank" class="gps-button">🚗 Y aller à {ville}</a>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # RECETTES
        st.markdown("### 📖 Recettes")
        
        # Filtres
        filtre_pays = st.radio("Filtrer:", ["Toutes", "🇲🇦 Maroc", "🇫🇷 France"], horizontal=True, key="filtre_pays")
        
        for nom_rec, rec in RECETTES_DETAILLEES.items():
            if filtre_pays != "Toutes" and filtre_pays not in rec['pays']:
                continue
            
            # Vérifier allergies
            ok, allergenes = verifier_allergenes(nom_rec, allergies_selectionnees)
            
            with st.expander(f"{rec['pays'][:2]} {nom_rec}"):
                st.write(f"💰 {rec['budget_assiette']}€ · ⏱️ {rec['duree_min']}min · {rec['difficulte']}")
                
                if not ok:
                    st.warning(f"⚠️ Contient: {', '.join(allergenes)}")
                
                if st.button("🍳 Cuisiner", key=f"cook_{nom_rec}"):
                    st.session_state.recette_en_cours = nom_rec
                    st.session_state.mode_cuisine = True
                    st.session_state.etape_cuisine = 0
                    st.rerun()
    
    # MODE CUISINE
    if st.session_state.mode_cuisine and st.session_state.recette_en_cours:
        rec_nom = st.session_state.recette_en_cours
        rec = RECETTES_DETAILLEES[rec_nom]
        
        st.markdown(f"""
        <div class="card">
            <h2 style="color: #FF6B35; text-align: center;">🍳 {rec_nom}</h2>
            <p style="text-align: center; color: #666;">{rec['pays']} · {rec['categorie']} · {rec['duree_min']} min</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Bouton quitter mode cuisine
        if st.button("❌ Quitter la recette"):
            st.session_state.mode_cuisine = False
            st.session_state.recette_en_cours = None
            st.rerun()
        
        # Navigation étapes
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("⬅️ Précédent") and st.session_state.etape_cuisine > 0:
                st.session_state.etape_cuisine -= 1
                st.rerun()
        
        with col2:
            nb_etapes = len(rec['etapes'])
            st.markdown(f"<div style='text-align: center; font-size: 18px; font-weight: bold;'>Étape {st.session_state.etape_cuisine + 1} / {nb_etapes}</div>", unsafe_allow_html=True)
        
        with col3:
            if st.session_state.etape_cuisine < len(rec['etapes']) - 1:
                if st.button("Suivant ➡️"):
                    st.session_state.etape_cuisine += 1
                    st.rerun()
            else:
                if st.button("✅ Terminé!"):
                    st.session_state.mode_cuisine = False
                    st.session_state.recette_en_cours = None
                    st.balloons()
                    st.success(f"Bravo! Tu as terminé {rec_nom}! Bsaha! 🎉")
                    st.rerun()
        
        # Afficher l'étape
        afficher_etape_cuisine()
        
        # Timer rapide
        st.markdown("---")
        st.markdown("### ⏱️ Timer rapide")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            timer_min = st.number_input("Minutes:", min_value=1, max_value=120, value=10, key="timer_min")
        with col_t2:
            timer_nom = st.text_input("Nom:", value="Cuisson", key="timer_nom")
        
        if st.button("▶️ Lancer timer"):
            st.components.v1.html(creer_timer_html(timer_min, timer_nom), height=150)
    
    # MODE CONVERSATION
    else:
        # Historique
        for entry in st.session_state.historique[-10:]:
            role_class = "message-user" if entry['role'] == 'user' else "message-assistant"
            st.markdown(f"""
            <div class="{role_class}">
                {entry['content']}
            </div>
            <div style="clear: both;"></div>
            """, unsafe_allow_html=True)
    
    # ZONE INPUT
    st.markdown("""
    <div class="micro-container">
        <div class="micro-title">🎤 Parle à Sarah ou écris</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_mic, col_txt = st.columns([1, 3])
    
    with col_mic:
        audio_bytes = audio_recorder(
            text="",
            recording_color="#FF0000",
            neutral_color="#FF6B35",
            icon_name="microphone",
            icon_size="3x",
            key="audio_main"
        )
        
        if audio_bytes:
            audio_hash = hash(audio_bytes)
            if audio_hash != st.session_state.last_audio_hash:
                st.session_state.last_audio_hash = audio_hash
                
                with st.spinner("🎤 Transcription..."):
                    text_audio = transcribe_audio_whisper(audio_bytes)
                
                if text_audio and len(text_audio) > 2:
                    # Détecter allergies
                    allergies_detectees = detecter_allergies(text_audio)
                    if allergies_detectees:
                        for a in allergies_detectees:
                            if a not in st.session_state.profil['allergies']:
                                st.session_state.profil['allergies'].append(a)
                        st.info(f"🔔 J'ai noté tes allergies: {', '.join(allergies_detectees)}")
                    
                    st.session_state.historique.append({'role': 'user', 'content': text_audio})
                    
                    # PRIORITÉ 1: Détecter si l'utilisateur veut lancer une recette
                    recette_detectee = detecter_recette_dans_message(text_audio)
                    if recette_detectee:
                        # Lancer directement le mode cuisine!
                        lancer_mode_cuisine(recette_detectee)
                        reponse = f"C'est parti pour {recette_detectee}! Yallah, suis les étapes! 🍳"
                        st.session_state.historique.append({'role': 'assistant', 'content': reponse})
                        lire_texte_vocal(reponse)
                        st.rerun()
                    
                    # PRIORITÉ 2: Détecter stress
                    elif detecter_stress(text_audio):
                        recettes_faciles = recettes_anti_stress()
                        reponse = f"Je vois que tu es pressé! Voici des recettes rapides et faciles: {', '.join(recettes_faciles)}. Laquelle te tente?"
                        st.session_state.historique.append({'role': 'assistant', 'content': reponse})
                        lire_texte_vocal(reponse)
                        st.rerun()
                    
                    # PRIORITÉ 3: Conversation normale
                    else:
                        with st.spinner("💭 Sarah réfléchit..."):
                            reponse = demander_sarah(text_audio)
                        st.session_state.historique.append({'role': 'assistant', 'content': reponse})
                        lire_texte_vocal(reponse)
                        st.rerun()
    
    with col_txt:
        user_input = st.chat_input("Écris ta question...", key="chat_main")
        
        if user_input:
            # Détecter allergies
            allergies_detectees = detecter_allergies(user_input)
            if allergies_detectees:
                for a in allergies_detectees:
                    if a not in st.session_state.profil['allergies']:
                        st.session_state.profil['allergies'].append(a)
            
            st.session_state.historique.append({'role': 'user', 'content': user_input})
            
            # PRIORITÉ 1: Détecter si l'utilisateur veut lancer une recette
            recette_detectee = detecter_recette_dans_message(user_input)
            if recette_detectee:
                # Lancer directement le mode cuisine!
                lancer_mode_cuisine(recette_detectee)
                reponse = f"C'est parti pour {recette_detectee}! Yallah, suis les étapes! 🍳"
                st.session_state.historique.append({'role': 'assistant', 'content': reponse})
                lire_texte_vocal(reponse)
                st.rerun()
            
            # PRIORITÉ 2: Détecter stress
            elif detecter_stress(user_input):
                recettes_faciles = recettes_anti_stress()
                reponse = f"Je vois que tu es pressé! Voici des recettes rapides: {', '.join(recettes_faciles)}. Laquelle te tente?"
                st.session_state.historique.append({'role': 'assistant', 'content': reponse})
                lire_texte_vocal(reponse)
                st.rerun()
            
            # PRIORITÉ 3: Conversation normale avec Sarah
            else:
                with st.spinner("💭 Sarah réfléchit..."):
                    reponse = demander_sarah(user_input)
                st.session_state.historique.append({'role': 'assistant', 'content': reponse})
                lire_texte_vocal(reponse)
                st.rerun()
    
    # FONCTIONNALITÉS SUPPLÉMENTAIRES
    st.markdown("---")
    
    with st.expander("📸 Scan Frigo (Anti-gaspi)"):
        st.markdown("Prends une photo de ton frigo et je te suggère des recettes!")
        uploaded_file = st.file_uploader("Photo du frigo:", type=['jpg', 'jpeg', 'png'], key="upload_frigo")
        
        if uploaded_file:
            image_bytes = uploaded_file.read()
            st.image(image_bytes, caption="Ta photo", use_container_width=True)
            
            if st.button("🔍 Analyser"):
                with st.spinner("🔍 Analyse en cours..."):
                    ingredients = analyser_photo_frigo(image_bytes)
                
                if ingredients:
                    st.success(f"Ingrédients détectés: {', '.join(ingredients)}")
                    
                    suggestions = suggerer_recettes_ingredients(ingredients)
                    if suggestions:
                        st.markdown("### 🍳 Recettes possibles:")
                        for nom, pourcent, rec in suggestions:
                            st.markdown(f"- **{nom}** ({pourcent:.0f}% des ingrédients)")
                else:
                    st.warning("Je n'ai pas pu identifier d'ingrédients. Essaie avec une meilleure photo!")
    
    with st.expander("🔄 Convertisseur"):
        st.markdown("Convertis tes mesures culinaires!")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            valeur = st.number_input("Valeur:", min_value=0.0, value=100.0, key="conv_val")
        with col2:
            de_unite = st.selectbox("De:", ["g", "ml", "tasse", "cuillere_soupe", "celsius", "oz", "kg", "lb"], key="conv_de")
        with col3:
            vers_unite = st.selectbox("Vers:", ["tasse_farine", "tasse_sucre", "tasse", "ml", "fahrenheit", "g", "lb", "kg"], key="conv_vers")
        
        if st.button("Convertir"):
            resultat = convertir_mesure(valeur, de_unite, vers_unite)
            if resultat:
                st.success(f"✅ {valeur} {de_unite} = **{resultat} {vers_unite}**")
            else:
                st.error("Conversion non disponible pour ces unités")
    
    with st.expander("💡 Suggestions intelligentes"):
        st.markdown("Trouve la recette parfaite selon tes critères!")
        
        col1, col2 = st.columns(2)
        with col1:
            budget_filtre = st.slider("Budget max (€/pers):", 0.5, 5.0, 3.0, 0.5, key="filtre_budget")
            temps_filtre = st.slider("Temps max (min):", 15, 180, 60, 15, key="filtre_temps")
        with col2:
            diff_filtre = st.selectbox("Difficulté:", ["", "Facile", "Moyen", "Difficile"], key="filtre_diff")
            saison_filtre = st.selectbox("Saison:", ["", "Hiver", "Été", "Toute"], key="filtre_saison")
        
        if st.button("🔍 Chercher"):
            suggestions = suggerer_recettes(
                budget_max=budget_filtre,
                temps_max=temps_filtre,
                difficulte=diff_filtre if diff_filtre else None,
                saison=saison_filtre if saison_filtre else None
            )
            
            if suggestions:
                st.markdown("### Recettes suggérées:")
                for nom, rec in suggestions:
                    st.markdown(f"- **{nom}** - {rec['budget_assiette']}€ · {rec['duree_min']}min · {rec['difficulte']}")
            else:
                st.info("Aucune recette ne correspond à ces critères. Essaie d'élargir ta recherche!")

# =============================================================================
# LANCEMENT
# =============================================================================

if __name__ == "__main__":
    main()
