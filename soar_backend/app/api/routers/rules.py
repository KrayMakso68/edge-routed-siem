from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.domain.schemas import RuleCreate, RuleResponse, StandardResponse, RuleSyncRequest, RuleBatchDeleteRequest
from app.services.sensor_service import SensorService
from app.services.rule_service import RuleService
from app.services.rule_source_service import RuleSourceService
from app.api.dependencies import get_rule_service, get_sensor_service, get_rule_source_service

router = APIRouter(prefix="/api/suricata", tags=["Rules"])

@router.get("/rules/{sensor_id}", response_model=List[RuleResponse])
def list_rules(sensor_id: int, r_service: RuleService = Depends(get_rule_service), s_service: SensorService = Depends(get_sensor_service)):
    try:
        sensor = s_service.get_by_id(sensor_id)
        return r_service.get_rules(sensor['ip'])
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@router.post("/rules/{sensor_id}", response_model=StandardResponse)
def add_rule(sensor_id: int, data: RuleCreate, r_service: RuleService = Depends(get_rule_service), s_service: SensorService = Depends(get_sensor_service)):
    try:
        sensor = s_service.get_by_id(sensor_id)
        res = r_service.add_rule(sensor['ip'], data.rule_text)
        return StandardResponse(status="success", message="Rule added", details=res)
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@router.delete("/rules/{sensor_id}", response_model=StandardResponse)
def delete_rule(sensor_id: int, data: RuleCreate, r_service: RuleService = Depends(get_rule_service), s_service: SensorService = Depends(get_sensor_service)):
    try:
        sensor = s_service.get_by_id(sensor_id)
        res = r_service.delete_rule(sensor['ip'], data.rule_text)
        return StandardResponse(status="success", message="Rule deleted", details=res)
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@router.post("/rules/{sensor_id}/sync", response_model=StandardResponse)
def sync_rules(
    sensor_id: int,
    data: RuleSyncRequest,
    r_service: RuleService = Depends(get_rule_service),
    s_service: SensorService = Depends(get_sensor_service),
    src_service: RuleSourceService = Depends(get_rule_source_service)
):
    try:
        # 1. Получаем сенсор
        sensor = s_service.get_by_id(sensor_id)
        # 2. Получаем источник правил
        source = src_service.get_by_id(data.source_id)
        # 3. Скачиваем правила из git
        repo_rules = src_service.fetch_rules_from_git(
            repo_url=source['url'],
            branch=source.get('branch', 'main'),
            rules_path=source.get('rules_path')
        )
        # 4. Синхронизируем правила на сенсоре
        res = r_service.sync_rules_from_source(sensor['ip'], repo_rules)
        return StandardResponse(status="success", message=res["message"], details=res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rules/{sensor_id}/batch-delete", response_model=StandardResponse)
def batch_delete_rules(
    sensor_id: int,
    data: RuleBatchDeleteRequest,
    r_service: RuleService = Depends(get_rule_service),
    s_service: SensorService = Depends(get_sensor_service)
):
    try:
        sensor = s_service.get_by_id(sensor_id)
        res = r_service.batch_delete_rules(sensor['ip'], data.rule_texts)
        return StandardResponse(status="success", message="Rules deleted", details=res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
