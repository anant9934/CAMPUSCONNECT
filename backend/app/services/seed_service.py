import logging
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.security import get_password_hash
from app.models import AdminUser, Category, FAQ, FAQSource

logger = logging.getLogger(__name__)

INITIAL_CATEGORIES = [
    {
        "name": "Academics & Curriculum",
        "slug": "academics",
        "description": "Academic policies, UMS portal, attendance criteria (75% requirement), course registration, and continuous assessment.",
        "icon": "GraduationCap",
        "display_order": 1,
    },
    {
        "name": "Examinations & Grading",
        "slug": "examinations",
        "description": "Date sheet schedules, End Term Examinations (ETE), Mid Term, admit card download, Block 34 exam division, and re-evaluation.",
        "icon": "FileText",
        "display_order": 2,
    },
    {
        "name": "Hostel & Residential Life",
        "slug": "hostel",
        "description": "Hostel room allocation, biometric attendance, night leave outpass via UMS, mess food committees, and warden contacts.",
        "icon": "Home",
        "display_order": 3,
    },
    {
        "name": "Transport & Bus Routes",
        "slug": "transport",
        "description": "University bus fleet, daily routes covering Jalandhar, Phagwara, Ludhiana, bus pass applications, and campus transit.",
        "icon": "Bus",
        "display_order": 4,
    },
    {
        "name": "Fees & Financial Services",
        "slug": "fees",
        "description": "Semester tuition fees, online payment methods via UMS, fee installment guidelines, scholarships, and fee receipts.",
        "icon": "CreditCard",
        "display_order": 5,
    },
    {
        "name": "Campus Facilities & Medical",
        "slug": "campus-services",
        "description": "UniHospital 24x7 emergency medical center, UniMall shopping complex, sports arena, and Division of Student Affairs (Block 13).",
        "icon": "Building2",
        "display_order": 6,
    },
    {
        "name": "Library Services",
        "slug": "library",
        "description": "Central Library (Block 37), digital book reservations, e-journals, reading halls, and working hours.",
        "icon": "BookOpen",
        "display_order": 7,
    },
    {
        "name": "Admissions & General Support",
        "slug": "admissions",
        "description": "Admissions verification, LPUNEST entrance test guidance, international student desk, and general campus contacts.",
        "icon": "HelpCircle",
        "display_order": 8,
    },
]

