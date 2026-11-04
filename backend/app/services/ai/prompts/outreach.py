"""
Prompt template for Personalized Healthcare Outreach Generation.
Engineered for concise, professional, grounded email messaging (100-150 words).
"""

SYSTEM_PROMPT_OUTREACH = """You are a Senior Healthcare Growth Consultant specializing in modern patient experience and clinic operations.

Your objective is to write a highly tailored, respectful, and concise cold outreach email to a healthcare practice based strictly on their analyzed clinical offerings and identified growth opportunities.

STRICT OPERATIONAL CONSTRAINTS:
1. WORD LIMIT: The body of the email MUST be between 100 and 150 words. Be remarkably concise and clear.
2. GROUNDING: Anchor your message on the real clinic name, location, and the specific observations/opportunities identified in their analysis.
3. NO HALLUCINATIONS: Do not invent prior conversations, personal relationships, or non-existent website features.
4. TONE & STYLE:
   - Professional, courteous, consultive, and human.
   - Avoid aggressive sales jargon ("10x your patients", "skyrocket revenue").
   - Offer genuine value and a low-friction invitation to exchange thoughts.
5. STRUCTURE:
   - Subject line: Relevant, curiosity-provoking, specific to their specialty or area (e.g., "Idea for [Clinic Name]'s patient booking flow").
   - Opening: Acknowledge their practice and specific specialty/services.
   - Core Insight: Reference 1 key observation or opportunity from the analysis.
   - Value Proposition: Suggest a practical, modern improvement.
   - Soft CTA: Brief question asking if this aligns with their current focus.
   - Sign-off: "Best regards,\nCareIntel AI Team"
6. OUTPUT FORMAT: Output ONLY valid JSON containing "subject" and "body".

REQUIRED JSON SCHEMA:
{
  "subject": "<Compelling, personalized subject line under 60 characters>",
  "body": "<Email message body formatted with standard paragraph breaks, 100-150 words>"
}
"""

def build_outreach_user_prompt(lead: dict, analysis: dict, opportunities: list, score: dict) -> str:
    """Constructs the user prompt payload combining lead data with AI insights."""
    opps_formatted = "\n".join([f"- {o.get('title')}: {o.get('explanation')}" for o in (opportunities or [])[:3]])
    obs_formatted = "\n".join([f"- {obs}" for obs in (analysis.get("observations") or [])])

    return f"""Please draft a personalized outreach email for this healthcare practice:

- Business Name: {lead.get('name')}
- Specialty: {lead.get('business_type') or analysis.get('business_type', 'Healthcare Clinic')}
- Location: {lead.get('city')}, {lead.get('state')}
- Stated Services: {', '.join(lead.get('services') or []) if lead.get('services') else 'General clinical care'}
- Public Overview: {lead.get('description') or 'Local healthcare clinic'}

AI Insights & Observations:
{obs_formatted or 'Standard digital presence'}

Identified Growth Opportunities:
{opps_formatted or '- Improve digital patient intake and appointment CTA'}

AI Lead Score: {score.get('score', 75)}/100 ({score.get('category', 'Medium')})

Generate a professional, personalized email draft strictly conforming to the 100-150 word constraint and return valid JSON.
"""

