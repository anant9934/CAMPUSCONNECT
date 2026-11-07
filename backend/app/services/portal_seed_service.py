import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.portal import StudentOpportunity, CampusEvent

logger = logging.getLogger(__name__)

VERIFIED_OPPORTUNITIES = [
    {
        "title": "Microsoft Campus Recruitment Drive 2026",
        "opportunity_type": "placement",
        "organizer": "Division of Career Services (DCS) x Microsoft",
        "description": "Full-time Software Development Engineer (SDE-1) campus recruitment drive for graduating batch. Includes online coding round, technical viva, and HR interview.",
        "eligibility": "B.Tech CSE/IT with CGPA >= 7.5 and 0 active backlogs on UMS profile.",
        "deadline": "November 30, 2026",
        "stipend_or_reward": "CTC ₹18 LPA - ₹44 LPA",
        "target_programmes": ["B.Tech CSE", "B.Tech IT", "MCA"],
        "application_link": "https://ums.lpu.in/lpuums/ (Placement Services > View Eligible Drives)"
    },
    {
        "title": "Smart India Hackathon (SIH 2026) Institutional Selection",
        "opportunity_type": "hackathon",
        "organizer": "Division of Student Welfare & School of CSE",
        "description": "Internal university evaluation to select top 35 teams representing LPU at SIH 2026. Teams receive mentor guidance, lab access, and official duty leave.",
        "eligibility": "Open to all enrolled undergraduate and postgraduate students. Team of 6 (minimum 1 female member).",
        "deadline": "December 15, 2026",
        "stipend_or_reward": "National Prize ₹1,00,000 per theme + Duty Leave + CA Exemption (CAT-04)",
        "target_programmes": ["All Engineering & Technology Programmes"],
        "application_link": "https://ums.lpu.in/lpuums/ (Events & Hackathons Portal)"
    },
    {
        "title": "LPU Startup School Incubation Cohort 8",
        "opportunity_type": "competition",
        "organizer": "LPU Startup School & Innovation Council",
        "description": "Comprehensive incubation programme offering co-working space in Block 13, prototyping labs, legal incorporation assistance, and investor demo day access.",
        "eligibility": "Students or alumni with a working prototype or validated business model.",
        "deadline": "January 10, 2027",
        "stipend_or_reward": "Up to ₹2,50,000 Seed Grant + Capstone Project Substitution (CAT-05)",
        "target_programmes": ["All Disciplines"],
        "application_link": "https://www.lpu.in/startupschool/"
    },
    {
        "title": "DRDO & National Agency Sponsored Research Internship",
        "opportunity_type": "internship",
        "organizer": "Division of Research & Development (DRD)",
        "description": "6-month research internship on cyber physical systems, radar signal processing, and defense AI models in collaboration with premier national defense labs.",
        "eligibility": "Pre-final and final year B.Tech/M.Tech students with strong fundamentals in AI/ML or Embedded Systems.",
        "deadline": "December 20, 2026",
        "stipend_or_reward": "Monthly Stipend ₹25,000 + 1 Grade Up in Core Course (LPU-EDREV-005)",
        "target_programmes": ["B.Tech CSE", "B.Tech ECE", "M.Tech CSE"],
        "application_link": "https://ums.lpu.in/lpuums/ (Research Cell > Apply Internship)"
    },
    {
        "title": "Semester Abroad & Global Exchange (Coventry & UNA)",
        "opportunity_type": "international",
        "organizer": "Division of International Affairs (DIA)",
        "description": "Study one full semester at accredited partner universities in the UK or USA with full academic credit transfer to your LPU transcript.",
        "eligibility": "Completed minimum 2 years of study with CGPA >= 7.0 and valid passport.",
        "deadline": "November 25, 2026",
        "stipend_or_reward": "100% Tuition Fee Waiver at Partner Institution (LPU Tuition Applicable)",
        "target_programmes": ["B.Tech", "BBA", "MBA", "B.Des"],
        "application_link": "https://www.lpu.in/international/study-abroad.php"
    }
]

VERIFIED_EVENTS = [
    {
        "title": "End-Term Theory & Practical Examinations (December 2026)",
        "category": "academic",
        "venue": "Assigned Examination Centers (Blocks 25–38)",
        "event_date": "Dec 01, 2026 - Dec 23, 2026",
        "description": "Statutory end-term theory and laboratory practical examinations. Final datesheet published on UMS Examination portal. RFID Student Card and Hall Ticket mandatory.",
        "organizing_department": "Division of Examination",
        "registration_link": "https://ums.lpu.in/lpuums/ (Examination > Datesheet)"
    },
    {
        "title": "One World & One India Cultural Fest 2026",
        "category": "cultural",
        "venue": "Baldev Raj Mittal Unipolis",
        "event_date": "Feb 12, 2027 - Feb 14, 2027",
        "description": "Flagship international and pan-Indian cultural exhibition featuring cultural pavilions, culinary showcases, traditional music, and student performances from 50+ countries.",
        "organizing_department": "Division of Student Welfare (DSW)",
        "registration_link": "https://ums.lpu.in/lpuums/ (DSW > Cultural Events)"
    },
    {
        "title": "LPU Global AI & Cyber Tech Conference",
        "category": "technical",
        "venue": "Shanti Devi Mittal Auditorium (North Campus)",
        "event_date": "Jan 18, 2027 - Jan 19, 2027",
        "description": "Keynote addresses by IEEE fellows, live generative AI workshops, and paper presentations on deep learning, generative models, and quantum security.",
        "organizing_department": "School of Computer Science & Engineering",
        "registration_link": "https://ums.lpu.in/lpuums/ (Conferences & Seminars)"
    },
    {
        "title": "Annual Inter-Hostel Sports Olympiad 2026",
        "category": "sports",
        "venue": "Uni-Stadium & Multi-Purpose Indoor Sports Complex",
        "event_date": "Dec 26, 2026 - Dec 30, 2026",
        "description": "Inter-hostel sports tournament covering football, cricket, basketball, volleyball, athletics, badminton, and chess. Medals, trophies, and official Duty Leave granted.",
        "organizing_department": "Department of Sports & Physical Education",
        "registration_link": "https://ums.lpu.in/lpuums/ (Sports Services > Tournaments)"
    }
]


async def seed_portal_data(db: AsyncSession) -> None:
    """Populates initial verified opportunities and events if not already present."""
    opp_count = (await db.execute(select(StudentOpportunity))).scalars().first()
    if not opp_count:
        for opp in VERIFIED_OPPORTUNITIES:
            db.add(StudentOpportunity(**opp, is_verified=True))
        logger.info(f"Seeded {len(VERIFIED_OPPORTUNITIES)} verified student opportunities.")

    evt_count = (await db.execute(select(CampusEvent))).scalars().first()
    if not evt_count:
        for evt in VERIFIED_EVENTS:
            db.add(CampusEvent(**evt, is_verified=True))
        logger.info(f"Seeded {len(VERIFIED_EVENTS)} verified campus events.")

    await db.commit()
