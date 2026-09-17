from pydantic import BaseModel
from typing import List, Any, Optional

class SensorBase(BaseModel):
    name: str
    ip: str
    network: str
    description: Optional[str] = ""

class SensorCreate(SensorBase):
    pass

class SensorUpdate(BaseModel):
    name: Optional[str] = None
    ip: Optional[str] = None
    network: Optional[str] = None
    description: Optional[str] = None

class SensorResponse(SensorBase):
    id: int

class RuleCreate(BaseModel):
    rule_text: str

class RuleResponse(BaseModel):
    id: int
    rule_text: str

class PcapFileDTO(BaseModel):
    filename: str
    size: str
    date: str

class StandardResponse(BaseModel):
    status: str
    message: str
    details: Any = None

class RuleSourceBase(BaseModel):
    name: str
    url: str
    branch: Optional[str] = "main"
    rules_path: Optional[str] = ""
    description: Optional[str] = ""

class RuleSourceCreate(RuleSourceBase):
    pass

class RuleSourceUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    branch: Optional[str] = None
    rules_path: Optional[str] = None
    description: Optional[str] = None

class RuleSourceResponse(RuleSourceBase):
    id: int

class RuleSyncRequest(BaseModel):
    source_id: int

class RuleBatchDeleteRequest(BaseModel):
    rule_texts: List[str]
