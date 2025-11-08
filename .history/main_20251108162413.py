from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine
from  core.Config import Setting
app = FastAPI() 

setting
@app.on_event("startup")
async def startup_event(app: FastAPI):

    postgres_url= f"postgresql+asyncpg://user:password@host:port/database_name"
    pass

@app.on_event("shutdown")
async def shutdown_event():
    pass