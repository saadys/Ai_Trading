
import asyncio
import asyncpg

async def reset():
    try:
        # Connexion directe à la base
        conn = await asyncpg.connect("postgresql://postgres:saadys@localhost:5432/Ai_Trading")
        # Suppression brutale de la table de version
        await conn.execute("DROP TABLE IF EXISTS alembic_version")
        print("Table alembic_version supprimée !")
        await conn.close()
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    asyncio.run(reset())
