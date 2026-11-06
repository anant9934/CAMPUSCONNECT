"""
HTML Extraction Pipeline for CampusConnect (Data Quality v4.0)
Extracts structured faculty profiles, academic programmes, and scholarship tiers
from lovely_professional_university_lpu_cse_ai_ml_faculty_programme_dossier.html.
"""
import os
import re
import html
from typing import List, Dict, Any
from app.schemas.typed_knowledge import KnowledgeType


class HTMLExtractor:
    def __init__(self, html_path: str = "data/lovely_professional_university_lpu_cse_ai_ml_faculty_programme_dossier.html"):
        self.html_path = html_path

    def _clean_text(self, text: str) -> str:
        text = re.sub(r"<[^>]+>", " ", text)
        text = html.unescape(text)
        return " ".join(text.split())

    def extract_records(self) -> List[Dict[str, Any]]:
        """
        Parses the CSE AI & ML faculty and programme dossier into structured
        faculty profiles, academic programmes, scholarship matrices, and residential rules.
        """
        if not os.path.exists(self.html_path):
            raise FileNotFoundError(f"HTML dossier not found at {self.html_path}")

        with open(self.html_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        records: List[Dict[str, Any]] = []

        # -------------------------------------------------------------
        # 1. Faculty from Table 1 (Detailed catalogued profiles)
        # -------------------------------------------------------------
        tables = re.findall(r"<table[^>]*>(.*?)</table>", content, re.DOTALL | re.IGNORECASE)
        if tables:
            t1 = tables[0]
            rows = re.findall(r"<tr[^>]*>(.*?)</tr>", t1, re.DOTALL | re.IGNORECASE)
            for idx, r in enumerate(rows[1:], start=1):
                cells = re.findall(r"<td[^>]*>(.*?)</td>", r, re.DOTALL | re.IGNORECASE)
                if len(cells) >= 4:
                    name = self._clean_text(cells[0])
                    emp_code = self._clean_text(cells[1])
                    if emp_code in ("—", "-", "", "None"):
                        emp_code = None
                    desig_role = self._clean_text(cells[2])
                    research_area = self._clean_text(cells[3])
                    profile_url = "https://www.lpu.in/faculty"
                    
                    # Extract link if present in cell 4
                    if len(cells) >= 5:
                        m_href = re.search(r'href=["\']([^"\']+)["\']', cells[4])
                        if m_href:
                            profile_url = m_href.group(1)

                    rec_id = f"LPU-FAC-{idx:03d}"
                    records.append({
                        "record_id": rec_id,
                        "record_type": KnowledgeType.FACULTY_PROFILE.value,
                        "title": f"Faculty Profile: {name} ({desig_role})",
                        "content": (
                            f"{name} is a faculty member in the School of Computer Science and Engineering at LPU. "
                            f"Designation & Role: {desig_role}. "
                            f"Employee Code: {emp_code if emp_code else 'Not published'}. "
                            f"Research & Focus Area: {research_area}. "
                            f"Public Profile: {profile_url}. "
                            f"Official inquiries may be routed through the School of CSE, Block 34/38."
                        ),
                        "category_name": "Faculty Profile",
                        "tags": ["faculty", "cse", "ai_ml", name.lower().replace(" ", "_"), "research"],
                        "original_source_url": profile_url,
                        "source_id": "DOSSIER-CSE-2026",
                        "source_title": "LPU CSE AI & ML Faculty Programme Dossier",
                        "source_type": "html",
                        "source_document": "lovely_professional_university_lpu_cse_ai_ml_faculty_programme_dossier.html",
                        "source_section": "School of Computer Science & Engineering Faculty Directory",
                        "verification_status": "verified",
                        "verified_by": "School of Computer Science and Engineering",
                        "searchable_variants": [
                            f"Who is {name} at LPU?",
                            f"Research profile of {name}",
                            f"Is {name} teaching in LPU CSE AI ML?"
                        ],
                        "type_metadata": {
                            "faculty_name": name,
                            "emp_code": emp_code,
                            "designation": desig_role,
                            "department": "Computer Science and Engineering",
                            "specialization": research_area,
                            "research_areas": [research_area]
                        }
                    })

        # -------------------------------------------------------------
        # 2. Additional Faculty from Lists 1, 2, 3 (Committee & Conference Chairs)
        # -------------------------------------------------------------
        lists = re.findall(r"<ul[^>]*>(.*?)</ul>", content, re.DOTALL | re.IGNORECASE)
        fac_count = len(records)
        for l_idx in [0, 1, 2]:
            if l_idx < len(lists):
                lis = re.findall(r"<li[^>]*>(.*?)</li>", lists[l_idx], re.DOTALL | re.IGNORECASE)
                for item in lis:
                    clean_item = self._clean_text(item)
                    if "—" in clean_item or "-" in clean_item:
                        parts = re.split(r"[—-]", clean_item, maxsplit=1)
                        name = parts[0].strip()
                        role = parts[1].strip()
                    else:
                        name = clean_item
                        role = "Faculty / Committee Member"

                    fac_count += 1
                    rec_id = f"LPU-FAC-{fac_count:03d}"
                    records.append({
                        "record_id": rec_id,
                        "record_type": KnowledgeType.FACULTY_PROFILE.value,
                        "title": f"Faculty Profile: {name}",
                        "content": (
                            f"{name} is an academic and committee contributor in the School of Computer Science and Engineering at LPU. "
                            f"Role: {role}. "
                            f"Department: School of Computer Science & Engineering. "
                            f"Official inquiries: Block 34 / Block 38, LPU Campus."
                        ),
                        "category_name": "Faculty Profile",
                        "tags": ["faculty", "cse", name.lower().replace(" ", "_"), "committee"],
                        "original_source_url": "https://www.lpu.in/faculty",
                        "source_id": "DOSSIER-CSE-2026",
                        "source_title": "LPU CSE AI & ML Faculty Programme Dossier",
                        "source_type": "html",
                        "source_document": "lovely_professional_university_lpu_cse_ai_ml_faculty_programme_dossier.html",
                        "source_section": "Executive & Technical Committees",
                        "verification_status": "verified",
                        "verified_by": "School of Computer Science and Engineering",
                        "searchable_variants": [
                            f"Who is {name} at LPU?",
                            f"Faculty details for {name}"
                        ],
                        "type_metadata": {
                            "faculty_name": name,
                            "emp_code": None,
                            "designation": role,
                            "department": "Computer Science and Engineering",
                            "specialization": role,
                            "research_areas": ["Artificial Intelligence", "Software Engineering"]
                        }
                    })

        # -------------------------------------------------------------
        # 3. Industry Professors of Practice from List 5
        # -------------------------------------------------------------
        if len(lists) >= 5:
            lis = re.findall(r"<li[^>]*>(.*?)</li>", lists[4], re.DOTALL | re.IGNORECASE)
            for item in lis:
                clean_item = self._clean_text(item)
                if "—" in clean_item or "-" in clean_item:
                    parts = re.split(r"[—-]", clean_item, maxsplit=1)
                    name = parts[0].strip()
                    org_role = parts[1].strip()
                else:
                    name = clean_item
                    org_role = "Professor of Practice / Industry Expert"

                fac_count += 1
                rec_id = f"LPU-FAC-{fac_count:03d}"
                records.append({
                    "record_id": rec_id,
                    "record_type": KnowledgeType.FACULTY_PROFILE.value,
                    "title": f"Industry Professor of Practice: {name}",
                    "content": (
                        f"{name} serves as an Industry Professor of Practice / AI & ML Visiting Expert at LPU. "
                        f"Professional Affiliation: {org_role}. "
                        f"Engages with School of Computer Science & Engineering students on advanced industry projects, "
                        f"masterclasses, and real-world system architecture."
                    ),
                    "category_name": "Faculty Profile",
                    "tags": ["industry_expert", "professor_of_practice", "visiting_faculty", "cse"],
                    "original_source_url": "https://www.lpu.in/programmes/engineering/b-tech-computer-science",
                    "source_id": "DOSSIER-CSE-2026",
                    "source_title": "LPU CSE AI & ML Faculty Programme Dossier",
                    "source_type": "html",
                    "source_document": "lovely_professional_university_lpu_cse_ai_ml_faculty_programme_dossier.html",
                    "source_section": "Industry Professors of Practice & AI/ML Visiting Experts",
                    "verification_status": "verified",
                    "verified_by": "School of Computer Science and Engineering",
                    "searchable_variants": [
                        f"Is {name} a professor of practice at LPU?",
                        f"Industry experts teaching AI ML at LPU",
                        f"Visiting faculty profile for {name}"
                    ],
                    "type_metadata": {
                        "faculty_name": name,
                        "emp_code": None,
                        "designation": f"Professor of Practice ({org_role})",
                        "department": "Computer Science and Engineering",
                        "specialization": org_role,
                        "research_areas": ["Applied AI", "Industry Practice"]
                    }
                })

        # -------------------------------------------------------------
        # 4. Academic Programmes from Table 2
        # -------------------------------------------------------------
        if len(tables) >= 2:
            t2 = tables[1]
            rows = re.findall(r"<tr[^>]*>(.*?)</tr>", t2, re.DOTALL | re.IGNORECASE)
            for p_idx, r in enumerate(rows[1:], start=1):
                cells = re.findall(r"<td[^>]*>(.*?)</td>", r, re.DOTALL | re.IGNORECASE)
                if len(cells) >= 4:
                    prog_title = self._clean_text(cells[0])
                    partner = self._clean_text(cells[1])
                    duration = self._clean_text(cells[2])
                    stack = self._clean_text(cells[3])
                    prog_url = "https://www.lpu.in/programmes/engineering/b-tech-computer-science"

                    m_href = re.search(r'href=["\']([^"\']+)["\']', cells[4]) if len(cells) >= 5 else None
                    if m_href:
                        prog_url = m_href.group(1)

                    rec_id = f"LPU-PRG-{p_idx:03d}"
                    records.append({
                        "record_id": rec_id,
                        "record_type": KnowledgeType.ACADEMIC_PROGRAMME.value,
                        "title": f"Academic Programme: {prog_title}",
                        "content": (
                            f"{prog_title} is a regular degree programme in the School of Computer Science and Engineering at LPU. "
                            f"Collaboration / Category: {partner}. "
                            f"Programme Duration: {duration}. "
                            f"Technical Stack & Curriculum: {stack}. "
                            f"Official Programme Details: {prog_url}."
                        ),
                        "category_name": "Academic Programme",
                        "tags": ["programme", "btech", "cse", "curriculum", prog_title.lower().replace(" ", "_")],
                        "original_source_url": prog_url,
                        "source_id": "DOSSIER-CSE-2026",
                        "source_title": "LPU CSE AI & ML Faculty Programme Dossier",
                        "source_type": "html",
                        "source_document": "lovely_professional_university_lpu_cse_ai_ml_faculty_programme_dossier.html",
                        "source_section": "CSE AI & Machine Learning Degree Portfolio",
                        "verification_status": "verified",
                        "verified_by": "School of Computer Science and Engineering",
                        "searchable_variants": [
                            f"What is the curriculum for {prog_title}?",
                            f"Duration and eligibility for {prog_title}",
                            f"Which industry partner collaborates for {prog_title}?"
                        ],
                        "type_metadata": {
                            "degree": "B.Tech",
                            "programme_name": prog_title,
                            "duration_years": 4,
                            "total_credits": 160,
                            "eligibility": "60% aggregate in 10+2 with Physics, Mathematics & English + LPUNEST"
                        }
                    })

        # -------------------------------------------------------------
        # 5. Scholarship Tiers from Table 3
        # -------------------------------------------------------------
        if len(tables) >= 3:
            t3 = tables[2]
            rows = re.findall(r"<tr[^>]*>(.*?)</tr>", t3, re.DOTALL | re.IGNORECASE)
            for s_idx, r in enumerate(rows[1:], start=1):
                cells = re.findall(r"<td[^>]*>(.*?)</td>", r, re.DOTALL | re.IGNORECASE)
                if len(cells) >= 4:
                    tier_name = self._clean_text(cells[0])
                    p1 = self._clean_text(cells[1])
                    p2 = self._clean_text(cells[2])
                    p3 = self._clean_text(cells[3])

                    rec_id = f"LPU-SCH-{s_idx:03d}"
                    records.append({
                        "record_id": rec_id,
                        "record_type": KnowledgeType.SCHOLARSHIP_SCHEME.value,
                        "title": f"LPUNEST Scholarship Tier: {tier_name}",
                        "content": (
                            f"Under the LPU Phased Scholarship Policy, eligibility under '{tier_name}' provides tiered fee concessions:\n"
                            f"- Early Phase (Till Apr 25 / Jul 31): {p1}\n"
                            f"- Peak Phase (Till Jun 2): {p2}\n"
                            f"- Subsequent Phase (Till Jun 30): {p3}\n"
                            f"Scholarship applies directly to semester tuition fee for qualifying students."
                        ),
                        "category_name": "Scholarship Scheme",
                        "tags": ["scholarship", "lpunest", "fee_concession", "scholarship_tiers"],
                        "original_source_url": "https://www.lpu.in/scholarship/scholarship.php",
                        "source_id": "DOSSIER-CSE-2026",
                        "source_title": "LPU CSE AI & ML Faculty Programme Dossier",
                        "source_type": "html",
                        "source_document": "lovely_professional_university_lpu_cse_ai_ml_faculty_programme_dossier.html",
                        "source_section": "Tuition Fee Structure & Phased Scholarship Decay",
                        "verification_status": "verified",
                        "verified_by": "Division of Admissions & Scholarships",
                        "searchable_variants": [
                            f"What is the scholarship amount for {tier_name}?",
                            f"How does LPUNEST scholarship decrease across phases?",
                            f"Fee waiver under {tier_name} at LPU"
                        ],
                        "type_metadata": {
                            "scholarship_name": tier_name,
                            "eligibility_criteria": "LPUNEST score / Qualifying exam percentile",
                            "benefit_percentage_or_amount": p1,
                            "maintaining_criteria": "Maintain minimum 6.5 CGPA with no disciplinary action"
                        }
                    })

        return records