INITIAL_FAQS = [
    {
        "category_slug": "academics",
        "canonical_question": "What is the mandatory attendance requirement at LPU?",
        "alternative_questions": [
            "How much attendance is required to sit in exams?",
            "What is the minimum attendance percentage at Lovely Professional University?",
            "Will I be debarred if my attendance is below 75 percent?",
            "Can duty leave or medical leave compensate attendance?"
        ],
        "answer": "At Lovely Professional University (LPU), students are required to maintain a minimum of 75% aggregate attendance in each registered course to be eligible to appear for the End Term Examinations (ETE). Attendance is tracked digitally via the LPU UMS (University Management System). Students with attendance between 65% and 74% may only be permitted under verified medical grounds or sanctioned university duty leave approved through the Relationship Management System (RMS) on UMS, subject to Academic Council guidelines.",
        "keywords": ["attendance", "75 percent", "debarred", "UMS", "eligibility", "end term examination", "duty leave", "medical"],
        "source_url": "https://ums.lpu.in",
        "source_title": "LPU Academic Regulations & Student Handbook",
        "source_type": "Official Policy",
        "content_owner": "Division of Academic Affairs",
    },
    {
        "category_slug": "academics",
        "canonical_question": "How do I access and log in to LPU UMS (University Management System)?",
        "alternative_questions": [
            "Where can I find LPU UMS portal?",
            "How do students check grades, timetable and notices?",
            "What is the website link for LPU student login?",
            "How to login to Lovely Professional University portal?"
        ],
        "answer": "LPU students access all academic services through the official University Management System (UMS) portal at https://ums.lpu.in or the official LPU Touch mobile app. Students log in using their unique university Registration Number and student password. UMS provides access to daily class timetables, digital course material, Continuous Assessment (CA) scores, teacher announcements, fee payments, and the RMS grievance ticketing system.",
        "keywords": ["UMS", "login", "portal", "registration number", "LPU Touch", "timetable", "grades", "notices"],
        "source_url": "https://ums.lpu.in",
        "source_title": "LPU UMS Student Portal",
        "source_type": "Official Portal",
        "content_owner": "Center for Information Technology",
    },
    {
        "category_slug": "examinations",
        "canonical_question": "How do I download my examination date sheet at LPU?",
        "alternative_questions": [
            "Where can I find the exam date sheet?",
            "How to check End Term Examination schedule?",
            "Where does LPU publish mid-term and end-term exam timetables?",
            "How do I download my date sheet from UMS?"
        ],
        "answer": "To download your examination date sheet at LPU: 1. Log in to your UMS portal at https://ums.lpu.in or open the LPU Touch application. 2. Navigate to the 'Examination' section in the main navigation menu. 3. Click on 'Date Sheet' / 'Final Date Sheet'. 4. Select your current academic term/semester. 5. Download and verify your course codes, exam dates, timings, and designated examination block (e.g., Block 34 / designated exam halls). Any clash or discrepancy must be reported immediately to the Examination Division via RMS.",
        "keywords": ["date sheet", "examination", "download date sheet", "exam schedule", "Block 34", "end term", "mid term"],
        "source_url": "https://ums.lpu.in",
        "source_title": "LPU Examination Division Guidelines",
        "source_type": "Official Portal",
        "content_owner": "Division of Examination",
    },
    {
        "category_slug": "examinations",
        "canonical_question": "Where is the LPU Central Examination Division located and how to reach them?",
        "alternative_questions": [
            "Which block is the examination department in LPU?",
            "Where do I submit exam re-evaluation or transcript requests?",
            "Where is Block 34 in LPU?",
            "How to contact LPU exam cell?"
        ],
        "answer": "The LPU Central Examination Division is situated in Block 34 on the main campus. Students can visit the Helpdesk counters in Block 34 for issues regarding Grade Cards, transcripts, degree certificates, re-evaluation inquiries, and examination clearances. For online inquiries, students should submit a ticket through the RMS (Relationship Management System) under the 'Examination' category.",
        "keywords": ["Block 34", "exam division", "transcripts", "grade card", "re-evaluation", "examination cell", "RMS"],
        "source_url": "https://ums.lpu.in",
        "source_title": "LPU Campus Directory — Examination Division",
        "source_type": "Campus Directory",
        "content_owner": "Division of Examination",
    },
    {
        "category_slug": "hostel",
        "canonical_question": "How do I apply for a hostel night leave or outpass at LPU?",
        "alternative_questions": [
            "How to get night pass in LPU hostel?",
            "What is the hostel outpass procedure?",
            "How do residential students get permission to go home?",
            "Can I apply for leave on LPU Touch app?"
        ],
        "answer": "Hostel residents at LPU must apply for night leave or an outpass digitally through the UMS portal or the LPU Touch app. Steps: 1. Open UMS -> 'Hostel Management' -> 'Leave / Outpass Application'. 2. Enter the departure date, return date, reason, and destination address. 3. Enter emergency contact / parent details. 4. The automated system or hostel warden verifies parental approval via registered SMS/call consent. 5. Once approved, the digital pass barcode is scanned at the hostel gate and university security turnstiles upon departure and return.",
        "keywords": ["hostel", "night leave", "outpass", "UMS", "warden", "biometric", "leave application", "parent consent"],
        "source_url": "https://ums.lpu.in",
        "source_title": "LPU Residential Services Handbook",
        "source_type": "Official Handbook",
        "content_owner": "Division of Student Residential Services",
    },
    {
        "category_slug": "hostel",
        "canonical_question": "How can I contact hostel administration and wardens?",
        "alternative_questions": [
            "How to contact hostel support in LPU?",
            "Where is the Chief Warden office?",
            "Who do I contact for hostel maintenance or room issues?",
            "How do I report hostel room problems?"
        ],
        "answer": "For hostel-related assistance at LPU: 1. Visit the Warden Office located on the ground floor of your respective hostel block (BH for Boys Hostels, GH for Girls Hostels). 2. For maintenance complaints (electrical, carpentry, plumbing, or AC servicing), log a maintenance ticket directly in UMS under 'Hostel Maintenance'. 3. For emergency issues, 24x7 security and warden control rooms are stationed at every residential complex entrance.",
        "keywords": ["hostel support", "warden", "maintenance", "BH", "GH", "room service", "residential"],
        "source_url": "https://ums.lpu.in",
        "source_title": "LPU Hostel Administrative Contacts",
        "source_type": "Administrative Directory",
        "content_owner": "Division of Student Residential Services",
    },
    {
        "category_slug": "transport",
        "canonical_question": "Where can I find LPU university bus routes and timings?",
        "alternative_questions": [
            "How do I check bus schedules for LPU?",
            "Does LPU provide transport from Jalandhar, Phagwara, or Ludhiana?",
            "Where to find the bus route list?",
            "How to apply for university bus transport pass?"
        ],
        "answer": "Lovely Professional University operates an extensive dedicated bus fleet connecting the campus (located on NH-44, Phagwara, Punjab) with key nearby cities including Jalandhar, Phagwara, Ludhiana, Amritsar, Hoshiarpur, and Kapurthala. Bus schedules, route stops, pickup timings, and bus numbers are published on the UMS portal under 'Transport Services'. To subscribe, students can apply for a semester transport pass via UMS and collect their digital RFID bus pass from the Transport Department in Block 30.",
        "keywords": ["bus routes", "transport", "bus timings", "Jalandhar", "Phagwara", "Ludhiana", "bus pass", "NH-44"],
        "source_url": "https://www.lpu.in/campus_life/transport.php",
        "source_title": "LPU Transport Department Services",
        "source_type": "Official Webpage",
        "content_owner": "Department of University Transport",
    },
    {
        "category_slug": "fees",
        "canonical_question": "How do I pay semester tuition fees and download fee receipts at LPU?",
        "alternative_questions": [
            "How can I pay my university fees online?",
            "Where to download fee receipt on UMS?",
            "What payment methods are supported for LPU fee payment?",
            "How do I check pending fee dues?"
        ],
        "answer": "To pay semester fees and obtain receipts: 1. Log in to LPU UMS at https://ums.lpu.in. 2. Navigate to 'Fee Management' -> 'Pay Fee Online'. 3. Review your fee breakdown (tuition, hostel, examination, transport). 4. Pay securely using Net Banking, UPI, Credit/Debit Card, or generate an RTGS/NEFT challan. 5. Immediately after successful transaction, fee receipts with official transaction IDs are available under 'Fee Statement & Receipts' for instant download as PDF.",
        "keywords": ["fee payment", "tuition fee", "fee receipt", "UMS", "challan", "UPI", "net banking", "fee statement"],
        "source_url": "https://ums.lpu.in",
        "source_title": "LPU Accounts & Finance Division",
        "source_type": "Official Portal",
        "content_owner": "Division of Accounts and Finance",
    },
    {
        "category_slug": "library",
        "canonical_question": "How do I access LPU Central Library services and digital resources?",
        "alternative_questions": [
            "Where is the main library in LPU?",
            "What are the library timings at Lovely Professional University?",
            "How to issue books in LPU library?",
            "Where is Block 37 in LPU?"
        ],
        "answer": "The LPU Central Library (Dr. S. Radhakrishnan Central Library) is located in Block 37. It is a multi-storey learning hub equipped with automated RFID circulation kiosks, thousands of reference volumes, silent study halls, and computer access terminals. Students can search the online public access catalog (OPAC) and access thousands of IEEE, Springer, Scopus, and Elsevier e-journals through the Digital Library tab on UMS. Books can be issued using your Student RFID Smart Card.",
        "keywords": ["library", "Block 37", "central library", "books", "RFID", "OPAC", "e-journals", "digital library"],
        "source_url": "https://www.lpu.in/academics/library.php",
        "source_title": "LPU Central Library Division (Block 37)",
        "source_type": "Official Webpage",
        "content_owner": "Department of Library Services",
    },
    {
        "category_slug": "campus-services",
        "canonical_question": "What medical facilities are available on the LPU campus?",
        "alternative_questions": [
            "Is there a hospital inside LPU campus?",
            "Where can I get emergency medical help in LPU?",
            "What are UniHospital contact details and services?",
            "Does LPU have 24/7 ambulance service?"
        ],
        "answer": "LPU maintains a dedicated 24x7 healthcare facility known as UniHospital (Uni-Hospital), situated on the main campus near the residential sector. UniHospital is equipped with resident doctors, nursing staff, clinical pathology labs, pharmacy, emergency beds, and 24x7 ambulance services. Basic consultations and emergency primary care are provided free of charge to registered university students upon showing their student ID card.",
        "keywords": ["UniHospital", "hospital", "medical", "doctor", "ambulance", "emergency", "health", "pharmacy"],
        "source_url": "https://www.lpu.in/campus_life/healthcare.php",
        "source_title": "LPU Healthcare & UniHospital",
        "source_type": "Official Webpage",
        "content_owner": "UniHospital Administration",
    },
    {
        "category_slug": "campus-services",
        "canonical_question": "Where can I find student services, clubs and welfare support in LPU?",
        "alternative_questions": [
            "Where is the Division of Student Affairs (DSA)?",
            "Which block handles cultural events, student clubs and sports?",
            "Where is Block 13 in LPU?",
            "What is UniMall in LPU?"
        ],
        "answer": "The Division of Student Welfare and Division of Student Affairs (DSA) are headquartered in Block 13. Block 13 coordinates student cultural clubs, technical societies, NCC, NSS, sports activities, and youth festivals. Additionally, the university campus features UniMall, a multi-level commercial hub providing stationery shops, postal services, bank branches (SBI, PNB, etc.), ATMs, salon, apparel, and food courts.",
        "keywords": ["Block 13", "DSA", "Division of Student Affairs", "student welfare", "clubs", "UniMall", "sports"],
        "source_url": "https://www.lpu.in/campus_life/campus_facilities.php",
        "source_title": "LPU Campus Life & Student Welfare",
        "source_type": "Official Webpage",
        "content_owner": "Division of Student Welfare",
    },
    {
        "category_slug": "academics",
        "canonical_question": "Where can I find the official LPU Academic Calendar?",
        "alternative_questions": [
            "How do I know semester start and end dates?",
            "When are summer and winter vacations at LPU?",
            "Where is the academic calendar published on UMS?",
            "What are the semester exam and break dates?"
        ],
        "answer": "The official LPU Academic Calendar for each session is published on the UMS portal (https://ums.lpu.in) under 'Academic Information' -> 'Academic Calendar'. It provides detailed semester timelines, including term commencement dates, continuous assessment submission windows, Mid-Term Examination schedules, End-Term Practical and Theory Examination periods, university holidays, and scheduled winter/summer breaks.",
        "keywords": ["academic calendar", "semester dates", "holidays", "vacation", "UMS", "exam dates", "term start"],
        "source_url": "https://ums.lpu.in",
        "source_title": "LPU Academic Calendar & Schedule",
        "source_type": "Official Portal",
        "content_owner": "Division of Academic Affairs",
    }
]


