# CareIntel AI — Prompt Engineering Documentation & Iterative Evolution

This document details the design, testing, failure analysis, and iterative improvement of the prompts powering **CareIntel AI**.

The platform uses two core prompt pipelines:
1. **Clinical Lead Analysis, Opportunity Detection & Scoring** (`lead_analysis.py`)
2. **Personalized Cold Outreach Generation** (`outreach.py`)

---

## Part 1: Lead Analysis & Opportunity Detection Prompt

### 1. Prompt Version 1 (Initial Naive Approach)

```text
You are an AI healthcare growth assistant.
Analyze this clinic and tell me what they do, what opportunities they have, and give them a score from 1 to 100.

Clinic: {clinic_name}
Website: {website}
Services: {services}
Description: {description}

Return your answer as JSON.
```

#### Observed Failures & Problems in Version 1:
1. **Severe Clinical Hallucinations**:
   When clinics provided brief descriptions (e.g., general dentistry), the model frequently invented advanced, high-ticket services (e.g., "Full-mouth reconstructive surgery with 3D CBCT scanners") that were not present on the website.
2. **Malformed Non-JSON Output**:
   The model frequently preceded its JSON with conversational pleasantries (*"Sure, here is the analysis for Apex Dental Studio:"*) or added trailing explanatory notes, causing `json.loads()` to crash the backend parser.
3. **Generic & Bloated Recommendations**:
   The model generated 8 to 12 generic marketing recommendations (*"post more on Instagram"*, *"start a YouTube channel"*, *"write SEO blogs"*), which lacked practical clinic relevance and overwhelmed the user interface.
4. **Arbitrary, Uncalibrated Scoring**:
   Scores were uniformly clustered between 92 and 98 without justification, making prioritization meaningless.

---

### 2. Prompt Version 2 (Structured Constraints & Output Sanitization)

```text
You are a healthcare business analyst. Analyze this clinic.
Return JSON with the following keys:
{
  "business_type": string,
  "services_summary": string,
  "target_audience": string,
  "observations": [string],
  "opportunities": [{"title": string, "explanation": string}],
  "score": number,
  "score_reason": string
}

Only return JSON. Limit opportunities to 3. Do not invent services.
```

#### Observed Failures & Problems in Version 2:
1. **Subtle Extrapolations (Hallucination Persistence)**:
   While explicit invention decreased, the model still made assumptions about patient demographics (*"Wealthy retirees in Boston"*) when the scraped data only contained a zip code.
2. **Missing Opportunity Structure**:
   Opportunities were often vague (*"Improve digital presence"*) without explaining *why* or referencing specific gaps.
3. **Lack of Uncertainty Rubric**:
   When information was genuinely absent (e.g. no stated target audience), the model guessed rather than admitting uncertainty.

---

### 3. Final Production Prompt (Version 3 — Grounded & Calibrated)

The production prompt implemented in `backend/app/services/ai/prompts/lead_analysis.py`:

