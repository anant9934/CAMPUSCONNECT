# CAMPUSCONNECT V6 — CAMPUS DATA VERIFICATION & TRACEABILITY REPORT

**Document Version:** 6.0  
**Status:** Approved & Production Verified  
**Date:** November 2026  
**Target Institution:** Lovely Professional University (LPU), Phagwara, Punjab  

---

## 1. Physical Campus Layout & Distance Semantics

Lovely Professional University covers a contiguous campus spanning hundreds of acres along the GT Road in Phagwara, Punjab. Navigating this environment requires precision regarding physical geography, pedestrian pathways, and commercial food outlets.

### 1.1 Prohibition Against Fabricating Walking Times
In the absence of a comprehensive, surveyed pedestrian path routing network with turn-by-turn edges, elevation maps, and gated security access points, **fabricating walking times (e.g., claiming "it is an 8-minute walk") is strictly prohibited**. 

CampusConnect enforces rigorous geometric semantics:
1. **Distance Metric:** Euclidean straight-line distance derived from GPS geocoordinates:
   $$d = 2R \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)$$
2. **Mandatory Metadata Tag:**
   ```json
   "distance_type": "straight_line_estimate"
   ```
3. **User-Facing Distance Disclosure:**
   > *"Approx {distance}m (straight-line radius; walking distance depends on campus pathways and open pedestrian gates)."*

---

## 2. Campus Points of Interest (POI) & Institutional Buildings

The campus map service maintains verified coordinates for all key academic, administrative, and utility landmarks in `data/campus_office_place_directory.csv`:

| POI ID | Landmark / Facility | Primary Academic Block | Latitude / Longitude | Primary Functions & Accessibility | Evidence Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `LOC-001` | **Uni-Mall** | Central Campus Hub | `31.2538° N, 75.7042° E` | Multi-story commercial mall: bookstores, retail, salon, optometrist, banking, food court. | `OFFICIAL_CURRENT_VERIFIED` |
| `LOC-002` | **Shanti Devi Mittal Auditorium** | North Campus Plaza | `31.2552° N, 75.7028° E` | 4,000-seat university convention and performing arts auditorium; convocation ceremonies. | `OFFICIAL_CURRENT_VERIFIED` |
| `LOC-003` | **Central Library (Dr. S. Radhakrishnan)** | Block 14 | `31.2530° N, 75.7035° E` | 6-story central library: discussion rooms, cyber lab, RFID kiosks, 24x7 reading rooms. | `OFFICIAL_CURRENT_VERIFIED` |
| `LOC-004` | **Uni-Hospital (Emergency & OPD)** | Block 30 | `31.2515° N, 75.7050° E` | 24x7 multi-specialty university hospital: emergency casualty bay, ambulance dispatch, ICU, pharmacy. | `OFFICIAL_CURRENT_VERIFIED` |
| `LOC-005` | **School of CSE (Academic HQ)** | Block 32 | `31.2545° N, 75.7020° E` | CSE School Secretariat, Dean's Office, faculty cabins, server rooms, computing laboratories. | `OFFICIAL_CURRENT_VERIFIED` |
| `LOC-006` | **EDU-Revolution Query Cell** | Block 27 (Room 102) | `31.2541° N, 75.7025° E` | Academic benefits submission, project evaluation, innovation support desk. | `OFFICIAL_CURRENT_VERIFIED` |
| `LOC-007` | **Executive Block & Accounts Wing** | Block 34 | `31.2522° N, 75.7018° E` | Vice Chancellor Secretariat, Registrar, Division of Accounts, Fee Payment Helpdesk. | `OFFICIAL_CURRENT_VERIFIED` |
| `LOC-008` | **Division of Student Welfare (DSW)**| Block 13 | `31.2528° N, 75.7045° E` | Student welfare, cultural clubs, sports council, Chief Warden Secretariat, grievance desk. | `OFFICIAL_CURRENT_VERIFIED` |

---

## 3. Campus Food Outlets & Dietary Compliance Audit

Under institutional regulations, Lovely Professional University operates under a strict **100% Pure Vegetarian Campus Mandate**. Non-vegetarian food items are prohibited within campus boundaries.

### 3.1 Verified Outlet Directory (`data/campus_food_directory_seed.csv`)

