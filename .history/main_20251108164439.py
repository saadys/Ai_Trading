from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from  core.Config import Settings
from sqlalchemy.orm import sessionmaker


app = FastAPI() 
settings = get_settings()


@app.on_event("startup")
async def startup_event(app: FastAPI):

    postgres_url= f"postgresql+asyncpg://{settings.Postgres_User}:{settings.Postgres_Password}@{settings.Postgres_Host}:{settings.Postgres_Port}/{settings.Postgres_DBName}"
    app.async_engine = create_async_engine(
        postgres_url
    )
    app.database_client = sessionmaker(
                bind=app.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
                ) 

@app.on_event("shutdown")
async def shutdown_event():
    app.database_client.dispose()
    pass