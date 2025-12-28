# 🍽️ Sarah'Miam - Assistant Culinaire Bi-culturel

**Ton chef personnel France-Maroc** 🇫🇷 🇲🇦

## ✨ Fonctionnalités

- 🍲 **40 recettes détaillées** (20 françaises + 20 marocaines)
- 🤖 **IA conversationnelle** avec Groq (Llama 3.3)
- 🎤 **Commande vocale** main-libre
- 📍 **Géolocalisation** automatique
- 🌤️ **Météo** avec suggestions contextuelles
- ⚠️ **Gestion allergies** automatique
- 👨‍👩‍👧‍👦 **Mode groupe** (multiplication portions)
- 📸 **Scan frigo** (reconnaissance ingrédients)
- ⏱️ **Timer cuisine** intégré
- 💰 **Comparateur prix** 5 enseignes
- 🗣️ **Code-switching** Français/Darija naturel

## 🚀 Installation

### Prérequis
- Python 3.8+
- Compte [Groq](https://console.groq.com) (gratuit)
- Compte [OpenWeather](https://openweathermap.org/api) (gratuit)

### En local

```bash
# Cloner le repo
git clone https://github.com/ton-username/sarahmiam.git
cd sarahmiam

# Installer les dépendances
pip install -r requirements.txt

# Créer le fichier secrets
mkdir -p .streamlit
echo 'GROQ_API_KEY = "ta_clé_groq"' > .streamlit/secrets.toml
echo 'OPENWEATHER_API_KEY = "ta_clé_meteo"' >> .streamlit/secrets.toml

# Lancer l'app
streamlit run app.py
```

### Sur Streamlit Cloud

1. Fork ce repo
2. Va sur [share.streamlit.io](https://share.streamlit.io)
3. Connecte ton GitHub
4. Déploie l'app
5. **Configure les Secrets** dans Settings :
   ```toml
   GROQ_API_KEY = "ta_clé_groq"
   OPENWEATHER_API_KEY = "ta_clé_meteo"
   ```

## 📱 Installation sur téléphone

1. Ouvre l'app dans Chrome/Safari
2. Menu ⋮ → "Ajouter à l'écran d'accueil"
3. L'app s'installera sous le nom **"Sarah'Miam"**

## 🔐 Sécurité

⚠️ **NE JAMAIS commit les secrets sur GitHub !**

Les clés API doivent être configurées :
- **En local** : dans `.streamlit/secrets.toml` (fichier ignoré par git)
- **Sur Streamlit Cloud** : dans Settings → Secrets

## 📁 Structure

```
SarahMiam/
├── app.py                  # Application principale
├── requirements.txt        # Dépendances Python
├── .streamlit/
│   └── config.toml        # Configuration thème (PAS de secrets ici!)
├── .gitignore             # Fichiers à ignorer
└── README.md              # Ce fichier
```

## 🛠️ Technologies

- **Frontend** : Streamlit
- **IA** : Groq (Llama 3.3, Whisper)
- **Météo** : OpenWeather API
- **Vocal** : Web Speech API

## 👨‍💻 Auteur

Développé par **Abdel** avec ❤️

## 📄 Licence

MIT License - Libre d'utilisation
