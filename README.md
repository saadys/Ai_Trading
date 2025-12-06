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

*(Optionnel)* Personnalisez votre terminal pour une meilleure lisibilité : 

```bash
export PS1="\[\033[01;32m\][\u@\h:\w]\[\033[00m\]\n\$ "
```
## How It's Made:

**Tech used:** Python, Docker, Postgres,SQlAlchemy

## Configuration

### Services Requis
Le projet necessite RabbitMQ et PostgreSQL. Assurez-vous qu'ils sont installés et en cours d'execution.

### Variables d'Environnement
Creez un fichier .env a la racine du projet avec les informations suivantes:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/trading_db
RABBITMQ_URL=amqp://guest:guest@localhost/
BINANCE_API_KEY=votre_cle
BINANCE_SECRET_KEY=votre_secret
```

## Lancement

1. Installer les dependances :
   ```bash
   pip install -r requirements.txt
   ```

2. Lancer l'application :
   ```bash
   uvicorn main:app --reload
   ```