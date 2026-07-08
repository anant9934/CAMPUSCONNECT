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
