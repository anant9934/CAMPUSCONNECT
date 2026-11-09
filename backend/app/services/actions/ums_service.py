import logging
import re
from typing import List, Dict, Any, Optional
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ums_catalog import UMSServiceCatalog
from app.schemas.ums import NavigationCard

logger = logging.getLogger(__name__)


class UMSServiceResolver:
    """
    Search and navigation resolver across all 234 UMS menu entries from
    ums_service_catalog_from_screenshots.csv.
    """

    @classmethod
    async def find_matching_service(
        cls,
        query: str,
        db: AsyncSession,
        module_filter: Optional[str] = None
    ) -> Optional[UMSServiceCatalog]:
        """
        Matches student query to the most relevant UMS service entry using:
        1. Exact/substring match against service_label
        2. Keyword and student synonym matches
        3. Module-scoped search
        """
        q = query.lower().strip()
        clean_q = re.sub(r"[^a-zA-Z0-9\s]", " ", q)
        query_words = [w for w in clean_q.split() if len(w) > 2]

        stmt = select(UMSServiceCatalog).where(UMSServiceCatalog.is_active == True)
        if module_filter:
            stmt = stmt.where(UMSServiceCatalog.module.ilike(f"%{module_filter}%"))

        res = await db.execute(stmt)
        all_services = res.scalars().all()

        best_match = None
        best_score = 0.0

        for svc in all_services:
            label_lower = svc.service_label.lower()
            module_lower = svc.module.lower()
            nav_lower = svc.navigation_path.lower()
            keywords = [k.lower() for k in (svc.keywords or [])]

            score = 0.0

            # 1. Exact or contained phrase in label
            if label_lower in q:
                score += 5.0
            elif any(part in q for part in label_lower.split() if len(part) > 3):
                score += 2.5

            # 2. Word overlap with service label
            label_words = set(re.findall(r"\w+", label_lower))
            overlap = label_words.intersection(query_words)
            score += len(overlap) * 2.0

            # 3. Synonym and keyword match
            kw_overlap = set(keywords).intersection(query_words)
            score += len(kw_overlap) * 1.5

            # 4. Module name match
            if module_lower in q:
                score += 1.0

            # Intent boost heuristics
            if "hostel" in q and "hostel" in label_lower:
                score += 8.0
            if ("doctor" in q or "clinic" in q or "physician" in q) and "doctor" in label_lower:
                score += 10.0
            if ("counseling" in q or "counselling" in q or "psychologist" in q or "yourdost" in q) and ("counsel" in label_lower or "psychologist" in label_lower):
                score += 10.0
            if ("discussion room" in q or "study room" in q) and "discussion room" in label_lower:
                score += 10.0
            if "language lab" in q and "language lab" in label_lower:
                score += 10.0
            if ("re-appear" in q or "reappear" in q or "backlog" in q) and ("re-appear" in label_lower or "reappear" in label_lower):
                score += 10.0
            if ("re-evaluation" in q or "reevaluation" in q) and "re-evaluation" in label_lower:
                score += 10.0
            if ("wi-fi" in q or "wifi" in q or "internet" in q) and ("wi-fi" in label_lower or "wifi" in label_lower):
                score += 10.0
            if "attendance" in q and "attendance" in label_lower:
                score += 6.0
            if "fee" in q and ("receipt" in q or "fee" in label_lower):
                score += 6.0
            if "rfid" in q and "rfid" in label_lower:
                score += 10.0
            if ("date sheet" in q or "datesheet" in q) and ("date sheet" in label_lower or "datesheet" in label_lower):
                score += 10.0
            if ("credit" in q or "prerequisite" in q or "syllabus" in q or "equivalence" in q) and "credit transfer" in label_lower:
                score += 15.0

            if score > best_score:
                best_score = score
                best_match = svc

        # Threshold for acceptable match
        if best_match and best_score >= 2.0:
            return best_match
        return None

    @classmethod
    async def search_services(
        cls,
        query: str,
        db: AsyncSession,
        limit: int = 10,
        module_filter: Optional[str] = None
    ) -> List[UMSServiceCatalog]:
        """Returns top matching UMS services for directory listing / autocompletion."""
        q = query.lower().strip()
        stmt = select(UMSServiceCatalog).where(UMSServiceCatalog.is_active == True)
        if module_filter:
            stmt = stmt.where(UMSServiceCatalog.module == module_filter)

        res = await db.execute(stmt)
        services = res.scalars().all()

        scored = []
        q_words = set(re.findall(r"\w+", q))
        for svc in services:
            label_lower = svc.service_label.lower()
            mod_lower = svc.module.lower()
            keywords = set(k.lower() for k in (svc.keywords or []))

            score = 0
            if q in label_lower:
                score += 10
            if q in mod_lower:
                score += 5
            score += len(q_words.intersection(re.findall(r"\w+", label_lower))) * 3
            score += len(q_words.intersection(keywords)) * 2

            if score > 0 or not q:
                scored.append((score, svc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:limit]]

    @classmethod
    def build_navigation_card(cls, svc: UMSServiceCatalog) -> NavigationCard:
        """Constructs a structured NavigationCard for frontend rendering."""
        # Formulate clean instruction
        clean_path = svc.navigation_path.replace(">", "→")
        auth_note = " Authentication required." if "required" in svc.ums_authentication else ""
        instruction = f"Open UMS, sign in with your student credentials, and follow: {clean_path}.{auth_note}"

        return NavigationCard(
            service_title=svc.service_label,
            module=svc.module,
            breadcrumb=svc.navigation_path,
            instruction=instruction,
            handoff_url=svc.deep_link_url or "https://ums.lpu.in/lpuums/",
            button_label="Open Official UMS",
        )