async def seed_database(db: AsyncSession) -> None:
    """Seed initial LPU categories, approved FAQs, and default admin user."""
    # 1. Seed Admin User
    admin_result = await db.execute(
        select(AdminUser).where(AdminUser.username == settings.ADMIN_DEFAULT_USERNAME)
    )
    admin = admin_result.scalars().first()
    if not admin:
        logger.info(f"Seeding default admin user '{settings.ADMIN_DEFAULT_USERNAME}'")
        admin = AdminUser(
            username=settings.ADMIN_DEFAULT_USERNAME,
            email=settings.ADMIN_DEFAULT_EMAIL,
            full_name="LPU Campus Administrator",
            hashed_password=get_password_hash(settings.ADMIN_DEFAULT_PASSWORD),
            role="superadmin",
            is_active=True,
        )
        db.add(admin)
        await db.flush()

    # 2. Seed Categories
    category_map = {}
    for cat_data in INITIAL_CATEGORIES:
        cat_result = await db.execute(
            select(Category).where(Category.slug == cat_data["slug"])
        )
        existing_cat = cat_result.scalars().first()
        if not existing_cat:
            logger.info(f"Seeding category '{cat_data['name']}'")
            category = Category(
                name=cat_data["name"],
                slug=cat_data["slug"],
                description=cat_data["description"],
                icon=cat_data["icon"],
                display_order=cat_data["display_order"],
                is_active=True,
            )
            db.add(category)
            await db.flush()
            category_map[cat_data["slug"]] = category
        else:
            category_map[cat_data["slug"]] = existing_cat

    # 3. Seed FAQs
    for faq_data in INITIAL_FAQS:
        cat = category_map.get(faq_data["category_slug"])
        if not cat:
            continue
        
        faq_result = await db.execute(
            select(FAQ).where(FAQ.canonical_question == faq_data["canonical_question"])
        )
        existing_faq = faq_result.scalars().first()
        if not existing_faq:
            logger.info(f"Seeding FAQ: '{faq_data['canonical_question']}'")
            faq = FAQ(
                category_id=cat.id,
                canonical_question=faq_data["canonical_question"],
                alternative_questions=faq_data["alternative_questions"],
                answer=faq_data["answer"],
                keywords=faq_data["keywords"],
                source_url=faq_data["source_url"],
                source_title=faq_data["source_title"],
                source_type=faq_data["source_type"],
                last_reviewed=datetime.now(timezone.utc),
                approval_status="approved",
                is_approved=True,
                content_owner=faq_data["content_owner"],
                version=1,
            )
            db.add(faq)
            await db.flush()

            # Add Source
            source = FAQSource(
                faq_id=faq.id,
                url=faq_data["source_url"],
                title=faq_data["source_title"],
                source_type="official_institutional_portal",
                verified=True,
                last_verified_at=datetime.now(timezone.utc),
            )
            db.add(source)

    # 4. Ingest Extended 80 FAQs CSV if present
    import os
    import csv
    from app.models import KnowledgeDocument, KnowledgeChunk
    from app.services.document_service import process_document_file

    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    csv_path = os.path.join(root_dir, "data", "campusconnect_lpu_knowledge_base_80_faqs.csv")
    if os.path.exists(csv_path):
        logger.info(f"Ingesting extended LPU knowledge base from {csv_path}")
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                q_text = row.get("canonical_question", "").strip()
                if not q_text:
                    continue

                # Check if already exists
                faq_exists = (await db.execute(
                    select(FAQ).where(FAQ.canonical_question == q_text)
                )).scalars().first()
                if faq_exists:
                    continue

                cat_raw = row.get("category", "General").strip()
                cat_slug = cat_raw.lower().replace(" ", "-").replace("&", "and")
                cat_obj = category_map.get(cat_slug)
                if not cat_obj:
                    # Look up in DB by name or slug
                    cat_db = (await db.execute(
                        select(Category).where((Category.slug == cat_slug) | (Category.name == cat_raw))
                    )).scalars().first()
                    if not cat_db:
                        cat_db = Category(
                            name=cat_raw,
                            slug=cat_slug,
                            description=f"Institutional knowledge regarding {cat_raw} at Lovely Professional University.",
                            icon="Folder",
                            display_order=len(category_map) + 1,
                            is_active=True,
                        )
                        db.add(cat_db)
                        await db.flush()
                    category_map[cat_slug] = cat_db
                    cat_obj = cat_db

                new_faq = FAQ(
                    category_id=cat_obj.id,
                    canonical_question=q_text,
                    alternative_questions=[q_text.replace("?", ""), f"LPU {q_text}"],
                    answer=row.get("answer", "").strip(),
                    keywords=[cat_raw.lower(), "lpu", "university", "phagwara"],
                    source_url=row.get("source_url", "https://ums.lpu.in").strip(),
                    source_title=row.get("source_title", "Official LPU Portal").strip(),
                    source_type="Official Portal",
                    last_reviewed=datetime.now(timezone.utc),
                    approval_status="approved",
                    is_approved=True,
                    content_owner="Lovely Professional University",
                    version=1,
                )
                db.add(new_faq)
                await db.flush()

                new_source = FAQSource(
                    faq_id=new_faq.id,
                    url=new_faq.source_url,
                    title=new_faq.source_title,
                    source_type="official_institutional_portal",
                    verified=True,
                    last_verified_at=datetime.now(timezone.utc),
                )
                db.add(new_source)

    # 5. Ingest Academic Benefits copy.pdf if present
    pdf_path = os.path.join(root_dir, "Academic Benefits copy.pdf")
    if os.path.exists(pdf_path):
        existing_doc = (await db.execute(
            select(KnowledgeDocument).where(KnowledgeDocument.filename == "Academic Benefits copy.pdf")
        )).scalars().first()
        if not existing_doc:
            logger.info("Ingesting official LPU Academic Benefits Guide PDF...")
            try:
                chunks = process_document_file(pdf_path, "application/pdf")
                academics_cat = category_map.get("academics")
                doc = KnowledgeDocument(
                    category_id=academics_cat.id if academics_cat else None,
                    title="LPU Academic Regulations & EDU Revolution Guide",
                    filename="Academic Benefits copy.pdf",
                    file_path=pdf_path,
                    file_size=os.path.getsize(pdf_path),
                    mime_type="application/pdf",
                    status="approved",
                    is_approved=True,
                    total_chunks=len(chunks),
                )
                db.add(doc)
                await db.flush()

                for ch in chunks:
                    chunk_obj = KnowledgeChunk(
                        document_id=doc.id,
                        chunk_index=ch["chunk_index"],
                        content=ch["content"],
                        clean_text=ch["clean_text"],
                        page_number=ch.get("page_number", 1),
                        token_count=ch.get("token_count", 0),
                    )
                    db.add(chunk_obj)
                logger.info(f"Ingested {len(chunks)} chunks from Academic Benefits guide.")
            except Exception as e:
                logger.error(f"Error ingesting PDF document: {e}")

    # 6. Ingest Unified Multi-Type Knowledge Records (12 Types)
    from app.services.ingestion.extended_pack_ingestor import ExtendedPackIngestor
    ingestor = ExtendedPackIngestor(root_dir)
    await ingestor.ingest_all(db)

    # 7. Ingest SRS v3.0 UMS Service Catalog (234 items), Action Workflows (24 items), & Campus Places
    from app.services.ingestion.ums_catalog_ingestor import (
        ingest_ums_service_catalog,
        ingest_action_workflows,
        seed_campus_places,
    )
    ums_csv = os.path.join(root_dir, "data", "ums_service_catalog_from_screenshots.csv")
    if not os.path.exists(ums_csv):
        ums_csv = os.path.join(root_dir, "ums_service_catalog_from_screenshots.csv")
    await ingest_ums_service_catalog(db, ums_csv)

    wf_csv = os.path.join(root_dir, "data", "ums_navigation_booking_action_workflows.csv")
    if not os.path.exists(wf_csv):
        wf_csv = os.path.join(root_dir, "ums_navigation_booking_action_workflows.csv")
    await ingest_action_workflows(db, wf_csv)

    await seed_campus_places(db)

    await db.commit()
    logger.info("Database seeding completed successfully.")
