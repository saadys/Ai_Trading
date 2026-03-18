from fastapi import APIRouter, Request, HTTPException ,status
from fastapi.responses import JSONResponse
from app.stream_processor.StreamProcessor import StreamProcessor
from app.models.enums.ResponseEnums import ResponseSignals
import asyncio

streaming_router = APIRouter(
    prefix="/Root/v1/Streaming",
    tags=["Root_v1", "Streaming"]
)

@streaming_router.get("/status")
async def get_btc_status(request: Request):
    stream_processor = getattr(request.app, "stream_processor", None)
    if stream_processor:
        stats = await stream_processor.status()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "SUCCESS": True,
                "stats": stats
            }
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "SUCCESS": False,
                "detail": "Stream not found"
            }       
        )

@streaming_router.post("/start")
async def start_stream(request: Request):
    stream_processor = getattr(request.app, "stream_processor", None)
    if not stream_processor:
        raise HTTPException(status_code=404, detail="BTC Processor non initialisé")
    
    if stream_processor.is_running:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "SUCCESS": True,
                "SIGNAL": ResponseSignals.STREAM_ALREADY_RUNNING
            }
        )
    
    asyncio.create_task(stream_processor.start())
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "SUCCESS": True,
            "SIGNAL": ResponseSignals.STREAM_START_SUCCESS
        }
    )

@streaming_router.post("/stop")
async def stop_stream(request: Request):
    stream_processor = getattr(request.app, "stream_processor", None)
    if not stream_processor:
        raise HTTPException(status_code=404, detail="BTC Processor non initialisé")
    
    if not stream_processor.is_running:
         return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "SUCCESS": True,
                "SIGNAL": ResponseSignals.STREAM_NOT_RUNNING
            }
        )

    await stream_processor.stop()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "SUCCESS": True,
            "SIGNAL": ResponseSignals.STREAM_STOP_SUCCESS
        }
    )
