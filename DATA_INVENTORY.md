# CampusConnect — Comprehensive Data Inventory (Data Quality v4.0)

**Project:** CampusConnect — Lovely Professional University (LPU) AI Campus Assistant  
**Date of Audit:** November 18, 2026  
**Auditor:** Principal Software Architect & RAG Specialist  
**Target Environment:** Production PostgreSQL / SQLite + Python FastAPI + Gemini Grounded RAG  

---

## 1. Executive Summary

A comprehensive forensic audit of the `data/` directory was performed. The data repository contains **11 primary files** totaling **2.24 MB** across CSV, PDF, and HTML formats.

The knowledge base covers:
1. **Institutional FAQs:** General university guidelines, admissions, examinations, hostels, transport, refunds, student welfare.
2. **Specialized Academic Policies & Regulations:** The 45-page official LPU "EDU Revolution Guide" (Revenue generation, NPTEL/MOOCs credits, DRDO/ISRO projects, 10% attendance benefits, duty leave).
3. **Program & Faculty Dossiers:** B.Tech. CSE (AI & ML) curriculum, specializations, laboratory infrastructure, and 77 faculty profiles.
4. **UMS Navigation & Action Workflows:** 234 menu items observed from official UMS screenshots and 24 actionable interactive workflows (doctor booking, hostel leaves, fee payment, RMS grievances).

---

## 2. Forensic File Inventory

