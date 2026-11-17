# UMS Comprehensive Coverage and Operational Verification Report

**Audit Timestamp:** 2026-11-19 | **Total Catalogued Services:** 234
**Pass Rate:** 234/234 (100.00%) | **Failures:** 0

## 1. Executive Summary & Module Distribution

| Module | Service Count | Primary Workflow Classification | Authentication Requirement |
| :--- | :--- | :--- | :--- |
| Learning Management System (LMS) | 37 | Executable Workflow (Action Handoff) | Required (Authenticated UMS) |
| Examination System | 32 | Informational / Navigation | Required (Authenticated UMS) |
| Campus Opportunities and Student Organisations | 24 | Executable Workflow (Action Handoff) | Required (Authenticated UMS) |
| Residential Services | 21 | Informational / Navigation | Required (Authenticated UMS) |
| Research and Development | 15 | Executable Workflow (Action Handoff) | Required (Authenticated UMS) |
| Policies, Rules, Guidelines and Formats | 13 | Informational / Navigation | Required (Authenticated UMS) |
| Fee and Scholarship System | 12 | Executable Workflow (Action Handoff) | Required (Authenticated UMS) |
| Placement Services | 11 | Executable Workflow (Action Handoff) | Required (Authenticated UMS) |
| Appointment System and Important Links | 10 | Executable Workflow (Action Handoff) | Required (Authenticated UMS) |
| Feedback and Surveys | 9 | Executable Workflow (Action Handoff) | Required (Authenticated UMS) |
| Project / Dissertation | 8 | Executable Workflow (Action Handoff) | Required (Authenticated UMS) |
| Capstone Dissertation Internships | 5 | Executable Workflow (Action Handoff) | Required (Authenticated UMS) |
| Cohorts | 4 | Informational / Navigation | Required (Authenticated UMS) |
| Library Management System | 4 | Executable Workflow (Action Handoff) | Required (Authenticated UMS) |
| Polling | 4 | Executable Workflow (Action Handoff) | Required (Authenticated UMS) |
| My Profile | 4 | Informational / Navigation | Required (Authenticated UMS) |
| Security and Safety | 4 | Informational / Navigation | Required (Authenticated UMS) |
| Account and Miscellaneous | 4 | Executable Workflow (Action Handoff) | Required (Authenticated UMS) |
| Skill Development Courses | 3 | Executable Workflow (Action Handoff) | Required (Authenticated UMS) |
| Alumni Services | 3 | Executable Workflow (Action Handoff) | Required (Authenticated UMS) |
| Central Mail System | 2 | Informational / Navigation | Required (Authenticated UMS) |
| Health Services | 2 | Executable Workflow (Action Handoff) | Required (Authenticated UMS) |
| Relationship Management System (RMS) | 2 | Executable Workflow (Action Handoff) | Required (Authenticated UMS) |
| Student Welfare | 1 | Informational / Navigation | Required (Authenticated UMS) |

## 2. Workflow Classification Breakdown

- **Executable Workflows (Financial transactions, bookings, grade appeals, leaves):** 123
- **Informational & Direct Navigation (Datesheets, syllabus, formats, policies):** 111
- **Public vs Authenticated Security Boundary:** 100% of executable actions strictly enforce authenticated session handoff via `NavigationCard` and `BookingCard` to safeguard student credentials.

## 3. Complete 234 Catalogued Services Audit Table

