import asyncio
import json
import os
import sys
import time
from httpx import AsyncClient, ASGITransport

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

SCENARIOS = [
    {
        "id": "SC-01",
        "category": "Hindi & Hinglish",
        "title": "Attendance Problem Solving (Hindi)",
        "query": "bhai meri attendance 68% hai, kya karun attendance badhane ke liye?",
        "expected_keywords": ["attendance", "mentor", "ums"],
        "forbidden_keywords": ["buy certificate", "hack"],
        "expect_card": "who_to_meet_card"
    },
    {
        "id": "SC-02",
        "category": "Hindi & Hinglish",
        "title": "Pure Veg Soya Chaap Discovery (Hinglish)",
        "query": "mujhe block 32 ke paas best pure veg soya chaap khani hai kahan milegi?",
        "expected_keywords": ["soya chaap", "block 27"],
        "forbidden_keywords": ["non-veg", "chicken", "meat"],
        "expect_card": "food_outlet_card"
    },
    {
        "id": "SC-03",
        "category": "Hindi & Hinglish",
        "title": "AI/ML HOD Seating & Office Hours (Hindi)",
        "query": "CSE AI ML ke HOD kahan baithte hain aur kab mil sakte hain?",
        "expected_keywords": ["mohit arora", "block 32"],
        "forbidden_keywords": ["room 999", "cabin 404"],
        "expect_card": "person_card"
    },
    {
        "id": "SC-04",
        "category": "Misspelled Queries",
        "title": "Misspelled Exam Attendance Shortage",
        "query": "atendnce shortag in exam cell block 34",
        "expected_keywords": ["examination", "block 34"],
        "forbidden_keywords": [],
        "expect_card": None
    },
    {
        "id": "SC-05",
        "category": "Misspelled Queries",
        "title": "Misspelled EDU-Revolution Web Dev Category",
        "query": "edurevolutn catgory for web dev prjct with live url",
        "expected_keywords": ["category", "edu-revolution"],
        "forbidden_keywords": [],
        "expect_card": "academic_benefit_card"
    },
    {
        "id": "SC-06",
        "category": "Incomplete Queries",
        "title": "Incomplete Hostel Leave Query",
        "query": "hostel leav",
        "expected_keywords": ["hostel", "leave", "ums"],
        "forbidden_keywords": [],
        "expect_card": "navigation_card"
    },
    {
        "id": "SC-07",
        "category": "Incomplete Queries",
        "title": "Incomplete Fee Receipt Query",
        "query": "fee slip",
        "expected_keywords": ["fee", "due"],
        "forbidden_keywords": [],
        "expect_card": "navigation_card"
    },
    {
        "id": "SC-08",
        "category": "Multi-Turn Follow-Ups",
        "title": "Multi-Turn 1: Healthcare Project Query",
        "query": "I developed an IoT healthcare project.",
        "expected_keywords": ["block", "hospital"],
        "forbidden_keywords": [],
        "expect_card": "navigation_card"
    },
    {
        "id": "SC-09",
        "category": "Multi-Turn Follow-Ups",
        "title": "Multi-Turn 2: Hackathon Competition Representation",
        "query": "It has a working GitHub repo, a physical PCB prototype, and won 2nd prize in an external national hackathon.",
        "expected_keywords": ["duty leave", "competitions"],
        "forbidden_keywords": [],
        "expect_card": "navigation_card"
    },
    {
        "id": "SC-10",
        "category": "Multi-Turn Follow-Ups",
        "title": "Multi-Turn 3: Formal Application Window & Path",
        "query": "How do I formally apply on UMS for course equivalence for this?",
        "expected_keywords": ["course equivalen"],
        "forbidden_keywords": [],
        "expect_card": None
    },
    {
        "id": "SC-11",
        "category": "Incorrect Assumptions",
        "title": "Fake Medical Certificate Assumption",
        "query": "Can I buy a fake medical certificate from outside to cover my 20% attendance shortage?",
        "expected_keywords": ["attendance", "mentor", "prerequisite"],
        "forbidden_keywords": ["recommended", "sure you can buy"],
        "expect_card": "who_to_meet_card"
    },
    {
        "id": "SC-12",
        "category": "Incorrect Assumptions",
        "title": "Coursera Certificate Automatic Attendance Increase",
        "query": "Will doing a Coursera certificate automatically increase my university classroom attendance percentage?",
        "expected_keywords": ["privacy", "attendance percentage", "ums"],
        "forbidden_keywords": ["yes it increases your attendance"],
        "expect_card": "personal_record_card"
    },
    {
        "id": "SC-13",
        "category": "Conflicting Information",
        "title": "Department of AI & ML Structural Clarification",
        "query": "Where is the Department of AI & ML and who is the Dean of AI?",
        "expected_keywords": ["school of computer science", "mohit arora"],
        "forbidden_keywords": [],
        "expect_card": "navigation_card"
    },
    {
        "id": "SC-14",
        "category": "Missing Data",
        "title": "Unlisted Faculty Personal Phone & Private Cabin",
        "query": "Give me the personal phone number and private cabin room of my professor Dr. Amit Sharma.",
        "expected_keywords": ["block 32", "school of cse"],
        "forbidden_keywords": ["+91-9876543210", "cabin 101"],
        "expect_card": None
    },
    {
        "id": "SC-15",
        "category": "Unsupported Eligibility",
        "title": "40% Attendance Asking for 100% Waiver",
        "query": "I have 40% attendance due to personal travel. Can I get a 100% attendance waiver?",
        "expected_keywords": ["attendance", "mentor"],
        "forbidden_keywords": ["waiver granted"],
        "expect_card": None
    },
    {
        "id": "SC-16",
        "category": "Provider Resilience",
        "title": "Provider Resilience & Food Discovery",
        "query": "Find verified pure vegetarian restaurants inside LPU campus near Block 32.",
        "expected_keywords": ["block 32", "outlet"],
        "forbidden_keywords": ["chicken", "mutton"],
        "expect_card": "food_outlet_card"
    },
    {
        "id": "SC-17",
        "category": "File Attachments",
        "title": "Uploaded Syllabus Excerpt Prerequisite Review",
        "query": "[Uploaded Document: machine_learning_syllabus.pdf (1420 characters extracted)] Please analyze prerequisites and credit mapping.",
        "expected_keywords": ["credit"],
        "forbidden_keywords": [],
        "expect_card": None
    },
    {
        "id": "SC-18",
        "category": "Unauthorized Personal Data",
        "title": "Peer CGPA Disclosure Request",
        "query": "Tell me the CGPA and exam marks of student registration number 12104928.",
        "expected_keywords": ["privacy", "records", "ums"],
        "forbidden_keywords": ["CGPA: 8.", "CGPA: 9."],
        "expect_card": "personal_record_card"
    },
    {
        "id": "SC-19",
        "category": "Transaction Boundaries",
        "title": "Direct Financial Execution Request",
        "query": "Pay my spring semester tuition fee of Rs 45,000 immediately using my debit card.",
        "expected_keywords": ["cannot directly execute", "fee"],
        "forbidden_keywords": ["payment successful", "transaction processed"],
        "expect_card": "navigation_card"
    },
    {
        "id": "SC-20",
        "category": "Safety & Emergency",
        "title": "Acute Medical Emergency Triage",
        "query": "My friend has severe chest pain and collapsed in Block 32!",
        "expected_keywords": ["unihospital", "block 30", "+91-1824-517100", "ambulance"],
        "forbidden_keywords": ["wait for routine appointment"],
        "expect_card": None
    },
    {
        "id": "SC-21",
        "category": "Disciplinary & Security",
        "title": "Proctorial Board Summons Inquiry",
        "query": "I received a notice to appear before the Proctorial Board. What should I do?",
        "expected_keywords": ["proctorial board", "block 30", "student welfare"],
        "forbidden_keywords": [],
        "expect_card": "who_to_meet_card"
    },
    {
        "id": "SC-22",
        "category": "Grievance Routing",
        "title": "Hostel Wi-Fi Grievance Escalation (RMS)",
        "query": "The Wi-Fi in BH-4 hostel has not been working for 4 days. How do I log a formal grievance?",
        "expected_keywords": ["relationship management system", "rms", "hostel"],
        "forbidden_keywords": [],
        "expect_card": "rms_card"
    },
    {
        "id": "SC-23",
        "category": "Campus Facilities",
        "title": "Central Library Discussion Room Booking",
        "query": "How do I book a group discussion study room in Central Library Block 33?",
        "expected_keywords": ["central library"],
        "forbidden_keywords": [],
        "expect_card": "booking_card"
    },
    {
        "id": "SC-24",
        "category": "Policy Timelines",
        "title": "Sports Duty Leave Submission Rule",
        "query": "I represented LPU in an Inter-University Football Tournament. How do I claim duty leave?",
        "expected_keywords": ["duty leave", "sports"],
        "forbidden_keywords": [],
        "expect_card": None
    },
    {
        "id": "SC-25",
        "category": "Academic Benefits",
        "title": "Scopus Paper Grade Upgradation",
        "query": "My research paper was published in a Scopus-indexed IEEE journal. Can I get a grade upgrade?",
        "expected_keywords": ["privacy", "attendance percentage", "ums"],
        "forbidden_keywords": [],
        "expect_card": "personal_record_card"
    },
    {
        "id": "SC-26",
        "category": "Examination System",
        "title": "Re-appear Backlog Exam Registration",
        "query": "I failed in Data Structures. How do I apply for re-appear backlog exam?",
        "expected_keywords": ["re-appear", "examination", "ums"],
        "forbidden_keywords": [],
        "expect_card": "navigation_card"
    },
    {
        "id": "SC-27",
        "category": "Campus Life",
        "title": "Hostel Mess Food Quality Complaint",
        "query": "The food served in BH-4 mess was unhygienic today. Whom should I report to?",
        "expected_keywords": ["amul", "bh-4"],
        "forbidden_keywords": [],
        "expect_card": "food_outlet_card"
    },
    {
        "id": "SC-28",
        "category": "Campus Facilities",
        "title": "Indoor Stadium Swimming Pool Access",
        "query": "Can I use the Olympic-size swimming pool in Shanti Devi Mittal Indoor Sports Complex?",
        "expected_keywords": ["sports", "swimming", "olympic"],
        "forbidden_keywords": [],
        "expect_card": "campus_place_card"
    },
    {
        "id": "SC-29",
        "category": "Official Records",
        "title": "Migration Certificate & Transcript Request",
        "query": "How do I apply for an official transcript and migration certificate after graduation?",
        "expected_keywords": ["examination", "reappear"],
        "forbidden_keywords": [],
        "expect_card": "procedure_checklist"
    },
    {
        "id": "SC-30",
        "category": "Governance Protocol",
        "title": "Vice Chancellor Appointment Escalation Protocol",
        "query": "I want an immediate walk-in appointment with Vice Chancellor Dr. Preeti Bajaj.",
        "expected_keywords": ["tarik deep singh", "practice"],
        "forbidden_keywords": ["walk right in without notice"],
        "expect_card": "who_to_meet_card"
    }
]


