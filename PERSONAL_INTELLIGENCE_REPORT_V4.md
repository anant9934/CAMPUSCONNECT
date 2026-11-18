# CampusConnect — LPU Personal Campus Intelligence Report v4.0
**Lovely Professional University AI Campus Assistant**

---

## 1. Executive Summary
CampusConnect has been expanded into an LPU-specific personal campus concierge per **CampusConnect Addendum v4.0**. The platform combines grounded RAG, structured entity retrieval, campus point-of-interest (POI) wayfinding, authenticated UMS action planning, a public people directory, a deterministic issue resolver, and an EDU-Revolution academic benefit advisor.

All 12 acceptance criteria have been implemented, tested, and verified with zero hallucinations, strict boundary preservation, and pure vegetarian campus compliance.

---

## 2. Seed Data Inventory (6 Core Files in `data/`)

| Seed File | Records | Core Entities / Schemas Covered | Institutional Sources & Compliance |
|:---|:---:|:---|:---|
| `data/campus_food_directory_seed.csv` | 10 | On-campus dining outlets, 100% vegetarian policy, GPS coords, opening hours, verified menu items, price samples | Official LPU Hospitality Directory & Vendor Audits. Includes Punjabi Tadka (Block 27) with verified Tandoori Soya Chaap & Soya Malai Chaap |
| `data/campus_office_place_directory.csv` | 14 | Blocks, offices, labs, libraries, hospitals, dining hubs, coordinates, pedestrian walkways, accessibility, hours | Official LPU Campus Wayfinding Directory, Estate Office records. Includes Block 32, Block 34, Block 27 Room 102, Block 30 UniHospital, Block 13 DSA, Block 14/37 Library |
| `data/public_people_directory_seed.csv` | 10 | Deans, HODs, coordinators, medical officers, student welfare leads, verified emails, source citations | Official LPU Faculty Dossier & University Leadership Directory. Clarifies Dr. Mohit Arora as HOD School of CSE (no distinct AI & ML dept HOD); room cabin unverified/not published |
| `data/who_to_meet_issue_router.csv` | 14 | Attendance discrepancies, EDU-Rev, DSR counseling, formal RMS grievances, international visas, placements, emergencies, doctor OPD, fee challans, hostels, Wi-Fi | Official DSA Handbook, CoE Helpdesk Charter, UniHospital Directorate, IT Services Manual |
| `data/edurev_project_academic_benefit_mapping.csv` | 9 | The 9 official EDU-Revolution categories (Certifications, AI/Software Projects, MOOCs, Hackathons, Startups, Competitive Exams, Consultancy, Social Impact, Freelancing) | Official LPU Academic Benefits Regulations & Standing Academic Committee guidelines. Explicitly separates academic credit from SCRGM commercial revenue |
| `data/edurev_workflow.csv` | 5 | 5-step lifecycle: Category identification -> Course mapping -> UMS RMS submission -> Committee evaluation -> Academic integration | Official EDU-Revolution Portal Guide and Standing Academic Committee SOP |

---

## 3. Backend Architecture & Core Services

### 3.1 Campus Food Discovery (`CampusFoodService`)
- **Vegetarian Mandate**: Strictly enforces LPU's 100% pure vegetarian campus policy.
- **Proximity & Walking Distance**: Calculates haversine great-circle distance in meters and walking time (standard 80 m/min pedestrian velocity) relative to GPS coordinates or user-selected landmark (Block 32, Uni-Centre, Block 34, Block 27, Block 13, BH-4, Uni-Mall).
- **Verified Menu Matching**: Searches verified menu items (JSON arrays) for query items (e.g. `soya chaap`, `dosa`, `pizza`, `coffee`, `sub`).
- **Zero Fabrication Fallback**: If an item (e.g. `sushi` or unverified dish) has no verified menu match, it explicitly informs the student and offers verified nearby vegetarian dining alternatives.

### 3.2 People & Faculty Leadership Directory (`PeopleDirectoryService`)
- **HOD Grounding Distinction**: Explicitly resolves that Dr. Mohit Arora is Professor & Head of School (HOD), School of Computer Science & Engineering. Correctly notes that AI & ML is a specialization cluster under the School of CSE with no separate published department HOD.
- **Zero Room Fabrication**: When personal cabins are not published in public directories, the assistant states `Not Published (Consult School Office, Block 32 Ground Floor)` and never invents cabin numbers.
- **Revalidation Notices**: Surfaces advisory warnings for historical records (e.g. DSR Counselor Block 32 Room 100, DIA Block 32 Room 308).

