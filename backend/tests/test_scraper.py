import pytest
from unittest.mock import patch, AsyncMock
from app.scrapers.healthcare_scraper import HealthcareWebScraper
from app.schemas.lead import LeadCreate

SAMPLE_SCHEMA_ORG_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Pacific Dental Care | Top Family Dentist</title>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "Dentist",
        "name": "Pacific Dental Care",
        "telephone": "+1-415-555-0199",
        "email": "info@pacificdentalcare.com",
        "description": "Comprehensive family dentistry and Invisalign services in San Francisco.",
        "medicalSpecialty": ["General Dentistry", "Orthodontics", "Dental Implants"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "500 Howard Street",
            "addressLocality": "San Francisco",
            "addressRegion": "CA",
            "postalCode": "94105",
            "addressCountry": "United States"
        }
    }
    </script>
</head>
<body>
    <h1>Welcome to Pacific Dental Care</h1>
</body>
</html>
"""

SAMPLE_FALLBACK_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Dr. Smith Chiropractic & Spine - Wellness Centre</title>
    <meta name="description" content="Dedicated chiropractic care and spinal adjustment in Seattle, WA.">
    <meta property="og:site_name" content="Dr. Smith Chiropractic & Spine">
</head>
<body>
    <h1>Spinal Rehabilitation & Wellness</h1>
    <p>We provide specialized spinal care to active individuals. Contact us today.</p>
    <div class="contact-info">
        <a href="tel:206-555-0144">Call 206-555-0144</a>
        <a href="mailto:contact@smithchiro.com">contact@smithchiro.com</a>
        <address>742 Evergreen Terrace, Seattle, WA 98101</address>
    </div>
    <section class="services-list">
        <h3>Our Treatments</h3>
        <ul>
            <li>Spinal Decompression</li>
            <li>Postural Rehab</li>
            <li>Massage Therapy</li>
        </ul>
    </section>
</body>
</html>
"""

def test_scraper_schema_org_extraction():
    scraper = HealthcareWebScraper()
    lead = scraper.extract_from_html(SAMPLE_SCHEMA_ORG_HTML, "https://www.pacificdentalcare.com")

    assert lead is not None
    assert lead.name == "Pacific Dental Care"
    assert lead.phone == "+1-415-555-0199"
    assert lead.email == "info@pacificdentalcare.com"
    assert lead.city == "San Francisco"
    assert lead.state == "CA"
    assert lead.country == "United States"
    assert lead.postal_code == "94105"
    assert "General Dentistry" in lead.services
    assert lead.business_type == "Dental Clinic"

def test_scraper_fallback_extraction():
    scraper = HealthcareWebScraper()
    lead = scraper.extract_from_html(SAMPLE_FALLBACK_HTML, "https://www.smithchiro.com")

    assert lead is not None
    assert "Chiropractic" in lead.name
    assert lead.phone is not None
    assert "555-0144" in lead.phone
    assert lead.email == "contact@smithchiro.com"
    assert "Seattle" in (lead.city or lead.address or "")
    assert lead.business_type == "Chiropractic & Spine"
    assert any("Spinal" in s for s in lead.services)

def test_scraper_invalid_url():
    scraper = HealthcareWebScraper()
    assert scraper.validate_url("not-a-valid-url") is False
    assert scraper.validate_url("") is False
    assert scraper.validate_url("https://example.com") is True

def test_scraper_empty_html():
    scraper = HealthcareWebScraper()
    with pytest.raises(ValueError):
        scraper.extract_from_html("", "https://example.com")

def test_scrape_api_endpoint(client):
    mock_lead = LeadCreate(
        name="Oakland Family Health",
        business_type="Clinic",
        city="Oakland",
        state="CA",
        country="United States",
        phone="+1 510-555-0188",
        email="info@oaklandhealth.org",
        website="https://www.oaklandhealth.org",
        services=["General Practice", "Pediatrics"],
        source_url="https://www.oaklandhealth.org",
        description="Non-profit family health centre in Oakland.",
        status="NEW"
    )

    with patch.object(HealthcareWebScraper, "scrape", new_callable=AsyncMock) as mock_scrape:
        mock_scrape.return_value = mock_lead

        res = client.post("/api/v1/scrape", json={
            "urls": ["https://www.oaklandhealth.org"]
        })
        assert res.status_code == 200
        data = res.json()
        assert data["total_sources"] == 1
        assert data["leads_created"] == 1
        assert data["results"][0]["status"] == "created"
        assert data["results"][0]["name"] == "Oakland Family Health"

def test_scrape_api_empty_urls(client):
    res = client.post("/api/v1/scrape", json={"urls": []})
    assert res.status_code == 400
