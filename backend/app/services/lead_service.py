import csv
import os
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, distinct, cast, String

from app.models.lead import HealthcareLead
from app.schemas.lead import (
    LeadCreate,
    LeadUpdate,
    LeadStatsResponse,
    compute_normalized_domain,
    clean_website_url
)
from app.schemas.scraper import ScrapeResultItem, ScrapeResponse
from app.scrapers.healthcare_scraper import HealthcareWebScraper
from app.services.ai.provider import get_ai_service
from app.core.logging import logger

def get_lead_by_id(db: Session, lead_id: int) -> Optional[HealthcareLead]:
    """Retrieve a single lead by primary key ID."""
    return db.query(HealthcareLead).filter(HealthcareLead.id == lead_id).first()

def create_or_get_lead(db: Session, lead_in: LeadCreate) -> Tuple[HealthcareLead, bool]:
    """
    Creates a new healthcare lead with strict deduplication.
    Deduplication rules:
    1. Match on normalized website domain (e.g., premierdental.com).
    2. Fallback match on identical clinic name + city.
    Returns: (lead_instance, is_created_flag)
    """
    normalized_domain = compute_normalized_domain(lead_in.website or lead_in.source_url)
    
    existing_lead = None
    if normalized_domain:
        existing_lead = db.query(HealthcareLead).filter(
            HealthcareLead.normalized_website == normalized_domain
        ).first()

    if not existing_lead and lead_in.name and lead_in.city:
        existing_lead = db.query(HealthcareLead).filter(
            func.lower(HealthcareLead.name) == lead_in.name.strip().lower(),
            func.lower(HealthcareLead.city) == lead_in.city.strip().lower()
        ).first()

    if existing_lead:
        logger.info(f"Deduplication hit: Lead '{existing_lead.name}' already exists (ID: {existing_lead.id})")
        return existing_lead, False

    # Create new lead
    new_lead = HealthcareLead(
        name=lead_in.name.strip(),
        business_type=lead_in.business_type or "Clinic",
        address=lead_in.address,
        city=lead_in.city,
        state=lead_in.state,
        country=lead_in.country or "Global",
        postal_code=lead_in.postal_code,
        phone=lead_in.phone,
        email=lead_in.email,
        website=clean_website_url(lead_in.website),
        normalized_website=normalized_domain,
        services=lead_in.services or [],
        source_url=lead_in.source_url,
        source_type=lead_in.source_type or "WEBSITE",
        description=lead_in.description,
        status=lead_in.status or "NEW"
    )
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)
    logger.info(f"Created new healthcare lead '{new_lead.name}' (ID: {new_lead.id})")
    return new_lead, True

def list_leads(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    city: Optional[str] = None,
    country: Optional[str] = None,
    status: Optional[str] = None,
    business_type: Optional[str] = None
) -> Tuple[List[HealthcareLead], int]:
    """Retrieves paginated and filtered list of leads."""
    query = db.query(HealthcareLead)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                HealthcareLead.name.ilike(search_term),
                HealthcareLead.description.ilike(search_term),
                HealthcareLead.city.ilike(search_term),
                HealthcareLead.website.ilike(search_term),
                cast(HealthcareLead.services, String).ilike(search_term)
            )
        )

    if city and city.strip():
        query = query.filter(HealthcareLead.city.ilike(f"%{city.strip()}%"))

    if country and country.strip() and country.lower() != "all":
        query = query.filter(HealthcareLead.country.ilike(f"%{country.strip()}%"))

    if status and status.strip() and status.lower() != "all":
        query = query.filter(HealthcareLead.status == status.strip().upper())

    if business_type and business_type.strip() and business_type.lower() != "all":
        query = query.filter(HealthcareLead.business_type.ilike(f"%{business_type.strip()}%"))

    total = query.count()
    offset = max(0, (page - 1) * page_size)
    items = query.order_by(HealthcareLead.created_at.desc()).offset(offset).limit(page_size).all()

    return items, total