| # | File Name | Format | Size | Records / Units | Primary Fields / Dimensions | SHA-256 Checksum (First 16 chars) | Data Coverage & Provenance |
|---|---|---|---|---|---|---|---|
| 1 | `Academic Benefits copy.pdf` | PDF | 1,869,475 B | 45 Pages | Unstructured narrative, tabular policies, flowcharts | `2bf80db51fce7eec...` | Division of Academic Affairs, LPU. Official EDU Revolution Guide. |
| 2 | `campusconnect_lpu_knowledge_base_80_faqs.csv` | CSV | 35,958 B | 80 Rows | 9 columns (`faq_id`, `category`, `canonical_question`, `answer`, `source_url`, `source_title`, `last_reviewed`, `status`, `review_note`) | `6fa5a6b86ea340ca...` | University-wide policies across 36 categories from `lpu.in`. |
| 3 | `campusconnect_lpu_knowledge_base_50_faqs.csv` | CSV | 21,396 B | 50 Rows | 9 columns (same as 80 FAQs) | `0baeae25a818627e...` | 100% strict subset of the 80 FAQs file. |
| 4 | `campusconnect_lpu_seed_faqs_v2.csv` | CSV | 10,722 B | 25 Rows | 9 columns (same as 80 FAQs) | `4dcec0610b95a836...` | 100% strict subset of the 80 FAQs file. |
| 5 | `faqs.csv` | CSV | 46,735 B | 56 Rows | 9 columns (`faq_id`, `category`, `canonical_question`, `paraphrases`, `answer`, `keywords`, `source_url`, `last_reviewed`, `status`) | `bde5d7d51dd29ce2...` | Program-specific (B.Tech CSE AI/ML) fees, exact hostel fee slabs, transport passes, refund brackets. |
| 6 | `lovely_professional_university_lpu_cse_ai_ml_faculty_programme_dossier.html` | HTML | 66,250 B | 933 Lines (65,791 chars) | Semantic HTML, tables, lists, profile cards | `3d310b2cb9f70fd1...` | School of Computer Science & Engineering, LPU. B.Tech CSE AI/ML dossier. |
| 7 | `lovely_professional_university_lpu_cse_ai_ml_faculty_programme_dossier (1).html` | HTML | 66,250 B | 933 Lines (65,791 chars) | Semantic HTML (identical to #6) | `3d310b2cb9f70fd1...` | Exact byte-for-byte duplicate of #6. |
| 8 | `lpu_cse_faculty_directory.csv` | CSV | 17,527 B | 77 Rows | 8 columns (`faculty_id`, `name`, `emp_code`, `designation`, `department`, `role_or_specialization`, `organization`, `source_url`) | `a56212cf3c33cd8a...` | Faculty roster for CSE department. |
| 9 | `rag_data_type_schema.csv` | CSV | 2,744 B | 14 Rows | 5 columns (`record_type`, `purpose`, `required_fields`, `retrieval_trigger`, `safety_rule`) | `e5af09fa58ae1723...` | Metadata schema governance defining 14 core knowledge categories. |
| 10 | `ums_navigation_booking_action_workflows.csv` | CSV | 8,889 B | 24 Rows | 6 columns (`action_id`, `user_intent`, `ums_navigation_path`, `chatbot_flow`, `evidence`, `execution_guardrail`) | `6fd5a8507b446ae2...` | Verified navigation and handoff workflows for high-frequency actions. |
| 11 | `ums_service_catalog_from_screenshots.csv` | CSV | 118,416 B | 234 Rows | 12 columns (`catalog_id`, `module`, `service_label_as_seen`, `action_type`, `public_chatbot_support`, `execution_boundary`, `ums_authentication`, `navigation_path_from_screenshot`, `deep_link_status`, `source_evidence`, `verification_status`, `notes`) | `ab8bc4f97bf7de88...` | Complete 234 UMS menu inventory extracted from official screenshots. |

---

## 3. Detailed File-by-File Analysis

### 3.1. `Academic Benefits copy.pdf`
- **File Type:** Adobe PDF Document (45 Pages).
- **Publisher / Department:** Division of Academic Affairs, Lovely Professional University.
- **Title / Subject:** EDU Revolution: Be the Change — Academic Benefits & Incentive Guidelines.
- **Coverage:**
  - Revenue Generation Framework ("Earn Your Fee"): Earning Rs. 50,000 to Rs. 2,00,000+ grants proportional course/fee waiver and attendance exemptions.
  - Research & Development Projects: Defense (DRDO), Space (ISRO), Atomic Energy (BARC), and government funded research project incentives.
  - MOOCs / NPTEL / SWAYAM / Coursera credit transfers and CGPA upgradation guidelines.
  - Recognition of Prior Learning (RPL), Hackathons, and Startup incubation benefits.
  - Duty Leave policy & mandatory 10% Attendance Benefit for approved academic/co-curricular activities.
  - Application process via UMS: `Login UMS -> LMS -> Edu Revolution: Be the Change -> Apply for EDU Revolution`.
  - Offline Helpdesk / Verification: Query Zone at Block 38, Room 205B.
- **Missing Fields:** Needs chunk-level page numbers, policy clause IDs, and effective validity periods.
- **Data Quality Issues:** Text flowcharts and tabular matrices require careful segmentation so numerical criteria (e.g., minimum CGPA 6.5, attendance threshold 75%) are not dissociated from their governing clauses.
- **Recommended Treatment:** Segment into 45 page-indexed markdown chunks, extract 15 distinct policy/regulation records, and index in `knowledge_records` with exact page and section citations.

### 3.2. `campusconnect_lpu_knowledge_base_80_faqs.csv`
- **File Type:** Delimited CSV (80 records, 9 columns).
- **Coverage:** Broad institutional coverage spanning 36 categories: General, Admissions, Examinations, Hostels, Transport, Attendance, Fees, Placements, Library, Medical, Grievances, Sexual Harassment Redressal, International Exchange, and Research.
- **Missing Fields:** `paraphrases` and `keywords` columns are absent in this file (present in `faqs.csv`).
- **Data Quality Issues:** Some answers give general advisory statements rather than exact step-by-step UMS paths (e.g., hostel booking gives the general website rather than exact UMS menus).
- **Recommended Treatment:** Primary baseline dataset. Enrich with searchable variants, link to corresponding UMS menu items, and assign typed knowledge schemas.

### 3.3. `campusconnect_lpu_knowledge_base_50_faqs.csv` & `campusconnect_lpu_seed_faqs_v2.csv`
- **File Type:** Delimited CSV (50 records and 25 records respectively).
- **Findings:** Both files are 100% strict subsets of `campusconnect_lpu_knowledge_base_80_faqs.csv`.
- **Deduplication Verdict:** Mark as superseded. Ingesting them alongside the 80-FAQ file would cause 75 duplicate records. Retain in backup for audit trails.

### 3.4. `faqs.csv`
- **File Type:** Delimited CSV (56 records, 9 columns).
- **Coverage:** Highly specific, actionable questions with `paraphrases` and `keywords`. Covers:
  - Exact tuition fees for B.Tech. CSE (AI and ML) for 2026-2027 (Rs. 1,40,000/semester standard, scholarship slabs: Phase 1 Rs. 98,000, Phase 2 Rs. 1,12,000, Phase 3 Rs. 1,26,000).
  - Exact hostel room slabs (Standard 4-seater Air Cooled Rs. 83,700/yr with 300 free units, AC 4-seater Rs. 98,700/yr).
  - University bus transport pass routes and boarding passes.
  - Step-by-step fee refund percentages according to UGC/LPU calendar.
- **Missing Fields:** None.
- **Data Quality Issues:** Program-specific fee details (B.Tech CSE AI/ML) could be mistaken for university-wide flat fees if retrieved out of context.
- **Recommended Treatment:** Merge into the unified knowledge base with explicit scoping metadata (`programme_scope: B.Tech CSE (AI & ML)`, `academic_session: 2026-2027`).

### 3.5. `lovely_professional_university_lpu_cse_ai_ml_faculty_programme_dossier.html` & Duplicate
- **File Type:** Semantic HTML (933 lines, 65,791 characters).
- **Duplicate Verification:** `lovely_professional_university_lpu_cse_ai_ml_faculty_programme_dossier (1).html` has identical SHA-256 hash (`3d310b2cb9f70fd1...`).
- **Coverage:** Complete curriculum schema for B.Tech CSE (AI & ML):
  - Specialization tracks: Deep Learning, Natural Language Processing, Computer Vision, Reinforcement Learning, MLOps.
  - Industry partnerships: Google Cloud, AWS Academy, Intel, NVIDIA Deep Learning Institute.
  - Faculty directory with academic designations and research areas.
- **Data Quality Issues:** Contact numbers and personal emails are absent from the public dossier; must remain unpopulated rather than fabricated.
- **Recommended Treatment:** Discard duplicate copy `(1).html`. Ingest primary copy using `html_extractor.py` to extract program regulations, lab descriptions, and faculty profiles.

### 3.6. `lpu_cse_faculty_directory.csv`
- **File Type:** Delimited CSV (77 records, 8 columns).
- **Coverage:** Faculty names, designations (Prof., Assoc. Prof., Asst. Prof.), specialization areas (NLP, Computer Vision, Cloud, Cybersecurity, IoT), department ("Computer Science and Engineering").
- **Missing Fields:** `emp_code` is missing for 60 records; contact email and phone are not published in this dataset.
- **Data Quality Issues:** Missing employee IDs.
- **Recommended Treatment:** Ingest 77 faculty profiles. Preserve missing `emp_code` as `null`. Enforce rule: Never fabricate email addresses or office room numbers.

### 3.7. `rag_data_type_schema.csv`
- **File Type:** Governance CSV (14 records, 5 columns).
- **Coverage:** Defines 14 foundational RAG types with required fields, retrieval triggers, and safety guardrails.
- **Recommended Treatment:** Baseline blueprint expanded into the 30-type Typed Knowledge Architecture.

### 3.8. `ums_navigation_booking_action_workflows.csv`
- **File Type:** Action Workflow CSV (24 records, 6 columns).
- **Coverage:** Actionable student workflows: Doctor appointment booking, hostel leave/night-pass, mess change, reappears, fee payment, RMS grievance, language lab, wifi renewal.
- **Recommended Treatment:** Integrated into the Action Engine with strict `NAVIGATE`, `PREPARE`, and `BOOK/HANDOFF` boundaries.

### 3.9. `ums_service_catalog_from_screenshots.csv`
- **File Type:** System Inventory CSV (234 records, 12 columns).
- **Coverage:** Complete menu tree across all student modules: Examination, Fee, Hostel, Transport, RMS, Library, LMS, Placement, Student Affairs.
- **Data Quality Issues:** 184 entries are labeled `menu_label_observed` (UI navigation path verified from screenshot, but internal transaction forms require active student login).
- **Recommended Treatment:** Canonical UMS catalog. Enrich with natural language synonyms, breadcrumb generators, and strict boundary notices.

---

## 4. Summary of Data Quality Findings & Actions

| Data Finding | Quantity | Action Taken |
|---|---|---|
| Exact duplicate HTML dossier | 1 file | Flagged and excluded from ingestion |
| Strict subset FAQ files (50 & 25) | 75 records | Marked superseded by `80_faqs.csv` |
| Program-specific fee and hostel slabs | 56 records | Merged with explicit program and session scoping |
| Missing faculty employee codes | 60 records | Preserved as null; no fabrication permitted |
| Menu-only observed UMS services | 184 records | Guardrailed with `NAVIGATE` / `HANDOFF` boundaries |
| High-value academic policy PDF | 45 pages | Extracted into structured markdown policy records |

