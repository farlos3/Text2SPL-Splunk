from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class SPLRequest(BaseModel):
    query: str
    verbose: Optional[bool] = False


class CompanyInfo(BaseModel):
    company_name: str
    product_name: str
    index: Optional[str] = None
    sourcetype: Optional[str] = None
    data_model: Optional[List[str]] = []
    confidence_score: float
    method: str
    company_index: int


class SPLResponse(BaseModel):
    success: bool
    spl_query: Optional[str] = None
    company: Optional[str] = None
    index: Optional[str] = None
    sourcetype: Optional[str] = None
    confidence: Optional[float] = None
    detection_method: Optional[str] = None
    syntax_valid: Optional[bool] = None
    issues: Optional[List[str]] = []
    error: Optional[str] = None


class SPLValidationResponse(BaseModel):
    valid: bool
    issues: List[str]
    suggestions: Optional[List[str]] = []


class RelevanceCheckResponse(BaseModel):
    is_splunk_related: bool
    confidence: float
    method: str
