"""
🍽️ SARAH'MIAM - Assistant Culinaire Bi-culturel France-Maroc
Version: 2.0 COMPLÈTE
Auteur: Abdel
Date: 26 Décembre 2025

FONCTIONNALITÉS:
- 40 recettes ultra-détaillées (20 FR + 20 MA)
- Génération IA illimitée via Groq
- Budget strict par assiette
- Anti-gaspi via photo frigo
- Transmission culturelle
- Détection stress vocal
- Suggestions météo
- Code-switching FR/Darija naturel
"""

# Charger .env automatiquement
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import streamlit as st
import os
from groq import Groq
from datetime import datetime
import hashlib
from audio_recorder_streamlit import audio_recorder
import tempfile
import requests

# =============================================================================
# CONFIGURATION GROQ API
# =============================================================================

# Lire depuis Streamlit secrets
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    OPENWEATHER_API_KEY = st.secrets.get("OPENWEATHER_API_KEY", "")
except:
    st.error("⚠️ GROQ_API_KEY manquant! Crée le fichier .streamlit/secrets.toml")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# =============================================================================
# CONSTANTES
# =============================================================================

BUDGET_MAX_PAR_ASSIETTE = 3.0  # euros

# Dictionnaire Darija
DICTIONNAIRE_DARIJA = {
    "tomate": "matecha", "oignon": "besla", "carotte": "khizou",
    "pomme de terre": "batata", "poulet": "djaj", "viande": "l7em",
    "poisson": "hout", "agneau": "ghanem", "cumin": "kamoun",
    "cannelle": "karfa", "safran": "zafran", "gingembre": "skinjbir",
    "farine": "dqiq", "huile": "zit", "sel": "mel7a", "poivre": "ibzar"
}

EXPRESSIONS_DARIJA = {
    "bienvenue": "Marhaba bik !", "bon_appetit": "Bsaha !",
    "delicieux": "Benin bezzaf !", "commence": "Yallah, nwellou !",
    "regarde": "Chouf !", "facile": "Sahel !", "excellent": "Mezyan bezzaf !"
}

# Prix enseignes pour comparateur
PRIX_ENSEIGNES = {
    "Lidl": {"poulet_kg": 4.80, "boeuf_kg": 11.20, "tomates_kg": 2.10, "oignons_kg": 0.95},
    "Aldi": {"poulet_kg": 4.90, "boeuf_kg": 11.50, "tomates_kg": 2.20, "oignons_kg": 0.99},
    "Leclerc": {"poulet_kg": 5.50, "boeuf_kg": 12.90, "tomates_kg": 2.80, "oignons_kg": 1.20},
    "Auchan": {"poulet_kg": 5.80, "boeuf_kg": 12.80, "tomates_kg": 2.90, "oignons_kg": 1.30},
    "Carrefour": {"poulet_kg": 6.20, "boeuf_kg": 13.50, "tomates_kg": 3.10, "oignons_kg": 1.50}
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
    }
}

# =============================================================================
# PRIX DES PRODUITS (Prix moyens France 2025)
# =============================================================================

