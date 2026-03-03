from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Union
from app.controllers.PredLSTMControllers import lstm_controller

router = APIRouter(prefix="/lstm", tags=["LSTM Prediction"])

class PredictionRequest(BaseModel):
    # Accepts either a flat array of 21 features, or a sequence (array of arrays) of 21 features
    features: Union[List[float], List[List[float]]] = Field(..., description="Array of 21 numerical features, or array of arrays for sequences")
    threshold: float = Field(default=0.5, description="Decision threshold for the Sigmoid output (0.0 to 1.0)")

@router.post("/predict")
async def predict_lstm(request: PredictionRequest):

    try:
        result = lstm_controller.predict(request.features, request.threshold)
        
        if not result.get("status"):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "SUCCESS": False,
                    "detail": result.get("error")
                }
            )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "SUCCESS": True,
                "SIGNAL": "LSTM_PREDICTION_SUCCESS",
                "prediction": result
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