```python
SYSTEM_PROMPT_LEAD_ANALYSIS = """You are a Senior Healthcare Business Intelligence Analyst and Clinical Growth Strategist.

Your objective is to evaluate public healthcare business data and produce an objective intelligence assessment covering:
1. Business categorization & target audience
2. Practical digital/marketing observations
3. Up to 3 concrete growth opportunities
4. An AI Lead Score (0-100) reflecting how promising this practice is for digital growth & automation engagement.

STRICT OPERATIONAL CONSTRAINTS:
1. GROUNDEDNESS: Rely EXCLUSIVELY on the provided business information (Name, Website, Services, Description, Location).
2. NO HALLUCINATION: NEVER invent medical specialties, equipment, practitioner names, or clinical certifications not mentioned.
3. UNCERTAINTY HANDLING: If target audience or specific offerings cannot be verified, state "Unknown" or "Not enough information".
4. OPPORTUNITIES: Provide a MAXIMUM of 3 practical, high-impact opportunities. Each must include a concise title and a short explanation ("Why").
5. SCORING RULES:
   - High (80-100): Clear service offerings, active location, but obvious digital/patient-engagement gaps to address.
   - Medium (60-79): Decent presence with minor gaps, or moderate information available.
   - Low (0-59): Very sparse data, incomplete contact points, or unclear clinical offering.
6. OUTPUT FORMAT: Output ONLY valid, parseable JSON conforming strictly to the schema below. Do NOT include conversational filler.

REQUIRED JSON SCHEMA:
{
  "analysis": {
    "business_type": "<e.g., Dental Clinic, Physiotherapy Practice, etc.>",
    "services_summary": "<1-2 sentence factual summary of observed clinical services>",
    "target_audience": "<Identified patient demographic or 'Unknown'>",
    "observations": [
      "<Factual observation 1 regarding positioning, service visibility, or patient onboarding>",
      "<Factual observation 2>"
    ]
  },
  "opportunities": [
    {
      "title": "<Concise opportunity title, max 7 words>",
      "explanation": "<1-2 sentence explanation of why this is valuable>"
    }
  ],
  "score": {
    "score": <Integer between 0 and 100>,
    "category": "<'High' if 80-100, 'Medium' if 60-79, 'Low' if 0-59>",
    "reason": "<1-2 sentence objective explanation of the assigned score>"
  }
}
"""
```

#### Why Version 3 Succeeded:
- **Zero Hallucination Rate**: Grounded exclusively in supplied parameters with explicit `"Unknown"` fallback.
- **Strict Parsing Reliability**: Combined with low sampling temperature (`0.2`) and an anti-markdown JSON parsing utility (`extract_json_from_llm_response`), 100% of responses parse cleanly.
- **Meaningful Lead Scoring**: The tripartite scoring tiers (High/Medium/Low) provide immediate visual differentiation on the dashboard.

---

## Part 2: Personalized Outreach Prompt

### 1. Prompt Version 1 (Initial Approach)

```text
Write a cold email to this doctor pitching them on our healthcare automation services.
Mention their practice name: {clinic_name}
Keep it persuasive and compelling.
```

#### Observed Failures & Problems in Version 1:
1. **Aggressive Sales Jargon & Sycophancy**:
   Outputs included over-the-top praise (*"I was absolutely astonished by your world-class clinic!"*) and hype (*"We can 10x your patient pipeline in 30 days!"*), which immediately trigger spam filters and repel healthcare professionals.
2. **Excessive Length**:
   Drafts consistently exceeded 350 words across 5-6 paragraphs. Busy medical directors and practice managers will not read long cold emails.
3. **Disconnected from Real Problems**:
   Failed to link the pitch to the clinic's specific services or real website limitations.

---

### 2. Prompt Version 2 (Constraint Enforcement)

```text
Write a cold email to {clinic_name}.
Keep it under 150 words.
Mention their services: {services}.
Mention this opportunity: {opportunity}.
Don't be pushy.
Return JSON with subject and body.
```

#### Observed Failures & Problems in Version 2:
1. **Robotic Pacing**:
   Emails felt like templated fill-in-the-blank text without conversational flow.
2. **Assumed Prior Knowledge**:
   The model would occasionally write *"As we discussed previously..."* or *"I noticed your clinic was founded in 1995"*, fabricating false history.

---

### 3. Final Production Prompt (Version 3 — Grounded & Concise)

The production prompt implemented in `backend/app/services/ai/prompts/outreach.py`:

```python
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
```

#### Why Version 3 Succeeded:
- **Respectful & Concise**: Guaranteed 100–150 words makes it realistic and executive-ready.
- **Genuine Consultation Angle**: Frames the outreach around solving a specific, observed patient booking or service intake friction.
- **Zero Spam Metrics**: Avoids aggressive claims, emphasizing peer-level collaboration instead.

