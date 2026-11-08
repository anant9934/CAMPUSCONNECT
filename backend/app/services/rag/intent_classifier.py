"""
CampusConnect 12-Category Query Intent Classifier (Data Quality v4.0)
Maps student queries to institutional intents, candidate record types,
safety guardrails, and optimal retrieval strategies.
"""
import re
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple


class QueryIntent(str, Enum):
    ACADEMIC_REGULATION = "academic_regulation"
    EXAMINATION_SCHEDULE = "examination_schedule"
    HOSTEL_HOUSING = "hostel_housing"
    TRANSPORT_MOBILITY = "transport_mobility"
    FEES_SCHOLARSHIP = "fees_scholarship"
    PLACEMENT_CAREER = "placement_career"
    CAMPUS_FACILITY_NAV = "campus_facility_nav"
    HEALTH_EMERGENCY = "health_emergency"
    GRIEVANCE_RMS = "grievance_rms"
    FACULTY_DIRECTORY = "faculty_directory"
    UMS_SERVICE_NAV = "ums_service_nav"
    GENERAL_CAMPUS_LIFE = "general_campus_life"


INTENT_METADATA: Dict[QueryIntent, Dict[str, Any]] = {
    QueryIntent.ACADEMIC_REGULATION: {
        "candidate_types": ["academic_regulation", "policy", "attendance_policy", "grading_system"],
        "category_slugs": ["academics", "academic-regulations"],
        "guardrail": "Explain institutional rules, minimum CGPA, and attendance thresholds. Clarify that personal attendance requires authenticated UMS login."
    },
    QueryIntent.EXAMINATION_SCHEDULE: {
        "candidate_types": ["examination_rule", "important_date_academic_calendar", "process_sop"],
        "category_slugs": ["examinations", "academic-calendar"],
        "guardrail": "Provide official exam rules, admit card guidelines, and datesheet navigation. Note that specific personal seating plans are inside UMS."
    },
    QueryIntent.HOSTEL_HOUSING: {
        "candidate_types": ["hostel_rule", "fee_structure", "process_sop", "action_workflow"],
        "category_slugs": ["hostel", "residential-services"],
        "guardrail": "Explain room types, appliances allowed, curfews, and booking procedures. Never claim to book a room directly without UMS handoff."
    },
    QueryIntent.TRANSPORT_MOBILITY: {
        "candidate_types": ["transport_route", "process_sop", "fee_structure"],
        "category_slugs": ["transport"],
        "guardrail": "Provide commuter bus timings, routes, and bus pass application procedures."
    },
    QueryIntent.FEES_SCHOLARSHIP: {
        "candidate_types": ["fee_structure", "scholarship_scheme", "policy"],
        "category_slugs": ["fees", "scholarships"],
        "guardrail": "Quote verified published fee slabs and LPUNEST scholarship brackets. Explicitly state program applicability (e.g. B.Tech CSE AI/ML). Never execute payments."
    },
    QueryIntent.PLACEMENT_CAREER: {
        "candidate_types": ["placement_policy", "placement_statistic", "process_sop"],
        "category_slugs": ["placements", "career-services"],
        "guardrail": "Provide official eligibility criteria (CGPA, backlogs) and dream offer policies."
    },
    QueryIntent.CAMPUS_FACILITY_NAV: {
        "candidate_types": ["campus_facility", "campus_place", "library_resource", "research_centre_lab"],
        "category_slugs": ["campus-services", "library", "campus-places"],
        "guardrail": "Provide verified block numbers, room coordinates, and operating hours."
    },
    QueryIntent.HEALTH_EMERGENCY: {
        "candidate_types": ["medical_health_service", "security_emergency_protocol"],
        "category_slugs": ["campus-health", "safety"],
        "guardrail": "For urgent medical distress, prioritize Uni-Hospital Block 30 and emergency ambulance helpline (+91-1824-517000 / Ext 100) before any online booking."
    },
    QueryIntent.GRIEVANCE_RMS: {
        "candidate_types": ["grievance_redressal_mechanism", "action_workflow", "policy"],
        "category_slugs": ["student-grievance", "student-safety"],
        "guardrail": "Guide student to official RMS portal on UMS. Remind student never to submit sensitive confidential grievance evidence in public chat."
    },
    QueryIntent.FACULTY_DIRECTORY: {
        "candidate_types": ["faculty_profile", "office_directory"],
        "category_slugs": ["faculty-profile", "office-directory"],
        "guardrail": "Provide verified faculty designations, research areas, and employee codes. Do not fabricate unpublished personal phone numbers or emails."
    },
    QueryIntent.UMS_SERVICE_NAV: {
        "candidate_types": ["ums_service", "action_workflow"],
        "category_slugs": ["ums-services", "ums-and-lms"],
        "guardrail": "Provide exact menu breadcrumbs observed from official screenshots with official login handoff link."
    },
    QueryIntent.GENERAL_CAMPUS_LIFE: {
        "candidate_types": ["faq", "student_club", "event_activity", "policy"],
        "category_slugs": ["general", "campus-life"],
        "guardrail": "Provide general institutional assistance grounded in official university records."
    }
}