def update_lead(db: Session, lead_id: int, lead_update: LeadUpdate) -> Optional[HealthcareLead]:
    """Updates an existing lead's fields."""
    lead = get_lead_by_id(db, lead_id)
    if not lead:
        return None

    update_data = lead_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "website" and value:
            setattr(lead, "website", clean_website_url(value))
            setattr(lead, "normalized_website", compute_normalized_domain(value))
        else:
            setattr(lead, field, value)

    db.commit()
    db.refresh(lead)
    return lead

def delete_lead(db: Session, lead_id: int) -> bool:
    """Deletes a lead by ID."""
    lead = get_lead_by_id(db, lead_id)
    if not lead:
        return False
    db.delete(lead)
    db.commit()
    logger.info(f"Deleted lead ID {lead_id}")
    return True

def get_lead_stats(db: Session) -> LeadStatsResponse:
    """Computes high-level intelligence stats for dashboard header."""
    total_leads = db.query(func.count(HealthcareLead.id)).scalar() or 0
    ai_analyzed = db.query(func.count(HealthcareLead.id)).filter(HealthcareLead.ai_analysis.isnot(None)).scalar() or 0
    high_potential = db.query(func.count(HealthcareLead.id)).filter(HealthcareLead.ai_score >= 80).scalar() or 0
    outreach_ready = db.query(func.count(HealthcareLead.id)).filter(HealthcareLead.ai_outreach_subject.isnot(None)).scalar() or 0
    cities_count = db.query(func.count(distinct(HealthcareLead.city))).filter(HealthcareLead.city.isnot(None)).scalar() or 0
    websites_processed = db.query(func.count(distinct(HealthcareLead.source_url))).scalar() or 0
    successful_records = db.query(func.count(HealthcareLead.id)).filter(HealthcareLead.status != "FAILED").scalar() or 0

    return LeadStatsResponse(
        total_leads=total_leads,
        ai_analyzed=ai_analyzed,
        high_potential=high_potential,
        outreach_ready=outreach_ready,
        websites_processed=websites_processed,
        successful_records=successful_records,
        failed_records=0,
        cities_count=cities_count
    )

async def analyze_lead_with_ai(db: Session, lead_id: int) -> HealthcareLead:
    """
    Executes AI analysis for a healthcare lead.
    Extracts business info, observations, opportunities, and calculates AI Lead Score.
    Persists results in the database.
    """
    lead = get_lead_by_id(db, lead_id)
    if not lead:
        raise ValueError(f"Healthcare lead with ID {lead_id} does not exist")

    lead_data = {
        "id": lead.id,
        "name": lead.name,
        "business_type": lead.business_type,
        "website": lead.website,
        "source_url": lead.source_url,
        "city": lead.city,
        "state": lead.state,
        "country": lead.country,
        "phone": lead.phone,
        "email": lead.email,
        "services": lead.services or [],
        "description": lead.description
    }

    ai_service = get_ai_service()
    ai_result = await ai_service.analyze_lead(lead_data)

    # Persist structured AI outputs
    lead.ai_analysis = ai_result.get("analysis")
    lead.ai_opportunities = ai_result.get("opportunities")
    
    score_data = ai_result.get("score") or {}
    lead.ai_score = score_data.get("score")
    lead.ai_score_category = score_data.get("category")
    lead.ai_score_reason = score_data.get("reason")
    lead.ai_analyzed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(lead)
    logger.info(f"AI analysis completed for lead ID {lead.id} ({lead.name}) - Score: {lead.ai_score}")
    return lead

