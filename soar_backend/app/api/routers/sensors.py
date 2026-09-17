from fastapi import APIRouter, Depends
from typing import List
from app.domain.schemas import SensorCreate, SensorUpdate, SensorResponse, StandardResponse
from app.services.sensor_service import SensorService
from app.api.dependencies import get_sensor_service
from app.core.telemetry import SENSOR_METRICS

router = APIRouter(prefix="/api/sensors", tags=["Sensors"])

@router.get("/status")
def get_status():
    return SENSOR_METRICS

@router.get("/", response_model=List[SensorResponse])
def get_all(service: SensorService = Depends(get_sensor_service)):
    return service.get_all()

@router.post("/", response_model=SensorResponse)
def create(data: SensorCreate, service: SensorService = Depends(get_sensor_service)):
    return service.create(data)

@router.put("/{sensor_id}", response_model=SensorResponse)
def update(sensor_id: int, data: SensorUpdate, service: SensorService = Depends(get_sensor_service)):
    return service.update(sensor_id, data)

@router.delete("/{sensor_id}", response_model=StandardResponse)
def delete(sensor_id: int, service: SensorService = Depends(get_sensor_service)):
    service.delete(sensor_id)
    return StandardResponse(status="success", message="Sensor deleted")
