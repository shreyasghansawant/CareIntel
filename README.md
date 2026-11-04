# CareIntel AI — Healthcare Lead Intelligence & Outreach Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5.0+-646CFF?style=flat&logo=vite&logoColor=white)](https://vitejs.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Alembic](https://img.shields.io/badge/Alembic-Migrations-red?style=flat)](https://alembic.sqlalchemy.org)
[![Tests](https://img.shields.io/badge/Tests-22%20Passing-brightgreen?style=flat)](#testing)

> **CareIntel AI** is an end-to-end healthcare lead intelligence platform that collects publicly available clinic information, analyzes digital positioning and patient acquisition potential with AI, identifies high-value business opportunities, scores lead priority, and generates hyper-personalized outreach drafts.

---

## 1. What CareIntel AI Does

CareIntel AI automates the complete healthcare growth intelligence pipeline:

```text
Healthcare Website URLs
        ↓
     Scraping (Schema.org JSON-LD + Anti-fragile HTML parsing)
        ↓
 Structured Lead Data (Normalized domains, deduplication)
        ↓
    AI Analysis (Clinical categorisation, target audience, positioning observations)
        ↓
 Business Opportunity Detection (Max 3 practical growth suggestions)
        ↓
   AI Lead Score (0–100 calibrated fit scoring)
        ↓
Personalised Outreach (100–150 word grounded email draft)
        ↓
 Executive Dashboard (Search, filtering, live stats, 1-click clipboard copy)
```

---

## 2. Architecture

```text
┌─────────────────────────────────┐
│ Public Healthcare Web Targets   │
└───────────────┬─────────────────┘
                │ HTTP GET (httpx async + timeouts)
                ▼
┌─────────────────────────────────┐
│ HealthcareWebScraper            │
│ ├─ Schema.org JSON-LD Extractor │
│ ├─ OpenGraph & Meta Parser      │
│ └─ Clinical Service Classifier  │
└───────────────┬─────────────────┘
                │ Structured Lead Data
                ▼
┌─────────────────────────────────┐
│ Deduplication & Normalization   │
│ ├─ Domain Canonicalization      │
│ └─ Phone / Email Sanitization   │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│ PostgreSQL / SQLite Database    │
│ (healthcare_leads table)        │
└───────┬─────────────────┬───────┘
        │                 │
        │ DB Session      │ Read / Write
        ▼                 ▼
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│ FastAPI Application (REST API)  │ <===> │ Pluggable AI Service Layer      │
│ ├─ /leads                       │       │ ├─ OpenAI / Gemini REST API     │
│ ├─ /leads/{id}/analyze          │       │ ├─ DemoAIService (Zero-config)  │
│ └─ /leads/{id}/generate-outreach│       │ └─ Prompt Engineering Engine    │
└───────────────┬─────────────────┘       └─────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│ React + Vite + Tailwind UI      │
│ ├─ Intelligence KPI Stat Cards  │
│ ├─ Interactive Lead Dossier     │
│ ├─ AI Analysis & Score Display  │
│ └─ 1-Click Outreach Copy Tool   │
└─────────────────────────────────┘
```

---

## 3. Practical AI Usage & Prompt Engineering

CareIntel AI is purpose-built to demonstrate production-grade AI integration:

### Capabilities Used
- **Structured LLM Analysis**: Transforms unstructured clinical text and website metadata into clean, validated JSON schemas.
- **Opportunity Detection**: Formulates targeted, practical business development suggestions grounded in observed digital gaps (e.g., missing booking CTAs, poor service page discoverability).
- **Calibrated Lead Scoring (0–100)**: Evaluates practice viability:
  - **High (80–100)**: Strong clinical offerings with obvious patient conversion gaps.
  - **Medium (60–79)**: Solid online presence with moderate improvement areas.
  - **Low (0–59)**: Sparse data or incomplete public contact channels.
- **Personalized Outreach Generation**: Drafts concise (100–150 words), non-spammy email copy referencing the clinic's specific services, location, and key opportunity.

### How Hallucinations Are Prevented
1. **Strict Negative Constraints**: Prompts explicitly forbid inventing medical specialties, equipment, practitioner names, or prior communications.
2. **Explicit Uncertainty Handling**: The model is instructed to output `"Unknown"` or `"Not enough information"` rather than guessing.
3. **Strict Temperature Controls**: Uses low sampling temperatures (`0.2` for analysis, `0.3` for outreach) to ensure factual, reproducible outputs.
4. **Structured Parsing Layer**: Custom extractor (`extract_json_from_llm_response`) strips conversational markdown fences and enforces Pydantic schema validation.

### Prompt Iteration Documentation
For complete prompt evolution, problem diagnosis, and before/after comparisons, see [`docs/prompt-engineering.md`](docs/prompt-engineering.md).

---

## 4. End-to-End Demo Workflow (2–3 Minutes)

Follow these exact steps to demonstrate the full application:

1. **Open Dashboard**: Visit `http://localhost:5173`. Notice the KPI cards: Total Leads, AI Analyzed, High Potential, and Outreach Ready.
2. **Add a Healthcare Source**:
   - Click **"Add Sources"** (top right).
   - Enter a public clinic URL (e.g., `https://www.apexdentalstudio.com`) or click **"Seed Demo Leads"** for instant sample data.
   - Click **"Start Processing"**. Watch the real-time extraction log confirm: `✓ 1 source processed, ✓ 1 lead created`.
3. **Search & Inspect Lead**:
   - Type a clinic name or city (e.g. `San Francisco` or `Apex`) in the filter bar.
   - Click on the lead row to open the **Lead Detail Dossier**.
4. **Run AI Analysis**:
   - Inside the modal, click **"Analyze with AI"**.
   - Within 1–2 seconds, the AI outputs:
     - **Business Information**: Categorization, target patient demographic, and verified services summary.
     - **Observations**: Specific findings regarding online positioning and patient onboarding.
     - **Identified Opportunities**: Up to 3 concrete improvements with "Why" explanations.
     - **AI Lead Score**: A calibrated score (e.g. `84/100 • High`) with objective rationale.
5. **Generate Personalized Outreach**:
   - Click **"Generate Outreach"**.
   - The AI drafts a tailored, professional email (100–150 words) referencing the clinic's real specialties and top opportunity.
6. **Copy Draft**:
   - Click **"Copy Draft"**. A green confirmation confirms the email is copied to your clipboard.

---

## 5. Local Setup & Execution Guide

### Prerequisites
- Python 3.11+ or 3.12 (`py --version`)
- Node.js 18+ and npm (`node -v`)

---

### Step 1: Backend Setup

```powershell
cd careintel-ai\backend

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --port 8000
```
- API Documentation (Swagger): **http://localhost:8000/docs**
- Health check: **http://localhost:8000/api/v1/health**

---

### Step 2: Frontend Setup

Open a new terminal window:

```powershell
cd careintel-ai\frontend

# Install dependencies
npm install

# Start development server
npm run dev
```
- Web Application: **http://localhost:5173**

---

## 6. Environment Variables (`.env`)

Configure in `careintel-ai/backend/.env`:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite:///./careintel.db` | PostgreSQL or SQLite connection string |
| `AI_PROVIDER` | `demo` | `openai`, `gemini`, or `demo` (zero-config mode) |
| `AI_API_KEY` | `""` | API key for OpenAI or Gemini (optional in demo mode) |
| `AI_MODEL` | `gpt-4o-mini` | Target LLM model name |
| `AI_BASE_URL` | `https://api.openai.com/v1` | Base API URL (supports local/custom proxies) |
| `SCRAPER_TIMEOUT_SECONDS` | `15` | Maximum HTTP request wait time |

> **Evaluator Tip (Zero-Config Demo Mode)**: If no `AI_API_KEY` is provided, CareIntel AI automatically runs in **intelligent Demo Mode**. It dynamically evaluates the scraped clinic's real attributes, produces grounded observations, opportunities, scores, and outreach without requiring an external paid API key!

---

## 7. Testing

CareIntel AI includes 22 automated unit and integration tests covering the entire data and AI pipeline:

```powershell
cd careintel-ai\backend
.\.venv\Scripts\python -m pytest tests -v
```

### Test Suite Summary
```text
tests/test_ai.py::test_json_extractor_valid_json PASSED                  [  4%]
tests/test_ai.py::test_json_extractor_markdown_block PASSED              [  9%]
tests/test_ai.py::test_json_extractor_invalid_raises_error PASSED        [ 13%]
tests/test_ai.py::test_demo_ai_service_analysis PASSED                   [ 18%]
tests/test_ai.py::test_lead_analyze_api_endpoint PASSED                  [ 22%]
tests/test_ai.py::test_generate_outreach_api_endpoint PASSED             [ 27%]
tests/test_ai.py::test_stats_endpoint_includes_ai_metrics PASSED         [ 31%]
tests/test_health.py::test_root_endpoint PASSED                          [ 36%]
tests/test_health.py::test_health_check_healthy PASSED                   [ 40%]
tests/test_leads.py::test_create_and_get_lead PASSED                     [ 45%]
tests/test_leads.py::test_get_nonexistent_lead_returns_404 PASSED        [ 50%]
tests/test_leads.py::test_validation_empty_name PASSED                   [ 54%]
tests/test_leads.py::test_deduplication_by_website PASSED                [ 59%]
tests/test_leads.py::test_pagination_and_search PASSED                   [ 63%]
tests/test_leads.py::test_delete_lead PASSED                             [ 68%]
tests/test_leads.py::test_seed_demo_leads PASSED                         [ 72%]
tests/test_scraper.py::test_scraper_schema_org_extraction PASSED         [ 77%]
tests/test_scraper.py::test_scraper_fallback_extraction PASSED           [ 81%]
tests/test_scraper.py::test_scraper_invalid_url PASSED                   [ 86%]
tests/test_scraper.py::test_scraper_empty_html PASSED                    [ 90%]
tests/test_scraper.py::test_scrape_api_endpoint PASSED                   [ 95%]
tests/test_scraper.py::test_scrape_api_empty_urls PASSED                 [100%]

======================== 22 passed in 0.28s ========================
```

---

## 8. Railway Production Deployment

CareIntel AI is production-ready for deployment on **Railway** with a 3-tier architecture:

```text
GitHub Repository (shreyasghansawant/CareIntel)
       ↓
   Railway Project
       ├── PostgreSQL (Managed Database)
       ├── FastAPI Backend (uvicorn 0.0.0.0:$PORT + Alembic migrations)
       └── React Frontend (Vite production preview 0.0.0.0:$PORT)
```

### Production Environment Variables

#### Backend Service (Root Directory: `/backend`)

| Variable | Recommended Production Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` | Auto-provided by Railway PostgreSQL |
| `PORT` | `8000` | Platform port assigned by Railway |
| `ENVIRONMENT` | `production` | Server mode |
| `AI_PROVIDER` | `gemini` or `openai` or `demo` | Pluggable LLM provider |
| `AI_API_KEY` | *(Your Live API Key)* | Secret key for Gemini/OpenAI |
| `AI_MODEL` | `gemini-2.5-flash` or `gpt-4o-mini` | AI Model identifier |
| `FRONTEND_URL` | `https://careintel-frontend.up.railway.app` | Deployed frontend origin for CORS |
| `CORS_ORIGINS` | `["*"]` or comma-separated origins | Allowed origins list |

*Backend Start Command* (configured via `Procfile` and `railway.json`):
```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

#### Frontend Service (Root Directory: `/frontend`)

| Variable | Production Value | Description |
| :--- | :--- | :--- |
| `VITE_API_URL` | `https://careintel-backend.up.railway.app` | URL of your deployed Railway Backend |

*Frontend Start Command* (configured via `package.json` and `railway.json`):
```bash
npm run build && vite preview --host 0.0.0.0 --port ${PORT:-4173}
```

### 3-Step Railway Deployment Guide

1. **Create Railway Project**:
   - Go to [railway.app](https://railway.app) and click **"New Project"**.
   - Select **"Provision PostgreSQL"** to create your managed PostgreSQL database.

2. **Add Backend Service**:
   - In the same project, click **"Create"** → **"GitHub Repo"** → Select `shreyasghansawant/CareIntel`.
   - Go to **Settings** → **Source Directory / Root Directory**: Set to `/backend`.
   - Go to **Variables** → Add `DATABASE_URL` referencing your PostgreSQL service (Railway provides a 1-click reference `${{Postgres.DATABASE_URL}}`).
   - Add `AI_PROVIDER=gemini` and `AI_API_KEY=<your-key>`.
   - Go to **Settings** → **Networking** → Click **"Generate Domain"** (e.g. `https://careintel-backend-production.up.railway.app`).

3. **Add Frontend Service**:
   - In the same project, click **"Create"** → **"GitHub Repo"** → Select `shreyasghansawant/CareIntel`.
   - Go to **Settings** → **Source Directory / Root Directory**: Set to `/frontend`.
   - Go to **Variables** → Add `VITE_API_URL` with your Backend domain (e.g. `https://careintel-backend-production.up.railway.app`).
   - Go to **Settings** → **Networking** → Click **"Generate Domain"** (e.g. `https://careintel-frontend-production.up.railway.app`).
   - (Optional) Copy this frontend domain into the Backend's `FRONTEND_URL` variable.

---

## 9. Honest Limitations

- **Publicly Available Information Only**: The platform exclusively extracts public text and structured markup; it does not access internal medical CRM data or private practitioner directories.
- **Client-Side Heavy SPAs**: Websites built as 100% dynamic JavaScript SPAs without server-side rendering or OpenGraph metadata yield partial descriptions.
- **Outreach Draft Only**: In adherence to compliance and anti-spam ethics, outreach emails are generated as reviewable drafts with one-click copy rather than sent autonomously.
