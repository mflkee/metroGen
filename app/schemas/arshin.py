from __future__ import annotations
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class VriIdOut(BaseModel):
    certificate: str
    vri_id: Optional[str] = None
    year_used: Optional[int] = None
    error: Optional[str] = None

class VriIdListOut(BaseModel):
    items: List[VriIdOut]

class VriDetailOut(BaseModel):
    certificate: Optional[str] = None
    vri_id: Optional[str] = None
    organization: Optional[str] = None
    vrfDate: Optional[str] = None
    validDate: Optional[str] = None
    applicable: Optional[bool] = None
    protocol_url: Optional[str] = None
    regNumber: Optional[str] = None
    mitypeNumber: Optional[str] = None
    mitypeTitle: Optional[str] = None
    mitypeType: Optional[str] = None
    mitypeType_short: Optional[str] = None
    manufactureNum: Optional[str] = None
    manufactureYear: Optional[int] = None
    rankCode: Optional[str] = None
    rankTitle: Optional[str] = None
    etalon_line: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class VriDetailListOut(BaseModel):
    items: List[VriDetailOut]

