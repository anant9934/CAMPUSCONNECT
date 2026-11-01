# CampusConnect — LPU AI Campus Assistant
### Production-Structured Full-Stack Implementation (SRS Version 2.0)

> **One campus. One conversation. Reliable answers backed by evidence.**

CampusConnect is a dedicated institutional AI information assistant built specifically for **Lovely Professional University (LPU)**, Phagwara, Punjab, India. It provides students, visitors, and faculty with grounded, factual guidance regarding academics, examination schedules, hostel regulations, campus transport, fees, and healthcare facilities.

---

## 1. Key Architectural Decisions & Institutional Scope

- **Institution**: Lovely Professional University (LPU), Phagwara, Punjab (NH-44).
- **Language**: English only.
- **Student Access Model**: Completely public and anonymous (no registration number required, no login wall, zero personal tracking).
- **Admin Access Model**: Secure administrative portal with JWT authentication, role-based controls, and audit logging.
- **AI Provider**: Google Gemini Developer API (Free Tier optimized, `google-genai` Python SDK).
- **Frontend**: React 18 + Vite 6 + TypeScript + Tailwind CSS + Lucide Icons.
- **Backend**: Python 3.12 + FastAPI + Pydantic v2 + Uvicorn.
- **Database**: PostgreSQL with SQLAlchemy 2.0 + Alembic migrations (with automated SQLite fallback for instant zero-dependency local testing).
- **RAG Architecture**: Calibrated Hybrid Search fusing Keyword BM25 with LPU domain boosts, Scikit-learn TF-IDF, Dense Semantic Cosine Similarity, Source Freshness penalties, and anti-hallucination Grounding validation.
- **Design System**: Premium minimalist warm-white theme (`#FAFAF9` background, `#FFFFFF` surfaces, subtle `#E2E8F0` borders, LPU terracotta accents).

---

## 2. Quick Start & Local Execution

### Prerequisites
- Python 3.11+ or 3.12+ (CPython)
- Node.js v18+ or v20+ / v24+
- (Optional) PostgreSQL database server (if using PostgreSQL instead of SQLite)

---

### Step 1: Clone and Set Up Backend

```bash
# Navigate to project root
cd /path/to/cahtbot

# Create and activate Python virtual environment
python3 -m venv backend/.venv
source backend/.venv/bin/activate

# Install Python dependencies
pip install -r backend/requirements.txt greenlet

# Configure environment variables
cp .env.example .env
```

Edit `.env` to configure your Gemini API Key (optional for testing, as CampusConnect includes automatic verified FAQ fallback):
```env
GEMINI_API_KEY=your_google_ai_studio_api_key_here
GEMINI_MODEL=gemini-2.5-flash
DATABASE_URL=sqlite+aiosqlite:///./campusconnect.db
```

---

### Step 2: Initialize Database & Run Migrations

```bash
# Run Alembic migrations
PYTHONPATH=backend backend/.venv/bin/alembic -c backend/alembic.ini upgrade head

# Seed initial LPU knowledge base & default admin user
PYTHONPATH=backend backend/.venv/bin/python -c "
import asyncio
from app.core.database import AsyncSessionLocal
from app.services.seed_service import seed_database

async def seed():
    async with AsyncSessionLocal() as session:
        await seed_database(session)
    print('LPU Knowledge Base Seeded Successfully!')

asyncio.run(seed())
"
```

---

### Step 3: Build & Run Frontend

```bash
# Install frontend dependencies
cd frontend
npm install

# Build production assets
npm run build
cd ..
```

---

### Step 4: Run the Application

You can run the complete full-stack application (FastAPI backend serving both the REST API and the built React frontend) with a single command:

```bash
PYTHONPATH=backend backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **Public Web Application**: [http://localhost:8000](http://localhost:8000)
- **Interactive OpenAPI Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **System Health Status**: [http://localhost:8000/health](http://localhost:8000/health)
- **AI Quota & Circuit Breaker Health**: [http://localhost:8000/api/v1/health/ai](http://localhost:8000/api/v1/health/ai)

---

### Frontend Hot-Reload Development (Optional)
If modifying React code actively:
```bash
cd frontend
npm run dev
```
The Vite development server runs at `http://localhost:5173` and automatically proxies `/api` calls to FastAPI at `http://127.0.0.1:8000`.

