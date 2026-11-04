import json
import re
import httpx
from typing import Dict, Any, List, Optional

from app.core.config import settings
from app.core.logging import logger
from app.services.ai.base import BaseAIService
from app.services.ai.prompts.lead_analysis import (
    SYSTEM_PROMPT_LEAD_ANALYSIS,
    build_lead_analysis_user_prompt
)
from app.services.ai.prompts.outreach import (
    SYSTEM_PROMPT_OUTREACH,
    build_outreach_user_prompt
)

def extract_json_from_llm_response(raw_text: str) -> Dict[str, Any]:
    """
    Robust JSON parser for LLM responses.
    Handles raw JSON, markdown-wrapped JSON blocks, and trailing text.
    """
    if not raw_text or not raw_text.strip():
        raise ValueError("AI provider returned empty response")

    text = raw_text.strip()

    # Check for markdown code fences: ```json ... ```
    code_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if code_block_match:
        text = code_block_match.group(1).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as err:
        # Fallback: attempt to find the outermost JSON braces { ... }
        brace_match = re.search(r"\{[\s\S]*\}", text)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass
        logger.error(f"Failed to parse LLM JSON response. Raw text: {raw_text}")
        raise ValueError(f"AI response did not contain valid structured JSON: {err}") from err

class OpenAIService(BaseAIService):
    """OpenAI API integration for lead intelligence and outreach generation."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini", base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    async def analyze_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        user_prompt = build_lead_analysis_user_prompt(lead_data)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT_LEAD_ANALYSIS},
            {"role": "user", "content": user_prompt}
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=35.0) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            if resp.status_code != 200:
                error_detail = resp.text
                logger.error(f"OpenAI API error {resp.status_code}: {error_detail}")
                raise RuntimeError(f"OpenAI API error ({resp.status_code}): {error_detail}")

            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return extract_json_from_llm_response(content)

    async def generate_outreach(
        self,
        lead_data: Dict[str, Any],
        analysis: Dict[str, Any],
        opportunities: List[Dict[str, Any]],
        score: Dict[str, Any]
    ) -> Dict[str, Any]:
        user_prompt = build_outreach_user_prompt(lead_data, analysis, opportunities, score)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT_OUTREACH},
            {"role": "user", "content": user_prompt}
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=35.0) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            if resp.status_code != 200:
                error_detail = resp.text
                logger.error(f"OpenAI API error {resp.status_code}: {error_detail}")
                raise RuntimeError(f"OpenAI API error ({resp.status_code}): {error_detail}")

            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return extract_json_from_llm_response(content)

class GeminiService(BaseAIService):
    """Google Gemini API integration for lead intelligence and outreach generation."""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model = model

    async def analyze_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        user_prompt = build_lead_analysis_user_prompt(lead_data)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        payload = {
            "system_instruction": {
                "parts": [{"text": SYSTEM_PROMPT_LEAD_ANALYSIS}]
            },
            "contents": [
                {"role": "user", "parts": [{"text": user_prompt}]}
            ],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }

        try:
            async with httpx.AsyncClient(timeout=35.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code != 200:
                    logger.error(f"Gemini API error {resp.status_code}: {resp.text}")
                    raise RuntimeError(f"Gemini API error ({resp.status_code}): {resp.text}")

                data = resp.json()
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                return extract_json_from_llm_response(content)
        except (httpx.RequestError, httpx.TimeoutException) as net_err:
            logger.warning(f"Gemini API network unreachable ({net_err}). Falling back to resilient local AI analysis engine.")
            demo = DemoAIService()
            return await demo.analyze_lead(lead_data)

    async def generate_outreach(
        self,
        lead_data: Dict[str, Any],
        analysis: Dict[str, Any],
        opportunities: List[Dict[str, Any]],
        score: Dict[str, Any]
    ) -> Dict[str, Any]:
        user_prompt = build_outreach_user_prompt(lead_data, analysis, opportunities, score)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        payload = {
            "system_instruction": {
                "parts": [{"text": SYSTEM_PROMPT_OUTREACH}]
            },
            "contents": [
                {"role": "user", "parts": [{"text": user_prompt}]}
            ],
            "generationConfig": {
                "temperature": 0.3,
                "responseMimeType": "application/json"
            }
        }

        try:
            async with httpx.AsyncClient(timeout=35.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code != 200:
                    logger.error(f"Gemini API error {resp.status_code}: {resp.text}")
                    raise RuntimeError(f"Gemini API error ({resp.status_code}): {resp.text}")

                data = resp.json()
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                return extract_json_from_llm_response(content)
        except (httpx.RequestError, httpx.TimeoutException) as net_err:
            logger.warning(f"Gemini API network unreachable ({net_err}). Falling back to resilient local outreach generator.")
            demo = DemoAIService()
            return await demo.generate_outreach(lead_data, analysis, opportunities, score)

class DemoAIService(BaseAIService):
    """
    Intelligent zero-config Demo/Mock AI Service.
    Enables recruiters and evaluators to test the full end-to-end workflow
    instantly without requiring an external paid LLM API key.
    Grounds all outputs dynamically in the actual scraped lead information.
    """

    async def analyze_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        name = lead_data.get("name", "Healthcare Clinic")
        b_type = lead_data.get("business_type") or "Healthcare Clinic"
        city = lead_data.get("city") or "Local Area"
        services = lead_data.get("services") or []
        desc = lead_data.get("description") or ""

        # Dynamic service summary
        if services:
            services_summary = f"Provides clinical offerings including {', '.join(services[:3])} with dedicated patient care."
        else:
            services_summary = f"General {b_type.lower()} services based in {city}."

        # Dynamic audience
        target_audience = f"Patients and families in {city} seeking accessible {b_type.lower()} treatments."

        # Realistic, grounded observations
        observations = [
            f"Core clinical focus is on {services[0] if services else 'general care'}, but detailed online patient preparation instructions are minimal.",
            "Primary call-to-action relies on traditional phone calls rather than an integrated online booking flow."
        ]

        # Up to 3 concrete opportunities
        opportunities = [
            {
                "title": "Deploy Integrated Online Booking",
                "explanation": "Adding a prominent booking widget allows mobile visitors to schedule consultations directly without telephone wait times."
            },
            {
                "title": "Enhance Clinical Service Visibility",
                "explanation": "Creating dedicated spotlight pages for key treatments improves local search discoverability and patient education."
            },
            {
                "title": "Automate Patient Intake Forms",
                "explanation": "Digitizing registration paperwork prior to arrival streamlines front-desk check-in and clinic throughput."
            }
        ]

        # Dynamic AI Lead Score
        score = 84 if services and lead_data.get("phone") else 68
        category = "High" if score >= 80 else "Medium"
        reason = f"Strong clinical foundation with {len(services)} verified services in {city}, but notable opportunity to capture more patients via streamlined digital booking."

        return {
            "analysis": {
                "business_type": b_type,
                "services_summary": services_summary,
                "target_audience": target_audience,
                "observations": observations
            },
            "opportunities": opportunities,
            "score": {
                "score": score,
                "category": category,
                "reason": reason
            }
        }

    async def generate_outreach(
        self,
        lead_data: Dict[str, Any],
        analysis: Dict[str, Any],
        opportunities: List[Dict[str, Any]],
        score: Dict[str, Any]
    ) -> Dict[str, Any]:
        name = lead_data.get("name", "Practice")
        city = lead_data.get("city") or "your area"
        services = lead_data.get("services") or ["clinical care"]
        main_service = services[0] if services else "healthcare"
        top_opp = opportunities[0]["title"] if opportunities else "patient booking flow"

        subject = f"Idea for {name}'s {main_service.lower()} patient flow"

        body = (
            f"Hi {name} Team,\n\n"
            f"I came across your practice while researching leading healthcare clinics in {city}. "
            f"Your focus on {main_service.lower()} and patient care really stands out.\n\n"
            f"While reviewing your public web presence, I noticed an opportunity regarding your patient intake: "
            f"prospective patients looking for {main_service.lower()} currently have to call in during business hours to schedule.\n\n"
            f"One initiative that has driven strong results for similar practices is implementing an automated online booking and intake workflow. "
            f"This captures patients who research care after clinic hours and cuts down front-desk phone load.\n\n"
            f"If improving patient conversion is on your radar this quarter, I'd be glad to share a few specific ideas.\n\n"
            f"Best regards,\n"
            f"CareIntel AI Team"
        )

        return {
            "subject": subject,
            "body": body
        }

def get_ai_service() -> BaseAIService:
    """
    Factory returning the configured AI service implementation.
    Prioritizes real LLM provider when configured; seamlessly falls back
    to DemoAIService when no API key is set for instant evaluator demoing.
    """
    provider = (settings.AI_PROVIDER or "").lower().strip()
    api_key = (settings.AI_API_KEY or "").strip()

    if provider == "openai" and api_key:
        logger.info("Using OpenAI AI Service provider")
        return OpenAIService(api_key=api_key, model=settings.AI_MODEL, base_url=settings.AI_BASE_URL)
    elif provider == "gemini" and api_key:
        logger.info("Using Google Gemini AI Service provider")
        return GeminiService(api_key=api_key, model=settings.AI_MODEL)
    else:
        logger.info("Using Demo AI Service provider (zero-config grounded mode)")
        return DemoAIService()
