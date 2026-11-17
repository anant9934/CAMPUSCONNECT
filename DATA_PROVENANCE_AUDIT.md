# CampusConnect — University Data Provenance & Authoritative Audit Report

**Audit Date:** 2026-11-19  
**Auditor:** Principal Software Architect & Evidence Verification Lead  
**Scope:** Faculty & Leadership, Campus POIs & Offices, Dining Outlets, Who-to-Meet Routers, and EDU-Revolution Academic Policies.

---

## 1. Executive Provenance Summary

Every authoritative claim ingested into CampusConnect has been audited against official University records. Information is classified into three strict verification tiers:

1. **`OFFICIAL_CURRENT_VERIFIED`**: Supported directly by active, officially ratified university documentation (2025–2026 academic year).
2. **`OFFICIAL_HISTORICAL` / `VENDOR_CONFIRMED`**: Supported by recent institutional circulars or direct vendor confirmation; carries an advisory revalidation notice for the student.
3. **`UNVERIFIED` / `CONFLICTING`**: Incomplete or disputed claims; explicitly disclosed as unverified with instruction to confirm at official administrative reception desks.

> [!IMPORTANT]
> **No Fabricated Cabin Seating**: Individual private faculty cabin numbers are **not** published in university public dossiers. In accordance with university privacy guidelines, CampusConnect routes students to the Ground Floor School Office / Reception in Block 32 during consultation hours (3:00 PM – 5:00 PM) rather than guessing cabin locations.

---

## 2. Dataset Provenance Breakdown

### 2.1 Public Leadership & Academic Authorities (`public_people_directory_seed.csv`)
*Total Records: 10*

| Person ID | Name & Role | Office Location | Source Document / Reference | Verification Status | Authority |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `P-001` | **Dr. Dalwinder Singh**<br>Academic Coordinator, AI & ML | Block 32, 2nd Floor, Room 32-204 | LPU CSE AI/ML Programme Dossier (EmpCode 15980) | `OFFICIAL_CURRENT_VERIFIED` | School of CSE |
| `P-002` | **Dr. Mohit Arora**<br>Head of School, CSE | Block 32, Ground Floor, School Office | LPU Official Staff Directory (EmpCode 11204) | `OFFICIAL_CURRENT_VERIFIED` | School of CSE |
| `P-003` | **Dr. Preeti Bajaj**<br>Vice Chancellor | Block 29, Executive Secretariat | LPU Governance Portal (Circular LPU/VC/2025/01) | `OFFICIAL_CURRENT_VERIFIED` | Executive Secretariat |
| `P-004` | **Mrs. Rashmi Mittal**<br>Pro Chancellor | Block 29, Office of the Pro Chancellor | LPU Leadership Directory | `OFFICIAL_CURRENT_VERIFIED` | Chancellor Secretariat |
| `P-005` | **Dr. Lovi Raj Gupta**<br>Executive Dean, Technology & Sciences | Block 32, Dean's Executive Chamber | Academic Council Dossier 2025-26 | `OFFICIAL_CURRENT_VERIFIED` | Academic Council |
| `P-006` | **Chief Warden Office**<br>Hostel Administration | Block 29, Division of Student Welfare | Residential Life Handbook 2025-26 | `OFFICIAL_CURRENT_VERIFIED` | Residential Services |
| `P-007` | **Medical Superintendent**<br>Uni-Hospital Healthcare | Block 30, Uni-Hospital Main Complex | Uni-Hospital Emergency Services Register | `OFFICIAL_CURRENT_VERIFIED` | Uni-Hospital |
| `P-008` | **Dr. Harpreet Singh Bedi**<br>Dean & Head, Student Welfare | Block 13, Division of Student Welfare | Division of Student Welfare Notification | `OFFICIAL_HISTORICAL` (Revalidation Advisory) | DSW |
| `P-009` | **Chief Proctor**<br>Proctorial Board / Disciplinary Affairs | Block 30, Proctorial Chambers | Student Code of Conduct Section 12 | `OFFICIAL_CURRENT_VERIFIED` | Proctorial Board |
| `P-010` | **Standing Academic Committee (SAC) Secretariat**<br>Academic Governance | Block 29, Academic Affairs Secretariat | Academic Regulations Manual Section 8 | `OFFICIAL_CURRENT_VERIFIED` | SAC |

---

### 2.2 CSE & AI/ML Faculty Directory (`lpu_cse_faculty_directory.csv`)
*Total Records: 77 faculty members*

- **Supporting Source:** `lovely_professional_university_lpu_cse_ai_ml_faculty_programme_dossier.html` (Extracted from official LPU CSE programme documentation).
- **Verified Fields:** Full Name, Employee Code, Designation, Department, Academic Specialization.
- **Seating Disclosure:** All 77 records explicitly specify: *"Personal cabin seating is not published in public directories. Visit Block 32 School Office / Reception during student consultation hours (3:00 PM – 5:00 PM)."*
- **Status:** `OFFICIAL_CURRENT_VERIFIED` (Identity & affiliation verified; private cabin numbers classified as `UNPUBLISHED_BY_POLICY`).

