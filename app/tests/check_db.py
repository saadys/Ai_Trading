import asyncio
import sys
import os

# Ajout du path pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.Config import Settings

async def check_database_exists():
    settings = Settings()
    print(f"Checking for database: {settings.Postgres_DBName}...")
    
    # Connexion à 'postgres' (base par défaut toujours présente)
    root_url = f"postgresql+asyncpg://{settings.Postgres_User}:{settings.Postgres_Password}@{settings.Postgres_Host}:{settings.Postgres_Port}/postgres"
    
    try:
        engine = create_async_engine(root_url)
        async with engine.connect() as conn:
            # Requete simple pour lister les bases
            query = text("SELECT 1 FROM pg_database WHERE datname = :dbname")
            result = await conn.execute(query, {"dbname": settings.Postgres_DBName})
            exists = result.scalar() is not None
            
            if exists:
                print(f"\n✅ SUCCESS: The database '{settings.Postgres_DBName}' EXISTS!")
            else:
                print(f"\n❌ FAILURE: The database '{settings.Postgres_DBName}' does NOT exist.")
                
        await engine.dispose()
        
    except Exception as e:
        print(f"\n⚠️ CONNECTION ERROR: Could not connect to Postgres.\nError: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_database_exists())
