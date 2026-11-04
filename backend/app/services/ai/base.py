from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseAIService(ABC):
    """
    Abstract AI Service Interface for CareIntel AI.
    Provides pluggable, decoupled LLM intelligence for clinical lead analysis,
    opportunity detection, scoring, and personalized outreach generation.
    """

    @abstractmethod
    async def analyze_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes a scraped healthcare business lead to extract:
        - business categorization and audience
        - factual digital observations
        - up to 3 concrete growth opportunities
        - AI lead score (0-100) with category and reason
        """
        pass

    @abstractmethod
    async def generate_outreach(
        self,
        lead_data: Dict[str, Any],
        analysis: Dict[str, Any],
        opportunities: List[Dict[str, Any]],
        score: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generates a concise (100-150 words), personalized outreach email
        grounded in the clinic's specific services and identified opportunities.
        Returns: {"subject": str, "body": str}
        """
        pass
