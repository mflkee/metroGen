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
