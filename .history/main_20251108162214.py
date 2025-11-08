from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine
from 
app = FastAPI() 

@app.on_event("startup")
async def startup_event(app: FastAPI):

    postgres_url= f"postgresql+asyncpg://user:password@host:port/database_name
    pass

@app.on_event("shutdown")
async def shutdown_event():
    pass