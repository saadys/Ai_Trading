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
