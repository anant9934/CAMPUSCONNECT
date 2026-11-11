from typing import Dict, Any, List

# Declarative metadata for tools available to the conversation orchestrator
CAMPUSCONNECT_TOOLS: List[Dict[str, Any]] = [
    {
        "name": "search_campus_food",
        "description": "Searches for verified pure vegetarian food outlets, cuisines, menu items, prices, and operating hours inside Lovely Professional University (LPU).",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Food item or outlet name (e.g. 'soya chaap', 'punjabi tadka', 'thali')"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_people_directory",
        "description": "Looks up verified Lovely Professional University leadership, school deans, HODs, faculty members, and research mentors. Does NOT invent private room numbers.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Name, role, or expertise (e.g. 'Dr. Mohit Arora', 'AI ML HOD', 'cybersecurity mentor')"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "assess_academic_benefits",
        "description": "Evaluates a student's technical project, hackathon win, research paper, or startup under the official LPU EDU-Revolution framework. Returns eligible academic benefits, evidence checklist, and submission timeline.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Student's project description, achievement, or credential"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "resolve_student_issue",
        "description": "Routes campus problems (attendance discrepancies, fee issues, hostel maintenance, medical emergencies) to the responsible first contact office and 3-tier escalation ladder.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Description of the student grievance, discrepancy, or inquiry"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_campus_places",
        "description": "Finds verified academic blocks, administrative offices, auditoriums, libraries, and hospitals inside LPU campus with exact coordinates.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Campus place or building block name (e.g. 'Block 32', 'Uni-Mall', 'Block 14')"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "lookup_ums_service",
        "description": "Searches all 234 official LPU University Management System (UMS) services and navigation action workflows. Returns exact breadcrumbs and authentic handoff links.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "UMS feature name or student goal (e.g. 'datesheet', 'fee receipt', 'hostel leave')"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_institutional_knowledge",
        "description": "Executes hybrid BM25 and semantic RAG over official LPU policies, examination rules, academic calendars, fee guidelines, and scholarship regulations.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Detailed institutional policy question"}
            },
            "required": ["query"]
        }
    }
]
