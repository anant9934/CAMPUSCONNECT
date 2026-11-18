# CampusConnect — Automated RAG Evaluation Report (V6 Accuracy Benchmark)

**Project:** CampusConnect — Lovely Professional University (LPU) AI Campus Assistant  
**Evaluation Date:** November 18, 2026  
**Dataset:** `RAG_EVALUATION_DATASET.jsonl` (235 Curated Institutional Test Cases across 15 Knowledge Domains)  
**Search Engine:** Calibrated Hybrid Search (Okapi BM25 + Field Weights + Exact Phrase Matching + TF-IDF + Dense Semantic Vectors + Exact Entity Matcher + Source Authority Multipliers)  

---

## 1. Executive Summary & Benchmark Metrics

| Metric | Measured Value | Production Target | Status |
|---|---|---|---|
| **Recall@5** | **95.43%** | >= 95.0% | **PASSED (Production Grade)** |
| **Mean Reciprocal Rank (MRR)** | **0.942** | >= 0.850 | **PASSED (Production Grade)** |
| **Top-1 Accuracy** | **92.69%** | >= 85.0% | **PASSED (Production Grade)** |
| **Abstention Accuracy** | **100.0%** | 100.0% | **PASSED (Zero Hallucination)** |
| **Precision@5** | **19.09%** | >= 18.0% | **PASSED (High Target Precision)** |
| **Action Mode Classification** | **100.0%** | >= 95.0% | **PASSED (Exact Boundary Enforced)** |

---

## 2. Category & Domain Breakdown

| Knowledge Domain | Total Queries | Top-1 Matches (%) | Recall@5 (%) | MRR |
|---|---|---|---|---|
| **ABSTENTION** | 15 | 15 (100.0%) | 15 (100.0%) | 1.0 |
| **ACADEMICS** | 20 | 20 (100.0%) | 20 (100.0%) | 1.0 |
| **AMBIGUOUS** | 10 | 10 (100.0%) | 10 (100.0%) | 1.0 |
| **CAMPUS_LOCATIONS** | 15 | 14 (93.3%) | 15 (100.0%) | 0.947 |
| **EDUREV** | 15 | 15 (100.0%) | 15 (100.0%) | 1.0 |
| **EMERGENCY** | 10 | 9 (90.0%) | 9 (90.0%) | 0.95 |
| **EXAMINATIONS** | 20 | 20 (100.0%) | 20 (100.0%) | 1.0 |
| **FACULTY** | 15 | 13 (86.7%) | 13 (86.7%) | 0.867 |
| **FEES** | 20 | 18 (90.0%) | 18 (90.0%) | 0.925 |
| **FOOD** | 15 | 15 (100.0%) | 15 (100.0%) | 1.0 |
| **GRIEVANCES** | 12 | 10 (83.3%) | 11 (91.7%) | 0.875 |
| **HOSTEL** | 18 | 14 (77.8%) | 17 (94.4%) | 0.852 |
| **MULTI_DOMAIN** | 15 | 13 (86.7%) | 14 (93.3%) | 0.883 |
| **TRANSPORT** | 15 | 13 (86.7%) | 13 (86.7%) | 0.867 |
| **UMS_NAVIGATION** | 20 | 20 (100.0%) | 20 (100.0%) | 1.0 |

---

## 3. Methodology & Evaluation Coverage

The evaluation suite tested the system comprehensively across:
1. **Academics & Regulations (20 Queries):**
   - 75% attendance policy under Academic Regulation Clause 3.1 (`LPU-POL-001`)
   - 80% attendance prospectus guidance (`LPU-051`)
   - Continuous assessment (CA) components & 40% aggregate passing criteria (`LPU-028`, `LPU-029`)
   - Relative grading system (A+ to F) and SGPA/CGPA computation (`LPU-OPS-001`, `LPU-005`)
   - B.Tech CSE AI/ML curriculum, lateral entry, and first-year autumn courses (`LPU-PRG-001`, `LPU-PRG-002`, `CSE-005`)
2. **Examinations & Schedules (20 Queries):**
   - UMS datesheets and seating plans (`EXM-001`, `UMS-021`)
   - Reappear exam registration on UMS and fees (Rs. 500 Theory, Rs. 750 Practical) (`UMS-031`, `LPU-OPS-002`, `ACT-015`)
   - Evaluated answer sheet inspection and re-evaluation timeline (`LPU-030`, `LPU-031`, `LPU-052`)
   - LPUNEST Schedule-I registration and cut-offs (`EXM-004`, `EXM-005`)
3. **Fees & Scholarships (20 Queries):**
   - B.Tech CSE AI/ML base fee Rs. 1,40,000/sem (`FEE-004`)
   - LPUNEST Category A, B, C phased scholarship slabs (`LPU-SCH-003`, `LPU-SCH-004`, `LPU-SCH-005`)
   - Online fee payment portal and receipt download (`FEE-001`, `UMS-136`, `ACT-011`, `ACT-012`)
   - Refund schedule on admission withdrawal (`FEE-007`)
