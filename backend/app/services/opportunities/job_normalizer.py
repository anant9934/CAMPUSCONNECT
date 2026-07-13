"""
JobNormalizer: Normalizes salaries, locations, skill aliases, and education titles.
"""

import re
from typing import Dict, Any, Tuple, Optional

class JobNormalizer:
    def __init__(self):
        self.location_clusters = {
            "Punjab-Tricity": ["mohali", "chandigarh", "panchkula", "jalandhar", "ludhiana", "phagwara"],
            "Delhi-NCR": ["gurgaon", "gurugram", "noida", "delhi", "new delhi", "faridabad", "ghaziabad"],
            "Bangalore": ["bangalore", "bengaluru"],
            "Pune": ["pune"],
            "Hyderabad": ["hyderabad"],
            "Remote": ["remote", "work from home", "wfh"]
        }

    def parse_salary_inr(self, salary_str: str) -> Tuple[Optional[float], Optional[float], str]:
        if not salary_str:
            return None, None, "annual"
        # Check LPA format e.g. "6 - 12 LPA"
        lpa_m = re.search(r'(\d+(?:\.\d+)?)\s*(?:-\s*(\d+(?:\.\d+)?))?\s*LPA', salary_str, re.IGNORECASE)
        if lpa_m:
            min_val = float(lpa_m.group(1)) * 100000.0
            max_val = float(lpa_m.group(2)) * 100000.0 if lpa_m.group(2) else min_val
            return min_val, max_val, "annual"
        # Check monthly format e.g. "25,000 - 40,000 /month"
        mo_m = re.search(r'([\d,]+)\s*(?:-\s*([\d,]+))?\s*(?:/month|per month|monthly)', salary_str, re.IGNORECASE)
        if mo_m:
            min_val = float(mo_m.group(1).replace(",", "")) * 12.0
            max_val = float(mo_m.group(2).replace(",", "")) * 12.0 if mo_m.group(2) else min_val
            return min_val, max_val, "monthly"
        return 360000.0, 500000.0, "annual"

    def normalize_location(self, loc_str: str) -> str:
        loc_lower = loc_str.lower()
        for cluster, places in self.location_clusters.items():
            for p in places:
                if p in loc_lower:
                    return cluster
        return "Other"

    def normalize_job_title(self, raw_title: str) -> str:
        t = raw_title.strip()
        if re.search(r'frontend|react|angular|vue|ui developer', t, re.IGNORECASE):
            return "Frontend Developer"
        if re.search(r'backend|python|fastapi|django|node|java developer', t, re.IGNORECASE):
            return "Backend Developer"
        if re.search(r'full stack|fullstack', t, re.IGNORECASE):
            return "Full Stack Engineer"
        if re.search(r'machine learning|ml|data scientist|ai engineer', t, re.IGNORECASE):
            return "AI / Machine Learning Engineer"
        if re.search(r'data analyst|business analyst', t, re.IGNORECASE):
            return "Data Analyst"
        if re.search(r'devops|cloud|sre', t, re.IGNORECASE):
            return "DevOps & Cloud Engineer"
        if re.search(r'qa|sdet|test automation', t, re.IGNORECASE):
            return "QA Automation Engineer"
        return "Software Engineer"

    def resolve_skill_alias(self, skill: str) -> str:
        aliases = {
            "k8s": "Kubernetes", "ts": "TypeScript", "js": "JavaScript", "py": "Python",
            "react.js": "React", "nextjs": "Next.js", "postgres": "PostgreSQL", "mongo": "MongoDB",
            "sklearn": "Scikit-Learn", "tf": "TensorFlow", "dsa": "Data Structures & Algorithms"
        }
        return aliases.get(skill.lower(), skill)

    def parse_degree(self, text: str) -> str:
        if re.search(r'b\.?tech|b\.?e', text, re.IGNORECASE):
            return "B.Tech"
        if re.search(r'mca', text, re.IGNORECASE):
            return "MCA"
        if re.search(r'm\.?tech', text, re.IGNORECASE):
            return "M.Tech"
        return "Any Graduate"
