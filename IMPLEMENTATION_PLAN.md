# CampusConnect — LPU AI Campus Assistant
## Implementation Plan (SRS v2.0 Production-Structured Full-Stack Implementation)

### 1. Project Overview & Institutional Scope
- **Institution**: Lovely Professional University (LPU), Phagwara, Punjab, India.
- **Audience**: LPU students, prospective students, visitors, faculty, and administrative staff.
- **Language**: English only.
- **Student Access Model**: Completely public and anonymous (no login, no registration number required, isolated session tokens).
- **Admin Access Model**: Secure administrative portal with JWT authentication, role-based access, and audit logging.
- **Core Technology Stack**:
  - **Frontend**: React 18 / 19 + Vite + TypeScript + Tailwind CSS + Lucide React.
  - **Backend**: Python 3.12 + FastAPI + Pydantic v2 + Uvicorn.
  - **Database**: PostgreSQL with SQLAlchemy 2.0 (async/sync compatible) + Alembic migrations + SQLite fallback compatibility for zero-config testing.
  - **AI Provider**: Google Gen AI SDK (`google-genai`), using Gemini Flash models with free-tier resilience, exponential backoff, circuit breaking, and verified fallback.
  - **Information Retrieval**: Multi-stage Hybrid Retrieval Engine (BM25/Keyword, TF-IDF, Dense Semantic Cosine Similarity, Calibrated Confidence, Grounding Verification).

---

### 2. Repository Initial State & Findings
- **Workspace**: `/Users/quantum/Desktop/cahtbot` (Initial state: empty, no existing files or git repository).
- **Toolchains Verified**:
  - Python: 3.12.15 (`/Users/quantum/.local/bin/python3.12`, `uv` available).
  - Node.js: v24.22.0 (`/Users/quantum/.local/bin/node`, npm 10.9.2).
- **Secrets Audit**: Clean (0 existing files, 0 committed secrets).

---

### 3. Execution Phases & Milestones

#### Phase 1: Architecture, Repository Setup & Foundations
- Initialize Git repository and standard structure.
- Define architecture specifications (`ARCHITECTURE.md`).
- Define task tracker (`TASK_TRACKER.md`).
- Establish project directory structure (`backend/`, `frontend/`, `docs/`, `scripts/`).

#### Phase 2: Design System & React Frontend Architecture
- Set up Vite + React + TypeScript in `frontend/`.
- Configure Tailwind CSS with a warm white, minimalist institutional palette (Warm white `#FAFAF9`, neutral surface `#FFFFFF`, crisp borders `#E2E8F0`, deep slate text `#0F172A`, subtle LPU accents).
- Build Modular UI Components:
  - **Sidebar**: CampusConnect logo, New Chat, Search, Home, Recent Chats, Campus Services, About, Privacy, Admin link.
  - **Chat Workspace**: Welcome hero, prompt suggestion chips, campus service category grid, central composer with auto-resize, voice/file buttons, disclaimers.
  - **Active Conversation View**: User bubbles, AI message streaming with markdown formatting, multi-step thinking indicator, source citation cards, action toolbars (Copy, Thumbs Up/Down, Retry, Follow-up prompts).
  - **Thinking Progress Tracker**: 5 explicit states (1. Preparing question, 2. Searching LPU knowledge, 3. Analysing retrieved information, 4. Generating response, 5. Completed).
  - **Modals**: About LPU CampusConnect, Privacy & Data Disclaimer (Gemini Free Tier notice), Search Dialog.
  - **Admin Interface**: Complete dashboard for FAQs, Document Ingestion, Categories, Unanswered Queries, Analytics, and Settings.

#### Phase 3: FastAPI Backend & Database Schema
- Set up Python virtual environment (`uv` / `venv`) with dependencies:
  - `fastapi`, `uvicorn`, `pydantic`, `pydantic-settings`, `sqlalchemy`, `alembic`, `asyncpg`, `psycopg2-binary`, `python-jose`, `passlib[bcrypt]`, `python-multipart`, `google-genai`, `scikit-learn`, `numpy`, `pytest`, `httpx`, `pypdf`, `python-docx`.
- Implement SQLAlchemy 2.0 models for the 12 required tables:
  1. `admin_users`
  2. `categories`
  3. `faqs`
  4. `faq_sources`
  5. `knowledge_documents`
  6. `knowledge_chunks`
  7. `anonymous_sessions`
  8. `conversations`
  9. `messages`
  10. `feedback`
  11. `query_logs`
  12. `audit_logs`
- Set up Alembic migration environment and baseline migration.
- Configure multi-dialect database engine supporting PostgreSQL (`postgresql+asyncpg://` or `postgresql://`) and local SQLite testing (`sqlite+aiosqlite:///` or `sqlite:///`).

#### Phase 4: LPU Knowledge Base & Seed Data
- Create demonstration dataset covering key LPU campus domains:
  - Academics (Curriculum, UMS Portal, Attendance 75% rule, CA/ETE components, Grading system).
  - Examinations (Date sheet download via UMS, re-evaluations, admit cards, Block 34 exam cell).
  - Hostel & Residential Life (Hostel check-in/out, night passes, laundry, mess menu, warden contacts).
  - Campus Transport & Bus Routes (Campus bus service, city routes Jalandhar/Phagwara/Ludhiana, bus pass registration).
  - Fees & Financial Services (Fee payment via portal, late fee policies, scholarship criteria, fee slip download).
  - Campus Life & Student Services (UniMall, UniHospital 24x7 emergency, Student Welfare Wing Block 13, Library Block 37, Division of Student Affairs).
