# Ai_Trading

Est une application d’analyse et d’exécution de stratégies de trading utilisant un pipeline complet de données de marché, des modèles de machine learning, des indicateurs techniques et un module d’aide à la décision basé sur LLM. Le projet suit une architecture propre et modulaire pour garantir une séparation claire entre la collecte des données, l’analyse, la prédiction et le trading.

## Exigences

### Installer Python en utilisant Miniconda

1. Téléchargez et installez Miniconda depuis :  
   https://www.anaconda.com/docs/getting-started/miniconda/install#macos-linux-installation

2. Créez un nouvel environnement :

   ```bash
   conda create -n Robot-Trading python=3.11
   ```

3. Activez l'environnement :
   ```bash
   conda activate Robot-Trading
   ```

_(Optionnel)_ Personnalisez votre terminal pour une meilleure lisibilité :

```bash
export PS1="\[\033[01;32m\][\u@\h:\w]\[\033[00m\]\n\$ "
```

## How It's Made:

**Tech used:** Python, Docker, Postgres,SQlAlchemy

## Configuration

### Pré-requis Système

- **PostgreSQL** : Doit être installé et le service démarré.
- **RabbitMQ** : Doit être installé et le service démarré (avec le plugin Management activé de préférence).
- **TA-Lib** : Librairie C nécessaire pour les indicateurs techniques.
  - _Windows_ : Télécharger le `.whl` compatible ou installer via `conda install -c conda-forge ta-lib` avant pip.
  - _Linux_ : `sudo apt-get install libta-lib0` (ou compiler depuis les sources).

### Configuration de la Base de Données

1.  Créer la base de données PostgreSQL :
    ```sql
    CREATE DATABASE "Ai_Trading";
    ```
2.  Appliquer les migrations (création des tables) via Alembic :
    ```bash
    alembic upgrade head
    ```

### Configuration des Outils de Téléchargement (Env Vars)

L'application utilise des variables d'environnement pour se connecter aux APIs externes (Binance pour le marché, NewsData pour les infos).

Créez un fichier `.env` à la racine `Ai_Trading/` :

```env
# --- Base de Données ---
POSTGRES_USER=postgres
POSTGRES_PASSWORD=votre_mot_de_passe
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DBNAME=Ai_Trading

# --- Broker ---
RABBITMQ_DEFAULT_USER=guest
RABBITMQ_DEFAULT_PASS=guest
RABBITMQ_DEFAULT_VHOST=/

# --- APIs de Téléchargement ---

# 1. Binance (Données de Marché)
# Clés API pour le trading ou les données privées (optionnel pour les données publiques)
BINANCE_API_KEY=votre_cle_binance
BINANCE_SECRET_KEY=votre_secret_binance

# 2. NewsData.io (Données d'Actualités/Sentiment)
# Nécessaire pour le NewsCollector
NEWSDATA_API_KEY=votre_cle_newsdata
```

> **Note** : Les scripts de collecte (`MarketDataCollector`, `NewsCollector`) sont conçus pour tourner en tâche de fond ou être instanciés par `main.py`. Assurez-vous d'avoir les crédits API nécessaires.

## Lancement

1. Installer les dependances :

   ```bash
   pip install -r requirements.txt
   ```

2. Lancer l'application :
   ```bash
   uvicorn main:app --reload
   ```

## Utilisation de la Base de Données

Le projet utilise **PostgreSQL** comme base de données principale (nommée `Ai_Trading`).
L'ORM SQLAlchemy est utilisé en conjonction avec **Alembic** pour la gestion des schémas (migrations).

- **Connexion locale** : Vous pouvez vous connecter à la base de données via n'importe quel client SQL (comme DBeaver, pgAdmin, ou DataGrip) en utilisant les identifiants fournis dans votre fichier `.env` (par défaut : utilisateur `postgres` sur `localhost:5432`).
- **Tables principales** : La base stocke les données historiques (OHLCV), les indicateurs techniques pré-calculés, l'historique des prédictions des modèles ML ainsi que l'historique des décisions de trading prises par le LLM.

## Utilisation des APIs (FastAPI)

L'application expose plusieurs endpoints RESTful. Une fois l'application lancée via `uvicorn`, vous pouvez tester toutes les routes directement depuis l'interface interactive générée automatiquement :
👉 **Swagger UI** : [http://localhost:8000/docs](http://localhost:8000/docs)
👉 **ReDoc** : [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Principales routes disponibles :

#### 🔄 Streaming & Ingestion (WebSockets)

Gère le flux de données en direct depuis l'exchange (ex: Binance).

- `POST /streaming/start` : Lance l'acquisition continue des données du marché en temps réel.
- `POST /streaming/stop` : Arrête proprement le flux de données.
- `GET /streaming/status` : Retourne l'état actuel du processus de streaming.

#### 🧠 Décision LLM

Gère l'interface avec l'Intelligence Artificielle générative pour le trading.

- `GET /llm/context` : Récupère le snapshot complet du contexte actuel (Prix actuels, Indicateurs RSI/MACD/etc., Sentiment actuel des actualités, et les dernières prédictions). C'est ce contexte qui est envoyé à l'IA.
- `POST /llm/provider/{provider_name}` : Permet de basculer à chaud entre différents modèles LLM (ex: Gemini, OpenAI) pour la prise de décision.

#### 📈 Prédiction Machine Learning (LSTM)

Gère l'inférence via les modèles de Deep Learning.

- `POST /api/v1/lstm/predict` : Permet d'envoyer un vecteur de features temporelles (séquence) au modèle LSTM pour obtenir une prédiction sur la trajectoire future des prix.
