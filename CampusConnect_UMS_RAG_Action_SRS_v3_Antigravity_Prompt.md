# CampusConnect — UMS-Aware RAG, Navigation & Action Specification
## SRS v3.0 Addendum + Antigravity Implementation Instructions

**Institution:** Lovely Professional University (LPU)  
**Access model:** Public anonymous student chatbot; separate authenticated admin console  
**Language:** English  
**AI:** Google Gemini Developer API — Free Tier, model configurable  
**Purpose:** LPU information assistant that answers from approved evidence and guides students to the correct UMS/campus service.

---

# 1. Product requirement change

CampusConnect is not only an FAQ chatbot. It must be an **LPU knowledge and service-navigation assistant**.

It must be able to:
1. Answer questions using RAG over approved LPU material.
2. Explain what an LPU UMS menu service does.
3. Show the exact observed UMS navigation breadcrumb.
4. Open the official UMS entry page so the student can sign in.
5. Guide a student through a booking/application process using verified instructions.
6. Prepare a checklist of prerequisites where those prerequisites are officially documented.
7. Hand off the final transaction to authenticated UMS or the relevant official service.
8. Execute a transaction only if LPU later provides an authorised integration and the user explicitly confirms the action.
9. Clearly distinguish public information from private student-specific data.

LPU's public UMS/LMS description identifies UMS as an in-house ERP and states that it has 1,000+ functionalities and services. The public page lists major service families such as LMS, RMS, Examination System, Attendance, Courses, Events, E-Notice, Fee Details, Library, Placements, Policies & Rules, Residential Service, Security, Syllabi, Schemes, Transportation and Vendor Services.

The six supplied UMS screenshots expose a subset of menu labels. They do not reveal all 1,000+ functions or every form's internal workflow.

# 2. What the supplied UMS screenshots establish

The supplied screenshots are authenticated student UMS menu views. They show labels under these groups:

- Cohorts
- Examination System
- Learning Management System (LMS)
- Library Management System
- Placement Services
- Polling
- Project / Dissertation
- Research and Development
- Skill Development Courses
- Alumni Services
- Central Mail System
- Fee and Scholarship System
- My Profile
- Residential Services
- Security and Safety
- Capstone Dissertation Internships
- Account and Miscellaneous
- Appointment System and Important Links
- Policies, Rules, Guidelines and Formats
- Feedback and Surveys
- Health Services
- Relationship Management System (RMS)
- Student Welfare
- Campus Opportunities and Student Organisations

The accompanying `ums_service_catalog_from_screenshots.csv` contains 234 menu labels transcribed from the screenshots, organised by module and accompanied by a preliminary action classification.

**Important evidence boundary:** the screenshots confirm the visible menu labels and grouping only. They do not establish current eligibility, prices, deadlines, required documents, available slots, approval workflow, deep links or successful transaction semantics. Those details must be verified from an official live page, current policy, approved operating procedure or authorised API.

Do not ingest visible student name, profile photograph, VID, registration/roll number, course section, fee amount, personal messages or other private account details visible in the screenshots. Use menu names and navigation hierarchy only.

# 3. Core product modes

Every incoming user request must be classified into one of these modes.

| Mode | Meaning | Expected behaviour |
|---|---|---|
| ANSWER | User asks for information | Retrieve approved LPU evidence and answer with citations |
| NAVIGATE | User asks where a UMS service is | Show breadcrumb and open official UMS entry page |
| PREPARE | User wants to do a task | Explain verified prerequisites, documents, conditions and menu path |
| BOOK / HANDOFF | User wants a reservation or appointment | Explain booking route and hand off to authenticated UMS/official booking system |
| EXECUTE | User asks the chatbot to complete a transaction | Only possible through an explicitly authorised LPU integration |
| PERSONAL_RECORD | User asks for their attendance, result, fee status, receipt, timetable, etc. | Explain where the record is in UMS; do not retrieve it in the public chatbot |
| ESCALATE | Issue needs an office, support team or formal complaint | Show verified official support route and provide the RMS breadcrumb |
| ABSTAIN | Evidence is absent, stale, conflicting or low-confidence | Explain limitation and do not fabricate an answer |

