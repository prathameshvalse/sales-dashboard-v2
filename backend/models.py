from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class LeadBase(BaseModel):
    lead_name: str
    poc_name: Optional[str] = "Unknown"
    contact_no: Optional[str] = ""
    email: Optional[str] = ""
    category: str
    status: str = "New"
    salesperson: str
    po_value_expected: float = 0.0
    comments: Optional[str] = ""
    priority: str = "Medium"
    source: str = "Web App"

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    po_value_expected: Optional[float] = None
    comments: Optional[str] = None

class LeadResponse(LeadBase):
    lead_id: str
    last_updated: str
    created_date: str
    ai_pitch: Optional[str] = ""

class LoginRequest(BaseModel):
    username: str
    password: str

class AIPitchRequest(BaseModel):
    lead_name: str
    category: str
    comments: str
    po_value: float