PRIX_INGREDIENTS = {
    # Viandes
    "viande_mouton_kg": 12.50,
    "viande_hachee_kg": 8.90,
    "poulet_kg": 6.50,
    "merguez_kg": 9.50,
    "dinde_kg": 7.80,
    "veau_kg": 18.00,
    "boeuf_kg": 15.00,
    "lardons_kg": 10.00,
    "jambon_kg": 12.00,
    "chair_saucisse_kg": 8.50,
    "pigeon_ou_poulet_kg": 8.00,
    
    # Poissons
    "thon_kg": 20.00,
    "anchois_kg": 35.00,
    "poisson_blanc_kg": 16.00,
    
    # Légumes
    "tomates_kg": 2.80,
    "oignon_kg": 1.50,
    "carotte_kg": 1.20,
    "courgette_kg": 2.50,
    "aubergine_kg": 3.00,
    "poivron_kg": 4.00,
    "pomme_terre_kg": 1.30,
    "legumes_kg": 2.50,
    "navet_kg": 1.80,
    "poireau_kg": 2.20,
    "celeri_kg": 2.00,
    "champignon_kg": 7.00,
    "oignon_grelot_kg": 3.50,
    
    # Légumineuses
    "lentilles_kg": 3.50,
    "pois_chiches_kg": 3.20,
    "feves_seches_kg": 4.00,
    
    # Céréales
    "farine_kg": 1.20,
    "semoule_couscous_kg": 2.00,
    "semoule_fine_kg": 1.80,
    "vermicelles_kg": 2.50,
    "pain_mie_kg": 2.50,
    "pate_brisee_kg": 3.50,
    "feuilles_brick_kg": 8.00,
    "msemmen_ou_crepes_kg": 5.00,
    
    # Herbes et aromates
    "coriandre_kg": 8.00,
    "persil_kg": 8.00,
    "ail_kg": 6.00,
    "thym_kg": 20.00,
    "herbes_kg": 15.00,
    "fines_herbes_kg": 20.00,
    
    # Produits laitiers
    "creme_kg": 5.00,
    "lait_kg": 1.10,
    "beurre_kg": 10.00,
    "smen_beurre_kg": 15.00,
    "fromage_rape_kg": 12.00,
    "gruyere_kg": 14.00,
    "jaune_oeuf_kg": 8.00,
    "oeuf_kg": 3.50,
    "oeuf_dur_kg": 3.50,
    
    # Fruits
    "citron_kg": 3.50,
    "citron_confit_kg": 12.00,
    "citron_frais_kg": 3.50,
    "marron_kg": 18.00,
    
    # Autres
    "olives_kg": 8.00,
    "olive_kg": 8.00,
    "huile_olive_kg": 8.00,
    "huile_kg": 5.00,
    "huile_friture_kg": 4.00,
    "sucre_kg": 1.50,
    "miel_kg": 15.00,
    "chocolat_kg": 12.00,
    "cacao_kg": 8.00,
    "amandes_kg": 18.00,
    "sesame_kg": 10.00,
    "raisins_secs_kg": 8.00,
    "cannelle_kg": 25.00,
    "muscade_kg": 30.00,
    "cumin_kg": 15.00,
    "paprika_kg": 12.00,
    "fenugrec_kg": 10.00,
    "levure_kg": 8.00,
    "sel_kg": 1.00,
    "vin_rouge_kg": 8.00,
    "eau_fleur_oranger_kg": 12.00,
    "os_moelle_kg": 5.00
}

# =============================================================================
# FONCTIONS AUDIO, MÉTÉO, COMPARATEUR, MODE CUISINE
# =============================================================================

def obtenir_meteo():
    """Récupère météo OpenWeather pour la ville de l'utilisateur"""
    if not OPENWEATHER_API_KEY:
        return None
    
    ville = st.session_state.ville_utilisateur
    if not ville:
        return None
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={ville}&appid={OPENWEATHER_API_KEY}&units=metric&lang=fr"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'temp': round(data['main']['temp'], 1),
                'description': data['weather'][0]['description'],
                'ville': ville
            }
        else:
            return None
    except Exception as e:
        return None

def transcribe_audio_whisper(audio_bytes):
    """Transcription Whisper Groq"""
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
    """Synthèse vocale - VERSION STABLE SIMPLE"""
    if not texte or len(texte) < 3:
        return
    
    # Nettoyer le texte
    texte_clean = texte.replace("'", " ").replace('"', ' ').replace('\n', ' ').strip()
    texte_clean = texte_clean[:300]  # Max 300 caractères
    
    # ID unique
    unique_id = abs(hash(texte_clean + str(datetime.now().timestamp()))) % 100000
    
    html = f"""
    <div id="speech-{unique_id}"></div>
    <script>
    (function() {{
        // RESET COMPLET
        if (window.speechSynthesis) {{
            window.speechSynthesis.cancel();
        }}
        
        // Attendre que tout soit propre
        setTimeout(function() {{
            try {{
                const text = `{texte_clean}`;
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'fr-FR';
                utterance.rate = 0.9;
                utterance.pitch = 1.0;
                utterance.volume = 1.0;
                
                // Parler
                window.speechSynthesis.speak(utterance);
            }} catch(e) {{
                console.log('Audio:', e);
            }}
        }}, 500);
    }})();
    </script>
    """
    st.components.v1.html(html, height=0)

