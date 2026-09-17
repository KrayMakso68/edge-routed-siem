from fastapi import APIRouter, Depends, HTTPException
from app.services.ml_service import MLService
from app.core.alerts_consumer import RECENT_ALERTS

router = APIRouter(prefix="/api/ml", tags=["ML Agent"])

def get_ml_service():
    return MLService()

@router.post("/start")
def start_ml_agent(ml_service: MLService = Depends(get_ml_service)):
    try:
        return ml_service.start_agent()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
def stop_ml_agent(ml_service: MLService = Depends(get_ml_service)):
    try:
        return ml_service.stop_agent()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
def get_ml_status(ml_service: MLService = Depends(get_ml_service)):
    return ml_service.get_status()

@router.get("/alerts")
def get_recent_alerts():
    return RECENT_ALERTS