async def generate_lead_outreach(db: Session, lead_id: int) -> HealthcareLead:
    """
    Generates a personalized, concise outreach draft for a healthcare lead.
    If lead has not yet been analyzed, automatically runs analysis first.
    Persists subject and email body in database.
    """
    lead = get_lead_by_id(db, lead_id)
    if not lead:
        raise ValueError(f"Healthcare lead with ID {lead_id} does not exist")

    # If lead not analyzed yet, run analysis first to extract opportunities
    if not lead.ai_analysis or not lead.ai_opportunities:
        lead = await analyze_lead_with_ai(db, lead_id)

    lead_data = {
        "id": lead.id,
        "name": lead.name,
        "business_type": lead.business_type,
        "website": lead.website,
        "city": lead.city,
        "state": lead.state,
        "services": lead.services or [],
        "description": lead.description
    }

    score_data = {
        "score": lead.ai_score,
        "category": lead.ai_score_category
    }

    ai_service = get_ai_service()
    outreach_result = await ai_service.generate_outreach(
        lead_data=lead_data,
        analysis=lead.ai_analysis or {},
        opportunities=lead.ai_opportunities or [],
        score=score_data
    )

    lead.ai_outreach_subject = outreach_result.get("subject")
    lead.ai_outreach_body = outreach_result.get("body")

    db.commit()
    db.refresh(lead)
    logger.info(f"Outreach generated for lead ID {lead.id} ({lead.name})")
    return lead

async def process_urls(db: Session, urls: List[str]) -> ScrapeResponse:
    """
    Executes discovery scraper against a list of public healthcare URLs.
    Handles deduplication, error logging, and status tracking.
    """
    scraper = HealthcareWebScraper()
    results: List[ScrapeResultItem] = []
    leads_created = 0
    duplicates_skipped = 0
    failed = 0

    for raw_url in urls:
        url = raw_url.strip()
        if not url:
            continue

        try:
            lead_in = await scraper.scrape(url)
            if not lead_in:
                raise ValueError("No healthcare lead details could be extracted")

            lead, is_created = create_or_get_lead(db, lead_in)
            if is_created:
                leads_created += 1
                results.append(ScrapeResultItem(
                    url=url,
                    status="created",
                    lead_id=lead.id,
                    name=lead.name,
                    city=lead.city
                ))
            else:
                duplicates_skipped += 1
                results.append(ScrapeResultItem(
                    url=url,
                    status="duplicate_skipped",
                    lead_id=lead.id,
                    name=lead.name,
                    city=lead.city
                ))

        except Exception as e:
            failed += 1
            error_msg = str(e)
            logger.warning(f"Scrape failed for {url}: {error_msg}")
            results.append(ScrapeResultItem(
                url=url,
                status="failed",
                error=error_msg
            ))

    return ScrapeResponse(
        total_sources=len(urls),
        processed=len(urls),
        leads_created=leads_created,
        duplicates_skipped=duplicates_skipped,
        failed=failed,
        results=results
    )

def seed_demo_leads(db: Session, csv_file_path: str) -> Dict[str, Any]:
    """
    Loads safe public sample demo leads from CSV for instant recruiter testing.
    """
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"Demo CSV not found at: {csv_file_path}")

    created_count = 0
    skipped_count = 0

    with open(csv_file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            services_raw = row.get("services", "")
            services_list = [s.strip() for s in services_raw.split(";") if s.strip()] if services_raw else []

            lead_in = LeadCreate(
                name=row["name"],
                business_type=row.get("business_type", "Clinic"),
                address=row.get("address"),
                city=row.get("city"),
                state=row.get("state"),
                country=row.get("country", "Global"),
                postal_code=row.get("postal_code"),
                phone=row.get("phone"),
                email=row.get("email"),
                website=row.get("website"),
                services=services_list,
                source_url=row.get("source_url") or row.get("website") or "https://example-health.org",
                source_type="CSV_IMPORT",
                description=row.get("description"),
                status=row.get("status", "NEW")
            )
            _, is_created = create_or_get_lead(db, lead_in)
            if is_created:
                created_count += 1
            else:
                skipped_count += 1

    return {
        "status": "success",
        "created": created_count,
        "duplicates_skipped": skipped_count,
        "total_seeded": created_count + skipped_count
    }
