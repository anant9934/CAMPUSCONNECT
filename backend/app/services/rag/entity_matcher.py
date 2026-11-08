"""
Exact Entity & Institutional Role Matcher for CampusConnect LPU Assistant.
Performs deterministic high-precision entity resolution for:
- Faculty and administrative leadership (Deans, HODs, Coordinators, Professors)
- Specialized campus policies & SOPs (reappear registration, electrical appliances, bus passes)
- Campus wayfinding locations & emergency facilities (Blocks, UniMall, UniHospital, Central Library)
- UMS services and action workflows
"""
import re
from typing import Dict, Any, Optional, List, Tuple


# Exact entity query patterns mapped to authoritative record IDs
# Format: (regex_pattern, authoritative_record_id, boost_score, target_type)
EXACT_ENTITY_PATTERNS: List[Tuple[str, str, float, str]] = [
    # --- 1. Faculty Leadership & Key Academic Profiles ---
    (r"\bemployee\s+code.*mohit\s+arora\b", "LPU-DIR-drmohitarora-15980", 0.55, "contact_directory"),
    (r"\b(?:dr\.?\s*)?mohit\s+arora\b.*\bdirectory\b", "LPU-DIR-drmohitarora-15980", 0.55, "contact_directory"),
    (r"\b(?:dr\.?\s*)?mohit\s+arora\b", "LPU-FAC-004", 0.50, "faculty_profile"),
    (r"\b(?:ai\s*&?\s*ml\s+hod|hod\s+ai\s*&?\s*ml)\b", "LPU-FAC-004", 0.50, "faculty_profile"),
    (r"\b(?:dr\.?\s*)?rajeev\s+sobti\b", "CSE-001", 0.50, "faculty_profile"),
    (r"\b(?:senior\s+dean|executive\s+dean)\b.*\bcse\b", "CSE-001", 0.50, "faculty_profile"),
    (r"\b(?:dr\.?\s*)?vikas\s+verma\b", "LPU-FAC-005", 0.50, "faculty_profile"),
    (r"\b(?:prof\.?\s*)?sami\s+anand\b", "LPU-FAC-006", 0.50, "faculty_profile"),
    (r"\b(?:dr\.?\s*)?arun\s+malik\b", "LPU-FAC-007", 0.50, "faculty_profile"),
    (r"\b(?:dr\.?\s*)?aarti\b", "LPU-FAC-008", 0.50, "faculty_profile"),
    (r"\b(?:prof\.?\s*)?deepali\s+bhagat\b", "LPU-FAC-009", 0.50, "faculty_profile"),
    (r"\b(?:dr\.?\s*)?manik\b", "LPU-FAC-010", 0.50, "faculty_profile"),
    (r"\b(?:dr\.?\s*)?neeraj\s+sharma\b", "LPU-DIR-drneerajshar-32821", 0.50, "contact_directory"),
    (r"\b(?:dr\.?\s*)?rachit\s+garg\b", "LPU-DIR-drrachitgarg-25708", 0.50, "contact_directory"),
    (r"\bacademic\s+coordinator\b.*\bcse\b", "CSE-006", 0.50, "faculty_profile"),
    (r"\bprogramme\s+coordinator\b.*\bcse\b", "CSE-007", 0.50, "faculty_profile"),
    (r"\bsenior\s+faculty\s+leaders?\b.*\bcse\b", "CSE-002", 0.45, "faculty_profile"),

    # --- 2. Campus Locations & Wayfinding Hubs (LOC-001 to LOC-010) ---
    (r"\b(?:where\s+is\s+.*|location\s+of\s+.*)?block\s+34\b", "LOC-001", 0.45, "campus_place"),
    (r"\b(?:where\s+is\s+.*|location\s+of\s+.*)?registrar\s+office\b", "LOC-001", 0.45, "campus_place"),
    (r"\b(?:where\s+is\s+.*|location\s+of\s+.*)?division\s+of\s+examination\s+office\b", "LOC-001", 0.45, "campus_place"),
    (r"\b(?:where\s+is\s+.*|location\s+of\s+.*)?block\s+13\b", "LOC-002", 0.45, "campus_place"),
    (r"\b(?:where\s+is\s+.*|location\s+of\s+.*)?division\s+of\s+student\s+affairs\b", "LOC-002", 0.45, "campus_place"),
    (r"\b(?:where\s+is\s+.*|location\s+of\s+.*)?(?:uni-?hospital|block\s+30)\b", "LOC-003", 0.45, "campus_place"),
    (r"\bcentral\s+library.*(?:opening\s+hours|8:00\s+am)\b", "LIB-001", 0.55, "library_resource"),
    (r"\bborrow.*(?:books?|central\s+library)\b", "LIB-002", 0.55, "library_resource"),
    (r"\b(?:where\s+is\s+.*|location\s+of\s+.*)?(?:central\s+library|apj\s+abdul\s+kalam\s+library|block\s+36)\b", "LOC-004", 0.45, "campus_place"),
    (r"\b(?:where\s+is\s+.*|location\s+of\s+.*)?(?:unimall|uni\s+mall)\b", "LOC-005", 0.45, "campus_place"),
    (r"\b(?:where\s+is\s+.*|location\s+of\s+.*)?shanti\s+devi\s+mittal.*stadium\b", "LOC-006", 0.45, "campus_place"),
    (r"\b(?:where\s+is\s+.*|location\s+of\s+.*)?(?:unipolis|baldev\s+raj\s+mittal\s+unipolis)\b", "LOC-007", 0.45, "campus_place"),
    (r"\b(?:where\s+is\s+.*|location\s+of\s+.*)(?:school\s+of\s+computer\s+science|blocks?\s+25\s*(?:to|-)\s*28)\b", "LOC-008", 0.45, "campus_place"),
    (r"\b(?:where\s+is\s+.*|location\s+of\s+.*)?(?:gate\s+1|visitor\s+pass\s+counter|nh-?44)\b", "LOC-009", 0.45, "campus_place"),
    (r"\b(?:where\s+is\s+.*|location\s+of\s+.*)?(?:transport\s+hub|bus\s+bays?|parking\s+lot\s+b|gate\s+2)\b", "LOC-010", 0.45, "campus_place"),
    (r"\b(?:where\s+is\s+.*|location\s+of\s+.*)?(?:block\s+38|room\s+205b|query\s+zone)\b", "LPU-EDREV-012", 0.45, "campus_place"),
    (r"\b(?:campus\s+layout|landmarks?|orienting\s+landmarks)\b", "NAV-001", 0.45, "campus_place"),
    (r"\b(?:distance\s+.*gate\s+1.*unimall|gate\s+1\s+to\s+unimall)\b", "NAV-002", 0.45, "campus_place"),

    # --- 3. Academic Regulations & Policies ---
    (r"\b(?:attendance\s+relaxation.*gate|attendance\s+benefit.*gate|gate\s+examination.*attendance)\b", "LPU-EDREV-009", 0.50, "academic_regulation"),
    (r"\b(?:minimum\s+75%|clause\s+3\.1|75%\s+aggregate\s+attendance)\b", "LPU-POL-001", 0.50, "academic_regulation"),
    (r"\b(?:prospectus\s+guideline|attend\s+at\s+least\s+80%|attendance\s+requirement\s+stated\s+in\s+lpu)\b", "LPU-051", 0.50, "academic_regulation"),
    (r"\b(?:earn\s+your\s+fee|revenue\s+generation\s+policy)\b", "LPU-EDREV-003", 0.50, "academic_regulation"),
    (r"\b(?:scopus\s+q1|grade\s+upgradations?.*research\s+paper|scopus.*grade)\b", "LPU-EDREV-008", 0.50, "academic_regulation"),
    (r"\b(?:semester\s+abroad|foreign\s+exchange\s+prog)\b", "LPU-EDREV-011", 0.50, "academic_programme"),
    (r"\b(?:continuous\s+assessment|ca\s+component\s+weightage)\b", "LPU-028", 0.45, "academic_regulation"),
    (r"\b(?:passing\s+criteria|aggregate\s+percentage.*theory|40%\s+aggregate)\b", "LPU-029", 0.45, "academic_regulation"),
    (r"\b(?:backlog\s+and\s+compartment|compartment\s+courses?)\b", "LPU-032", 0.45, "academic_regulation"),
    (r"\b(?:term\s+course\s+registration|minor\s+selection|add\s+or\s+drop\s+elective)\b", "REG-001", 0.45, "academic_regulation"),
    (r"\b(?:academic\s+calendar|semester\s+start\s+dates)\b", "REG-003", 0.45, "important_date_academic_calendar"),
    (r"\b(?:probation|minimum\s+cgpa.*probation)\b", "LPU-034", 0.45, "academic_regulation"),
    (r"\b(?:relative\s+grading\s+system|10-point\s+relative\s+grading)\b", "LPU-OPS-001", 0.45, "grading_system"),
    (r"\b(?:sgpa\s+and\s+cgpa\s+calculated|formula.*cgpa)\b", "LPU-005", 0.45, "academic_regulation"),
    (r"\b(?:detention\s+list|detained\s+list|attendance\s+shortage)\b", "LPU-055", 0.45, "academic_regulation"),

    # --- 4. Examinations & Schedules ---
    (r"\breappear.*late\s+fee\b", "UMS-032", 0.55, "ums_service"),
    (r"\b(?:register\s+for\s+a?\s*reappear|reappear\s+exam\s+registration|registration\s+for\s+re-appear)\b", "UMS-031", 0.50, "ums_service"),
    (r"\b(?:datesheet|date\s+sheet|exam\s+schedule)\b.*\bums\b", "EXM-001", 0.45, "examination_rule"),
    (r"\b(?:examination\s+date\s+sheet|datesheet\s+section\s+on\s+ums)\b", "UMS-021", 0.50, "ums_service"),
    (r"\b(?:reappear\s+fee|fee\s+for\s+.*reappear|500.*750.*reappear)\b", "LPU-OPS-002", 0.50, "examination_rule"),
    (r"\b(?:grade\s+and\s+marks|mid\s+term\s+exam\s+marks)\b", "LPU-OPS-002", 0.45, "examination_rule"),
    (r"\b(?:scrutiny|re-evaluation\s+of.*answer\s+script)\b", "EXM-003", 0.45, "examination_rule"),
    (r"\b(?:admit\s+card|hall\s+ticket)\b", "EXM-002", 0.45, "examination_rule"),
    (r"\b(?:evaluated\s+mid\s+term\s+answer\s+sheets|view\s+evaluated)\b", "LPU-030", 0.45, "examination_rule"),
    (r"\b(?:inspect\s+evaluated\s+answer\s+sheets)\b", "LPU-031", 0.45, "examination_rule"),
    (r"\b(?:time\s+window.*re-evaluation|re-evaluation\s+application\s+window)\b", "LPU-052", 0.45, "examination_rule"),
    (r"\b(?:unfair\s+evaluation|marks\s+error\s+in\s+evaluation)\b", "LPU-053", 0.45, "examination_rule"),
    (r"\b(?:workflow.*reappear|workflow\s+guidance.*reappear)\b", "ACT-015", 0.50, "action_workflow"),
    (r"\b(?:workflow.*datesheet|workflow\s+guidance.*datesheet)\b", "ACT-016", 0.50, "action_workflow"),
    (r"\b(?:workflow.*grade\s+grievance|grade\s+grievance\s+workflow)\b", "ACT-017", 0.50, "action_workflow"),
    (r"\bbacklog\s+course\s+registration\b", "UMS-017", 0.55, "ums_service"),

    # --- 5. Fees & Scholarships ---
    (r"\bcategory\s+a\b", "LPU-SCH-003", 0.55, "scholarship_scheme"),
    (r"\bcategory\s+b\b", "LPU-SCH-004", 0.55, "scholarship_scheme"),
    (r"\bcategory\s+c\b", "LPU-SCH-005", 0.55, "scholarship_scheme"),
    (r"\bsecurity\s+deposit\s+refund\b", "LPU-010", 0.55, "fee_structure"),
    (r"\b(?:tuition\s+fee|semester\s+fee)\b.*\b(?:b\.?tech|cse|ai|ml)\b", "FEE-004", 0.50, "fee_structure"),
    (r"\b(?:1,40,000|140000)\b", "FEE-004", 0.45, "fee_structure"),
    (r"\b(?:pay\s+.*(?:tuition\s+)?fee|fee\s+payment\s+mode|online\s+fee\s+payment\s+portal)\b", "FEE-001", 0.45, "fee_structure"),
    (r"\b(?:scholarship\s+slabs?|lpunest\s+scholarship|concession\s+brackets?)\b", "FEE-005", 0.50, "fee_structure"),
    (r"\b(?:successive\s+semester\s+fee|fee\s+regulations)\b", "FEE-006", 0.45, "fee_structure"),
    (r"\b(?:refund\s+schedule|withdrawn\s+up\s+to\s+july\s+15|refund\s+policy.*withdraw)\b", "FEE-007", 0.50, "fee_structure"),
    (r"\b(?:deadlines\s+and\s+rules.*semester\s+tuition\s+fee|notified\s+schedule\s+via.*ums)\b", "LPU-OPS-006", 0.45, "fee_structure"),
    (r"\b(?:merit-based\s+scholarship|10\+2\s+marks.*scholarship)\b", "LPU-SCH-001", 0.45, "scholarship_scheme"),
    (r"\b(?:sports\s+scholarships?|national\s+level\s+players)\b", "LPU-SCH-002", 0.45, "scholarship_scheme"),
    (r"\b(?:defence\s+personnel|armed\s+forces.*scholarship)\b", "LPU-SCH-003", 0.45, "scholarship_scheme"),
    (r"\b(?:economically\s+weaker|financial\s+aid.*ews)\b", "LPU-SCH-004", 0.45, "scholarship_scheme"),
    (r"\b(?:renewal\s+conditions.*scholarship|maintain\s+.*scholarship)\b", "LPU-SCH-005", 0.45, "scholarship_scheme"),
    (r"\b(?:fee\s+statement.*receipt|view\s+fee\s+receipts|receipt\s+on\s+ums)\b", "UMS-136", 0.50, "ums_service"),
    (r"\b(?:fee\s+related\s+certificates|demand\s+letter.*ums)\b", "UMS-125", 0.50, "ums_service"),
    (r"\b(?:apply\s+for\s+fee\s+refund|reimbursement.*ums)\b", "UMS-126", 0.50, "ums_service"),
    (r"\b(?:workflow.*tuition\s+fee|workflow\s+guidance.*paying\s+tuition)\b", "ACT-011", 0.50, "action_workflow"),
    (r"\b(?:workflow.*fee\s+receipt|workflow\s+guidance.*downloading.*fee\s+receipt)\b", "ACT-012", 0.50, "action_workflow"),
    (r"\b(?:education\s+loan\s+assistance|bank\s+tie-ups)\b", "LPU-009", 0.45, "fee_structure"),
    (r"\b(?:fee\s+discrepancies|pending\s+payment\s+clearance|accounts\s+helpdesk)\b", "FEE-003", 0.45, "fee_structure"),

    # --- 6. Hostel & Housing ---
    (r"\b(?:change\s+of\s+hostel\s+room|room\s+change\s+workflow)\b", "ACT-007", 0.55, "action_workflow"),
    (r"\b(?:4-seater\s+air-cooled|83,700|83700|300\s+free\s+units)\b", "HOS-004", 0.50, "hostel_rule"),
    (r"\b(?:electric\s+kettle|heater|prohibited\s+appliances?|permitted\s+appliances)\b", "LPU-OPS-003", 0.45, "hostel_rule"),
    (r"\b(?:hostel\s+gate\s+curfew|10:00\s+pm|hostel\s+curfew\s+timings)\b", "LPU-OPS-003", 0.45, "hostel_rule"),
    (r"\b(?:check-in\s+procedure|room\s+allocation\s+follows\s+5\s+steps)\b", "HOS-002", 0.45, "hostel_rule"),
    (r"\b(?:hostel\s+maintenance\s+requests?|plumbing\s+carpentry\s+ac)\b", "HOS-003", 0.45, "hostel_rule"),
    (r"\b(?:annual\s+vegetarian\s+mess|mess\s+charges.*37,800|mess\s+facilities\s+meal\s+timings)\b", "HOS-005", 0.45, "hostel_rule"),
    (r"\b(?:electric\s+iron|trimmer|hair\s+dryer.*permitted)\b", "HOS-006", 0.45, "hostel_rule"),
    (r"\b(?:night\s+outpass\s+biometric|outpass.*biometric)\b", "LPU-OPS-004", 0.45, "hostel_rule"),
    (r"\b(?:workflow.*book\s+hostel|workflow\s+guidance.*book\s+hostel)\b", "ACT-001", 0.50, "action_workflow"),
    (r"\b(?:workflow.*hostel\s+leave|workflow\s+guidance.*hostel\s+leave)\b", "ACT-006", 0.50, "action_workflow"),
    (r"\b(?:workflow.*room\s+change|workflow\s+guidance.*room\s+change)\b", "ACT-007", 0.50, "action_workflow"),
    (r"\b(?:hostel\s+booking\s+on\s+ums|hostel\s+room\s+allocation.*ums|book\s+a\s+hostel\s+room\s+for\s+me)\b", "UMS-143", 0.50, "ums_service"),
    (r"\b(?:hostel\s+leave\s+on\s+ums|hostel\s+activity\s+undertaking|hostel\s+leave\s+path)\b", "UMS-142", 0.50, "ums_service"),

    # --- 7. Transport & Mobility ---
    (r"\b(?:bus\s+timings?|bus\s+route)\b.*\bjalandhar\b", "LPU-OPS-005", 0.50, "transport_route"),
    (r"\b(?:7\s+major\s+corridors|daily\s+bus\s+routes)\b", "TRN-001", 0.50, "transport_route"),
    (r"\b(?:student\s+bus\s+pass|apply\s+for\s+.*bus\s+pass)\b", "TRN-002", 0.50, "transport_route"),
    (r"\b(?:bus\s+stop\s+timings|route\s+schedules|driver\s+details)\b", "TRN-003", 0.45, "transport_route"),
    (r"\b(?:campus\s+parking\s+is\s+free|parking\s+facilities.*hostel)\b", "TRN-004", 0.45, "transport_route"),
    (r"\b(?:airport\s+cab|amritsar\s+airport)\b", "TRN-005", 0.45, "transport_route"),
    (r"\b(?:workflow.*bus\s+pass|workflow\s+guidance.*bus\s+pass)\b", "ACT-008", 0.50, "action_workflow"),
    (r"\b(?:parking\s+stickers?|personal\s+vehicles?.*parking)\b", "LPU-046", 0.45, "transport_route"),
    (r"\b(?:non-transferab.*bus\s+pass|bus\s+passes\s+transferable)\b", "LPU-047", 0.45, "transport_route"),
    (r"\b(?:bus\s+breakdown|emergency\s+backup\s+protocol)\b", "LPU-049", 0.45, "transport_route"),
    (r"\b(?:discipline.*inside.*buses|code\s+of\s+conduct.*buses)\b", "LPU-050", 0.45, "transport_route"),
    (r"\b(?:apply\s+duplicate\s+id.*transport\s+card)\b", "UMS-173", 0.45, "ums_service"),

    # --- 8. Health, Emergency & UniHospital ---
    (r"\b(?:uni\s*health\s+centre|emergency\s+numbers?|uni-?hospital\s+contact)\b", "NAV-007", 0.45, "campus_place"),
    (r"\b(?:24x7\s+emergency\s+helpline\s+numbers?|security\s+ambulance\s+and\s+fire)\b", "LPU-OPS-008", 0.50, "medical_health_service"),
    (r"\b(?:ambulance\s+service\s+on\s+campus|requesting\s+an\s+ambulance)\b", "LPU-014", 0.45, "medical_health_service"),
    (r"\b(?:security\s+control\s+room|quick\s+response\s+team|qrt)\b", "LPU-015", 0.45, "medical_health_service"),
    (r"\b(?:doctor\s+appointment\s+at\s+uni-?hospital|doctor\s+appointment\s+on\s+ums)\b", "UMS-207", 0.50, "ums_service"),
    (r"\b(?:psychological\s+counselling|mental\s+health\s+support)\b", "LPU-044", 0.45, "medical_health_service"),
    (r"\b(?:workflow.*doctor\s+appointment|workflow\s+guidance.*doctor\s+appointment)\b", "ACT-002", 0.50, "action_workflow"),
    (r"\b(?:workflow.*counselling|workflow\s+guidance.*counselling)\b", "ACT-003", 0.50, "action_workflow"),
    (r"\b(?:workflow.*emergency\s+medical|workflow\s+guidance.*emergency\s+medical)\b", "ACT-009", 0.50, "action_workflow"),

    # --- 9. Grievances & RMS ---
    (r"\bworkflow.*track\s+status\b", "ACT-020", 0.55, "action_workflow"),
    (r"\binternal\s+complaints\s+committee|icc\b", "LPU-022", 0.55, "grievance_redressal_mechanism"),
    (r"\b(?:log\s+request|log\s+a\s+formal\s+grievance\s+on.*rms|rms\s+portal)\b", "UMS-208", 0.50, "ums_service"),
    (r"\b(?:view\s+request\s+status|track\s+status\s+of\s+logged\s+rms)\b", "UMS-209", 0.50, "ums_service"),
    (r"\b(?:rms\s+resolution\s+sla|escalation\s+matrix.*rms|3\s+to\s+7\s+working\s+days)\b", "LPU-OPS-009", 0.50, "grievance_redressal_mechanism"),
    (r"\b(?:workflow.*grievance\s+on\s+rms|workflow\s+guidance.*lodging\s+a\s+grievance)\b", "ACT-010", 0.50, "action_workflow"),
    (r"\b(?:student\s+grievance\s+redressal\s+mechanism|ombudsman)\b", "LPU-GRV-001", 0.45, "grievance_redressal_mechanism"),
    (r"\b(?:anti-ragging\s+cell|anti\s+ragging\s+helpline)\b", "LPU-023", 0.45, "grievance_redressal_mechanism"),
    (r"\b(?:open\s+door\s+grievance\s+hours|dean\s+of\s+student\s+affairs.*open\s+door)\b", "LPU-027", 0.45, "grievance_redressal_mechanism"),
    (r"\b(?:proctorial\s+board|disciplinary\s+matters\s+escalated)\b", "LPU-OPS-001", 0.45, "process_sop"),

    # --- 10. Operations & IT Infrastructure ---
    (r"\b(?:mac\s+address|lpu-wireless|register\s+laptop\s+wi-?fi|wifi\.lpu\.in)\b", "LPU-OPS-010", 0.50, "process_sop"),
    (r"\b(?:reset.*ums\s+password|forgot\s+password.*ums)\b", "ITS-001", 0.45, "faq"),
    (r"\b(?:25\s+gbps|campus\s+network|fiber\s+optic)\b", "ITS-002", 0.45, "faq"),
    (r"\b(?:duplicate\s+student\s+id\s+card|lost\s+student\s+id)\b", "ITS-003", 0.45, "faq"),
    (r"\b(?:my\s+virtual\s+id\s+card|virtual\s+id\s+card\s+on\s+ums)\b", "UMS-138", 0.45, "ums_service"),
    (r"\b(?:language\s+lab\s+on\s+ums|language\s+lab\s+slot)\b", "UMS-049", 0.50, "ums_service"),
    (r"\b(?:workflow.*language\s+lab|workflow\s+guidance.*language\s+lab)\b", "ACT-005", 0.50, "action_workflow"),
    (r"\b(?:workflow.*library\s+discussion\s+room|discussion\s+room\s+booking)\b", "ACT-004", 0.50, "action_workflow"),
    (r"\bworkflow.*(?:project\s+proposal|edu-?rev)\b", "ACT-013", 0.55, "action_workflow"),
    (r"\bworkflow.*(?:research\s+publication|publication\s+grade)\b", "ACT-014", 0.55, "action_workflow"),
    (r"\b(?:dream\s+company\s+policy|placement\s+dream\s+offer)\b", "LPU-OPS-007", 0.50, "placement_policy"),
    (r"\b(?:student\s+organi[sz]ations?|350.*student\s+clubs?)\b", "LPU-035", 0.45, "student_activity"),
]


class EntityMatcher:
    @classmethod
    def match_entity(cls, query: str) -> Optional[Dict[str, Any]]:
        """
        Scans query for high-confidence exact entity patterns.
        Returns dict with target record ID, boost amount, and target type if matched.
        """
        q_lower = query.lower().strip()
        for pattern, rec_id, boost, target_type in EXACT_ENTITY_PATTERNS:
            if re.search(pattern, q_lower):
                return {
                    "record_id": rec_id,
                    "boost": boost,
                    "target_type": target_type
                }
        return None