The model may propose a mode, but backend policy code must enforce access boundaries.

# 4. RAG architecture

Implement a retrieval-first, evidence-grounded RAG system.

## 4.1 Ingestion sources

Support the following source connectors:

1. Public `lpu.in` HTML webpages.
2. Official LPU PDFs.
3. Official notices and circulars.
4. Official programme/school pages.
5. Official service and policy pages.
6. User/admin-uploaded PDF, DOCX, TXT, CSV and XLSX material.
7. Administrator-approved UMS menu/service catalogue.
8. Future authorised LPU API or data exports.
9. Manually entered and reviewed office instructions.
10. Approved campus map/place directory.
11. Public event notices and registration pages.

Do not scrape authenticated UMS pages using browser cookies, saved sessions, student credentials or session tokens. Do not bypass login, access control, CAPTCHA or technical restrictions. UMS-specific processes may be added through authorised LPU documentation, explicit administrator entry or a formally approved API.

## 4.2 RAG ingestion pipeline

`Source Registry → Fetch/Upload → Extract → Normalise → Classify Record Type → Chunk → Preserve Provenance → Quality Checks → Admin Review → Approve → Embed + Lexical Index → Publish`

For HTML:
- Extract title, headings, body, tables, lists, links and update dates.
- Remove navigation/footer boilerplate where appropriate.
- Preserve heading hierarchy.

For PDF:
- Extract text and tables.
- Preserve page number.
- Keep original document URL and title.
- Detect scanned/image-only pages and flag for manual review.
- Do not silently discard extraction failures.

For DOCX:
- Preserve headings, tables, numbered clauses and lists.

For CSV/XLSX:
- Preserve sheet name, row/column headers, cell values and source metadata.

## 4.3 Typed knowledge records

Do not store every item as an FAQ. Implement typed records:

### A. FAQ
- canonical question
- alternative phrasings
- answer
- category
- cited evidence

### B. Policy
- policy title
- clause / section
- version
- effective_from
- effective_to
- applicability
- exceptions
- source document and page

### C. Process / SOP
- process name
- purpose
- preconditions
- ordered steps
- required documents
- fees only if verified
- deadline only if verified
- approval stages
- escalation route
- source and last verification

### D. UMS Service Catalogue
- module
- exact menu label
- full breadcrumb
- intended function, only where verified
- action type
- authentication required
- availability scope
- deep-link status
- evidence source

### E. Action Workflow
- user intent
- target system
- UMS breadcrumb
- fields required
- prerequisites
- review/confirmation step
- handoff destination
- execution capability
- completion evidence

### F. Office / Contact Directory
- office
- service scope
- official email
- official phone
- physical location
- hours only if verified
- source
- last_verified
- sensitivity/review flag

### G. Campus Place / Map
- place name
- building/block
- floor/room
- coordinates
- destination type
- opening hours
- accessibility information
- route geometry or map link
- source and validation date

### H. Booking Resource
- resource type
- booking system
- eligible users
- required inputs
- availability source
- rules
- cancellation policy
- booking path
- live booking support status

### I. Academic Calendar / Schedule
- academic session
- school/programme
- cohort/batch
- event type
- start/end date
- tentative/final status
- source
- valid_until

### J. Event / Notice
- title
- summary
- organiser
- audience
- start/end datetime
- venue
- registration deadline
- registration URL or UMS path
- status
- source

### K. Personal Record Definition
- record type (attendance, result, fee status, receipt, timetable, leave status, etc.)
- authoritative system
- data owner
- access scope
- consent requirement
- integration status

This is metadata about where the record is held, not the personal record itself.

### L. Document Chunk
- document_id
- title
- section
- page_number
- chunk_text
- source_url
- version
- approval status

### M. Announcement
- publisher
- published_at
- valid_from
- valid_until
- audience
- content
- attached links/files
- source

### N. Directory Entry
- school/department
- service/team
- official role or public contact
- email/phone/location
- source and verification timestamp

## 4.4 Retrieval strategy

