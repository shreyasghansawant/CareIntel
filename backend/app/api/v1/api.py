from fastapi import APIRouter
from app.api.v1.endpoints import health, leads, scraper

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(leads.router, prefix="/leads", tags=["Healthcare Leads"])
api_router.include_router(scraper.router, prefix="/scrape", tags=["Lead Discovery & Scraper"])
