from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
import math
import os

from app.db.session import get_db
from app.schemas.lead import (
    LeadResponse,
    LeadCreate,
    LeadUpdate,
    LeadPaginationResponse,
    LeadStatsResponse
)
from app.services.lead_service import (
    get_lead_by_id,
    create_or_get_lead,
    list_leads,
    update_lead,
    delete_lead,
    get_lead_stats,
    seed_demo_leads,
    analyze_lead_with_ai,
    generate_lead_outreach
)
from app.core.logging import logger

router = APIRouter()

@router.get("", response_model=LeadPaginationResponse, summary="List leads with search and filters")
def get_leads(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term for clinic name, services, city or description"),
    city: Optional[str] = Query(None, description="Filter by city"),
    country: Optional[str] = Query(None, description="Filter by country"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (NEW, VERIFIED, etc.)"),
    business_type: Optional[str] = Query(None, description="Filter by healthcare business type"),
    db: Session = Depends(get_db)
):
    """
    Retrieves paginated healthcare leads with comprehensive full-text search,
    location filtering, and category sorting.
    """
    leads, total = list_leads(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        city=city,
        country=country,
        status=status_filter,
        business_type=business_type
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return LeadPaginationResponse(
        items=[LeadResponse.model_validate(lead) for lead in leads],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/stats", response_model=LeadStatsResponse, summary="Get lead discovery statistics")
def get_stats(db: Session = Depends(get_db)):
    """Computes overall lead intelligence metrics for the dashboard."""
    return get_lead_stats(db)

@router.get("/{lead_id}", response_model=LeadResponse, summary="Get lead details by ID")
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    """Fetches complete profile and source metadata for a specific lead."""
    lead = get_lead_by_id(db, lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Healthcare lead with ID {lead_id} was not found"
        )
    return LeadResponse.model_validate(lead)

@router.post("/{lead_id}/analyze", response_model=LeadResponse, summary="Perform AI analysis on healthcare lead")
async def analyze_lead(lead_id: int, db: Session = Depends(get_db)):
    """
    Triggers AI-powered clinical offering analysis, opportunity detection,
    and calculates an objective AI Lead Score (0-100).
    """
    try:
        updated_lead = await analyze_lead_with_ai(db, lead_id)
        return LeadResponse.model_validate(updated_lead)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"AI analysis failed for lead {lead_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI analysis failed: {str(e)}"
        )

@router.post("/{lead_id}/generate-outreach", response_model=LeadResponse, summary="Generate personalized outreach draft")
async def generate_outreach(lead_id: int, db: Session = Depends(get_db)):
    """
    Generates a personalized 100-150 word cold outreach email draft
    grounded in the lead's clinical offerings and identified opportunities.
    """
    try:
        updated_lead = await generate_lead_outreach(db, lead_id)
        return LeadResponse.model_validate(updated_lead)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Outreach generation failed for lead {lead_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Outreach generation failed: {str(e)}"
        )

@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED, summary="Create a lead manually")
def create_lead(lead_in: LeadCreate, db: Session = Depends(get_db)):
    """Creates a new healthcare lead record with automated deduplication."""
    lead, is_created = create_or_get_lead(db, lead_in)
    return LeadResponse.model_validate(lead)

@router.delete("/{lead_id}", status_code=status.HTTP_200_OK, summary="Delete lead by ID")
def remove_lead(lead_id: int, db: Session = Depends(get_db)):
    """Deletes a lead from the platform database."""
    success = delete_lead(db, lead_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Healthcare lead with ID {lead_id} not found"
        )
    return {"message": f"Lead {lead_id} successfully deleted", "lead_id": lead_id}

@router.post("/seed-demo", summary="Seed safe demo healthcare dataset")
def seed_demo_data(db: Session = Depends(get_db)):
    """
    Populates database with high-quality public healthcare business examples.
    Ideal for recruiters evaluating Phase 1 without scraping live targets.
    """
    # Locate demo_leads.csv relative to backend root
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    demo_path = os.path.join(backend_dir, "data", "demo_leads.csv")
    
    if not os.path.exists(demo_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Demo dataset file not found at {demo_path}"
        )

    try:
        result = seed_demo_leads(db, demo_path)
        return result
    except Exception as e:
        logger.error(f"Failed to seed demo data: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to seed demo dataset: {str(e)}"
        )