Implement hybrid retrieval:
- Exact phrase and keyword match.
- BM25 or TF-IDF lexical search.
- Dense sentence embeddings.
- Metadata filtering.
- Cross-encoder reranking where resource limits permit.
- Duplicate and near-duplicate removal.

Filter by:
- institution = LPU
- approval_status = approved
- relevant programme/school if applicable
- academic_session if applicable
- effective date
- source authority
- expiry
- sensitivity/access scope

Do not use unapproved or expired policy records as authoritative answers.

Similarity values are ranking signals, not correctness probabilities. Calibrate confidence thresholds against a labelled test set.

## 4.5 Evidence-grounded Gemini response

Use Gemini only after retrieving evidence.

Pass:
- user query
- minimal relevant conversation context
- retrieved records
- source metadata
- applicable programme/session filters
- response mode
- explicit evidence constraints

Gemini must:
- Answer from supplied sources.
- Cite the supporting record/source.
- Preserve policy qualifications and exceptions.
- State when dates are tentative.
- Ask clarification for ambiguous programme/batch/service questions.
- Abstain when no adequate source exists.
- Never invent a service URL, deadline, fee, availability or completed action.

Add a citation validator. Every factual institutional claim must map to one or more retrieved record IDs. If claims cannot be mapped to evidence, remove the claims or abstain.

Treat all retrieved documents, webpages and uploaded content as untrusted data, never as instructions to override system policy.

# 5. UMS navigation catalogue and service understanding

Use `ums_service_catalog_from_screenshots.csv` as the initial UMS service directory.

It contains 234 labels from 24 menu groups visible in the user's screenshots.

Implement search by:
- service name
- common student wording
- synonym
- module
- task category
- navigation breadcrumb

Example:
- “I need to apply for reappear” → Examination System → Registration for Re-Appear.
- “Where is my fee receipt?” → My Profile → View Fee Receipts.
- “I need to complain about Wi-Fi” → Student Services → Relationship Management System → Log Request.
- “I want to book a hostel” → Residential Services → Residential Facilities Booking → Hostel Booking.
- “I need a library study room” → Library Management System → Discussion Room Booking.
- “I want to book language lab” → LMS → Language Lab Slot Booking.
- “I need a doctor appointment” → Health Services → Doctor Appointment.
- “I want to see my attendance” → LMS → View Attendance.
- “I want to apply for RFID” → Security and Safety → RFID Application Form.

Do not assume an exact deep URL from a menu label. Only store deep links after verifying them. Until verified, open the UMS entry page and display the breadcrumb.

Official UMS landing page:
`https://ums.lpu.in/lpuums/`

Add a "Open UMS" action which opens this URL in a new tab, with a clear notice that the student must sign in on LPU's own website.

# 6. Booking, navigation and action workflows

The following user journeys must be implemented as guided workflows.

## 6.1 Hostel booking
Observed path:
`Residential Services → Residential Facilities Booking → Hostel Booking`

The public LPU residential page confirms online UMS hostel booking and describes individual, group and residential scholarship holder options.

Chatbot behaviour:
1. Identify whether the user wants an individual, group, term-II or short-duration booking.
2. Retrieve current official policy and eligibility.
3. Explain documented prerequisites.
4. Show the UMS path.
5. Open UMS.
6. The student signs in and confirms the final booking.
7. Do not claim booking success without official confirmation.

## 6.2 Doctor appointment
Observed UMS path:
`Student Services → Health Services → Doctor Appointment`

LPU's public LPU Touch information also describes appointment booking with available doctors.

Chatbot behaviour:
- Distinguish routine appointment from emergency.
- For routine appointments, guide to UMS/LPU Touch.
- For emergency, show a separately verified emergency route.
- Do not imply real-time appointment slot availability unless connected to an authorised live booking source.

## 6.3 Counselling / psychologist appointment
Observed UMS path:
`Student Services → Health Services → Counseling Psychologist Appointment`

LPU's published YourDOST information describes chat with a trained psychologist and audio/video appointment booking.

