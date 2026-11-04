# CareIntel AI — Architecture Documentation (Phase 1)

## 1. System Overview

**CareIntel AI** is a production-style healthcare lead intelligence platform designed to automate the discovery, extraction, normalization, and management of publicly available clinical business information.

Phase 1 provides the high-reliability foundation layer:
- Ingestion of public healthcare business URLs (or CSV batch uploads).
- Intelligent HTML extraction leveraging Schema.org JSON-LD and resilient regex fallback pipelines.
- Data validation, canonicalization, and deduplication.
- PostgreSQL database storage managed via SQLAlchemy ORM and Alembic migrations.
- High-performance FastAPI REST API endpoints.
- Interactive, responsive React + Vite SaaS dashboard.
- Pluggable AI Service abstraction designed for Phase 2 (Analysis) & Phase 3 (Opportunity Scoring).

---

## 2. End-to-End Data Pipeline

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
│ ├─ Tel: / Mailto: & Regex Heur. │
│ └─ Clinical Service Identifier  │
└───────────────┬─────────────────┘
                │ Raw Lead Data
                ▼
┌─────────────────────────────────┐
│ Data Normalization & Validation │
│ ├─ Domain Normalization         │
│ ├─ Phone/Email Validation       │
│ └─ Pydantic Schema Enforcement  │
└───────────────┬─────────────────┘
                │ Structured LeadCreate
                ▼
┌─────────────────────────────────┐
│ Deduplication & Persistence     │
│ ├─ Normalized Domain Match      │
│ ├─ Clinic Name + City Fallback  │
│ └─ SQLAlchemy Session           │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│ PostgreSQL / SQLite Database    │
│ (healthcare_leads table)        │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│ REST API (FastAPI)              │
│ ├─ Pagination & Full-text Search│
│ ├─ Batch Scraper Endpoint       │
│ └─ CSV Ingestion                │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│ React + Vite + Tailwind UI      │
│ (SaaS Executive Dashboard)      │
└─────────────────────────────────┘
```

---

## 3. Database Schema

The `healthcare_leads` table stores strictly publicly accessible business intelligence:

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `INTEGER` | Primary key, autoincrementing index |
| `name` | `VARCHAR(255)` | Clinic or practice legal/trading name |
| `business_type` | `VARCHAR(100)` | Classified category (e.g. Dental, Physiotherapy, Dermatology) |
| `address` | `VARCHAR(500)` | Physical street address |
| `city` | `VARCHAR(100)` | City / locality (indexed for fast location queries) |
| `state` | `VARCHAR(100)` | State, province, or region |
| `country` | `VARCHAR(100)` | Country jurisdiction |
| `postal_code` | `VARCHAR(50)` | Zip / postal code |
| `phone` | `VARCHAR(100)` | Public telephone number |
| `email` | `VARCHAR(255)` | Public business inquiry email |
| `website` | `VARCHAR(500)` | Formatted website URL |
| `normalized_website` | `VARCHAR(500)` | Domain-level canonical string for fast deduplication |
| `services` | `JSON` | List of clinical treatments, procedures, and offerings |
| `source_url` | `VARCHAR(1000)`| Original webpage URL scraped or imported |
| `source_type` | `VARCHAR(50)` | Source type (`WEBSITE`, `CSV_IMPORT`, `DIRECTORY`) |
| `description` | `TEXT` | Clinic overview and mission text |
| `status` | `VARCHAR(50)` | Status lifecycle (`NEW`, `VERIFIED`, `CONTACTED`, `UNQUALIFIED`) |
| `raw_data` | `JSON` | Scraped Schema.org metadata for auditability |
| `created_at` | `TIMESTAMP` | Record timestamp (UTC) |
| `updated_at` | `TIMESTAMP` | Last updated timestamp (UTC) |

---

## 4. Scraper Engine Architecture

CareIntel AI adopts an ethical, non-intrusive scraping pattern:
1. **Schema.org Priority**: Modern healthcare websites frequently deploy structured Schema.org JSON-LD tags (`MedicalBusiness`, `Dentist`, `Physician`, `Hospital`). The scraper detects and prioritizes these structured properties, guaranteeing high extraction accuracy.
2. **Graceful Fallbacks**: If structured JSON-LD is absent, the scraper falls back to OpenGraph meta tags, HTML `<address>` elements, `tel:` and `mailto:` anchors, and regular expressions for phone numbers and emails.
3. **Safety & Compliance**:
   - Strictly collects publicly available business contact information.
   - Enforces configurable HTTP timeouts (default 15 seconds) to avoid hanging workers.
   - Identifies itself with a standard user-agent.
   - Does not bypass authentication, paywalls, or CAPTCHAs.

---

## 5. Deduplication Strategy

To prevent duplicate lead entries across repeated scraping cycles:
1. **Normalized Domain Matching**:
   URLs are stripped of protocols (`http://`, `https://`), subdomains like `www.`, path segments, query strings, and port numbers. If `https://www.clinic.com/about` and `http://clinic.com/contact` are submitted, both resolve to `clinic.com`.
2. **Name + City Fallback**:
   If a website is omitted, a composite case-insensitive match on `(name, city)` prevents duplicate clinic creation.

---

## 6. AI Extensibility (Phase 2 & Phase 3 Roadmap)

To maintain clean separation of concerns and avoid coupling core business logic to a single AI provider, CareIntel AI uses an abstract interface:

```python
class BaseAIService(ABC):
    @abstractmethod
    async def analyze_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 2: Comprehensive clinical offering and tech stack analysis."""
        pass

    @abstractmethod
    async def identify_opportunities(self, lead_data: Dict[str, Any]) -> List[str]:
        """Phase 3: Detect expansion, patient engagement, and automation gaps."""
        pass

    @abstractmethod
    async def score_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 3: Compute fit score and priority tiers."""
        pass

    @abstractmethod
    async def generate_outreach(self, lead_data: Dict[str, Any], template_type: str) -> str:
        """Phase 4: Hyper-personalized outreach messaging."""
        pass
```

In Phase 1, `StubAIService` implements this contract with typed stubs, ready for zero-friction LLM integration in subsequent phases.