---

## 3. Administrative Credentials & Control Panel

An administrative portal is embedded directly into the application for managing LPU institutional truth.

- **Admin Login Trigger**: Click **Admin** / **Admin Login** in the bottom sidebar or top-right navbar.
- **Default Username**: `admin`
- **Default Email**: `admin@lpu.co.in`
- **Default Password**: `CampusAdmin@2026`

### Protected Administrative Capabilities
1. **Overview Dashboard**: Real-time KPI metrics for approved FAQs, pending documents, total student queries, low-confidence queries, and student satisfaction percentages.
2. **Unified Repository (12 Data Types)**: Comprehensive governance screen supporting all 12 institutional schemas (`faq`, `policy`, `academic_schedule`, `contact_directory`, `facility_service`, `library_resource`, `placement_procedure`, `international_programme`, `research_facility`, `student_activity`, `grievance_procedure`, `official_notice`). Filter by type, inspect clause/page/contact metadata, review sensitive policies (attendance, debarment, fees), generate Gemini query variants without mutating facts, and approve/delete records.
3. **UMS Service Catalog (234 Entries)**: Administrative inspection and management of all 234 UMS menu items transcribed from student screenshots across 24 modules. Search, filter by module, inspect breadcrumbs, edit navigation paths, verification status, and deep link URLs.
4. **Action Workflows (24 Workflows)**: View and review guided campus workflows (Doctor, Hostel, Counselling, Library discussion rooms, RMS, Re-Appear, Fee receipts, etc.) with prerequisites and guardrails.
5. **Campus Wayfinding Directory**: Inspect and manage verified locations (Block 34, Block 13, Block 30 UniHospital, Central Library, UniMall, etc.) with room details, operating hours, and accessibility tags.
6. **FAQ Management**: Create, edit, delete, and review canonical LPU questions, paraphrases, answers, and official portal URLs.
7. **Knowledge Document Ingestion**: Upload PDF notices, DOCX handbooks, and TXT files. Automatic text cleaning, prompt-injection neutralization, overlapping chunking, chunk preview, and admin approval.
8. **Campus Categories**: Inspect and organize the 8 LPU campus categories.
9. **Source Review**: Audit source URLs, verified badges, and freshness dates.
10. **Unanswered Queries**: Inspect student questions where retrieval confidence was low, with one-click conversion into new FAQ drafts.
11. **Student Feedback**: Review thumbs up/down student evaluations and user comments.
12. **Analytics & Quota Monitor**: Live tracking of Google Gemini API requests, HTTP 429 rate limits, token usage, and circuit-breaker status.
13. **Settings & Instant Reindexing**: Force re-indexing of all approved FAQs, knowledge records, UMS services, and document chunks into memory.

---

## 4. RAG Intelligence & Grounding Pipeline

```
Student Question
      │
      ▼
1. Query Normalization & Acronym Resolution (UMS, RMS, Block 34, UniHospital)
      │
      ▼
2. Calibrated Hybrid Retrieval
   ├── Keyword Matcher (BM25 + LPU domain boosts: 3.5x for campus landmarks)
   ├── TF-IDF Vectorizer (N-gram 1-2 cosine similarity)
   └── Dense Semantic Projection (Concept cluster cosine affinity)
      │
      ▼
3. Confidence Evaluation & Calibration
   ├── High (>= 0.70): Proceed to Gemini Grounded Synthesis
   ├── Medium (0.45 - 0.69): Proceed with Synthesis & Verification
   └── Low / None (< 0.45): Trigger Verified Institutional Fallback / Clarification
      │
      ▼
4. Google Gemini Generation (Structured prompt enforcing strict 12-rule system instruction)
      │
      ▼
5. Post-Generation Grounding Validator
   ├── Reject forbidden ERP transaction assertions
   ├── Sanitize unauthorized external URLs to ums.lpu.in
   └── Attach structured verified citation cards & follow-up suggestions
      │
      ▼
Response Delivered to Student with 5 Transparent Thinking Steps
```

---

## 5. Automated Test Suite

Run the complete 24-test automated verification suite:

```bash
PYTHONPATH=backend backend/.venv/bin/pytest backend/tests/ -v
```

