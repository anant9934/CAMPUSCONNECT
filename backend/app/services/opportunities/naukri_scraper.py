"""
Naukri and job board parsing engine with backoff and error handling.
"""

import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class NaukriOpportunityScraper:
    def __init__(self, backoff_factor: float = 1.5, max_retries: int = 3):
        self.backoff_factor = backoff_factor
        self.max_retries = max_retries
        self.user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        ]

    def parse_job_snippet(self, raw_html: str) -> Dict[str, Any]:
        """Simulated extractor of job attributes from DOM snippet."""
        title_match = re.search(r'<title>(.*?)</title>', raw_html, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else "Software Engineer"
        return {"raw_title": title, "parsed": True}

    def get_request_headers(self, idx: int = 0) -> Dict[str, str]:
        ua = self.user_agents[idx % len(self.user_agents)]
        return {
            "User-Agent": ua,
            "Accept": "application/json, text/html, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.naukri.com/"
        }

    def extract_dom_fields(self, html_text: str) -> Dict[str, str]:
        company = "Unknown"
        comp_m = re.search(r'class="companyName">([^<]+)<', html_text)
        if comp_m:
            company = comp_m.group(1).strip()
        loc = "Punjab/Delhi"
        loc_m = re.search(r'class="loc">([^<]+)<', html_text)
        if loc_m:
            loc = loc_m.group(1).strip()
        return {"company": company, "location": loc}

    def extract_salary_text(self, text: str) -> Optional[str]:
        patterns = [
            r'(\d+(?:\.\d+)?\s*(?:-\s*\d+(?:\.\d+)?)?\s*(?:LPA|PA|P\.A\.))',
            r'(₹\s*[\d,]+\s*(?:-\s*[\d,]+)?\s*(?:/month|per month|monthly)?)',
            r'(\d+k\s*-\s*\d+k\s*/\s*mo)'
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                return m.group(1)
        return None

    def extract_experience_range(self, text: str) -> Dict[str, float]:
        m = re.search(r'(\d+)\s*-\s*(\d+)\s*(?:yrs|years)', text, re.IGNORECASE)
        if m:
            return {"min": float(m.group(1)), "max": float(m.group(2))}
        if re.search(r'fresher|intern', text, re.IGNORECASE):
            return {"min": 0.0, "max": 1.0}
        return {"min": 0.0, "max": 2.0}

    def extract_skill_tags(self, text: str, known_skills: List[str]) -> List[str]:
        found = []
        for skill in known_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
                found.append(skill)
        return list(dict.fromkeys(found))