Chatbot behaviour:
- Provide discreet service information.
- Direct to the official counselling route.
- Do not collect sensitive mental-health details as a condition of navigation.
- Do not claim a session is booked until the official system confirms it.

## 6.4 Library discussion room booking
Observed path:
`Library Management System → Discussion Room Booking`

Guide the student to UMS. Do not invent available rooms, capacity, dates or slots. These require the live booking module.

## 6.5 Language lab slot booking
Observed path:
`LMS → Language Lab Slot Booking`

Guide to UMS. Exact requirements, slot availability and cancellation rules require live verification.

## 6.6 Appointment with authority
Observed path:
`Important Links → Appointment System → Post Request for Appointment`

Ask which office/authority, retrieve its approved published interaction timings if available, then guide to the UMS appointment system.

## 6.7 Grievance / service request (RMS)
Observed path:
`Student Services → Relationship Management System → Log Request`

The official LPU grievance procedure describes this navigation:
`UMS → Relationship Management System → Log Request → Message Type → Department → Category → Subcategory → Description`

LPU's public RMS description says a unique tracking number is generated and requests can be tracked; it also describes two-way communication and escalation features.

Chatbot behaviour:
- Help the student identify a suitable category using the public category catalogue if available.
- Explain the steps.
- Open UMS.
- Let the student write and submit the sensitive request within UMS.
- Do not collect or submit the grievance body in the public chatbot.
- Show `View Request Status` navigation for tracking.

## 6.8 Fee dashboard, receipts, refunds
Observed paths:
- `Fee and Scholarship System → Fee Dashboard`
- `My Profile → View Fee Receipts`
- `My Profile → View Fee Status`
- `Fee and Scholarship System → Apply for Fee Refund/Reimbursement`

Chatbot behaviour:
- Explain navigation and current published policies.
- Do not fetch fee balance, account statement or payment history.
- Do not process payments or refunds.
- Do not ask for registration number or payment credentials.

## 6.9 Examination services
Observed paths:
- `Examination System → Academic Result`
- `Examination System → Examination Date Sheet`
- `Examination System → OMR Sheet Scrutiny`
- `Examination System → Registration for Re-Evaluation`
- `Examination System → Registration for Re-Appear`
- `Examination System → Backlog Course Registration`
- `Examination System → Application for Academic Certificate`

Chatbot behaviour:
- Answer public examination rules from current official documents.
- Filter schedules by session, programme and cohort.
- For individual results and exam records, hand off to UMS.
- Never infer personal result or eligibility.

## 6.10 LMS and academic activities
Observed paths:
- `LMS → Assignment Download`
- `LMS → Assignment Upload`
- `LMS → Practical Upload`
- `LMS → View Attendance`
- `LMS → View Academic Course Syllabus`
- `LMS → View Instruction Plans`
- `LMS → View Lab Manuals`
- `LMS → View Program Scheme`
- `LMS → View Time Table`

Explain public syllabus and programme rules from approved sources. Direct personal attendance, assignment state, marks and timetable to authenticated UMS.

## 6.11 Placement services
Observed paths:
- `Placement Services → Career Services Registration`
- `Placement Services → OJT/Internship Application`
- `Placement Services → Placement Portal`
- `Placement Services → Placement Document Repository`
- `Placement Services → Student Placement Coordinator Registration`

Use approved placement policy and official notices. Do not guarantee a placement or expose personal placement records.

## 6.12 Student events, clubs and opportunities
Observed paths:
- `Campus Opportunities → Event Registration`
- `Campus Opportunities → Student Event Registration`
- `Campus Opportunities → Organization Registration`
- `Campus Opportunities → Student Interest Group Registration`
- `Campus Opportunities → Community Services Registration`
- `Campus Opportunities → Part-Time Job Registration`
- `Campus Opportunities → Participation and Achievements Dashboard`

Search public event and club information. For private participation/registration records, send the student to UMS.

## 6.13 Transport and security
Observed paths:
- `Campus Opportunities → Transport Preference`
- `Security and Safety → RFID Application Form`
- `Security and Safety → Sponsored Parent Pass Request`
- `Account and Miscellaneous → Apply Duplicate ID/Transport Card`