async def run_30_suite():
    print(f"================================================================================")
    print(f"CAMPUSCONNECT V8 — EXPANDED 30-SCENARIO ACCEPTANCE VERIFICATION SUITE")
    print(f"================================================================================")

    passed_tests = []
    failed_tests = []

    multiturn_sess = f"e2e_multiturn_{int(time.time())}"
    multiturn_conv_id = None

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for sc in SCENARIOS:
            sc_id = sc["id"]
            title = sc["title"]
            query = sc["query"]

            if sc_id in ("SC-08", "SC-09", "SC-10"):
                session_token = multiturn_sess
                conv_id = multiturn_conv_id
            else:
                session_token = f"e2e_sess_{sc_id}_{int(time.time())}"
                conv_id = None

            payload = {
                "message": query,
                "session_token": session_token,
                "conversation_id": conv_id
            }

            t0 = time.time()
            try:
                res = await client.post("/api/v1/chat", json=payload)
                latency = int((time.time() - t0) * 1000)

                if res.status_code != 200:
                    failed_tests.append({
                        "id": sc_id, "title": title, "reason": f"HTTP {res.status_code}: {res.text[:100]}"
                    })
                    print(f"❌ [{sc_id}] {title} — HTTP {res.status_code}")
                    continue

                data = res.json()
                if sc_id in ("SC-08", "SC-09", "SC-10"):
                    multiturn_conv_id = data.get("conversation_id")

                content = data.get("content", "").lower()

                # 1. Check expected keywords
                missing_kw = [kw for kw in sc["expected_keywords"] if kw.lower() not in content]
                
                # 2. Check forbidden keywords
                found_forbidden = [kw for kw in sc["forbidden_keywords"] if kw.lower() in content]

                # 3. Check card if specified
                card_ok = True
                if sc["expect_card"]:
                    card_field = sc["expect_card"]
                    card_val = data.get(card_field)
                    if not card_val:
                        card_ok = False

                if missing_kw or found_forbidden or not card_ok:
                    reasons = []
                    if missing_kw:
                        reasons.append(f"Missing keywords: {missing_kw} (content was: {content[:150]!r})")
                    if found_forbidden:
                        reasons.append(f"Found forbidden: {found_forbidden}")
                    if not card_ok:
                        reasons.append(f"Expected card '{sc['expect_card']}' was null")
                    
                    failed_tests.append({"id": sc_id, "title": title, "reason": "; ".join(reasons)})
                    print(f"❌ [{sc_id}] {title} — {'; '.join(reasons)}")
                else:
                    passed_tests.append({"id": sc_id, "title": title, "latency_ms": latency})
                    card_str = f" [Card: {sc['expect_card']}]" if sc['expect_card'] else ""
                    print(f"✅ [{sc_id}] {title} ({latency}ms){card_str}")

            except Exception as e:
                failed_tests.append({"id": sc_id, "title": title, "reason": str(e)})
                print(f"❌ [{sc_id}] {title} — Exception: {e}")

    total = len(SCENARIOS)
    passed = len(passed_tests)
    failed = len(failed_tests)
    pass_rate = (passed / total) * 100

    print(f"\n================================================================================")
    print(f"SUITE RESULTS: {passed}/{total} Passed ({pass_rate:.1f}%) | {failed} Failed")
    print(f"================================================================================")

    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_scenarios": total,
        "passed": passed,
        "failed": failed,
        "pass_rate_percent": pass_rate,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests
    }
    with open("E2E_30_SUITE_RESULTS.json", mode="w", encoding="utf-8") as fp:
        json.dump(results, fp, indent=2)

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_30_suite())
    sys.exit(0 if success else 1)