def detecter_ville(user_input):
    """Détecte si l'utilisateur mentionne sa ville"""
    villes_france = ["Paris", "Lyon", "Marseille", "Toulouse", "Nice", "Nantes", "Strasbourg",
                     "Montpellier", "Bordeaux", "Lille", "Rennes", "Reims", "Le Havre",
                     "Clermont-Ferrand", "Gerzat", "Aubière", "Beaumont", "Cournon"]
    
    user_lower = user_input.lower()
    
    if "j'habite" in user_lower or "je vis" in user_lower or "je suis de" in user_lower or "je suis à" in user_lower:
        for ville in villes_france:
            if ville.lower() in user_lower:
                st.session_state.ville_utilisateur = ville
                return ville
    
    return None

def comparer_prix(ingredients):
    """Compare prix entre enseignes"""
    comparaison = {}
    details = {}
    for enseigne, prix in PRIX_ENSEIGNES.items():
        total = sum(prix.get(i, 0) * q for i, q in ingredients.items())
        comparaison[enseigne] = round(total, 2)
        details[enseigne] = {ing: round(prix.get(ing, 0) * q, 2) for ing, q in ingredients.items()}
    return dict(sorted(comparaison.items(), key=lambda x: x[1])), details

def obtenir_ville_via_ip():
    """Géolocalisation automatique via IP - API gratuite ipapi.co"""
    try:
        response = requests.get('https://ipapi.co/json/', timeout=3)
        if response.status_code == 200:
            data = response.json()
            ville = data.get('city', '')
            pays = data.get('country_name', '')
            
            if ville:
                return ville
    except:
        pass
    
    return "France"

def reverse_geocoding(lat, lon):
    """Convertir lat/lon en ville avec Nominatim (gratuit)"""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        headers = {'User-Agent': 'SarahMiam/1.0'}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})
            
            # Essayer différents niveaux
            ville = (address.get('city') or 
                    address.get('town') or 
                    address.get('village') or 
                    address.get('municipality') or
                    address.get('county') or
                    'France')
            
            return ville
    except Exception as e:
        return None
    
    return None

