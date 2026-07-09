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