### 3.3 Who-to-Meet Issue Router (`IssueToOfficeResolver`)
- **Deterministic First-Step Routing**: Prevents premature escalations to deans or HODs. For attendance discrepancies, directs students to their Class Mentor / Course Instructor first, requires biometric logs and duty leave documentation, and outlines the escalation ladder (`1. Course Instructor -> 2. Class Coordinator -> 3. Head of School`).
- **EDU-Rev In-Person Support**: Routes in-person queries directly to Block 27 Room 102.
- **Emergency Triage**: Medical emergencies are routed directly to UniHospital in Block 30 (24x7 ambulance: +91-1824-517100).

### 3.4 EDU-Revolution Academic Benefit Advisor (`AcademicBenefitAdvisor`)
- **9 Category Matching**: Evaluates software, AI models, GitHub codebases, patents, or certifications against institutional criteria.
- **Evidence Checklist**: Requires public GitHub repository with commit history, live deployment link, architecture PDF, and live demonstration.
- **Strict Institutional Caveats**:
  - Requires Standing Academic Committee approval and active term course mapping within the first 4 weeks of the semester.
  - Never promises automatic grades, marks, or attendance waivers.
  - Explicitly distinguishes academic benefit from the Student-Centric Revenue Generation Model (SCRGM).

### 3.5 Wayfinding & Campus Places (`CampusMapService`)
- Integrates both database `campus_places` and `campus_office_place_directory.csv`.
- Resolves queries for Block 32, Block 34, Block 27 Room 102, UniHospital, Central Library, Uni-Centre, Uni-Mall, Indoor Stadium, and Unipolis.

---

## 4. Frontend Action Cards & User Experience

Built with React, TypeScript, and Tailwind CSS adhering to warm-white minimalism:
1. **`FoodOutletCardView.tsx`**: Displays pure vegetarian indicator, outlet type tag, zone, walking distance/time, opening hours, live status, menu matches, sample price, or nearby alternatives.
2. **`PersonCardView.tsx`**: Displays full name, designation, school, building block, cabin status (with unpublished room warning), email link, distinction notes, and revalidation advisory.
3. **`WhoToMeetCardView.tsx`**: Displays category title, primary contact role, physical office, copyable UMS breadcrumb, prerequisite action box, required documents tags, interactive escalation ladder, and revalidation warnings.
4. **`BenefitAssessmentCardView.tsx`**: Displays category badge, matched criteria, potential academic benefits, evidence checklist, submission channel, physical guidance desk (Block 27 Room 102), and SCRGM distinction box.
5. **`EvidenceCardView.tsx`**: Displays source title, type, document reference, clause or page, verification date, and revalidation warning badge.
6. **Campus Landmark Selector**: Pill in `MessageComposer.tsx` allowing instant selection of reference campus locations (`Block 32`, `Uni-Centre`, `Block 34`, `Block 27`, `Block 13`, `Block 30`, `Uni-Mall`, `BH-4`).

---

## 5. Verification & Acceptance Testing (12/12 Criteria)

Automated test suite in `backend/tests/test_personal_intelligence_v4.py`:

```
============================= test session starts ==============================
collected 12 items

backend/tests/test_personal_intelligence_v4.py ............              [100%]

======================== 12 passed in 1.26s ========================
```

### Full Test Suite Results (52/52 Tests Passing):
- `backend/tests/test_personal_intelligence_v4.py`: 12/12 passed (Acceptance criteria 1–12)
- `backend/tests/test_ums_actions.py`: 10/10 passed (UMS workflows, breadcrumbs, booking handoffs)
- `backend/tests/test_data_quality_v4.py`: 6/6 passed (Data deduplication, authority weighting)
- `backend/tests/test_extended_knowledge.py`: 8/8 passed (Typed knowledge records, multi-type RAG)
- `backend/tests/test_retrieval.py`: 4/4 passed (Calibrated confidence, hybrid search)
- `backend/tests/test_gemini_service.py`: 4/4 passed (Grounding, fallback generation)
- `backend/tests/test_security.py`: 4/4 passed (JWT auth, admin role guardrails)
- `backend/tests/test_api.py`: 4/4 passed (Conversation sessions, chat endpoints)

**Total: 52 passed, 0 failed, 0 errors.**

### Frontend Production Build:
```bash
npm run build --prefix frontend
> tsc && vite build
✓ 1601 modules transformed.
✓ built in 954ms (0 errors, 0 warnings)
```