### Test Coverage Highlights
- `tests/test_ums_actions.py`: **SRS v3.0 UMS Action Suite**: 234 screenshot entries loaded, 24 action workflows loaded, campus wayfinding places, 8-mode Action Classifier (ANSWER, NAVIGATE, PREPARE, BOOK_HANDOFF, PERSONAL_RECORD, ESCALATE, EXECUTE, ABSTAIN), UMS service resolver & synonym matching, doctor booking vs emergency medical triage, RMS 5-stage grievance hierarchy, campus wayfinding matching, chat action card enrichment, public & admin UMS catalog endpoints.
- `tests/test_extended_knowledge.py`: Ingestion & validation of all 12 record types, deterministic SHA-256 duplicate detection, dynamic temporal expiration exclusion, sensitive governance tagging, type-specific citations (clause, page, email, phone, hours), Gemini question variant generation without altering facts, and admin CRUD/approval endpoints.
- `tests/test_retrieval.py`: Exact matching, natural paraphrases, LPU keyword boosts, and ungrounded query rejection.
- `tests/test_gemini_service.py`: Verified FAQ fallback when unconfigured, HTTP 429 quota exhaustion & circuit-breaker tripping, anti-hallucination forbidden claim detection, unapproved URL sanitization.
- `tests/test_security.py`: Bcrypt password hashing, JWT bearer generation and expiry, prompt injection neutralization in document text, file upload format restriction.
- `tests/test_api.py`: System health endpoints, campus categories, end-to-end anonymous chat flow with 5 thinking steps and citations, cross-session isolation, admin login & dashboard metrics.

---

## 6. Project Structure

```
cahtbot/
├── backend/
│   ├── alembic/                 # Alembic database migrations
│   │   ├── versions/
│   │   │   └── 001_initial_schema.py
│   │   └── env.py
│   ├── app/
│   │   ├── api/v1/              # Versioned API routes
│   │   │   ├── endpoints/       # Chat, Sessions, FAQs, Docs, Admin, Analytics
│   │   │   └── router.py
│   │   ├── core/                # Config, Security (JWT/bcrypt), Database
│   │   ├── models/              # 12 SQLAlchemy models
│   │   ├── schemas/             # Pydantic v2 validation models
│   │   ├── services/
│   │   │   ├── rag/             # Modular Hybrid RAG engine
│   │   │   │   ├── keyword_search.py
│   │   │   │   ├── tfidf_search.py
│   │   │   │   ├── semantic_search.py
│   │   │   │   ├── confidence.py
│   │   │   │   ├── source_validator.py
│   │   │   │   └── hybrid_search.py
│   │   │   ├── gemini_service.py # Google Gen AI SDK + Quota circuit breaker
│   │   │   ├── grounding_service.py
│   │   │   ├── document_service.py
│   │   │   └── seed_service.py
│   │   └── main.py              # FastAPI application entrypoint
│   ├── requirements.txt         # Python dependencies
│   └── tests/                   # 16 automated tests
├── frontend/
│   ├── src/
│   │   ├── components/          # Sidebar, WelcomeHero, ChatArea, ThinkingIndicator, Composer
│   │   │   └── admin/           # AdminDashboard, AdminLoginModal
│   │   ├── services/api.ts      # API client & session manager
│   │   ├── types/               # TypeScript interfaces
│   │   ├── App.tsx              # Application coordinator
│   │   └── main.tsx
│   ├── package.json
│   ├── tailwind.config.js       # Warm white & LPU terracotta design tokens
│   └── vite.config.ts
├── ARCHITECTURE.md              # System architecture, sequence diagrams, ER model
├── IMPLEMENTATION_PLAN.md       # Master engineering plan
├── TASK_TRACKER.md              # Detailed milestone tracking
├── TEST_REPORT.md               # Automated testing report
├── .env.example                 # Documented environment variables template
└── README.md                    # System documentation
```

---

## 7. Institutional Truth & Safety Guarantees

CampusConnect guarantees that:
1. No student identity or registration number is ever required to access campus knowledge.
2. Unapproved or pending documents/FAQs are never queryable by public students.
3. The AI never fabricates fee amounts, exam dates, or university policies.
4. If the Gemini API key is missing or quota is exhausted, verified institutional FAQ answers are returned directly with official portal citations.

