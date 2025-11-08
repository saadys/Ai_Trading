from fastapi import FastAPI

app = FastAPI() 

@app.on_event("startup")
async def startup_event(app: FastAPI):
    postgres
    pass

@app.on_event("shutdown")
async def shutdown_event():
    pass