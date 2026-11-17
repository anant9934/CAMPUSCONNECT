# CampusConnect — Data Deduplication & Version Control Report (Data Quality v4.0)

**Project:** CampusConnect — Lovely Professional University (LPU) AI Campus Assistant  
**Date:** November 18, 2026  
**Auditor:** Principal Software Architect & RAG Specialist  

---

## 1. Executive Summary

A forensic deduplication and conflict-resolution analysis was conducted across all datasets in the CampusConnect repository. Overlapping FAQ files, duplicate HTML dossiers, and potential semantic contradictions between general institutional policies and program-specific schedules were evaluated.

Key Results:
- **75 exact duplicate FAQ records** were identified and marked as superseded (50 in `50_faqs.csv` and 25 in `seed_faqs_v2.csv`).
- **1 duplicate HTML file** (`lovely_professional_university_lpu_cse_ai_ml_faculty_programme_dossier (1).html`) was verified to be a bit-for-bit duplicate of the primary dossier via SHA-256 content hashing.
- **56 program-specific records** in `faqs.csv` were reconciled against `80_faqs.csv`: 3 high-similarity topics were classified as complementary program-specific variations rather than destructive overwrites.
- **Zero data loss** was achieved by preserving both general institutional and specific degree-level facts with explicit provenance metadata.

---

## 2. HTML Dossier Hash Verification

A cryptographic content hash audit was executed on both HTML files:

| File Name | File Size | SHA-256 Hash | Verdict |
|---|---|---|---|
| `lovely_professional_university_lpu_cse_ai_ml_faculty_programme_dossier.html` | 66,250 bytes | `3d310b2cb9f70fd195ce03fd4ae73358fb35d29ad58f81516d54f2be9c806455` | **Primary Canonical Source** |
| `lovely_professional_university_lpu_cse_ai_ml_faculty_programme_dossier (1).html` | 66,250 bytes | `3d310b2cb9f70fd195ce03fd4ae73358fb35d29ad58f81516d54f2be9c806455` | **Exact Duplicate (Excluded)** |

**Treatment:** Only the primary canonical file is processed by `html_extractor.py`. The redundant file is preserved in `data_backup/` for provenance auditing.

---

## 3. FAQ Deduplication Matrix

### 3.1. Exact ID & Content Matches (Subsets)
- `campusconnect_lpu_knowledge_base_50_faqs.csv` (50 records): Every single record ID (`LPU-001` through `LPU-050`) matches `80_faqs.csv` with identical questions, answers, and sources.
- `campusconnect_lpu_seed_faqs_v2.csv` (25 records): Every single record ID (`LPU-001` through `LPU-025`) matches `80_faqs.csv` identically.

**Resolution:** Both files are classified as **SUPERSEDED_BY_80_FAQS**. They are logged in `duplicate_records.csv` and excluded from the ingestion pipeline to prevent database bloat and duplicate vector indexing.

### 3.2. Semantic Reconciliation (`faqs.csv` vs `80_faqs.csv`)
`faqs.csv` contains 56 distinct records with program-specific IDs (`FEE-001` to `FEE-005`, `HOS-001` to `HOS-006`, `TRN-001` to `TRN-005`, `ACA-001` to `ACA-005`, `REG-001` to `REG-005`, `EXAM-001` to `EXAM-005`, `LIB-001` to `LIB-005`, `PLC-001` to `PLC-005`, `INT-001` to `INT-003`, `DIS-001` to `DIS-003`, `MED-001` to `MED-003`, `EVT-001` to `EVT-003`, `RES-001` to `RES-003`).

Three topics exhibited high semantic proximity:
1. **Hostel Booking:** `HOS-001` ("How can I apply for hostel accommodation?") vs `LPU-017` ("How do students book LPU hostel accommodation?").
   - *Analysis:* `HOS-001` provides LPUADMIT details for *new incoming students*; `LPU-017` provides UMS navigation for *existing enrolled students*.
   - *Resolution:* **Coexist with Persona Scoping**. `HOS-001` tagged with `audience: prospective_students`, `LPU-017` tagged with `audience: enrolled_students`.
2. **Academic Calendar:** `REG-003` ("Where is the academic calendar?") vs `LPU-009` ("Where can I find the LPU academic calendar?").
   - *Analysis:* Both reference `https://www.lpu.in/academics/calendar-regular.php`. `REG-003` includes semester break guidelines; `LPU-009` notes tentative exam dates.
   - *Resolution:* Merged into canonical knowledge record with comprehensive calendar navigation.
3. **Fee Refund:** `FEE-003` / `ADM-004` vs `LPU-054` / `LPU-055`.
   - *Analysis:* `faqs.csv` gives exact percentage deductions based on days before/after classes start (UGC guidelines); `80_faqs.csv` provides non-refundable head definitions (prospectus, entrance fee).
   - *Resolution:* **Complementary merge**. Retained both clauses under `Fee Refund Policy` with admin-review flag set to `True` for financial sensitivity.

---

## 4. Conflict Resolution Protocol

1. **Preserve Both Records:** Never silently delete or overwrite differing figures (e.g. general tuition vs B.Tech CSE AI/ML tuition).
2. **Scoping & Applicability:** Attach explicit metadata tags:
   - `programme_scope`: e.g. `B.Tech Computer Science and Engineering (AI and ML)` vs `University-Wide`.
   - `academic_session`: e.g. `2026-2027`.
   - `effective_date`: Valid timestamp.
3. **Administrative Escalation:** When conflicting numbers or policies appear without clear precedence, the record is flagged with `requires_admin_review = True` and `approval_status = 'pending_review'`.
4. **Authoritative Output Guarantee:** The public chatbot retrieves only records where `is_approved = True` and `is_active = True`.

---

## 5. Artifacts Generated
- `DATA_INVENTORY.md`: Forensic inventory of all 11 files in `data/`.
- `DATA_DEDUPLICATION_REPORT.md`: This report.
- `duplicate_records.csv`: 78 logged duplicate/overlap cases with match types and resolutions.
- `data_merge_report.csv`: 56 merge strategy decisions across program-specific and general records.

