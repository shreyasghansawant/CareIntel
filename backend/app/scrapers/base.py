from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from app.schemas.lead import LeadCreate

class BaseScraper(ABC):
    """Abstract base class for all CareIntel AI scrapers."""

    @abstractmethod
    async def scrape(self, url: str) -> Optional[LeadCreate]:
        """Fetch and extract lead intelligence from a given target URL."""
        pass

    @abstractmethod
    def extract_from_html(self, html: str, url: str) -> Optional[LeadCreate]:
        """Parses raw HTML and extracts structured healthcare lead information."""
        pass

    def validate_url(self, url: str) -> bool:
        """Basic check for valid HTTP/HTTPS URL."""
        if not url or not isinstance(url, str):
            return False
        clean = url.strip().lower()
        return clean.startswith("http://") or clean.startswith("https://")
