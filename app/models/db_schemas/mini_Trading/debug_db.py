
import asyncio
import asyncpg

async def check_db():
    # URL matches alembic.ini: postgresql+asyncpg://postgres:saadys@localhost:5432/Ai_Trading
    # asyncpg uses slightly different format for connect
    dsn = "postgresql://postgres:saadys@localhost:5432/Ai_Trading"
    
    print(f"Connecting to {dsn}...")
    try:
        conn = await asyncpg.connect(dsn)
        print("Connected successfully.")
        
        # Check if table exists
        exists = await conn.fetchval("""
            SELECT EXISTS (
               SELECT FROM information_schema.tables 
               WHERE  table_schema = 'public'
               AND    table_name   = 'alembic_version'
            );
        """)
        
        if exists:
            print("Table 'alembic_version' FOUND.")
            version = await conn.fetchval("SELECT version_num FROM alembic_version")
            print(f"Current version in DB: {version}")
            
            print("Dropping table 'alembic_version'...")
            await conn.execute("DROP TABLE alembic_version")
            print("Table dropped.")
        else:
            print("Table 'alembic_version' NOT FOUND. The database appears clean.")
            
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_db())
