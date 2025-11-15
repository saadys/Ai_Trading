from app.services.streaming.QueueManager import QueueManager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from core.Config import Settings, get_settings
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI


app = FastAPI() 
settings = get_settings()

@app.on_event("startup")
async def startup_event(app: FastAPI):
    #Base de donnees POstgresSQl
    postgres_url= f"postgresql+asyncpg://{settings.Postgres_User}:{settings.Postgres_Password}@{settings.Postgres_Host}:{settings.Postgres_Port}/{settings.Postgres_DBName}"
    app.async_engine = create_async_engine(
        postgres_url
    )
    app.database_client = sessionmaker(
                bind=app.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
                ) 
    #RabbitMQ 
    app.queue_manager = QueueManager(settings)
    await app.queue_manager.connect()
    await app.queue_manager.setup_broker()

@app.on_event("shutdown")
async def shutdown_event():
    await app.queue_manager.disconnect()
    await app.database_client.dispose()
    