def afficher_etape_cuisine():
    """Affiche mode cuisine vocal avec étapes détaillées"""
    if st.session_state.recette_en_cours and st.session_state.mode_cuisine:
        recette = RECETTES_DETAILLEES.get(st.session_state.recette_en_cours)
        if not recette:
            return
            
        etapes = recette['etapes']
        etape_actuelle = st.session_state.etape_cuisine
        
        if etape_actuelle < len(etapes):
            etape = etapes[etape_actuelle]
            st.markdown(f"""
            <div class="etape-box">
                <h2>🍳 ÉTAPE {etape_actuelle + 1} / {len(etapes)}</h2>
                <h3>{etape['titre']}</h3>
                <p style="font-size: 22px; margin-top: 20px;">{etape['description']}</p>
                <p style="font-size: 18px; margin-top: 15px;">🌡️ {etape['temperature']} - ⏱️ {etape['duree']}</p>
                <p style="font-size: 16px; font-style: italic; margin-top: 10px;">💡 {etape['astuce']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if etape_actuelle == 0:
                lire_texte_vocal(f"Étape {etape_actuelle + 1}: {etape['description']}")
        else:
            msg_fin = "Bsaha ! Ton plat est prêt ! Bon appétit ! 🎉"
            if "darija" in recette and recette['darija']:
                msg_fin = "Bsaha ! " + recette['darija']
            st.success(msg_fin)
            lire_texte_vocal(msg_fin)
            st.session_state.mode_cuisine = False


# =============================================================================
# CSS PERSONNALISÉ
# =============================================================================

st.markdown("""
<style>
    /* Fond général */
    .main {
        background: linear-gradient(135deg, #FFF8E7 0%, #FFE4B5 100%);
    }
    
    /* Titre principal */
    h1 {
        color: #FF6B35;
        text-align: center;
        font-size: 3.5em !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 30px;
        font-family: 'Arial Black', sans-serif;
    }
    
    /* Boutons */
    .stButton>button {
        background: linear-gradient(135deg, #FF6B35 0%, #FF8C42 100%);
        color: white;
        font-size: 22px;
        padding: 18px 35px;
        border-radius: 15px;
        border: none;
        width: 100%;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(255,107,53,0.3);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #FF8C42 0%, #FFA366 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255,107,53,0.4);
    }
    
    /* Cartes de recettes */
    .recette-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 15px 0;
        border-left: 5px solid #FF6B35;
    }
    
    /* Messages */
    .stChatMessage {
        border-radius: 15px;
        margin: 10px 0;
    }
    
    /* Boîte étapes cuisine */
    .etape-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        font-size: 24px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# INITIALISATION SESSION STATE
# =============================================================================

if 'profil' not in st.session_state:
    st.session_state.profil = {
        'nom': 'Utilisateur',  # Nom par défaut
        'situation': '',
        'ville': '',
        'preferences': []
    }

if 'historique' not in st.session_state:
    st.session_state.historique = []

if 'recette_en_cours' not in st.session_state:
    st.session_state.recette_en_cours = None

if 'mode_cuisine' not in st.session_state:
    st.session_state.mode_cuisine = False

if 'etape_cuisine' not in st.session_state:
    st.session_state.etape_cuisine = 0

if 'last_audio_hash' not in st.session_state:
    st.session_state.last_audio_hash = None

if 'ville_utilisateur' not in st.session_state:
    # Géolocalisation IP automatique au premier lancement
    ville_auto = obtenir_ville_via_ip()
    st.session_state.ville_utilisateur = ville_auto
    st.session_state.profil['ville'] = ville_auto

if 'bienvenue_jouee' not in st.session_state:
    st.session_state.bienvenue_jouee = False

if 'app_initialisee' not in st.session_state:
    st.session_state.app_initialisee = True

# =============================================================================
# FONCTIONS GROQ
# =============================================================================

def demander_sarah(user_input, contexte="conversation"):
    """Appelle Groq - TON ULTRA-PROFESSIONNEL STRICT"""
    
    meteo = obtenir_meteo()
    
    profil_text = ""
    if st.session_state.profil['nom']:
        profil_text = f"""
PROFIL:
- Prénom: {st.session_state.profil['nom']}
- Situation: {st.session_state.profil.get('situation', '')}
- Ville: {st.session_state.ville_utilisateur}
"""
    
    if contexte == "profil":
        system_prompt = f"""Tu es Sarah, assistante culinaire PROFESSIONNELLE.

TON STRICTEMENT PROFESSIONNEL:
- Utilise UNIQUEMENT le prénom donné
- JAMAIS de surnom (INTERDIT: "chéri", "BOBO", "ma belle", "mon cœur")
- Tutoiement simple et direct
- Réponses COURTES (2-3 phrases MAX)

{profil_text}

RÈGLE ABSOLUE: Réponds de manière professionnelle et concise."""

    else:
        system_prompt = f"""Tu es Sarah, assistante culinaire PROFESSIONNELLE bi-culturelle France-Maroc.

TON ULTRA-PROFESSIONNEL ET STRICT:
1. Utilise UNIQUEMENT le prénom de l'utilisateur
2. INTERDICTIONS ABSOLUES:
   - Surnoms affectifs ("chéri", "mon cœur", "BOBO", "ma belle")
   - Expressions bizarres ("fourchettes et couteaux", "étincelle")  
   - Familiarité excessive
3. Tutoiement professionnel simple
4. Réponses CONCISES (3-4 phrases MAX)
5. Emoji OK mais avec modération: 🍽️ 🥘 💚

DARIJA:
- Pour recettes marocaines uniquement
- Expressions simples et naturelles
- Pas de traduction systématique

{profil_text}

EXEMPLES CORRECTS:
User: "Bonjour"
Sarah: "Salut ! Comment je peux t'aider aujourd'hui ?"

User: "Je veux faire une harira"
Sarah: "Super ! La harira c'est parfait pour l'hiver. Je te guide étape par étape ?"

EXEMPLES INTERDITS:
❌ "Salut mon chéri !"
❌ "Bonjour BOBO !"
❌ "Coucou ma belle !"
❌ "Fourchettes et couteaux étincelle !"

Réponds de manière professionnelle, chaleureuse mais sobre."""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.6,
            max_tokens=250
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erreur technique... 😅"

def generer_recette_ia(description):
    """Génère une recette complète via Groq"""
    
    system_prompt = """Tu es un chef cuisinier expert bi-culturel France-Maroc.

Génère une recette COMPLÈTE au format JSON avec cette structure EXACTE:

{
  "nom": "Nom de la recette",
  "pays": "🇫🇷 France" ou "🇲🇦 Maroc",
  "categorie": "Plat principal/Dessert/Entrée/etc",
  "budget_assiette": 2.50,
  "duree_min": 60,
  "difficulte": "Facile/Moyen/Difficile",
  "saison": "Hiver/Été/Toute",
  "darija": "Si marocain: traduction/expression en darija",
  "ingredients": {
    "ingredient1_kg": 0.5,
    "ingredient2_kg": 0.3
  },
  "etapes": [
    {
      "num": 1,
      "titre": "🔥 Titre étape",
      "description": "Description détaillée",
      "temperature": "Feu vif/Four 180°C/etc",
      "duree": "15 minutes",
      "astuce": "Conseil pratique"
    }
  ],
  "anecdote": "Histoire ou anecdote culturelle"
}

IMPORTANT:
- Minimum 5 étapes détaillées
- Températures et durées précises
- Une astuce par étape
- Budget réaliste
- Si marocain: ajoute expressions darija"""
def get_professional_css():
    """CSS Design Professionnel - Couleurs chaudes cuisine"""
    return """
    <style>
    /* RESET & BASE */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* GRADIENTS CHAUDS */
    .gradient-header {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 50%, #FFC837 100%);
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 10px 40px rgba(255, 107, 53, 0.3);
    }
    
    /* CARDS MODERNES */
    .card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(255, 107, 53, 0.2);
    }
    
    /* MÉTÉO CARD */
    .weather-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
    
    .weather-desc {
        font-size: 18px;
        opacity: 0.9;
    }
    
    /* SARAH AVATAR & MESSAGE */
    .sarah-welcome {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(240, 147, 251, 0.3);
        position: relative;
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
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    
    .sarah-message {
        font-size: 24px;
        font-weight: 500;
        text-align: center;
        line-height: 1.5;
    }
    
    /* RECETTES CARDS */
    .recette-card {
        background: white;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .recette-card:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 30px rgba(255, 107, 53, 0.3);
    }
    
    .recette-image {
        width: 100%;
        height: 200px;
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 60px;
    }
    
    .recette-content {
        padding: 20px;
    }
    
    .recette-title {
        font-size: 20px;
        font-weight: bold;
        color: #FF6B35;
        margin-bottom: 10px;
    }
    
    .recette-info {
        display: flex;
        gap: 15px;
        font-size: 14px;
        color: #666;
    }
    
    /* MICRO PROFESSIONNEL */
    .micro-container {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(255, 107, 53, 0.3);
        position: sticky;
        bottom: 20px;
        margin-top: 30px;
    }
    
    .micro-title {
        color: white;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    
    /* COMPARATEUR */
    .comparateur-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 8px 25px rgba(17, 153, 142, 0.3);
    }
    
    .prix-badge {
        background: white;
        color: #11998e;
        padding: 8px 15px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 5px;
    }
    
    /* GPS BUTTON */
    .gps-button {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 15px 30px;
        border-radius: 30px;
        text-decoration: none;
        font-size: 18px;
        font-weight: bold;
        display: inline-block;
        box-shadow: 0 8px 20px rgba(240, 147, 251, 0.4);
        transition: all 0.3s ease;
    }
    
    .gps-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(240, 147, 251, 0.5);
    }
    
    /* ANIMATIONS */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .animate-slide {
        animation: slideIn 0.5s ease-out;
    }
    
    /* CHAT MESSAGES */
    .message-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 20px 20px 5px 20px;
        margin: 10px 0;
        max-width: 80%;
        float: right;
        clear: both;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    .message-assistant {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px 0;
        max-width: 80%;
        float: left;
        clear: both;
        box-shadow: 0 5px 15px rgba(255, 107, 53, 0.3);
    }
    
    /* RESPONSIF */
    @media (max-width: 768px) {
        .weather-temp {
            font-size: 36px;
        }
        .sarah-message {
            font-size: 20px;
        }
        .recette-image {
            height: 150px;
        }
    }
    </style>
    """


def main():
    # Config page
    st.set_page_config(
        page_title="Sarah'Miam - Chef Personnel",
        page_icon="🍽️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS Professionnel
    css = get_professional_css()
    st.markdown(css, unsafe_allow_html=True)
    
    # HEADER GRADIENT
    st.markdown("""
    <div class="gradient-header">
        <h1 style="color: white; text-align: center; font-size: 48px; margin: 0;">
            🍽️ SARAH'MIAM
        </h1>
        <p style="color: white; text-align: center; font-size: 20px; margin-top: 10px; opacity: 0.9;">
            Ton chef personnel France-Maroc 🇫🇷 🇲🇦
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # GÉOLOCALISATION + MÉTÉO
    ville = st.session_state.ville_utilisateur or "France"
    meteo = obtenir_meteo()
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if meteo:
            st.markdown(f"""
            <div class="weather-card animate-slide">
                <div style="font-size: 20px; font-weight: bold;">📍 {meteo['ville']}</div>
                <div class="weather-temp">{meteo['temp']}°C</div>
                <div class="weather-desc">{meteo['description']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="weather-card animate-slide">
                <div style="font-size: 20px; font-weight: bold;">📍 {ville}</div>
                <div style="font-size: 16px; margin-top: 10px;">Bienvenue !</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        now = datetime.now()
        st.markdown(f"""
        <div class="card animate-slide">
            <div style="text-align: center;">
                <div style="font-size: 24px; color: #FF6B35; font-weight: bold;">
                    📅 {now.strftime('%d %B %Y')}
                </div>
                <div style="font-size: 20px; color: #666; margin-top: 5px;">
                    ⏰ {now.strftime('%H:%M')}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Bouton changer ville
        if st.button("📍 Ville", use_container_width=True):
            st.session_state.show_ville = not st.session_state.get('show_ville', False)
    
    if st.session_state.get('show_ville', False):
        nv = st.text_input("Ta ville:", key="change_ville_pro")
        if st.button("✅ OK") and nv:
            st.session_state.ville_utilisateur = nv
            st.session_state.profil['ville'] = nv
            st.session_state.show_ville = False
            st.rerun()
    
    # BIENVENUE SARAH (si premier message)
    if len(st.session_state.historique) == 0:
        msg_bienvenue = "Marhaba ! Je suis Sarah, ton chef personnel France-Maroc ! Qu'est-ce qui te ferait plaisir aujourd'hui ?"
        
        st.markdown(f"""
        <div class="sarah-welcome animate-slide">
            <div class="sarah-avatar">👩‍🍳</div>
            <div class="sarah-message">{msg_bienvenue}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Vocal bienvenue UNE SEULE FOIS
        if not st.session_state.get('bienvenue_jouee', False):
            lire_texte_vocal(msg_bienvenue)
            st.session_state.bienvenue_jouee = True
    
    # SIDEBAR
    with st.sidebar:
        st.markdown("### 👤 Profil")
        nom = st.text_input("Prénom:", value=st.session_state.profil.get('nom', 'Utilisateur'), key="prof_nom")
        if nom != st.session_state.profil.get('nom'):
            st.session_state.profil['nom'] = nom
        
        st.markdown("---")
        st.markdown("### 🛒 Comparateur Prix")
        
        rec_comp = st.selectbox("Recette:", [""] + list(RECETTES_DETAILLEES.keys())[:10], key="comp_rec")
        
        if rec_comp and st.button("💰 Comparer", key="btn_comp"):
            rec = RECETTES_DETAILLEES[rec_comp]
            comp, _ = comparer_prix(rec['ingredients'])
            
            meilleur = list(comp.keys())[0]
            
            st.markdown(f"""
            <div class="comparateur-card">
                <div style="font-size: 20px; font-weight: bold; margin-bottom: 15px;">
                    🏆 Meilleur prix: {meilleur}
                </div>
                <div class="prix-badge">{comp[meilleur]}€</div>
            </div>
            """, unsafe_allow_html=True)
            
            for ens, px in comp.items():
                st.write(f"• {ens}: {px}€")
            
            if ville and meilleur in LIENS_ENSEIGNES:
                lien = LIENS_ENSEIGNES[meilleur]['gps'].format(ville=ville)
                st.markdown(f"""
                <a href="{lien}" target="_blank" class="gps-button">
                    🚗 Y ALLER À {ville.upper()}
                </a>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 📖 Recettes Populaires")
        
        # Top 6 recettes avec cards
        for nom, rec in list(RECETTES_DETAILLEES.items())[:6]:
            with st.expander(f"{rec['pays']} {nom}"):
                st.write(f"💰 {rec['budget_assiette']}€ · ⏱️ {rec['duree_min']}min")
                if st.button("🍳 Cuisiner", key=f"cook_{nom}"):
                    st.session_state.recette_en_cours = nom
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
            <p style="text-align: center; color: #666;">{rec['pays']} · {rec['categorie']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Préc") and st.session_state.etape_cuisine > 0:
                st.session_state.etape_cuisine -= 1
                st.rerun()
        with col2:
            st.markdown(f"<div style='text-align: center; font-size: 18px; font-weight: bold;'>Étape {st.session_state.etape_cuisine + 1}/{len(rec['etapes'])}</div>", unsafe_allow_html=True)
        with col3:
            if st.session_state.etape_cuisine < len(rec['etapes']) - 1:
                if st.button("Suiv ➡️"):
                    st.session_state.etape_cuisine += 1
                    st.rerun()
            else:
                if st.button("✅ Fini"):
                    st.session_state.mode_cuisine = False
                    st.balloons()
                    st.rerun()
        
        afficher_etape_cuisine()
    
    # CONVERSATION
    else:
        # Historique messages
        for entry in st.session_state.historique[-10:]:
            role_class = "message-user" if entry['role'] == 'user' else "message-assistant"
            st.markdown(f"""
            <div class="{role_class}">
                {entry['content']}
            </div>
            <div style="clear: both;"></div>
            """, unsafe_allow_html=True)
    
    # MICRO CONTAINER FIXE
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
            key="audio_pro"
        )
        
        audio_hash = hash(audio_bytes) if audio_bytes else None
        
        if audio_bytes and audio_hash != st.session_state.last_audio_hash:
            st.session_state.last_audio_hash = audio_hash
            
            with st.spinner("🎤"):
                text_audio = transcribe_audio_whisper(audio_bytes)
            
            if text_audio and len(text_audio) > 2:
                st.session_state.historique.append({'role': 'user', 'content': text_audio})
                
                with st.spinner("💭"):
                    reponse = demander_sarah(text_audio)
                
                st.session_state.historique.append({'role': 'assistant', 'content': reponse})
                lire_texte_vocal(reponse)
                st.rerun()
    
    with col_txt:
        user_input = st.chat_input("Écris ta question...", key="chat_pro")
        
        if user_input:
            st.session_state.historique.append({'role': 'user', 'content': user_input})
            
            with st.spinner("💭"):
                reponse = demander_sarah(user_input)
            
            st.session_state.historique.append({'role': 'assistant', 'content': reponse})
            lire_texte_vocal(reponse)
            st.rerun()

if __name__ == "__main__":
    main()
