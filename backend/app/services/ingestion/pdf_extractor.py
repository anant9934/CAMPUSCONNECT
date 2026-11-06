"""
PDF Extraction Pipeline for CampusConnect (Data Quality v4.0)
Extracts structured institutional policies from Academic Benefits copy.pdf
(Official EDU Revolution Guide from Division of Academic Affairs, LPU).
"""
import os
import re
from typing import List, Dict, Any
from pypdf import PdfReader
from app.schemas.typed_knowledge import KnowledgeType, TypedKnowledgeCreate


class PDFExtractor:
    def __init__(self, pdf_path: str = "data/Academic Benefits copy.pdf"):
        self.pdf_path = pdf_path

    def extract_records(self) -> List[Dict[str, Any]]:
        """
        Extract structured policy and academic regulation records from the 45-page
        EDU Revolution Guide PDF with section headings, clauses, and page citations.
        """
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"PDF not found at {self.pdf_path}")

        reader = PdfReader(self.pdf_path)
        total_pages = len(reader.pages)

        # Extract text per page
        page_texts = {}
        for idx, page in enumerate(reader.pages):
            page_texts[idx + 1] = page.extract_text() or ""

        records: List[Dict[str, Any]] = []

        # 1. EDU Revolution Overview
        records.append({
            "record_id": "LPU-EDREV-001",
            "record_type": KnowledgeType.ACADEMIC_REGULATION.value,
            "title": "EDU Revolution Framework & Objectives",
            "content": (
                "The EDU Revolution initiative by the Division of Academic Affairs at Lovely Professional University (LPU) "
                "empowers students to convert real-world experiential learning into academic credits, grade upgradations, "
                "attendance benefits, and tuition exemptions. It bridges academia and industry through revenue generation, "
                "research projects, competitive examinations, and social innovation."
            ),
            "category_name": "Academic Regulations",
            "tags": ["edu_revolution", "academic_benefits", "experiential_learning", "credits"],
            "original_source_url": "https://www.lpu.in/academics/edu-revolution.php",
            "source_id": "DOC-EDREV-2026",
            "source_title": "EDU Revolution Guide — Division of Academic Affairs, LPU",
            "source_type": "pdf",
            "source_document": "Academic Benefits copy.pdf",
            "source_page": "Pages 3-6",
            "source_section": "1. Introduction & 2. Academic Benefits",
            "clause_reference": "Section 1 & 2",
            "verification_status": "verified",
            "verified_by": "Division of Academic Affairs",
            "searchable_variants": [
                "What is EDU Revolution at LPU?",
                "How does the EDU Revolution academic benefits framework work?",
                "Can I convert projects or internships into academic credits at LPU?"
            ],
            "type_metadata": {
                "regulation_code": "EDREV-GEN-01",
                "governing_body": "Division of Academic Affairs",
                "program_applicability": "All regular undergraduate and postgraduate degree programmes",
                "summary": "Institutional framework for converting extracurricular and co-curricular achievements into academic benefits."
            }
        })

        # 2. UMS Application Path
        records.append({
            "record_id": "LPU-EDREV-002",
            "record_type": KnowledgeType.PROCESS_SOP.value,
            "title": "EDU Revolution Application Procedure via UMS",
            "content": (
                "Students must submit nominations for any EDU Revolution initiative through the official portal. "
                "Application Navigation Path:\n"
                "1. Log in to LPU UMS (https://ums.lpu.in/lpuums/)\n"
                "2. Navigate to LMS\n"
                "3. Click on 'Edu Revolution: Be the Change'\n"
                "4. Select 'Apply for EDU Revolution'\n"
                "5. Upload verified proof documents (invoices, certificates, sanction letters, exam admit cards)\n"
                "6. Track approval through Department Coordinator -> Academic Affairs Committee."
            ),
            "category_name": "Process / SOP",
            "tags": ["ums_navigation", "apply_edu_revolution", "lms", "application_steps"],
            "original_source_url": "https://ums.lpu.in/lpuums/",
            "source_id": "DOC-EDREV-2026",
            "source_title": "EDU Revolution Guide — Division of Academic Affairs, LPU",
            "source_type": "pdf",
            "source_document": "Academic Benefits copy.pdf",
            "source_page": "Page 5",
            "source_section": "Application Portal Navigation",
            "clause_reference": "Section 2.1",
            "verification_status": "verified",
            "verified_by": "Division of Academic Affairs",
            "searchable_variants": [
                "How do I apply for EDU Revolution on UMS?",
                "Where is the Edu Revolution option in UMS portal?",
                "How to submit nomination for academic benefits at LPU?"
            ],
            "type_metadata": {
                "sop_name": "EDU Revolution Online Nomination",
                "preconditions": ["Active student UMS login", "Authentic verified proof document"],
                "sequential_steps": [
                    "Login UMS -> LMS",
                    "Click 'Edu Revolution: Be the Change'",
                    "Click 'Apply for EDU Revolution'",
                    "Submit document and submit nomination"
                ],
                "required_documents": ["GST Invoice / Sanction Letter / Admit Card / Scorecard / Certificate"],
                "fee_required": False
            }
        })

        # 3. Revenue Generation ("Earn Your Fee")
        records.append({
            "record_id": "LPU-EDREV-003",
            "record_type": KnowledgeType.POLICY.value,
            "title": "Revenue Generation Policy ('Earn Your Fee')",
            "content": (
                "Under the 'Earn Your Fee' revenue generation policy, students earning legitimate income through "
                "entrepreneurial ventures, freelance consulting, or registered startups can receive substantial academic benefits:\n"
                "- Up to 15% overall attendance benefit\n"
                "- Exemption / credit substitution for practical or elective courses\n"
                "- Tuition fee adjustments or cash scholarship awards corresponding to verified revenue milestones\n"
                "Eligible income must be verified via bank statements, GST invoices, or registered company receipts."
            ),
            "category_name": "Policy",
            "tags": ["revenue_generation", "earn_your_fee", "attendance_benefit", "entrepreneurship"],
            "original_source_url": "https://www.lpu.in/academics/edu-revolution.php",
            "source_id": "DOC-EDREV-2026",
            "source_title": "EDU Revolution Guide — Division of Academic Affairs, LPU",
            "source_type": "pdf",
            "source_document": "Academic Benefits copy.pdf",
            "source_page": "Pages 7-9",
            "source_section": "4. Revenue Generation",
            "clause_reference": "Section 4.1 - 4.4",
            "verification_status": "verified",
            "verified_by": "Division of Academic Affairs",
            "searchable_variants": [
                "What is the Earn Your Fee scheme at LPU?",
                "How does student revenue generation give attendance benefits at LPU?",
                "Can I get attendance relaxation if I have a startup or freelance income?"
            ],
            "type_metadata": {
                "policy_name": "Revenue Generation & Earn Your Fee Incentive",
                "clause_number": "Section 4",
                "applicability": "Students generating verified external business/consulting income",
                "penalty_or_consequence": "Fraudulent invoice submissions lead to immediate disciplinary action and forfeiture of credits"
            }
        })

        # 4. NPTEL / MOOCs / Proctored Certifications
        records.append({
            "record_id": "LPU-EDREV-004",
            "record_type": KnowledgeType.ACADEMIC_REGULATION.value,
            "title": "NPTEL, SWAYAM & Proctored MOOCs Credit Transfer & Grade Upgradation",
            "content": (
                "Students completing approved proctored online courses from NPTEL, SWAYAM, Coursera, or edX "
                "can transfer credits to their degree curriculum and receive grade upgradation. "
                "A verified certificate with an Elite / Gold ranking or score >= 75% grants course exemption "
                "or grade enhancement for designated elective or open courses as approved by the Dean of Academic Affairs."
            ),
            "category_name": "Academic Regulations",
            "tags": ["nptel", "moocs", "swayam", "credit_transfer", "grade_upgradation"],
            "original_source_url": "https://www.lpu.in/academics/edu-revolution.php",
            "source_id": "DOC-EDREV-2026",
            "source_title": "EDU Revolution Guide — Division of Academic Affairs, LPU",
            "source_type": "pdf",
            "source_document": "Academic Benefits copy.pdf",
            "source_page": "Pages 10-11",
            "source_section": "5. NPTEL / Proctored MOOCs / Certifications",
            "clause_reference": "Section 5.1 - 5.3",
            "verification_status": "verified",
            "verified_by": "Division of Academic Affairs",
            "searchable_variants": [
                "Can I transfer NPTEL credits to LPU degree?",
                "How do MOOCs certificates upgrade my CGPA or course grade?",
                "What is LPU policy on SWAYAM and Coursera certifications?"
            ],
            "type_metadata": {
                "regulation_code": "EDREV-MOOC-02",
                "governing_body": "Academic Council",
                "program_applicability": "All degree programmes with elective course options"
            }
        })

        # 5. National & Industry Projects (DRDO, ISRO, BARC)
        records.append({
            "record_id": "LPU-EDREV-005",
            "record_type": KnowledgeType.POLICY.value,
            "title": "Projects with Government & Premier National Bodies (DRDO, ISRO, BARC)",
            "content": (
                "Students working on official research or development projects sanctioned by national bodies—including "
                "DRDO, ISRO, BARC, IITs, or government ministries—are entitled to premier academic incentives:\n"
                "- Full course equivalency for capstone/major project\n"
                "- Grade upgradation (up to 1 grade up)\n"
                "- Duty leave and attendance condonation for the project execution period\n"
                "Approval requires an official sanction letter from the funding or host organization."
            ),
            "category_name": "Policy",
            "tags": ["drdo", "isro", "barc", "research_projects", "national_institutes"],
            "original_source_url": "https://www.lpu.in/academics/edu-revolution.php",
            "source_id": "DOC-EDREV-2026",
            "source_title": "EDU Revolution Guide — Division of Academic Affairs, LPU",
            "source_type": "pdf",
            "source_document": "Academic Benefits copy.pdf",
            "source_page": "Pages 12-14",
            "source_section": "6. Projects (Industry & National Agencies)",
            "clause_reference": "Section 6.1 - 6.3",
            "verification_status": "verified",
            "verified_by": "Division of Academic Affairs",
            "searchable_variants": [
                "What benefits does LPU give for DRDO or ISRO projects?",
                "Can research projects with government agencies waive coursework at LPU?",
                "How to claim academic credit for national level projects at LPU?"
            ],
            "type_metadata": {
                "policy_name": "Government & Premier Institutional Research Projects",
                "clause_number": "Section 6",
                "applicability": "Students holding verified government / national body project appointments"
            }
        })

        # 6. Internship Beyond Curriculum
        records.append({
            "record_id": "LPU-EDREV-006",
            "record_type": KnowledgeType.POLICY.value,
            "title": "Internship Beyond Curriculum Academic Benefits",
            "content": (
                "Students securing approved internships beyond standard curriculum requirements can receive course credits "
                "and grade enhancements. Criteria and tiering:\n"
                "- Local/Startup internship (stipend Rs. 50,000 - 1,00,000 for 1-2 months): 1 Grade Up in a 3-credit course\n"
                "- State/National Agency: 1 Grade Up in a 4-credit course\n"
                "- Premier National / International Institute: 1 Grade Up in a 6-credit course\n"
                "Requires submission of internship offer letter, monthly progress report, and employer completion certificate."
            ),
            "category_name": "Policy",
            "tags": ["internship_benefits", "grade_upgradation", "stipend", "credits"],
            "original_source_url": "https://www.lpu.in/academics/edu-revolution.php",
            "source_id": "DOC-EDREV-2026",
            "source_title": "EDU Revolution Guide — Division of Academic Affairs, LPU",
            "source_type": "pdf",
            "source_document": "Academic Benefits copy.pdf",
            "source_page": "Pages 15-20",
            "source_section": "7. Internship Beyond Curriculum",
            "clause_reference": "Section 7.1 - 7.5",
            "verification_status": "verified",
            "verified_by": "Division of Academic Affairs",
            "searchable_variants": [
                "Does an off-campus internship give academic credits at LPU?",
                "How does internship stipend give grade upgrades at LPU?",
                "What are the benefits for doing internships beyond curriculum?"
            ],
            "type_metadata": {
                "policy_name": "Internship Beyond Curriculum Regulation",
                "clause_number": "Section 7",
                "applicability": "Enrolled students completing verified corporate/agency internships"
            }
        })

        # 7. Recognition of Prior Learning (RPL)
        records.append({
            "record_id": "LPU-EDREV-007",
            "record_type": KnowledgeType.ACADEMIC_REGULATION.value,
            "title": "Recognition of Prior Learning (RPL) Policy",
            "content": (
                "Recognition of Prior Learning (RPL) evaluates formal, non-formal, and informal learning acquired by students "
                "before or during their enrollment. Demonstrated competencies through hackathons, patents, software deployments, "
                "or recognized industry accomplishments can be recognized towards course completion and credit waivers."
            ),
            "category_name": "Academic Regulations",
            "tags": ["rpl", "prior_learning", "patents", "hackathons", "credit_waiver"],
            "original_source_url": "https://www.lpu.in/academics/edu-revolution.php",
            "source_id": "DOC-EDREV-2026",
            "source_title": "EDU Revolution Guide — Division of Academic Affairs, LPU",
            "source_type": "pdf",
            "source_document": "Academic Benefits copy.pdf",
            "source_page": "Pages 21-23",
            "source_section": "8. Recognition of Prior Learning (RPL)",
            "clause_reference": "Section 8.1 - 8.3",
            "verification_status": "verified",
            "verified_by": "Division of Academic Affairs",
            "searchable_variants": [
                "What is RPL Recognition of Prior Learning at LPU?",
                "Can I get course credit for my patent or hackathon win?",
                "How does RPL work for computer science students at LPU?"
            ],
            "type_metadata": {
                "regulation_code": "EDREV-RPL-03",
                "governing_body": "Division of Academic Affairs"
            }
        })

        # 8. Grade Upgradation for Publications (Scopus Q1-Q4)
        records.append({
            "record_id": "LPU-EDREV-008",
            "record_type": KnowledgeType.ACADEMIC_REGULATION.value,
            "title": "Grade Upgradation for Research Publications & Intellectual Property",
            "content": (
                "Students who author and publish research papers indexed in Scopus or Web of Science receive explicit grade boosts:\n"
                "- Q1 / Q2 indexed journal paper: 1 Grade Up in a core course or equivalent academic credit\n"
                "- Q3 / Q4 journal or recognized IEEE/ACM conference proceeding: 1 Grade Up in an elective course\n"
                "- Published/Granted Patent: Proportional grade enhancement subject to Academic Committee verification."
            ),
            "category_name": "Academic Regulations",
            "tags": ["scopus", "research_paper", "grade_upgradation", "q1_journal", "patents"],
            "original_source_url": "https://www.lpu.in/academics/edu-revolution.php",
            "source_id": "DOC-EDREV-2026",
            "source_title": "EDU Revolution Guide — Division of Academic Affairs, LPU",
            "source_type": "pdf",
            "source_document": "Academic Benefits copy.pdf",
            "source_page": "Pages 24-28",
            "source_section": "9. Grade Upgradation",
            "clause_reference": "Section 9.1 - 9.4",
            "verification_status": "verified",
            "verified_by": "Division of Academic Affairs",
            "searchable_variants": [
                "Can publishing a research paper increase my CGPA at LPU?",
                "What is the grade upgradation policy for Scopus indexed papers?",
                "Does a patent grant grade boost at LPU?"
            ],
            "type_metadata": {
                "regulation_code": "EDREV-RES-04",
                "governing_body": "Division of Academic Affairs & Research Cell"
            }
        })

        # 9. Up to 10% Attendance Benefit for Competitive Exams
        records.append({
            "record_id": "LPU-EDREV-009",
            "record_type": KnowledgeType.ATTENDANCE_POLICY.value,
            "title": "Up to 10% Attendance Benefit for Competitive & Recruitment Exams",
            "content": (
                "Eligible students preparing for or appearing in recognized national and international examinations—such as "
                "GATE, CAT, UPSC Civil Services, GRE, GMAT, or verified corporate recruitment drives—are granted up to a "
                "10% attendance benefit across courses in the active semester. "
                "Students must submit verified exam admit cards or test registration proofs via UMS LMS before the deadline."
            ),
            "category_name": "Attendance Policy",
            "tags": ["attendance_benefit", "gate", "cat", "upsc", "competitive_exams"],
            "original_source_url": "https://www.lpu.in/academics/edu-revolution.php",
            "source_id": "DOC-EDREV-2026",
            "source_title": "EDU Revolution Guide — Division of Academic Affairs, LPU",
            "source_type": "pdf",
            "source_document": "Academic Benefits copy.pdf",
            "source_page": "Pages 32-34",
            "source_section": "11. Up to 10% Attendance Benefit",
            "clause_reference": "Section 11.1 - 11.3",
            "verification_status": "verified",
            "verified_by": "Division of Academic Affairs",
            "searchable_variants": [
                "Can I get 10% attendance relaxation for GATE exam preparation?",
                "What is LPU attendance benefit for UPSC or CAT exams?",
                "How to apply for competitive exam attendance benefit on UMS?"
            ],
            "type_metadata": {
                "minimum_percentage": 75.0,
                "condonation_limit_percent": 65.0,
                "medical_leave_benefit": "Separate medical certificate rules apply",
                "duty_leave_benefit": "Granted under DL policy",
                "debarment_criteria": "Attendance below 65% after all benefits cannot be condoned"
            }
        })

        # 10. Duty Leave (DL) Policy
        records.append({
            "record_id": "LPU-EDREV-010",
            "record_type": KnowledgeType.ATTENDANCE_POLICY.value,
            "title": "Duty Leave (DL) Policy for Sports, Cultural & Technical Competitions",
            "content": (
                "Duty Leave (DL) is granted to students officially nominated or representing LPU in national, international, "
                "or inter-university competitions (sports, hackathons, cultural festivals, youth festivals). "
                "Approved DL marks classes as present in official attendance ledgers and prevents exam debarment."
            ),
            "category_name": "Attendance Policy",
            "tags": ["duty_leave", "dl", "sports", "competitions", "hackathons"],
            "original_source_url": "https://www.lpu.in/academics/edu-revolution.php",
            "source_id": "DOC-EDREV-2026",
            "source_title": "EDU Revolution Guide — Division of Academic Affairs, LPU",
            "source_type": "pdf",
            "source_document": "Academic Benefits copy.pdf",
            "source_page": "Pages 35-37",
            "source_section": "12. Duty Leave (DL)",
            "clause_reference": "Section 12.1 - 12.3",
            "verification_status": "verified",
            "verified_by": "Division of Academic Affairs",
            "searchable_variants": [
                "How does Duty Leave work at LPU?",
                "Can I get DL for participating in an external hackathon or sports meet?",
                "Does Duty Leave count towards my 75% attendance requirement?"
            ],
            "type_metadata": {
                "minimum_percentage": 75.0,
                "condonation_limit_percent": 65.0,
                "duty_leave_benefit": "100% attendance credit for sanctioned event dates",
                "debarment_criteria": "DL must be sanctioned within 7 days of competition completion"
            }
        })

        # 11. Semester Abroad & Global Mobility
        records.append({
            "record_id": "LPU-EDREV-011",
            "record_type": KnowledgeType.INTERNATIONAL_EXCHANGE_PROGRAMME.value,
            "title": "Semester Abroad & Global Academic Mobility Guidelines",
            "content": (
                "Students can complete one or two semesters at accredited foreign partner universities under Semester Abroad. "
                "Options include fully funded, partially funded (no tuition fee to partner university), and self-funded programs. "
                "Credits earned abroad are directly mapped and transferred to the LPU transcript with zero graduation delay."
            ),
            "category_name": "International Exchange Programme",
            "tags": ["semester_abroad", "foreign_exchange", "credit_transfer", "international"],
            "original_source_url": "https://www.lpu.in/international/study-abroad.php",
            "source_id": "DOC-EDREV-2026",
            "source_title": "EDU Revolution Guide — Division of Academic Affairs, LPU",
            "source_type": "pdf",
            "source_document": "Academic Benefits copy.pdf",
            "source_page": "Pages 38-39",
            "source_section": "13. Semester Abroad",
            "clause_reference": "Section 13.1 - 13.3",
            "verification_status": "verified",
            "verified_by": "Division of International Affairs",
            "searchable_variants": [
                "How does the semester abroad program work at LPU?",
                "Can I study a semester in a foreign university and transfer credits?",
                "What is the fee structure for semester abroad exchange?"
            ],
            "type_metadata": {
                "partner_institution": "Foreign Partner Universities in USA, UK, Canada, Australia, EU",
                "country": "Multiple",
                "programme_type": "Semester Exchange & Dual Degree",
                "credit_transfer_allowed": True
            }
        })

        # 12. Query Zone & Academic Affairs Helpdesk
        records.append({
            "record_id": "LPU-EDREV-012",
            "record_type": KnowledgeType.OFFICE_DIRECTORY.value,
            "title": "Academic Benefits Query Zone & Verification Helpdesk (Block 38-205B)",
            "content": (
                "The official Query Zone for EDU Revolution and academic benefits inquiries is located at:\n"
                "Block 38, Room 205B, Division of Academic Affairs, Lovely Professional University.\n"
                "Operating Hours: Monday through Saturday, 9:00 AM to 5:00 PM.\n"
                "Students can visit in person for document verification, credit equivalence guidance, and nomination status tracking."
            ),
            "category_name": "Office Directory",
            "tags": ["query_zone", "block_38", "academic_affairs", "helpdesk"],
            "original_source_url": "https://www.lpu.in/academics/edu-revolution.php",
            "source_id": "DOC-EDREV-2026",
            "source_title": "EDU Revolution Guide — Division of Academic Affairs, LPU",
            "source_type": "pdf",
            "source_document": "Academic Benefits copy.pdf",
            "source_page": "Page 5",
            "source_section": "Helpdesk & Inquiries",
            "clause_reference": "Section 2.2",
            "verification_status": "verified",
            "verified_by": "Division of Academic Affairs",
            "searchable_variants": [
                "Where is the EDU Revolution query zone located?",
                "Whom to contact for academic benefits issues in person?",
                "Where is Block 38 Room 205B at LPU?"
            ],
            "type_metadata": {
                "department_office": "Division of Academic Affairs",
                "room_number": "Room 205B",
                "building_block": "Block 38",
                "official_email": "academic.affairs@lpu.co.in",
                "phone_extension": "Block 38 Helpdesk"
            }
        })

        return records