| Service ID | Service Name | Module | Breadcrumb Route | Searchable | Workflow Type | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `UMS-001` | Career Profiling | Cohorts | `UMS > Cohorts > Career Profiling` | Yes | Informational | **PASS** |
| `UMS-002` | My Cohorts Progress | Cohorts | `UMS > Cohorts > My Cohorts Progress` | Yes | Informational | **PASS** |
| `UMS-003` | My Cohorts Status | Cohorts | `UMS > Cohorts > My Cohorts Status` | Yes | Informational | **PASS** |
| `UMS-004` | Select Cohort | Cohorts | `UMS > Cohorts > Select Cohort` | Yes | Informational | **PASS** |
| `UMS-005` | Academic Result | Examination System | `UMS > Examination System > Academic Result` | Yes | Informational | **PASS** |
| `UMS-006` | Application for Academic Certificate | Examination System | `UMS > Examination System > Application for Academic Certificate` | Yes | Executable | **PASS** |
| `UMS-007` | Application for Certified Curriculum | Examination System | `UMS > Examination System > Application for Certified Curriculum` | Yes | Executable | **PASS** |
| `UMS-008` | Application for Degree Extension | Examination System | `UMS > Examination System > Application for Degree Extension` | Yes | Executable | **PASS** |
| `UMS-009` | Application for Guidance Classes Polling | Examination System | `UMS > Examination System > Application for Guidance Classes Polling` | Yes | Executable | **PASS** |
| `UMS-010` | Application for Letter of Recommendation | Examination System | `UMS > Examination System > Application for Letter of Recommendation` | Yes | Executable | **PASS** |
| `UMS-011` | Application for MOOC Certification | Examination System | `UMS > Examination System > Application for MOOC Certification` | Yes | Executable | **PASS** |
| `UMS-012` | Application for Placement Course Deregistration | Examination System | `UMS > Examination System > Application for Placement Course Deregistration` | Yes | Executable | **PASS** |
| `UMS-013` | Application for Provisional Academic Transcript | Examination System | `UMS > Examination System > Application for Provisional Academic Transcript` | Yes | Executable | **PASS** |
| `UMS-014` | Application for Scholarship Credit Card Scheme | Examination System | `UMS > Examination System > Application for Scholarship Credit Card Scheme` | Yes | Executable | **PASS** |
| `UMS-015` | Application for Term Off | Examination System | `UMS > Examination System > Application for Term Off` | Yes | Executable | **PASS** |
| `UMS-016` | Appointment for FRRO/VISA Reporting | Examination System | `UMS > Examination System > Appointment for FRRO/VISA Reporting` | Yes | Executable | **PASS** |
| `UMS-017` | Backlog Course Registration | Examination System | `UMS > Examination System > Backlog Course Registration` | Yes | Executable | **PASS** |
| `UMS-018` | Document Repository | Examination System | `UMS > Examination System > Document Repository` | Yes | Informational | **PASS** |
| `UMS-019` | Evaluation of Online Teaching Internship | Examination System | `UMS > Examination System > Evaluation of Online Teaching Internship` | Yes | Informational | **PASS** |
| `UMS-020` | Examination Attendance | Examination System | `UMS > Examination System > Examination Attendance` | Yes | Informational | **PASS** |
| `UMS-021` | Examination Date Sheet | Examination System | `UMS > Examination System > Examination Date Sheet` | Yes | Informational | **PASS** |
| `UMS-022` | Faculty Feedback | Examination System | `UMS > Examination System > Faculty Feedback` | Yes | Executable | **PASS** |
| `UMS-023` | OMR Sheet Scrutiny | Examination System | `UMS > Examination System > OMR Sheet Scrutiny` | Yes | Executable | **PASS** |
| `UMS-024` | Online Transactions | Examination System | `UMS > Examination System > Online Transactions` | Yes | Informational | **PASS** |
| `UMS-025` | Peer Tutoring Preference | Examination System | `UMS > Examination System > Peer Tutoring Preference` | Yes | Executable | **PASS** |
| `UMS-026` | Ph.D. Coursework Change for Scholar | Examination System | `UMS > Examination System > Ph.D. Coursework Change for Scholar` | Yes | Executable | **PASS** |
| `UMS-027` | Ph.D. Re-Evaluation Fee | Examination System | `UMS > Examination System > Ph.D. Re-Evaluation Fee` | Yes | Executable | **PASS** |
| `UMS-028` | Registration for Additional Tutoring Classes | Examination System | `UMS > Examination System > Registration for Additional Tutoring Classes` | Yes | Executable | **PASS** |
| `UMS-029` | Registration for R Grade Courses | Examination System | `UMS > Examination System > Registration for R Grade Courses` | Yes | Executable | **PASS** |
| `UMS-030` | Registration for Re-Evaluation | Examination System | `UMS > Examination System > Registration for Re-Evaluation` | Yes | Executable | **PASS** |
| `UMS-031` | Registration for Re-Appear | Examination System | `UMS > Examination System > Registration for Re-Appear` | Yes | Executable | **PASS** |
| `UMS-032` | Registration for Re-Appear (Late Fee) | Examination System | `UMS > Examination System > Registration for Re-Appear (Late Fee)` | Yes | Executable | **PASS** |
| `UMS-033` | Registration for Re-Appear Scrutiny | Examination System | `UMS > Examination System > Registration for Re-Appear Scrutiny` | Yes | Executable | **PASS** |
| `UMS-034` | Registration for Remedial/Tuition Classes | Examination System | `UMS > Examination System > Registration for Remedial/Tuition Classes` | Yes | Executable | **PASS** |
| `UMS-035` | Registration for Student Academic Support Program | Examination System | `UMS > Examination System > Registration for Student Academic Support Program` | Yes | Executable | **PASS** |
| `UMS-036` | Summer Term Backlog Course Preference | Examination System | `UMS > Examination System > Summer Term Backlog Course Preference` | Yes | Executable | **PASS** |
| `UMS-037` | Feedback of Training Programmes | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > Feedback of Training Programmes` | Yes | Executable | **PASS** |
| `UMS-038` | Assignment Download | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > Assignment Download` | Yes | Executable | **PASS** |
| `UMS-039` | Assignment Upload | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > Assignment Upload` | Yes | Executable | **PASS** |
| `UMS-040` | Career Aspiration Plan | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > Career Aspiration Plan` | Yes | Informational | **PASS** |
| `UMS-041` | Community Development Form | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > Community Development Form` | Yes | Executable | **PASS** |
| `UMS-042` | CR Nomination | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > CR Nomination` | Yes | Executable | **PASS** |
| `UMS-043` | Credit Transfer | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > Credit Transfer` | Yes | Informational | **PASS** |
| `UMS-044` | EDU - Revolution: Be the Change | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > EDU - Revolution: Be the Change` | Yes | Executable | **PASS** |
| `UMS-045` | EDU-Revolution Survey | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > EDU-Revolution Survey` | Yes | Informational | **PASS** |
| `UMS-046` | Education Revolution Board Feedback Platform | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > Education Revolution Board Feedback Platform` | Yes | Executable | **PASS** |
| `UMS-047` | Event Duty Leaves | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > Event Duty Leaves` | Yes | Executable | **PASS** |
| `UMS-048` | Investment LAB | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > Investment LAB` | Yes | Informational | **PASS** |
| `UMS-049` | Language Lab Slot Booking | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > Language Lab Slot Booking` | Yes | Executable | **PASS** |
| `UMS-050` | LPU Laboratory Dashboard | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > LPU Laboratory Dashboard` | Yes | Informational | **PASS** |
| `UMS-051` | Mark Teaching Practice Attendance | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > Mark Teaching Practice Attendance` | Yes | Informational | **PASS** |
| `UMS-052` | Meeting Proceedings | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > Meeting Proceedings` | Yes | Informational | **PASS** |
| `UMS-053` | My Value Added Course Certificates | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > My Value Added Course Certificates` | Yes | Executable | **PASS** |
| `UMS-054` | Personality Assessment Test | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > Personality Assessment Test` | Yes | Informational | **PASS** |
| `UMS-055` | Practical Upload | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > Practical Upload` | Yes | Executable | **PASS** |
| `UMS-056` | Registration for Value Added Course | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > Registration for Value Added Course` | Yes | Executable | **PASS** |
| `UMS-057` | Request for Change of Program | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > Request for Change of Program` | Yes | Executable | **PASS** |
| `UMS-058` | Self Learning Material | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > Self Learning Material` | Yes | Informational | **PASS** |
| `UMS-059` | Semester Exchange Registration | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > Semester Exchange Registration` | Yes | Executable | **PASS** |
| `UMS-060` | Session Calendar | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > Session Calendar` | Yes | Informational | **PASS** |
| `UMS-061` | Skill Set | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > Skill Set` | Yes | Informational | **PASS** |
| `UMS-062` | Student Centric Revenue Generation | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > Student Centric Revenue Generation` | Yes | Informational | **PASS** |
| `UMS-063` | Student Education Revolution Board Nomination | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > Student Education Revolution Board Nomination` | Yes | Executable | **PASS** |
| `UMS-064` | Student Education Revolution Feedback Platform | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > Student Education Revolution Feedback Platform` | Yes | Executable | **PASS** |
| `UMS-065` | Undertaking Format for Option Taking | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > Undertaking Format for Option Taking` | Yes | Executable | **PASS** |
| `UMS-066` | Upload Research Project Publication/Copyright Details | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > Upload Research Project Publication/Copyright Details` | Yes | Executable | **PASS** |
| `UMS-067` | View Academic Course Syllabus | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > View Academic Course Syllabus` | Yes | Informational | **PASS** |
| `UMS-068` | View Attendance | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > View Attendance` | Yes | Informational | **PASS** |
| `UMS-069` | View Instruction Plans | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > View Instruction Plans` | Yes | Informational | **PASS** |
| `UMS-070` | View Lab Manuals | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > View Lab Manuals` | Yes | Informational | **PASS** |
| `UMS-071` | View MakeUp and Adjustment Details | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > View MakeUp and Adjustment Details` | Yes | Informational | **PASS** |
| `UMS-072` | View Program Scheme | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > View Program Scheme` | Yes | Informational | **PASS** |
| `UMS-073` | View Time Table | Learning Management System (LMS) | `UMS > Learning Management System (LMS) > View Time Table` | Yes | Informational | **PASS** |
| `UMS-074` | Discussion Room Booking | Library Management System | `UMS > Library Management System > Discussion Room Booking` | Yes | Executable | **PASS** |
| `UMS-075` | Dissertation/Thesis | Library Management System | `UMS > Library Management System > Dissertation/Thesis` | Yes | Informational | **PASS** |
| `UMS-076` | E-Resources | Library Management System | `UMS > Library Management System > E-Resources` | Yes | Informational | **PASS** |
| `UMS-077` | Library Search | Library Management System | `UMS > Library Management System > Library Search` | Yes | Informational | **PASS** |
| `UMS-078` | Career Services Registration | Placement Services | `UMS > Placement Services > Career Services Registration` | Yes | Executable | **PASS** |
| `UMS-079` | Exit From Career Services | Placement Services | `UMS > Placement Services > Exit From Career Services` | Yes | Informational | **PASS** |
| `UMS-080` | Internship Recommendation Letter | Placement Services | `UMS > Placement Services > Internship Recommendation Letter` | Yes | Informational | **PASS** |
| `UMS-081` | OJT/Internship Application | Placement Services | `UMS > Placement Services > OJT/Internship Application` | Yes | Executable | **PASS** |
| `UMS-082` | OJT/Internship Attendance | Placement Services | `UMS > Placement Services > OJT/Internship Attendance` | Yes | Informational | **PASS** |
| `UMS-083` | Placement Document Repository | Placement Services | `UMS > Placement Services > Placement Document Repository` | Yes | Informational | **PASS** |
| `UMS-084` | Placement Portal | Placement Services | `UMS > Placement Services > Placement Portal` | Yes | Informational | **PASS** |
| `UMS-085` | Special Academic Benefits Request | Placement Services | `UMS > Placement Services > Special Academic Benefits Request` | Yes | Executable | **PASS** |
| `UMS-086` | Student Placement Coordinator Policy | Placement Services | `UMS > Placement Services > Student Placement Coordinator Policy` | Yes | Informational | **PASS** |
| `UMS-087` | Student Placement Coordinator Registration | Placement Services | `UMS > Placement Services > Student Placement Coordinator Registration` | Yes | Executable | **PASS** |
| `UMS-088` | Student Training and Placement Committee Registration | Placement Services | `UMS > Placement Services > Student Training and Placement Committee Registration` | Yes | Executable | **PASS** |
| `UMS-089` | Elective Specialization Polling | Polling | `UMS > Polling > Elective Specialization Polling` | Yes | Executable | **PASS** |
| `UMS-090` | Electives Polling | Polling | `UMS > Polling > Electives Polling` | Yes | Executable | **PASS** |
| `UMS-091` | Engineering Minor Area Preference | Polling | `UMS > Polling > Engineering Minor Area Preference` | Yes | Executable | **PASS** |
| `UMS-092` | Open Minor Area Preference | Polling | `UMS > Polling > Open Minor Area Preference` | Yes | Executable | **PASS** |
| `UMS-093` | CDP Certificate Download | Project / Dissertation | `UMS > Project / Dissertation > CDP Certificate Download` | Yes | Executable | **PASS** |
| `UMS-094` | Interdisciplinary Project Topics | Project / Dissertation | `UMS > Project / Dissertation > Interdisciplinary Project Topics` | Yes | Informational | **PASS** |
| `UMS-095` | Project / Dissertation Attendance View | Project / Dissertation | `UMS > Project / Dissertation > Project / Dissertation Attendance View` | Yes | Informational | **PASS** |
| `UMS-096` | Project / Dissertation Marks View | Project / Dissertation | `UMS > Project / Dissertation > Project / Dissertation Marks View` | Yes | Informational | **PASS** |
| `UMS-097` | Project / Dissertation Supervisor Information | Project / Dissertation | `UMS > Project / Dissertation > Project / Dissertation Supervisor Information` | Yes | Executable | **PASS** |
| `UMS-098` | Project Courses Group Formulation | Project / Dissertation | `UMS > Project / Dissertation > Project Courses Group Formulation` | Yes | Executable | **PASS** |
| `UMS-099` | Supervisor Profile Preview | Project / Dissertation | `UMS > Project / Dissertation > Supervisor Profile Preview` | Yes | Informational | **PASS** |
| `UMS-100` | Upload Research Project/Internship Certificate | Project / Dissertation | `UMS > Project / Dissertation > Upload Research Project/Internship Certificate` | Yes | Executable | **PASS** |
| `UMS-101` | Apply for Duty Leave and PVR | Research and Development | `UMS > Research and Development > Apply for Duty Leave and PVR` | Yes | Executable | **PASS** |
| `UMS-102` | Fellowship Process Feedback | Research and Development | `UMS > Research and Development > Fellowship Process Feedback` | Yes | Executable | **PASS** |
| `UMS-103` | International Research Program | Research and Development | `UMS > Research and Development > International Research Program` | Yes | Informational | **PASS** |
| `UMS-104` | IPR Idea Request | Research and Development | `UMS > Research and Development > IPR Idea Request` | Yes | Executable | **PASS** |
| `UMS-105` | Ph.D. Candidacy Letter | Research and Development | `UMS > Research and Development > Ph.D. Candidacy Letter` | Yes | Executable | **PASS** |
| `UMS-106` | Ph.D. Discipline Preference | Research and Development | `UMS > Research and Development > Ph.D. Discipline Preference` | Yes | Executable | **PASS** |
| `UMS-107` | Pre-submission Registration | Research and Development | `UMS > Research and Development > Pre-submission Registration` | Yes | Executable | **PASS** |
| `UMS-108` | Registration of Upcoming Activity | Research and Development | `UMS > Research and Development > Registration of Upcoming Activity` | Yes | Executable | **PASS** |
| `UMS-109` | Research Achievements Report | Research and Development | `UMS > Research and Development > Research Achievements Report` | Yes | Informational | **PASS** |
| `UMS-110` | Research Appreciation Awards for Ph.D. Scholars | Research and Development | `UMS > Research and Development > Research Appreciation Awards for Ph.D. Scholars` | Yes | Informational | **PASS** |
| `UMS-111` | Research Scholar Guidelines and Formats | Research and Development | `UMS > Research and Development > Research Scholar Guidelines and Formats` | Yes | Informational | **PASS** |
| `UMS-112` | SAS Registration Form | Research and Development | `UMS > Research and Development > SAS Registration Form` | Yes | Executable | **PASS** |
| `UMS-113` | Scholar Dashboard | Research and Development | `UMS > Research and Development > Scholar Dashboard` | Yes | Informational | **PASS** |
| `UMS-114` | Supervisor Selection Module | Research and Development | `UMS > Research and Development > Supervisor Selection Module` | Yes | Informational | **PASS** |
| `UMS-115` | View Ph.D. Attendance | Research and Development | `UMS > Research and Development > View Ph.D. Attendance` | Yes | Informational | **PASS** |
| `UMS-116` | CPE Certificate Details | Skill Development Courses | `UMS > Skill Development Courses > CPE Certificate Details` | Yes | Executable | **PASS** |
| `UMS-117` | Skill Development Courses | Skill Development Courses | `UMS > Skill Development Courses > Skill Development Courses` | Yes | Informational | **PASS** |
| `UMS-118` | Skill Development Program | Skill Development Courses | `UMS > Skill Development Courses > Skill Development Program` | Yes | Informational | **PASS** |
| `UMS-119` | Alumni Membership Fee | Alumni Services | `UMS > Alumni Services > Alumni Membership Fee` | Yes | Executable | **PASS** |
| `UMS-120` | Alumni Mentor Selection | Alumni Services | `UMS > Alumni Services > Alumni Mentor Selection` | Yes | Informational | **PASS** |
| `UMS-121` | Update Alumni Profile | Alumni Services | `UMS > Alumni Services > Update Alumni Profile` | Yes | Informational | **PASS** |
| `UMS-122` | Central Mail Receiving | Central Mail System | `UMS > Central Mail System > Central Mail Receiving` | Yes | Informational | **PASS** |
| `UMS-123` | Tracking Incoming Mail | Central Mail System | `UMS > Central Mail System > Tracking Incoming Mail` | Yes | Informational | **PASS** |
| `UMS-124` | Fee Dashboard | Fee and Scholarship System | `UMS > Fee and Scholarship System > Fee Dashboard` | Yes | Executable | **PASS** |
| `UMS-125` | Apply and Download Fee Related Certificates (Tuition Fee, Demand Letter etc.) | Fee and Scholarship System | `UMS > Fee and Scholarship System > Apply and Download Fee Related Certificates (Tuition Fee, Demand Letter etc.)` | Yes | Executable | **PASS** |
| `UMS-126` | Apply for Fee Refund/Reimbursement | Fee and Scholarship System | `UMS > Fee and Scholarship System > Apply for Fee Refund/Reimbursement` | Yes | Executable | **PASS** |
| `UMS-127` | Apply for Outer Agency Scholarship | Fee and Scholarship System | `UMS > Fee and Scholarship System > Apply for Outer Agency Scholarship` | Yes | Executable | **PASS** |
| `UMS-128` | Bank Loan Document Submission | Fee and Scholarship System | `UMS > Fee and Scholarship System > Bank Loan Document Submission` | Yes | Informational | **PASS** |
| `UMS-129` | Camp Registration | Fee and Scholarship System | `UMS > Fee and Scholarship System > Camp Registration` | Yes | Executable | **PASS** |
| `UMS-130` | Confirmation of Fee Deposited | Fee and Scholarship System | `UMS > Fee and Scholarship System > Confirmation of Fee Deposited` | Yes | Executable | **PASS** |
| `UMS-131` | Scholarship Award Request | Fee and Scholarship System | `UMS > Fee and Scholarship System > Scholarship Award Request` | Yes | Executable | **PASS** |
| `UMS-132` | Scholarship Continuation Request | Fee and Scholarship System | `UMS > Fee and Scholarship System > Scholarship Continuation Request` | Yes | Executable | **PASS** |
| `UMS-133` | Scholarship Letter | Fee and Scholarship System | `UMS > Fee and Scholarship System > Scholarship Letter` | Yes | Informational | **PASS** |
| `UMS-134` | Scholarship Policies | Fee and Scholarship System | `UMS > Fee and Scholarship System > Scholarship Policies` | Yes | Informational | **PASS** |
| `UMS-135` | View Fee Payment Schedule/Guidelines | Fee and Scholarship System | `UMS > Fee and Scholarship System > View Fee Payment Schedule/Guidelines` | Yes | Informational | **PASS** |
| `UMS-136` | View Fee Receipts | My Profile | `UMS > My Profile > View Fee Receipts` | Yes | Informational | **PASS** |
| `UMS-137` | View Fee Status | My Profile | `UMS > My Profile > View Fee Status` | Yes | Informational | **PASS** |
| `UMS-138` | My Virtual ID Card | My Profile | `UMS > My Profile > My Virtual ID Card` | Yes | Informational | **PASS** |
| `UMS-139` | Profile Update | My Profile | `UMS > My Profile > Profile Update` | Yes | Informational | **PASS** |
| `UMS-140` | Electricity Consumption View | Residential Services | `UMS > Residential Services > Electricity Consumption View` | Yes | Informational | **PASS** |
| `UMS-141` | Extended Time Request (Central Library) | Residential Services | `UMS > Residential Services > Extended Time Request (Central Library)` | Yes | Executable | **PASS** |
| `UMS-142` | Hostel Activity Undertaking | Residential Services | `UMS > Residential Services > Hostel Activity Undertaking` | Yes | Executable | **PASS** |
| `UMS-143` | Hostel Booking | Residential Services | `UMS > Residential Services > Hostel Booking` | Yes | Executable | **PASS** |
| `UMS-144` | Hostel Booking (Term-II) | Residential Services | `UMS > Residential Services > Hostel Booking (Term-II)` | Yes | Executable | **PASS** |
| `UMS-145` | Hostel Booking for Short Duration | Residential Services | `UMS > Residential Services > Hostel Booking for Short Duration` | Yes | Executable | **PASS** |
| `UMS-146` | Hostel Cloak Room Application | Residential Services | `UMS > Residential Services > Hostel Cloak Room Application` | Yes | Executable | **PASS** |
| `UMS-147` | Hostel Confiscation Item Acknowledgement | Residential Services | `UMS > Residential Services > Hostel Confiscation Item Acknowledgement` | Yes | Informational | **PASS** |
| `UMS-148` | Hostel Facilities Cancellation | Residential Services | `UMS > Residential Services > Hostel Facilities Cancellation` | Yes | Executable | **PASS** |
| `UMS-149` | Hostel Guidelines | Residential Services | `UMS > Residential Services > Hostel Guidelines` | Yes | Informational | **PASS** |
| `UMS-150` | Hostel Leave Application | Residential Services | `UMS > Residential Services > Hostel Leave Application` | Yes | Executable | **PASS** |
| `UMS-151` | Hostel Leave Slip | Residential Services | `UMS > Residential Services > Hostel Leave Slip` | Yes | Executable | **PASS** |
| `UMS-152` | Hostel Mail Acknowledgement | Residential Services | `UMS > Residential Services > Hostel Mail Acknowledgement` | Yes | Informational | **PASS** |
| `UMS-153` | Hostel Mutual Swap | Residential Services | `UMS > Residential Services > Hostel Mutual Swap` | Yes | Executable | **PASS** |
| `UMS-154` | House Keeping Rating | Residential Services | `UMS > Residential Services > House Keeping Rating` | Yes | Informational | **PASS** |
| `UMS-155` | Joy of Giving | Residential Services | `UMS > Residential Services > Joy of Giving` | Yes | Informational | **PASS** |
| `UMS-156` | Resident Details (For Day Scholars) | Residential Services | `UMS > Residential Services > Resident Details (For Day Scholars)` | Yes | Informational | **PASS** |
| `UMS-157` | Special Food Services | Residential Services | `UMS > Residential Services > Special Food Services` | Yes | Informational | **PASS** |
| `UMS-158` | Student Hostel Committee Registration | Residential Services | `UMS > Residential Services > Student Hostel Committee Registration` | Yes | Executable | **PASS** |
| `UMS-159` | Student Hostel Special Leave Request | Residential Services | `UMS > Residential Services > Student Hostel Special Leave Request` | Yes | Executable | **PASS** |
| `UMS-160` | View Residential Reporting Slip | Residential Services | `UMS > Residential Services > View Residential Reporting Slip` | Yes | Executable | **PASS** |
| `UMS-161` | Case Details | Security and Safety | `UMS > Security and Safety > Case Details` | Yes | Informational | **PASS** |
| `UMS-162` | RFID Application Form | Security and Safety | `UMS > Security and Safety > RFID Application Form` | Yes | Executable | **PASS** |
| `UMS-163` | Sponsored Parent Pass Request | Security and Safety | `UMS > Security and Safety > Sponsored Parent Pass Request` | Yes | Executable | **PASS** |
| `UMS-164` | Upload Case Statement | Security and Safety | `UMS > Security and Safety > Upload Case Statement` | Yes | Executable | **PASS** |
| `UMS-165` | External CA Format for Internship | Capstone Dissertation Internships | `UMS > Capstone Dissertation Internships > External CA Format for Internship` | Yes | Executable | **PASS** |
| `UMS-166` | Guidelines - Inviting External Examiners for Dissertation Evaluations | Capstone Dissertation Internships | `UMS > Capstone Dissertation Internships > Guidelines - Inviting External Examiners for Dissertation Evaluations` | Yes | Informational | **PASS** |
| `UMS-167` | Guidelines - Dissertation for Master Degree Programmes except M.Phil. | Capstone Dissertation Internships | `UMS > Capstone Dissertation Internships > Guidelines - Dissertation for Master Degree Programmes except M.Phil.` | Yes | Informational | **PASS** |
| `UMS-168` | Guidelines - Project Courses including Capstone/Semester 14-15 | Capstone Dissertation Internships | `UMS > Capstone Dissertation Internships > Guidelines - Project Courses including Capstone/Semester 14-15` | Yes | Informational | **PASS** |
| `UMS-169` | Guidelines for M.Phil Dissertation | Capstone Dissertation Internships | `UMS > Capstone Dissertation Internships > Guidelines for M.Phil Dissertation` | Yes | Informational | **PASS** |
| `UMS-170` | Change UMS Password | Account and Miscellaneous | `UMS > Account and Miscellaneous > Change UMS Password` | Yes | Executable | **PASS** |
| `UMS-171` | Reset Internet Password | Account and Miscellaneous | `UMS > Account and Miscellaneous > Reset Internet Password` | Yes | Informational | **PASS** |
| `UMS-172` | Animal House Facility (AHF) | Account and Miscellaneous | `UMS > Account and Miscellaneous > Animal House Facility (AHF)` | Yes | Informational | **PASS** |
| `UMS-173` | Apply Duplicate ID/Transport Card | Account and Miscellaneous | `UMS > Account and Miscellaneous > Apply Duplicate ID/Transport Card` | Yes | Executable | **PASS** |
| `UMS-174` | Admission Document Verification / Accommodation Inquiries / ID Card / Turnstiles / RFID | Appointment System and Important Links | `UMS > Appointment System and Important Links > Admission Document Verification / Accommodation Inquiries / ID Card / Turnstiles / RFID` | Yes | Executable | **PASS** |
| `UMS-175` | Compulsory Accommodation Details | Appointment System and Important Links | `UMS > Appointment System and Important Links > Compulsory Accommodation Details` | Yes | Informational | **PASS** |
| `UMS-176` | Emergency Contact Numbers | Appointment System and Important Links | `UMS > Appointment System and Important Links > Emergency Contact Numbers` | Yes | Informational | **PASS** |
| `UMS-177` | Interaction Timings with Higher Authorities | Appointment System and Important Links | `UMS > Appointment System and Important Links > Interaction Timings with Higher Authorities` | Yes | Informational | **PASS** |
| `UMS-178` | Post Request for Appointment | Appointment System and Important Links | `UMS > Appointment System and Important Links > Post Request for Appointment` | Yes | Executable | **PASS** |
| `UMS-179` | View Academic Calendar | Appointment System and Important Links | `UMS > Appointment System and Important Links > View Academic Calendar` | Yes | Informational | **PASS** |
| `UMS-180` | View Induction / University Map | Appointment System and Important Links | `UMS > Appointment System and Important Links > View Induction / University Map` | Yes | Informational | **PASS** |
| `UMS-181` | View List of Medical Staff at Uni Hospital | Appointment System and Important Links | `UMS > Appointment System and Important Links > View List of Medical Staff at Uni Hospital` | Yes | Informational | **PASS** |
| `UMS-182` | View Lost and Found Items | Appointment System and Important Links | `UMS > Appointment System and Important Links > View Lost and Found Items` | Yes | Informational | **PASS** |
| `UMS-183` | View My Messages | Appointment System and Important Links | `UMS > Appointment System and Important Links > View My Messages` | Yes | Informational | **PASS** |
| `UMS-184` | Academic Honour to Regular Students | Policies, Rules, Guidelines and Formats | `UMS > Policies, Rules, Guidelines and Formats > Academic Honour to Regular Students` | Yes | Informational | **PASS** |
| `UMS-185` | Extract of Changes in Rules and Regulations | Policies, Rules, Guidelines and Formats | `UMS > Policies, Rules, Guidelines and Formats > Extract of Changes in Rules and Regulations` | Yes | Informational | **PASS** |
| `UMS-186` | Attendance Marking Policy in Case of Late Registration | Policies, Rules, Guidelines and Formats | `UMS > Policies, Rules, Guidelines and Formats > Attendance Marking Policy in Case of Late Registration` | Yes | Informational | **PASS** |
| `UMS-187` | Download Formats | Policies, Rules, Guidelines and Formats | `UMS > Policies, Rules, Guidelines and Formats > Download Formats` | Yes | Informational | **PASS** |
| `UMS-188` | Dress Code and Uniform Policy | Policies, Rules, Guidelines and Formats | `UMS > Policies, Rules, Guidelines and Formats > Dress Code and Uniform Policy` | Yes | Informational | **PASS** |
| `UMS-189` | Examination Instructions and Guidelines | Policies, Rules, Guidelines and Formats | `UMS > Policies, Rules, Guidelines and Formats > Examination Instructions and Guidelines` | Yes | Informational | **PASS** |
| `UMS-190` | Guidelines for Credit Transfer as an Option | Policies, Rules, Guidelines and Formats | `UMS > Policies, Rules, Guidelines and Formats > Guidelines for Credit Transfer as an Option` | Yes | Informational | **PASS** |
| `UMS-191` | Guidelines for Issuance of Equipments (School of Journalism, Film and Creative Arts) | Policies, Rules, Guidelines and Formats | `UMS > Policies, Rules, Guidelines and Formats > Guidelines for Issuance of Equipments (School of Journalism, Film and Creative Arts)` | Yes | Informational | **PASS** |
| `UMS-192` | Guidelines for Option Taking | Policies, Rules, Guidelines and Formats | `UMS > Policies, Rules, Guidelines and Formats > Guidelines for Option Taking` | Yes | Informational | **PASS** |
| `UMS-193` | Library Policy | Policies, Rules, Guidelines and Formats | `UMS > Policies, Rules, Guidelines and Formats > Library Policy` | Yes | Informational | **PASS** |
| `UMS-194` | Policy for International Students | Policies, Rules, Guidelines and Formats | `UMS > Policies, Rules, Guidelines and Formats > Policy for International Students` | Yes | Informational | **PASS** |
| `UMS-195` | Scholarship to Regular Students | Policies, Rules, Guidelines and Formats | `UMS > Policies, Rules, Guidelines and Formats > Scholarship to Regular Students` | Yes | Informational | **PASS** |
| `UMS-196` | Semester / Year Abroad Policy | Policies, Rules, Guidelines and Formats | `UMS > Policies, Rules, Guidelines and Formats > Semester / Year Abroad Policy` | Yes | Informational | **PASS** |
| `UMS-197` | Alumni Feedback on Program/PSO | Feedback and Surveys | `UMS > Feedback and Surveys > Alumni Feedback on Program/PSO` | Yes | Executable | **PASS** |
| `UMS-198` | Feedback for Program Scheme and Courses | Feedback and Surveys | `UMS > Feedback and Surveys > Feedback for Program Scheme and Courses` | Yes | Informational | **PASS** |
| `UMS-199` | Feedback on Course Outcome | Feedback and Surveys | `UMS > Feedback and Surveys > Feedback on Course Outcome` | Yes | Executable | **PASS** |
| `UMS-200` | Feedback on Curriculum - Parents | Feedback and Surveys | `UMS > Feedback and Surveys > Feedback on Curriculum - Parents` | Yes | Executable | **PASS** |
| `UMS-201` | Feedback on Theory/Practical Courses | Feedback and Surveys | `UMS > Feedback and Surveys > Feedback on Theory/Practical Courses` | Yes | Executable | **PASS** |
| `UMS-202` | Grievances Description | Feedback and Surveys | `UMS > Feedback and Surveys > Grievances Description` | Yes | Informational | **PASS** |
| `UMS-203` | Guest Lecture Feedback | Feedback and Surveys | `UMS > Feedback and Surveys > Guest Lecture Feedback` | Yes | Executable | **PASS** |
| `UMS-204` | Online Survey | Feedback and Surveys | `UMS > Feedback and Surveys > Online Survey` | Yes | Informational | **PASS** |
| `UMS-205` | Rate Mentor Meeting | Feedback and Surveys | `UMS > Feedback and Surveys > Rate Mentor Meeting` | Yes | Informational | **PASS** |
| `UMS-206` | Counseling Psychologist Appointment | Health Services | `UMS > Health Services > Counseling Psychologist Appointment` | Yes | Executable | **PASS** |
| `UMS-207` | Doctor Appointment | Health Services | `UMS > Health Services > Doctor Appointment` | Yes | Executable | **PASS** |
| `UMS-208` | Log Request | Relationship Management System (RMS) | `UMS > Relationship Management System (RMS) > Log Request` | Yes | Executable | **PASS** |
| `UMS-209` | View Request Status | Relationship Management System (RMS) | `UMS > Relationship Management System (RMS) > View Request Status` | Yes | Informational | **PASS** |
| `UMS-210` | Approved Skill Courses | Student Welfare | `UMS > Student Welfare > Approved Skill Courses` | Yes | Informational | **PASS** |
| `UMS-211` | Campus Opportunities Registration | Campus Opportunities and Student Organisations | `UMS > Campus Opportunities and Student Organisations > Campus Opportunities Registration` | Yes | Executable | **PASS** |
| `UMS-212` | Club Attendance View | Campus Opportunities and Student Organisations | `UMS > Campus Opportunities and Student Organisations > Club Attendance View` | Yes | Informational | **PASS** |
| `UMS-213` | Community Services Registration | Campus Opportunities and Student Organisations | `UMS > Campus Opportunities and Student Organisations > Community Services Registration` | Yes | Executable | **PASS** |
| `UMS-214` | Event Planning Format | Campus Opportunities and Student Organisations | `UMS > Campus Opportunities and Student Organisations > Event Planning Format` | Yes | Executable | **PASS** |
| `UMS-215` | Event Registration | Campus Opportunities and Student Organisations | `UMS > Campus Opportunities and Student Organisations > Event Registration` | Yes | Executable | **PASS** |
| `UMS-216` | Idea Management System | Campus Opportunities and Student Organisations | `UMS > Campus Opportunities and Student Organisations > Idea Management System` | Yes | Executable | **PASS** |
| `UMS-217` | Individual Student Skill Course Registration | Campus Opportunities and Student Organisations | `UMS > Campus Opportunities and Student Organisations > Individual Student Skill Course Registration` | Yes | Executable | **PASS** |
| `UMS-218` | Interview Panel | Campus Opportunities and Student Organisations | `UMS > Campus Opportunities and Student Organisations > Interview Panel` | Yes | Informational | **PASS** |
| `UMS-219` | My Inventory Record | Campus Opportunities and Student Organisations | `UMS > Campus Opportunities and Student Organisations > My Inventory Record` | Yes | Informational | **PASS** |
| `UMS-220` | Opted Skill Courses | Campus Opportunities and Student Organisations | `UMS > Campus Opportunities and Student Organisations > Opted Skill Courses` | Yes | Informational | **PASS** |
| `UMS-221` | Organization Registration | Campus Opportunities and Student Organisations | `UMS > Campus Opportunities and Student Organisations > Organization Registration` | Yes | Executable | **PASS** |
| `UMS-222` | Organization Registration Report | Campus Opportunities and Student Organisations | `UMS > Campus Opportunities and Student Organisations > Organization Registration Report` | Yes | Executable | **PASS** |
| `UMS-223` | Part-Time Job Registration | Campus Opportunities and Student Organisations | `UMS > Campus Opportunities and Student Organisations > Part-Time Job Registration` | Yes | Executable | **PASS** |
| `UMS-224` | Participation and Achievements Dashboard | Campus Opportunities and Student Organisations | `UMS > Campus Opportunities and Student Organisations > Participation and Achievements Dashboard` | Yes | Executable | **PASS** |
| `UMS-225` | Policies | Campus Opportunities and Student Organisations | `UMS > Campus Opportunities and Student Organisations > Policies` | Yes | Informational | **PASS** |
| `UMS-226` | Press Release Request | Campus Opportunities and Student Organisations | `UMS > Campus Opportunities and Student Organisations > Press Release Request` | Yes | Executable | **PASS** |
| `UMS-227` | Request for Recruitment Drive | Campus Opportunities and Student Organisations | `UMS > Campus Opportunities and Student Organisations > Request for Recruitment Drive` | Yes | Executable | **PASS** |
| `UMS-228` | Student Event Participation | Campus Opportunities and Student Organisations | `UMS > Campus Opportunities and Student Organisations > Student Event Participation` | Yes | Executable | **PASS** |
| `UMS-229` | Student Event Registration | Campus Opportunities and Student Organisations | `UMS > Campus Opportunities and Student Organisations > Student Event Registration` | Yes | Executable | **PASS** |
| `UMS-230` | Student Interest Group Registration | Campus Opportunities and Student Organisations | `UMS > Campus Opportunities and Student Organisations > Student Interest Group Registration` | Yes | Executable | **PASS** |
| `UMS-231` | Student Organization Registration | Campus Opportunities and Student Organisations | `UMS > Campus Opportunities and Student Organisations > Student Organization Registration` | Yes | Executable | **PASS** |
| `UMS-232` | Transport Preference | Campus Opportunities and Student Organisations | `UMS > Campus Opportunities and Student Organisations > Transport Preference` | Yes | Executable | **PASS** |
| `UMS-233` | Uniform Size Selection | Campus Opportunities and Student Organisations | `UMS > Campus Opportunities and Student Organisations > Uniform Size Selection` | Yes | Executable | **PASS** |
| `UMS-234` | Vendor Services Search | Campus Opportunities and Student Organisations | `UMS > Campus Opportunities and Student Organisations > Vendor Services Search` | Yes | Informational | **PASS** |