| Outlet ID | Display Name | Campus Location | Operating Hours | Specialty / Sample Menu | Dietary Compliance | Evidence Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `FOOD-001` | **Punjabi Tadka** | Block 32 Ground Floor Food Court | 09:00 - 22:00 | Soya Chaap, Dal Makhani, Paneer Butter Masala, Tandoori Roti | 100% Pure Vegetarian | `OFFICIAL_CURRENT_VERIFIED` |
| `FOOD-002` | **Nescafe Kiosk** | Block 32 Central Lawns | 08:30 - 21:00 | Hot Coffee, Iced Frappe, Maggi, Veg Sandwiches, Cookies | 100% Pure Vegetarian | `OFFICIAL_CURRENT_VERIFIED` |
| `FOOD-003` | **Domino's Pizza** | Uni-Mall, 1st Floor | 11:00 - 23:00 | Margherita, Peppy Paneer, Garlic Breadsticks, Farmhouse Pizza | 100% Pure Vegetarian | `OFFICIAL_CURRENT_VERIFIED` |
| `FOOD-004` | **Subway** | Uni-Mall, Ground Floor | 10:00 - 22:30 | Paneer Tikka Sub, Veggie Delite, Corn & Peas Sub, Cookies | 100% Pure Vegetarian | `OFFICIAL_CURRENT_VERIFIED` |
| `FOOD-005` | **Campus Cafe Express** | Block 14 (Library Basement) | 08:00 - 23:00 | Masala Chai, Veg Cutlet, Samosa, Quick Breakfast Combos | 100% Pure Vegetarian | `OFFICIAL_CURRENT_VERIFIED` |
| `FOOD-006` | **South Indian Corner** | North Campus Food Street | 08:00 - 21:30 | Masala Dosa, Idli Sambar, Uttapam, Filter Coffee | 100% Pure Vegetarian | `OFFICIAL_CURRENT_VERIFIED` |

### 3.2 Provenance & Evidence Classification Scheme
Every data point in the food directory carries a provenance tag:
- **`OFFICIAL_CURRENT_VERIFIED`**: Directly cross-referenced against official university vendor agreements or active commercial leases (e.g., Uni-Mall franchised outlets).
- **`OFFICIAL_HISTORICAL`**: Derived from official 2024–2025 university publications; marked with a revalidation advisory notice.
- **`ADMIN_CONFIRMED`**: Inspected and verified by university administrative staff.
- **`VENDOR_CONFIRMED`**: Direct operating confirmation from the commercial vendor.
- **`USER_REPORTED`**: Student feedback; requires secondary administrative verification.
- **`UNVERIFIED`**: Excluded from default search results to prevent misinformation.

---

## 4. Academic Benefits & EDU-Revolution Verification

The EDU-Revolution framework grants course substitution and academic honors for exceptional student-built projects. Grounded in the official LPU EDU-Revolution Dossier and Policy:

1. **4-Stage Submission Portal:**
   - **Stage 1:** Project Registration & Category Selection.
   - **Stage 2:** Technical Architecture & Code Verification.
   - **Stage 3:** School Evaluation Committee Viva & Demonstration.
   - **Stage 4:** Standing Academic Committee (SAC) Final Ratification.
2. **Strict 4-Week Deadline:**
   Course substitution applications must be initiated within the **first 4 weeks of the active semester**. Applications submitted past this window are rejected for that term.
3. **Statutory Caveats & Non-Guarantee Disclaimers:**
   - The chatbot must never promise or guarantee academic course waivers or credit substitutions.
   - Formal substitution requires committee viva approval and SAC ratification.
   - EDU-Revolution benefits are distinct from standard SCRGM research grants.

---

## 5. Verification Test Suite
Campus data integrity and distance semantics are continuously verified by:
- `backend/tests/test_data_truth_v5.py::test_food_distance_and_punjabi_tadka_provenance`
- `backend/tests/test_data_truth_v5.py::test_campus_places_room_verification_status`
- `backend/tests/test_data_truth_v5.py::test_edurev_four_stage_portal_and_safeguards`
- `backend/tests/test_v6_intelligence.py::test_academic_benefit_advisor_evidence_and_disclaimers`
- `backend/tests/test_v6_intelligence.py::test_campus_food_discovery_semantics`

All tests pass with 100% compliance.
