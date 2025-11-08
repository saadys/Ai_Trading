from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine
from  core.Config import Setting

app = FastAPI() 
settings = get_settings()


@app.on_event("startup")
async def startup_event(app: FastAPI):

    postgres_url= f"postgresql+asyncpg://{user}:{settings.Postgres_Password}@{settings.Postgres_Host}:{settings.Postgres_Port}/{settings.Postgres_DBName}"
    pass

@app.on_event("shutdown")
async def shutdown_event():
    pass