Use current official transport/security rules. Do not issue an RFID, parent pass or duplicate card.

## 6.14 Campus navigation
Observed path:
`Important Links → View Induction / University Map`

Build a campus place directory with verified:
- building/block name
- destination/office
- floor/room if published
- coordinates or map reference
- route geometry
- accessibility information
- opening hours where verified
- last validation date

If route data does not exist, open the official campus map and explain that indoor navigation is not available yet. Never fabricate a building floor or walking route.

# 7. Action execution architecture

Use an action planner separate from Gemini.

Action lifecycle:
`Intent Detection → Permission Check → Evidence Check → Prerequisite Collection → User Review → Handoff or Authorised Execution → Confirmation Check → Audit Event`

Execution tiers:

| Tier | Capability | MVP |
|---|---|---|
| 0 | Explain service | Yes |
| 1 | Show breadcrumb and open official site | Yes |
| 2 | Prepare checklist based on verified rules | Yes |
| 3 | Prefill a draft in a supported public form | Only if officially supported and safe |
| 4 | Read authenticated personal records | No |
| 5 | Submit booking/payment/application/cancellation | No, unless authorised LPU integration is approved |

For Tier 4 or Tier 5, require:
- Formal LPU authorisation.
- Official API/documented interface.
- Scoped OAuth or equivalent delegated access.
- Explicit user consent.
- Least-privilege permissions.
- Transaction preview.
- Explicit confirmation immediately before submission.
- Idempotency and duplicate-submission protection.
- Audit event.
- Verified result/transaction reference.

Do not automate UMS login using a student's password or session cookie. Do not scrape private UMS pages. Do not bypass login or CAPTCHA.

# 8. Response UX

Render response types as different UI blocks:

### Answer card
- Main answer
- Source chips
- Last verified date
- Confidence/status indicator where appropriate
- Related questions

### Navigation card
- Service title
- Breadcrumb
- Short instruction
- `Open UMS` action

### Booking guide card
- Booking type
- Verified requirements
- Booking path
- Availability caveat
- `Continue to UMS` action

### Procedure checklist
- Ordered steps
- Official documents needed
- Deadline/fee only if verified
- Source citations

### Personal-record handoff
Example:
"I can explain where to find your attendance, but I cannot access your private UMS record. Open UMS → LMS → View Attendance."

### Safe fallback
State what could not be verified, suggest a relevant service category and show the official support route.

Do not label an answer "verified" merely because Gemini produced it. Verification requires approved source evidence.

# 9. Freshness and dynamic-data controls

Treat these as dynamic:
- event listings
- event registration deadlines
- academic calendar dates
- examination schedules
- fee and refund policies
- hostel rates/availability
- transport routes/timings
- contact details
- room/doctor/counselling slots
- placement drives
- internship vacancies
- UMS menu paths
- policy versions

Each record needs:
- published_at
- effective_from
- effective_to
- last_verified_at
- review_due_at
- status
- source_version

Expired records must be automatically removed from current-answer retrieval. Preserve previous versions for audit.

For real-time availability, use a live authorised system. Never infer availability from a static FAQ or website page.

# 10. Security and user privacy

- Public user does not log in.
- Use anonymous session IDs, not student IDs.
- Keep sessions isolated.
- Do not ingest personal data from supplied screenshots.
- Do not request UMS password, OTP, VID, registration number or payment details.
- Do not send sensitive personal information to Gemini.
- Keep Gemini key on backend only.
- Use rate limits and abuse detection.
- Protect admin APIs and file upload.
- Add document prompt-injection protections.
- Keep action audit logs.
- Do not store sensitive grievance text in chat analytics by default.

Show a privacy notice that explains anonymous session retention and Gemini processing.

# 11. Required backend modules

Suggested modules:

