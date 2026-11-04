from pydantic import BaseModel, Field
from typing import List, Optional

class ScrapeRequest(BaseModel):
    urls: List[str] = Field(..., description="List of public healthcare URLs to extract lead data from")

class ScrapeResultItem(BaseModel):
    url: str
    status: str  # "created" | "duplicate_skipped" | "failed"
    lead_id: Optional[int] = None
    name: Optional[str] = None
    city: Optional[str] = None
    error: Optional[str] = None

class ScrapeResponse(BaseModel):
    total_sources: int
    processed: int
    leads_created: int
    duplicates_skipped: int
    failed: int
    results: List[ScrapeResultItem]
