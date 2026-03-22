from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.controllers.LLMController import LLMController

llm_router = APIRouter(
    prefix="/Root/v1/LLM",
    tags=["Root_v1", "LLM"]
)

@llm_router.post("/trigger")
async def Trigger_Decision(request: Request):
    try:
        controller = LLMController(request.app)
        decision = await controller.Trigger_Decision()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "SUCCESS": True,
                "SIGNAL": "LLM_DECISION_SUCCESS",
                "decision": decision
            }
        )
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "SUCCESS": False,
                "detail": e.detail
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "SUCCESS": False,
                "detail": str(e)
            }
        )

@llm_router.get("/context")
async def Get_Current_Context(request: Request):
    try:
        controller = LLMController(request.app)
        context = controller.Get_Current_Context()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "SUCCESS": True,
                "SIGNAL": "CONTEXT_RETRIEVED_SUCCESS",
                "context": context
            }
        )
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "SUCCESS": False,
                "detail": e.detail
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "SUCCESS": False,
                "detail": str(e)
            }
        )

@llm_router.post("/provider/{provider_name}")
async def Change_Provider(request: Request, provider_name: str):
    try:
        controller = LLMController(request.app)
        result = controller.Change_Provider(provider_name)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "SUCCESS": True,
                "SIGNAL": "LLM_PROVIDER_CHANGED",
                "message": result.get("message")
            }
        )
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "SUCCESS": False,
                "detail": e.detail
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "SUCCESS": False,
                "detail": str(e)
            }
        )
