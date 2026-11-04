import re
import json
from typing import Optional, Dict, Any, List
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Avoid false positive email matches from web assets or libraries
EXCLUDED_EMAIL_DOMAINS = {
    "example.com", "domain.com", "sentry.io", "wix.com",
    "wordpress.org", "w3.org", "schema.org", "google.com",
    "cloudflare.com", "placeholder.com"
}
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico')

PHONE_PATTERNS = [
    # International (+1 / +61 / +44 etc.)
    r"\+?[1-9]\d{0,2}[ -]?(?:\(?\d{2,4}\)?[ -]?)?\d{3,4}[ -]?\d{3,4}",
    # Standard 10 digit (123) 456-7890 or 123-456-7890
    r"\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}",
    # Australian / UK format (e.g., 02 1234 5678 or 0412 345 678)
    r"\(?0[2-9]\)?[-. ]?\d{4}[-. ]?\d{4}",
    r"04\d{2}[-. ]?\d{3}[-. ]?\d{3}"
]

def clean_text(text: Optional[str]) -> Optional[str]:
    """Strips excessive whitespace, tabs, and newlines."""
    if not text:
        return None
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned if cleaned else None

def extract_schema_org_data(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extracts Schema.org JSON-LD structured data for healthcare/local business."""
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        if not script.string:
            continue
        try:
            data = json.loads(script.string.strip())
            # Sometimes data is a list of schemas or has @graph
            items = []
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                if "@graph" in data and isinstance(data["@graph"], list):
                    items = data["@graph"]
                else:
                    items = [data]

            for item in items:
                if not isinstance(item, dict):
                    continue
                schema_type = str(item.get("@type", "")).lower()
                healthcare_types = [
                    "medicalbusiness", "dentist", "physician", "medicalclinic",
                    "hospital", "pharmacy", "healthandbeautybusiness", "localbusiness",
                    "organization"
                ]
                if any(t in schema_type for t in healthcare_types):
                    return item
        except Exception:
            continue
    return {}

def extract_emails(soup: BeautifulSoup, html_text: str) -> List[str]:
    """Finds business emails from mailto: links and page body text."""
    emails = []

    # 1. Inspect mailto: links first (highest confidence)
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.lower().startswith("mailto:"):
            email_part = href[7:].split("?")[0].strip().lower()
            if email_part and "@" in email_part:
                emails.append(email_part)

    # 2. Body regex search
    pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    for match in re.findall(pattern, html_text):
        m = match.strip().lower()
        if not any(m.endswith(ext) for ext in IMAGE_EXTENSIONS):
            domain = m.split("@")[-1]
            if domain not in EXCLUDED_EMAIL_DOMAINS and not domain.endswith(".png"):
                emails.append(m)

    # Deduplicate while preserving order
    return list(dict.fromkeys(emails))

def extract_phones(soup: BeautifulSoup, html_text: str) -> List[str]:
    """Finds contact phone numbers from tel: links and regex patterns."""
    phones = []

    # 1. Inspect tel: links (highest confidence)
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.lower().startswith("tel:"):
            phone = clean_text(href[4:].split("?")[0])
            if phone and len(re.sub(r"\D", "", phone)) >= 7:
                phones.append(phone)

    # 2. Look for elements with phone-related classes or IDs
    contact_elements = soup.find_all(
        ["p", "span", "div", "a"],
        class_=re.compile(r"phone|tel|contact", re.I)
    )
    for el in contact_elements:
        text = el.get_text()
        for pat in PHONE_PATTERNS:
            for match in re.findall(pat, text):
                cleaned = clean_text(match)
                digits = re.sub(r"\D", "", cleaned)
                if 7 <= len(digits) <= 15:
                    phones.append(cleaned)

    # 3. Text fallback
    if not phones:
        for pat in PHONE_PATTERNS:
            for match in re.findall(pat, html_text[:50000]):
                cleaned = clean_text(match)
                digits = re.sub(r"\D", "", cleaned)
                if 7 <= len(digits) <= 15:
                    phones.append(cleaned)
                    if len(phones) >= 3:
                        break

    return list(dict.fromkeys(phones))

def extract_services(soup: BeautifulSoup) -> List[str]:
    """Extracts clinical services and treatments from headings, lists, and nav."""
    services = []
    
    # Check for service section containers
    service_sections = soup.find_all(
        ["section", "div", "ul"],
        class_=re.compile(r"service|treatment|specialt|procedure", re.I)
    )
    for section in service_sections:
        for li in section.find_all(["li", "h3", "h4", "a"]):
            text = clean_text(li.get_text())
            if text and 3 <= len(text) <= 50 and not any(kw in text.lower() for kw in ["view all", "learn more", "read more", "home", "contact"]):
                services.append(text)

    # Limit to top 10 unique services
    return list(dict.fromkeys(services))[:10]

def infer_business_type(text: str) -> str:
    """Classifies healthcare business type based on keywords."""
    t = text.lower()
    if any(k in t for k in ["dental", "dentist", "orthodont", "teeth"]):
        return "Dental Clinic"
    elif any(k in t for k in ["chiro", "chiropractic", "spine", "osteopath"]):
        return "Chiropractic & Spine"
    elif any(k in t for k in ["physio", "physical therapy", "physiotherapy"]):
        return "Physiotherapy & Rehab"
    elif any(k in t for k in ["derma", "skin", "aesthetic", "cosmetic"]):
        return "Dermatology & Skin"
    elif any(k in t for k in ["eye", "optom", "vision", "ophthalm"]):
        return "Optometry & Eye Care"
    elif any(k in t for k in ["mental", "psychol", "counsel", "psychiat"]):
        return "Mental Health & Wellness"
    elif any(k in t for k in ["pediatric", "child health", "paediatric"]):
        return "Pediatric Care"
    elif any(k in t for k in ["rehab"]):
        return "Physiotherapy & Rehab"
    elif any(k in t for k in ["hospital", "medical center", "urgent care", "surgery"]):
        return "Medical Center / Hospital"
    return "Healthcare Clinic"
