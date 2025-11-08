from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine
app = FastAPI() 

@app.on_event("startup")
async def startup_event(app: FastAPI):
    postgres_url=
    pass

@app.on_event("shutdown")
async def shutdown_event():
    pass