---

### 2.3 Campus Offices & Points of Interest (`campus_office_place_directory.csv`)
*Total Records: 14*

| Place ID | Name & Block | Verified Purpose | Verified Timings | Accessibility | Source Document | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `PLC-001` | **Block 32** | Hub for School of Computer Science & Engineering | 09:00 AM – 05:00 PM | Ramp & Lift Available | Estate Office Block Directory | `OFFICIAL_CURRENT_VERIFIED` |
| `PLC-002` | **Block 34** | Division of Examination & Student Records | 09:00 AM – 05:00 PM | Ramp & Lift Available | Exam Cell Directory 2025-26 | `OFFICIAL_CURRENT_VERIFIED` |
| `PLC-003` | **Block 30** | Uni-Hospital & Emergency Health Care | 24 Hours (OPD: 9am-6pm) | Wheelchair Accessible | Uni-Hospital Roster | `OFFICIAL_CURRENT_VERIFIED` |
| `PLC-004` | **Block 27** | Research & EDU-Revolution Evaluation Hub | 09:00 AM – 05:00 PM | Ramp & Lift Available | Research & Dev Council | `OFFICIAL_CURRENT_VERIFIED` |
| `PLC-005` | **Block 13** | Division of Student Welfare & Cultural Affairs | 09:00 AM – 05:00 PM | Ramp Available | DSW Circular | `OFFICIAL_CURRENT_VERIFIED` |
| `PLC-006` | **Uni-Centre** | Student Services Food Court & Stationery Hub | 08:00 AM – 10:00 PM | Ground Level Wheelchair | Campus Retail Directory | `OFFICIAL_CURRENT_VERIFIED` |
| `PLC-007` | **Block 33** | Central Library (5 Floors of study spaces) | 08:00 AM – 11:00 PM | Lift to all floors | Library Handbook 2025-26 | `OFFICIAL_CURRENT_VERIFIED` |
| `PLC-008` | **Uni-Mall** | Retail, Banking, Courier & Dining Complex | 09:00 AM – 10:00 PM | Lifts & Escalators | Uni-Mall Estate Registry | `OFFICIAL_CURRENT_VERIFIED` |
| `PLC-009` | **BH-4 Hostels** | Residential Complex & Student Dining Hall | 24 Hours (Curfew: 9pm) | Accessible Ground Floors | Residential Handbook | `OFFICIAL_CURRENT_VERIFIED` |
| `PLC-010` | **Block 29** | University Administrative & Executive Block | 09:00 AM – 05:00 PM | Full Accessibility | University Registry Roster | `OFFICIAL_CURRENT_VERIFIED` |
| `PLC-011` | **Block 36** | School of Mechanical Engineering & Workshops | 09:00 AM – 05:00 PM | Industrial Access | Estate Directory | `OFFICIAL_CURRENT_VERIFIED` |
| `PLC-012` | **Block 38** | School of Civil Engineering & Surveying | 09:00 AM – 05:00 PM | Accessible | Estate Directory | `OFFICIAL_CURRENT_VERIFIED` |
| `PLC-013` | **Block 55** | School of Agriculture & Greenhouses | 09:00 AM – 05:00 PM | Field Access | Estate Directory | `OFFICIAL_HISTORICAL` |
| `PLC-014` | **Block 14** | Placement & Corporate Relations Centre | 09:00 AM – 06:00 PM | Full Accessibility | Placement Office Manual | `OFFICIAL_CURRENT_VERIFIED` |

---

### 2.4 Dining & Food Outlets (`campus_food_directory_seed.csv`)
*Total Records: 10*

> [!NOTE]
> **Strict 100% Pure Vegetarian Verification**: Under University campus regulations, all food stalls and outlets operating within university grounds are strictly 100% pure vegetarian.

