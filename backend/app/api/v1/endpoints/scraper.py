import csv
import io
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.scraper import ScrapeRequest, ScrapeResponse
from app.services.lead_service import process_urls
from app.core.logging import logger

router = APIRouter()

@router.post("", response_model=ScrapeResponse, summary="Process list of healthcare website URLs")
async def scrape_sources(request: ScrapeRequest, db: Session = Depends(get_db)):
    """
    Accepts a list of public healthcare website URLs, fetches clinic information,
    extracts structured intelligence, normalizes fields, and records leads.
    """
    if not request.urls:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one URL must be provided in 'urls' array"
        )

    # Sanitize and deduplicate incoming input list
    clean_urls = list(dict.fromkeys([u.strip() for u in request.urls if u and u.strip()]))
    if not clean_urls:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid URLs provided"
        )

    logger.info(f"Initiating batch scrape for {len(clean_urls)} URL sources")
    response = await process_urls(db, clean_urls)
    return response

@router.post("/csv", response_model=ScrapeResponse, summary="Process healthcare website URLs from uploaded CSV")
async def scrape_csv_sources(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a CSV file containing healthcare URLs in a 'url' or 'source_url' column
    or as the first column of the file.
    """
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must be a .csv format"
        )

    content = await file.read()
    try:
        decoded = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        decoded = content.decode("latin-1")

    reader = csv.reader(io.StringIO(decoded))
    urls: List[str] = []

    for idx, row in enumerate(reader):
        if not row:
            continue
        first_val = row[0].strip()
        # Skip header if it contains text like url or website
        if idx == 0 and any(h in first_val.lower() for h in ["url", "website", "link", "source"]):
            continue
        if first_val.startswith("http://") or first_val.startswith("https://"):
            urls.append(first_val)
        elif "." in first_val and not "@" in first_val:
            urls.append(f"https://{first_val}")

    if not urls:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid URLs could be identified in the uploaded CSV file"
        )

    clean_urls = list(dict.fromkeys(urls))
    logger.info(f"Extracted {len(clean_urls)} URLs from CSV upload: {file.filename}")
    return await process_urls(db, clean_urls)