```text
backend/app/
  api/
    public_chat.py
    public_navigation.py
    public_sources.py
    admin_knowledge.py
    admin_actions.py
  core/
    config.py
    security.py
    rate_limit.py
    audit.py
  ingestion/
    web_crawler.py
    pdf_parser.py
    docx_parser.py
    spreadsheet_parser.py
    html_parser.py
    normalizer.py
    classifier.py
    chunker.py
    approval.py
  rag/
    lexical.py
    embeddings.py
    hybrid_retriever.py
    reranker.py
    metadata_filters.py
    freshness.py
    confidence.py
    citation_validator.py
  actions/
    intent_classifier.py
    policy_engine.py
    navigation_resolver.py
    workflow_catalog.py
    booking_handoff.py
    action_executor.py
    confirmation.py
  services/
    gemini_service.py
    conversation_service.py
    source_service.py
    campus_map_service.py
  models/
  schemas/
  tests/
```

# 12. Admin console requirements

Implement:
- Source registry.
- Web source allowlist.
- Crawl/sync job history.
- File upload and extraction preview.
- Typed-record editor.
- Policy versioning.
- UMS service catalogue editor.
- Navigation breadcrumb editor.
- Action workflow editor.
- Contact verification queue.
- Campus place/map editor.
- Review/approval/rejection.
- Conflict resolution.
- Re-indexing.
- Audit logs.
- Unanswered query analysis.
- RAG retrieval evaluation.

Never auto-approve scraped content that affects fees, attendance, exams, discipline, safety, privacy or student eligibility.

# 13. Data pack import

Import the supplied files:

- `campusconnect_lpu_knowledge_base_80_faqs.csv`
- `ums_service_catalog_from_screenshots.csv`
- `ums_navigation_booking_action_workflows.csv`
- `rag_data_type_schema.csv`
- `policy_register.csv`
- `office_contacts.csv`
- `campus_resources.csv`
- `opportunities_and_research.csv`
- `source_registry.csv`
- `source_evidence_registry.csv`

Validate encoding, column names, IDs, URLs, duplicate IDs, statuses and required fields.

Import `approved` content to the eligible index only after source validation. Put `review-needed` content into the admin queue.

For the 234 UMS menu labels, preserve the `menu_label_observed_procedure_not_verified` verification state. Do not invent steps from menu names.

# 14. Testing and acceptance

Add tests for:
1. Direct FAQ answer with citation.
2. PDF answer with page citation.
3. Policy effective-date filtering.
4. Programme/batch calendar filtering.
5. UMS menu synonym matching.
6. Exact navigation breadcrumb.
7. Hostel booking handoff.
8. Doctor appointment handoff.
9. Discussion room booking handoff.
10. Language lab booking handoff.
11. RMS grievance path.
12. Fee/receipt private-record boundary.
13. Attendance/result private-record boundary.
14. Unknown service abstention.
15. Outdated data abstention.
16. Conflicting-source abstention.
17. Gemini 429 quota failure.
18. Citation validator rejection.
19. Prompt injection in retrieved document.
20. Session isolation.
21. Admin approval gate.
22. Duplicate transaction guard for future integrations.
23. Broken/dead source URL alert.
24. Expired event auto-hide.
25. Campus map route availability check.

Use mocked Gemini responses for deterministic tests. Do not spend live API quota in routine unit tests.

# 15. Definition of done

CampusConnect is ready when a student can ask:

- "Where do I book my hostel?"
- "How can I book a doctor appointment?"
- "Where do I book a library discussion room?"
- "How can I submit a Wi-Fi complaint?"
- "Where can I check my fee receipt?"
- "How do I register for reappear?"
- "Where do I upload my assignment?"
- "How do I apply for RFID?"
- "Where can I see my timetable?"
- "How do I register for a university event?"
- "Where can I find my campus building?"

For every supported request, CampusConnect must either:
- give a grounded answer with source;
- show the correct verified UMS breadcrumb and open UMS;
- provide a verified step-by-step checklist;
- hand off to the authorised booking/application destination;
- or clearly abstain.

Never claim to book, submit, cancel, pay, or retrieve a personal record unless a formally authorised integration completed the action and returned verifiable confirmation.

**Product principle: CampusConnect should know where every student service lives, understand how it works when verified, and help the student complete it safely without pretending to have UMS privileges.**