- Enforce strict approval state machine: only `is_approved = True` and `status = 'approved'` records are queryable by public students.
- Ingestion pipeline for PDF, DOCX, and TXT documents with chunking, sanitization, page preservation, and admin review.

#### Phase 5: Modular Hybrid Retrieval Engine
- Build dedicated retrieval modules:
  - `keyword_search.py`: Lexical matching with LPU-specific token boost (e.g., UMS, RMS, Block 34, UniMall, UniHospital).
  - `tfidf_search.py`: Corpus TF-IDF vectorization across canonical questions, answers, keywords, and document chunks.
  - `semantic_search.py`: Dense semantic similarity (Gemini embeddings or calibrated vector distance with local fallback).
  - `confidence.py`: Dynamic confidence scoring, min-max score calibration, and strict confidence categorization (High >= 0.75, Medium 0.50-0.74, Low 0.35-0.49, None < 0.35).
  - `source_validator.py`: Integrity verification, link verification, approval confirmation, and freshness check.
  - `hybrid_search.py`: Unified fusion combining weighted keyword, TF-IDF, and semantic components with category filtering.

#### Phase 6: Gemini API Integration & Quota Manager
- Implement `backend/app/services/gemini_service.py` using `google-genai`:
  - Configurable model (Flash models: `gemini-2.5-flash`, `gemini-1.5-flash`, etc.).
  - Free-tier rate limiting and quota tracker (RPM, RPD counters).
  - Bounded exponential backoff with jitter for HTTP 429 and transient errors.
  - Circuit-breaker pattern: When quota is exhausted or API is unreachable, seamlessly fall back to verified FAQ answers.
  - Structured prompt assembly enforcing the mandatory CampusConnect system prompt.

#### Phase 7: RAG Grounding & Response Validation
- Implement post-generation response validation:
  - Check that claims in the generated response correspond to retrieved evidence snippets.
  - Hallucination detector: prevent invented fee amounts, exam dates, contact numbers, or fake URLs.
  - Citation attachment: map evidence sources into structured frontend citations (Title, URL, Source Type, Verified badge).
  - Safe fallback generator: if confidence is low or retrieval yields no match, return a helpful, honest message with suggested categories and official LPU portal links.

#### Phase 8: Anonymous Sessions & Conversation History
- Cryptographically secure anonymous session generation (`uuid4`).
- Session-scoped conversation storage and retrieval.
- Strict isolation: prevent cross-session access with query constraints.
- Session expiry and auto-cleanup.
- Feedback logging (thumbs up/down with optional user comment).

#### Phase 9: Admin Dashboard & Management Workflows
- Protected admin routes with JWT bearer authentication and role checks.
- Overview screen with live metrics (Queries, FAQs, Documents, Low Confidence Queries, Failures).
- FAQ Manager: Add, Edit, Delete, Approve, Reject, Set review dates, Add alternate phrasing.
- Document Manager: Upload file, extract text, preview chunks, approve, trigger reindex.
- Analytics & Query Log Viewer: Inspect recent queries, response latency, confidence distributions.

#### Phase 10: Security, Testing & QA
- Automated test suites:
  - Retrieval engine tests (Exact match, paraphrase, keyword match, low confidence, no match).
  - Gemini service tests (Mocked API responses, timeout handling, 429 quota exhaustion fallback).
  - Security & isolation tests (Admin auth, session boundary, rate limiting, prompt injection resistance).
  - API endpoint integration tests.
- Performance & type checking (`mypy` / `tsc`).

#### Phase 11: Deployment & Documentation
- Comprehensive README with quick-start steps for both frontend and backend.
- `.env.example` with documented configuration parameters.
- Architecture diagrams and API reference documentation.

#### Phase 12: Extended Multi-Type Knowledge Repository (12 Data Types)
- Supported 12 distinct schemas: `faq`, `policy`, `academic_schedule`, `contact_directory`, `facility_service`, `library_resource`, `placement_procedure`, `international_programme`, `research_facility`, `student_activity`, `grievance_procedure`, `official_notice`.
- Ingestion and temporal validation: automated expiry detection, SHA-256 content deduplication, and sensitive policy review classification.
- Gemini question variant generation preserving underlying institutional facts.

#### Phase 13: CampusConnect UMS RAG Action SRS v3.0 (Major Expansion)
- **Database Expansion**: Alembic migration `003_ums_actions_and_catalog.py` creating `ums_service_catalog`, `action_workflows`, and `campus_places`.
- **234 UMS Menu Entries**: Ingestion and indexing of all 234 services from `ums_service_catalog_from_screenshots.csv`.
- **Action Classifier (8 Modes)**: Classifies incoming requests into `ANSWER`, `NAVIGATE`, `PREPARE`, `BOOK_HANDOFF`, `PERSONAL_RECORD`, `ESCALATE`, `EXECUTE`, `ABSTAIN`.
- **Navigation & Breadcrumb Engine**: Natural language intent search with exact breadcrumbs and official `https://ums.lpu.in/lpuums/` handoff.
- **24 Guided Action Workflows**: Ingestion and guided logic for doctor, hostel, counselling, library-room, language-lab, and RMS grievance workflows.
- **Campus Wayfinding & Location Service**: Verified location directory for Block 34, Block 13, Block 30 UniHospital, Central Library, UniMall, stadiums, and labs.
- **Frontend Action Cards**: Structured interactive cards for Navigation, Booking Handoff, Procedure Checklists, RMS Grievance, and Private Record boundaries.
- **Admin UMS Console**: Management views for UMS catalog entries, action workflows, and campus places.
- **Acceptance & Automated Tests**: Comprehensive test suite covering the 25 acceptance criteria specified in SRS v3.0.

