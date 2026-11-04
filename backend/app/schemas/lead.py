from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List, Any, Dict
from datetime import datetime
import re

def clean_website_url(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    url = url.strip()
    if not url:
        return None
    # Add protocol if missing
    if not re.match(r"^https?://", url, re.I):
        url = "https://" + url
    return url.rstrip("/")

def compute_normalized_domain(url: Optional[str]) -> Optional[str]:
    """Extracts base normalized domain (e.g., example.com) for deduplication."""
    if not url:
        return None
    url = clean_website_url(url)
    if not url:
        return None
    # Remove protocol
    domain = re.sub(r"^https?://", "", url, flags=re.I)
    # Remove www.
    domain = re.sub(r"^www\.", "", domain, flags=re.I)
    # Take domain part before first slash or port
    domain = domain.split("/")[0].split(":")[0].strip().lower()
    return domain

class LeadBase(BaseModel):
    name: str
    business_type: Optional[str] = "Clinic"
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = "Global"
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    services: Optional[List[str]] = []
    source_url: str
    source_type: Optional[str] = "WEBSITE"
    description: Optional[str] = None
    status: Optional[str] = "NEW"

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Clinic/Business name cannot be empty")
        return v

    @field_validator("website")
    @classmethod
    def normalize_website(cls, v: Optional[str]) -> Optional[str]:
        return clean_website_url(v)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        v = v.strip().lower()
        # Basic email sanity regex
        if re.match(r"^[^@]+@[^@]+\.[^@]+$", v):
            return v
        return None

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        v = v.strip()
        # Clean out repetitive spaces
        v = re.sub(r"\s+", " ", v)
        return v if len(v) >= 5 else None

    @field_validator("services", mode="before")
    @classmethod
    def clean_services(cls, v: Any) -> List[str]:
        if v is None:
            return []
        if isinstance(v, str):
            # Comma-separated or semicolon-separated string
            items = [s.strip() for s in re.split(r"[,;|\n]", v) if s.strip()]
            return list(dict.fromkeys(items))
        if isinstance(v, list):
            items = [str(s).strip() for s in v if str(s).strip()]
            return list(dict.fromkeys(items))
        return []

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    name: Optional[str] = None
    business_type: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    services: Optional[List[str]] = None
    description: Optional[str] = None
    status: Optional[str] = None

class AIOpportunity(BaseModel):
    title: str
    explanation: str

class AIAnalysisInfo(BaseModel):
    business_type: str
    services_summary: str
    target_audience: str
    observations: List[str]

class AILeadScore(BaseModel):
    score: int
    category: str  # "High" (80-100), "Medium" (60-79), "Low" (0-59)
    reason: str

class AIAnalysisResult(BaseModel):
    analysis: AIAnalysisInfo
    opportunities: List[AIOpportunity]
    score: AILeadScore

class AIOutreachResult(BaseModel):
    subject: str
    body: str

class LeadResponse(LeadBase):
    id: int
    normalized_website: Optional[str] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    ai_opportunities: Optional[List[Dict[str, Any]]] = None
    ai_score: Optional[int] = None
    ai_score_category: Optional[str] = None
    ai_score_reason: Optional[str] = None
    ai_outreach_subject: Optional[str] = None
    ai_outreach_body: Optional[str] = None
    ai_analyzed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class LeadPaginationResponse(BaseModel):
    items: List[LeadResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class LeadStatsResponse(BaseModel):
    total_leads: int
    ai_analyzed: int = 0
    high_potential: int = 0
    outreach_ready: int = 0
    websites_processed: int
    successful_records: int
    failed_records: int
    cities_count: int