class IntentClassifier:
    """Classifies user messages into one of the 12 standardized query intents."""

    PATTERNS: List[Tuple[QueryIntent, List[str]]] = [
        (
            QueryIntent.HEALTH_EMERGENCY,
            [r"\bemergency\b", r"\bambulance\b", r"\bunihospital\b", r"\bhospital\b", r"\bdoctor\b", r"\bclinic\b", r"\bmedic(?:al|ine)\b", r"\bfirst aid\b", r"\bchest pain\b"]
        ),
        (
            QueryIntent.GRIEVANCE_RMS,
            [r"\brms\b", r"\bgrievance\b", r"\bcomplaint\b", r"\bharassment\b", r"\bragging\b", r"\bescalat(?:e|ion)\b", r"\bticket status\b"]
        ),
        (
            QueryIntent.FACULTY_DIRECTORY,
            [r"\bfaculty\b", r"\bprofessor\b", r"\bdr\.\s+[a-z]+", r"\bprof\.\s+[a-z]+", r"\bdean\b", r"\bhoc\b", r"\bhod\b", r"\bteacher\b", r"\bwho is (?:dr|prof|mr|ms)\b"]
        ),
        (
            QueryIntent.FEES_SCHOLARSHIP,
            [r"\bfee\b", r"\btuition\b", r"\bscholarship\b", r"\blpunest cut-?off\b", r"\bconcession\b", r"\binstallment\b", r"\brefund\b", r"\bchallan\b"]
        ),
        (
            QueryIntent.EXAMINATION_SCHEDULE,
            [r"\bexam(?:ination)?\b", r"\bdatesheet\b", r"\bdate sheet\b", r"\btime ?table\b", r"\bre-?appear\b", r"\bbacklog\b", r"\badmit card\b", r"\bmakeup exam\b"]
        ),
        (
            QueryIntent.HOSTEL_HOUSING,
            [r"\bhostel\b", r"\bmess\b", r"\bcurfew\b", r"\broom\b", r"\baccommodation\b", r"\boutpass\b", r"\bleave pass\b", r"\bwarden\b", r"\blaundry\b"]
        ),
        (
            QueryIntent.TRANSPORT_MOBILITY,
            [r"\bbus\b", r"\btransport\b", r"\bshuttle\b", r"\bparking\b", r"\broute\b", r"\bpick-?up\b", r"\bday scholar\b"]
        ),
        (
            QueryIntent.PLACEMENT_CAREER,
            [r"\bplacement\b", r"\bjob\b", r"\bpackage\b", r"\bsalary\b", r"\bdream company\b", r"\brecruit(?:ment|er)?\b", r"\binternship\b"]
        ),
        (
            QueryIntent.CAMPUS_FACILITY_NAV,
            [r"\bwhere is\b", r"\blocation of\b", r"\bblock \d+\b", r"\blibrary\b", r"\bunimall\b", r"\bgym\b", r"\bstadium\b", r"\bswimming pool\b", r"\bopac\b"]
        ),
        (
            QueryIntent.ACADEMIC_REGULATION,
            [r"\battendance\b", r"\b75%\b", r"\bcondonation\b", r"\bduty leave\b", r"\bdl\b", r"\bcgpa\b", r"\bgrading\b", r"\bcredits?\b", r"\bmoocs?\b", r"\bnptel\b", r"\bedu revolution\b"]
        ),
        (
            QueryIntent.UMS_SERVICE_NAV,
            [r"\bums\b", r"\bnavigation path\b", r"\bwhere on ums\b", r"\bportal menu\b", r"\bhow to find .* on ums\b", r"\blms\b"]
        ),
    ]

    @classmethod
    def classify(cls, query: str) -> Tuple[QueryIntent, float, Dict[str, Any]]:
        """
        Classifies query into QueryIntent with confidence score (0.0 to 1.0)
        and associated metadata (candidate types, guardrails).
        """
        q_lower = query.lower().strip()

        for intent, patterns in cls.PATTERNS:
            for pat in patterns:
                if re.search(pat, q_lower):
                    meta = INTENT_METADATA.get(intent, {})
                    return intent, 0.95, meta

        # Default fallback
        meta = INTENT_METADATA.get(QueryIntent.GENERAL_CAMPUS_LIFE, {})
        return QueryIntent.GENERAL_CAMPUS_LIFE, 0.60, meta