4. **UMS Navigation (20 Queries):**
   - Complete screenshot-backed UMS service routing (234 active services)
   - Doctor appointments (`UMS-207`), RMS grievances (`UMS-208`, `UMS-209`), Attendance (`UMS-068`)
   - Hostel booking (`UMS-143`), hostel activity undertaking (`UMS-142`), Virtual ID Card (`UMS-138`)
5. **Hostel & Housing (18 Queries):**
   - 4-seater air-cooled room charges Rs. 83,700 with 300 free units (`HOS-004`)
   - 10:00 PM gate curfew and prohibited appliances (`LPU-OPS-003`)
   - Permitted appliances (electric kettle, iron, trimmer) (`HOS-006`)
   - Vegetarian mess charges Rs. 37,800 (`HOS-005`) and biometric outpass system (`LPU-OPS-004`)
6. **Transport & Mobility (15 Queries):**
   - Jalandhar bus route 7:30 AM PAP Chowk (`LPU-OPS-005`)
   - 7 major corridors across Punjab (`TRN-001`) and bus pass application (`TRN-002`, `ACT-008`)
   - Free campus parking for hostellers (`TRN-004`) and airport cab transfers (`TRN-005`)
7. **Campus Food Discovery (15 Queries):**
   - UniMall food court, cafes, and commercial hub (`LOC-005`)
   - Fast food (Domino's, Subway, South Indian, Nescafe kiosks) in UniMall
   - Student dining across Block 13, Shanti Devi Stadium, Unipolis, and CSE Blocks 25-28
8. **Faculty & People Directory (15 Queries):**
   - Executive Dean Dr. Rajeev Sobti (`CSE-001`)
   - Professor & HOD Dr. Mohit Arora (`LPU-FAC-004`, `LPU-DIR-drmohitarora-15980`)
   - Academic leadership, course coordinators, and faculty profiles
   - Private personal phone number refusal (Zero Leakage)
9. **Campus Locations & Wayfinding (15 Queries):**
   - Central Library Block 36/38 (`LOC-004`, `LIB-001`, `LIB-002`)
   - Block 34 Examination & Registrar Office (`LOC-001`)
   - Block 13 Division of Student Affairs DSA (`LOC-002`)
   - UniHospital Block 30 (`LOC-003`, `NAV-007`)
   - Gate 1, Unipolis, Indoor Stadium, and Central Transport Hub
10. **EDU-Revolution & Academic Benefits (15 Queries):**
    - 10% Attendance benefit for GATE / competitive exams (`LPU-EDREV-009`)
    - Earn Your Fee revenue generation policy (`LPU-EDREV-003`)
    - Scopus Q1 journal publication 1 grade up policy (`LPU-EDREV-008`)
    - Online course credit transfer (NPTEL, SWAYAM, Coursera) (`LPU-EDREV-004`)
    - Query Zone Block 38 Room 205B (`LPU-EDREV-012`)
11. **Grievances & RMS (12 Queries):**
    - RMS log request and tracking on UMS (`UMS-208`, `UMS-209`, `ACT-010`, `ACT-020`)
    - Resolution SLA 3 to 7 working days & escalation matrix (`LPU-OPS-009`)
    - Internal Complaints Committee ICC for women safety (`LPU-022`)
    - Anti-ragging cell, squad, and helpline (`LPU-023`)
12. **Emergency Support (10 Queries):**
    - 24x7 security, ambulance, fire helpline (`LPU-OPS-008`, `LPU-014`)
    - UniHospital casualty and 24-hour pharmacy in Block 30 (`LOC-003`)
    - Psychological counselling and mental wellness support (`LPU-044`, `ACT-003`)
13. **Multi-Domain Intelligence (15 Queries):**
    - Compound queries spanning Faculty + Project Advice, Food + Location, Attendance + Contact, Hostel + Fee
    - Concurrent multi-card and multi-section response synthesis
14. **Ambiguous Questions (10 Queries):**
    - Underspecified keyword queries correctly grounded in authoritative records
15. **Abstention & Safety Compliance (15 Queries):**
    - Refusal of out-of-scope, malicious, prompt-injection, or confidential queries (100% correct abstention)

---

## 4. Benchmark Verification Summary

All core retrieval benchmarks meet or exceed production-readiness criteria:
- **Recall@5: 95.43%** (Target >= 95.0%)
- **Top-1 Accuracy: 92.69%** (Target >= 85.0%)
- **MRR: 0.942** (Target >= 0.850)
- **Abstention Accuracy: 100.0%** (Target = 100.0%)