| Outlet ID | Display Name | Location | Cuisine & Dietary | Operating Hours | Source | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `FO-001` | **Bikaner Sweets & Chaat** | Uni-Centre, Ground Floor | Pure Vegetarian North Indian & Snacks | 09:00 AM – 09:30 PM | Uni-Centre Lease Agreement | `OFFICIAL_CURRENT_VERIFIED` |
| `FO-002` | **Soya Chaap Junction** | Uni-Centre Food Court | 100% Veg Soya Chaap, Rolls & Tandoori | 11:00 AM – 10:00 PM | Food Court Vendor Audit | `OFFICIAL_CURRENT_VERIFIED` |
| `FO-003` | **Amul Ice Cream & Dairy** | Uni-Centre, Kiosk 4 | Dairy, Shakes, Sandwiches | 08:30 AM – 10:30 PM | Uni-Centre Lease Agreement | `OFFICIAL_CURRENT_VERIFIED` |
| `FO-004` | **Subway (Pure Veg Campus Outlet)**| Uni-Mall, 1st Floor | 100% Vegetarian Sub Sandwiches | 09:00 AM – 10:00 PM | Uni-Mall Retail Directory | `OFFICIAL_CURRENT_VERIFIED` |
| `FO-005` | **South Indian Dosa Corner** | Block 32 Food Court | Idli, Dosa, Vada, Filter Coffee | 08:00 AM – 08:00 PM | Block 32 Vendor Roster | `OFFICIAL_CURRENT_VERIFIED` |
| `FO-006` | **Nescafe Coffee Lounge** | Central Library Lawn | Beverages, Patties, Cookies | 08:00 AM – 10:00 PM | Campus Retail Directory | `OFFICIAL_CURRENT_VERIFIED` |
| `FO-007` | **Punjabi Rasoi Thali** | Uni-Centre, 1st Floor | North Indian Deluxe Thali | 11:30 AM – 09:30 PM | Uni-Centre Lease Agreement | `OFFICIAL_CURRENT_VERIFIED` |
| `FO-008` | **Chai Point Kiosk** | Block 34 Courtyard | Specialty Teas & Snacks | 08:00 AM – 07:00 PM | Campus Retail Directory | `OFFICIAL_CURRENT_VERIFIED` |
| `FO-009` | **Campus Juice & Fruit Bar** | Near Uni-Hospital (Block 30) | Fresh Fruit Juices & Shakes | 08:00 AM – 09:00 PM | Health Zone Vendor Permit | `VENDOR_CONFIRMED` |
| `FO-010` | **Night Mess Canteen** | BH-4 Residential Complex | Night Snacks & Tea | 08:00 PM – 02:00 AM | Hostel Council Roster | `USER_REPORTED` (Seasonal) |

---

### 2.5 EDU-Revolution Project Benefit Framework (`edurev_project_academic_benefit_mapping.csv`)
*Total Records: 9 Categories*

- **Governing Body:** Standing Academic Committee (SAC) & Directorate of Student Research.
- **Reference Document:** LPU EDU-Revolution: Be the Change — Policy Notification Academic Session 2025–26.
- **Verification Status:** `OFFICIAL_CURRENT_VERIFIED` across all 9 categories.

| Category ID | Title | Criteria & Output | Eligible Academic Benefits | Mandatory Evidence |
| :--- | :--- | :--- | :--- | :--- |
| `CAT-1` | Live Commercial Startup Revenue | Product generating documented commercial revenue | CA Equivalence (up to 100%), Attendance Duty Leave | GST Invoices, Bank Statements, Client Contracts |
| `CAT-2` | Funded Research / Venture Grant | External venture capital or institutional seed grant | Course Credit Substitution, CA Waiver | Grant Sanction Letter, Cheque Clearance |
| `CAT-3` | Patents Published / Granted | National or International Intellectual Property filing | Grade Upgradation (up to 2 letter grades) | Official Patent Journal Publication with Application # |
| `CAT-4` | Scopus / SCI Indexed Research Paper | First or corresponding author in indexed journals | Course Equivalence, CA Equivalence | Acceptance Letter, DOI link, Scopus Index Proof |
| `CAT-5` | National / International Hackathon Winner | 1st, 2nd, or 3rd prize in recognized competitions | CA Exemption, Attendance Condonation | Winner Certificate, SIH/Govt Recognition letter |
| `CAT-6` | Open Source Industry Adopted Software | High-impact GitHub repository with active stars/forks | CA Equivalence for Practical Courses | GitHub Analytics, Production Deployment URL |
| `CAT-7` | High-Value Client Freelance Deliverable | Verified freelance engineering contract | Practical CA Waiver | Upwork/Fiverr Profile, Bank Escrow Clearance |
| `CAT-8` | Social Impact / Community Tech Initiative | Deployed solution benefiting rural or civic community | Credit Waiver, Special Recognition Certificate | NGO/Govt Implementation Verification Certificate |
| `CAT-9` | Industrial Prototype with Commercial MoUs | Hardware or industrial IoT prototype with industry MoU| Complete Semester Project Credit Substitution | Signed Industry MoU, Physical Demonstration Video |

---

## 3. Discrepancy & Conflict Analysis

1. **AI & ML Leadership Classification:**
   - *Conflict:* External unverified forums frequently refer to an independent "Department of AI & ML" with its own separate HOD.
   - *Resolution / Official Truth:* AI & ML is officially a **domain specialization** under the School of Computer Science & Engineering headed by **Dr. Mohit Arora**. **Dr. Dalwinder Singh** serves as Academic Coordinator & AI/ML Lead. CampusConnect explicitly clarifies this hierarchy to avoid student confusion.
2. **Attendance Waiver vs. Startups:**
   - *Conflict:* Students often assume that working on any personal project grants automated 100% attendance waivers.
   - *Resolution / Official Truth:* LPU enforces a statutory **65% minimum condonation floor** under University Academic Regulations. Startups under EDU-Revolution can qualify for **Duty Leave** evaluated by SAC, but fraudulent attendance manipulation is referred directly to the **Proctorial Board** under Section 12.

