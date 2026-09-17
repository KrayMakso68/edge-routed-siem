from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.domain.schemas import RuleSourceCreate, RuleSourceUpdate, RuleSourceResponse, StandardResponse
from app.services.rule_source_service import RuleSourceService
from app.api.dependencies import get_rule_source_service

router = APIRouter(prefix="/api/suricata/sources", tags=["Rule Sources"])

@router.get("/", response_model=List[RuleSourceResponse])
def get_all(service: RuleSourceService = Depends(get_rule_source_service)):
    try:
        return service.get_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=RuleSourceResponse)
def create(data: RuleSourceCreate, service: RuleSourceService = Depends(get_rule_source_service)):
    try:
        return service.create(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{source_id}", response_model=RuleSourceResponse)
def update(source_id: int, data: RuleSourceUpdate, service: RuleSourceService = Depends(get_rule_source_service)):
    try:
        return service.update(source_id, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{source_id}", response_model=StandardResponse)
def delete(source_id: int, service: RuleSourceService = Depends(get_rule_source_service)):
    try:
        service.delete(source_id)
        return StandardResponse(status="success", message="Rule source deleted")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
