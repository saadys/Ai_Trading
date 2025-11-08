from fastapi import FastAPI

app = FastAPI() 

async def lifespan(app: FastAPI):
    pass