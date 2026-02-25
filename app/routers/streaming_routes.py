from fastapi import FastAPI,Depends, APIRouter
from core.Config import Settings, get_settings


app = FastAPI()
base_router = APIRouter(
    prefix="/Root/v1",
    tags=["Root_v1"]
)


@base_router.get("/")
async def root(app_settings : Settings=Depends(get_settings())):
    Application_Name = app_settings.NAME_APP
    App_Version = app_settings.APP_VERSION
    return {
        "App Name":Application_Name,
        "App Version":App_Version
        }