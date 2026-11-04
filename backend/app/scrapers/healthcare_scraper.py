import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Optional, Dict, Any, List
import re

from app.core.config import settings
from app.core.logging import logger
from app.schemas.lead import LeadCreate, clean_website_url
from app.scrapers.base import BaseScraper
from app.scrapers.utils import (
    clean_text,
    extract_schema_org_data,
    extract_emails,
    extract_phones,
    extract_services,
    infer_business_type
)

class HealthcareWebScraper(BaseScraper):
    """
    Production-grade web scraper for public healthcare clinic and medical business websites.
    Extracts structured clinic intelligence while respecting robots, timeouts, and privacy boundaries.
    """

    def __init__(self, timeout_seconds: int = None, user_agent: str = None):
        self.timeout = timeout_seconds or settings.SCRAPER_TIMEOUT_SECONDS
        self.user_agent = user_agent or settings.SCRAPER_USER_AGENT

    async def scrape(self, url: str) -> Optional[LeadCreate]:
        """Fetches public webpage and extracts structured healthcare lead."""
        if not self.validate_url(url):
            raise ValueError(f"Invalid URL provided: {url}")

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "DNT": "1"  # Do Not Track
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                html = response.text
                final_url = str(response.url)

            return self.extract_from_html(html, final_url)

        except httpx.TimeoutException as e:
            logger.warning(f"Timeout scraping {url}: {e}")
            raise TimeoutError(f"Connection timed out while fetching {url}") from e
        except httpx.HTTPStatusError as e:
            logger.warning(f"HTTP error {e.response.status_code} on {url}: {e}")
            raise ConnectionError(f"HTTP {e.response.status_code} error from server at {url}") from e
        except httpx.RequestError as e:
            logger.warning(f"Network request failed for {url}: {e}")
            raise ConnectionError(f"Network request failed for {url}: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error while scraping {url}: {e}", exc_info=True)
            raise RuntimeError(f"Failed to process source {url}: {str(e)}") from e

    def extract_from_html(self, html: str, url: str) -> Optional[LeadCreate]:
        """Extracts structured healthcare lead details from HTML."""
        if not html or not html.strip():
            raise ValueError("Webpage returned empty content")

        soup = BeautifulSoup(html, "lxml" if "lxml" in BeautifulSoup.__dict__ else "html.parser")
        parsed_url = urlparse(url)
        base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

        # 1. Attempt structured data extraction via Schema.org JSON-LD
        schema_data = extract_schema_org_data(soup)

        name = None
        phone = None
        email = None
        address = None
        city = None
        state = None
        country = "Global"
        postal_code = None
        services = []
        description = None
        business_type = None

        if schema_data:
            name = clean_text(schema_data.get("name"))
            phone = clean_text(schema_data.get("telephone"))
            email = clean_text(schema_data.get("email"))
            description = clean_text(schema_data.get("description"))
            
            # Address from Schema.org
            addr_obj = schema_data.get("address")
            if isinstance(addr_obj, dict):
                address = clean_text(addr_obj.get("streetAddress"))
                city = clean_text(addr_obj.get("addressLocality"))
                state = clean_text(addr_obj.get("addressRegion"))
                postal_code = clean_text(addr_obj.get("postalCode"))
                country = clean_text(addr_obj.get("addressCountry")) or "Global"
            elif isinstance(addr_obj, str):
                address = clean_text(addr_obj)

            # Services / specialty
            specialty = schema_data.get("medicalSpecialty")
            if specialty:
                if isinstance(specialty, list):
                    services.extend([clean_text(str(s)) for s in specialty if s])
                elif isinstance(specialty, str):
                    services.append(clean_text(specialty))

        # 2. Extract Clinic Name (if not from Schema.org)
        if not name:
            # Check og:site_name
            og_site_name = soup.find("meta", property="og:site_name")
            if og_site_name and og_site_name.get("content"):
                name = clean_text(og_site_name["content"])

        if not name:
            # Check og:title
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                name = clean_text(og_title["content"])

        if not name and soup.title:
            title_text = soup.title.get_text()
            # Clean common title tags: "ABC Dental | Trusted Family Dentist in Austin"
            cleaned_title = re.split(r"[-|–—•:]", title_text)[0]
            name = clean_text(cleaned_title)

        if not name:
            h1 = soup.find("h1")
            if h1:
                name = clean_text(h1.get_text())

        if not name:
            # Fallback to domain host capitalized
            name = parsed_url.netloc.replace("www.", "").split(".")[0].title() + " Healthcare"

        # 3. Contact information fallbacks
        extracted_phones = extract_phones(soup, html)
        if not phone and extracted_phones:
            phone = extracted_phones[0]

        extracted_emails = extract_emails(soup, html)
        if not email and extracted_emails:
            email = extracted_emails[0]

        # 4. Description fallback
        if not description:
            meta_desc = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
            if not meta_desc:
                meta_desc = soup.find("meta", property="og:description")
            if meta_desc and meta_desc.get("content"):
                description = clean_text(meta_desc["content"])

        if not description:
            # First meaningful paragraph
            for p in soup.find_all("p"):
                txt = clean_text(p.get_text())
                if txt and len(txt) > 60:
                    description = txt[:300]
                    break

        # 5. Services extraction
        web_services = extract_services(soup)
        for s in web_services:
            if s and s not in services:
                services.append(s)

        # 6. Address / Location fallback from footer or address tags
        if not address or not city:
            addr_tag = soup.find("address")
            if addr_tag:
                addr_text = clean_text(addr_tag.get_text())
                if addr_text:
                    if not address:
                        address = addr_text[:200]
                    # Attempt simple city/state parse
                    parts = [p.strip() for p in addr_text.split(",") if p.strip()]
                    if len(parts) >= 2 and not city:
                        city = parts[-2]
            
            # Look for contact section
            if not city:
                footer = soup.find(["footer", "div"], class_=re.compile(r"footer|contact|location", re.I))
                if footer:
                    footer_text = footer.get_text()
                    city_match = re.search(r"([A-Z][a-zA-Z\s]{2,20}),\s*([A-Z]{2}|\w+)\s*(\d{4,5})?", footer_text)
                    if city_match:
                        city = city_match.group(1).strip()
                        if not state:
                            state = city_match.group(2).strip()
                        if not postal_code and city_match.group(3):
                            postal_code = city_match.group(3).strip()

        # 7. Infer Business Type
        combined_text = f"{name} {description or ''} {' '.join(services)}"
        business_type = infer_business_type(combined_text)

        # 8. Ensure Website URL is well formatted
        website = clean_website_url(base_domain)

        return LeadCreate(
            name=name,
            business_type=business_type,
            address=address,
            city=city,
            state=state,
            country=country or "Global",
            postal_code=postal_code,
            phone=phone,
            email=email,
            website=website,
            services=services[:10],
            source_url=url,
            source_type="WEBSITE",
            description=description,
            status="NEW"
        )
