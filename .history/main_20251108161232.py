from fastapi import FastAPI

app = FastAPI() 

@app.on_event("startup")
async def startup_event(app: FastAPI):
    pass

@app.on_event("shutdown")
def shutdown_event():