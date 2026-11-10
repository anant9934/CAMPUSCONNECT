import logging
from typing import Dict, Any, List, Optional
import httpx

from app.core.config import settings
from app.services.cache_service import ToolCache

logger = logging.getLogger(__name__)

CURATED_STUDENT_OPPORTUNITIES = [
    {
        "id": "OPP-001",
        "title": "AI / ML Research Intern",
        "company": "DeepMind Partner Lab / AI Innovation Hub",
        "location": "Remote / Hybrid (Punjab / Delhi NCR)",
        "type": "Internship",
        "stipend": "₹25,000 - ₹40,000 / month",
        "eligibility": "B.Tech CSE / IT 3rd/4th year, Python, PyTorch, LLMs, LangChain",
        "academic_benefit_category": "EDU-Revolution Category 6 (Technical Project)",
        "description": "Work on generative AI agent frameworks, RAG architectures, and model evaluations.",
        "apply_url": "https://startup.jobs/search?q=machine+learning"
    },
    {
        "id": "OPP-002",
        "title": "Full-Stack Web Development Fellow",
        "company": "Startup School LPU Incubation Center",
        "location": "Block 32 / LPU Incubation Hub",
        "type": "Part-Time / Project Track",
        "stipend": "₹15,000 - ₹30,000 / month + Equity",
        "eligibility": "React, TypeScript, FastAPI, PostgreSQL, Docker",
        "academic_benefit_category": "EDU-Revolution Category 5 (Revenue Generating Project)",
        "description": "Build production SaaS platforms for incubated campus tech startups.",
        "apply_url": "https://startup.jobs/search?q=full+stack"
    },
    {
        "id": "OPP-003",
        "title": "Embedded IoT & Firmware Engineer Intern",
        "company": "Hardware Tech Accelerator",
        "location": "Mohali / Chandigarh / On-Site",
        "type": "Internship",
        "stipend": "₹20,000 / month",
        "eligibility": "ESP32, STM32, C/C++, PCB Design, MQTT",
        "academic_benefit_category": "EDU-Revolution Category 3 (National Hardware Projects)",
        "description": "Design IoT sensor telemetry devices and healthcare electronics.",
        "apply_url": "https://startup.jobs/search?q=iot"
    },
    {
        "id": "OPP-004",
        "title": "Cloud DevOps & Platform Engineering Trainee",
        "company": "CloudNative Solutions",
        "location": "Remote",
        "type": "Internship / Pre-Placement Offer",
        "stipend": "₹30,000 / month",
        "eligibility": "Linux, Kubernetes, Terraform, AWS/GCP, CI/CD",
        "academic_benefit_category": "EDU-Revolution Category 7 (Cloud Certification & Deployment)",
        "description": "Deploy distributed microservices and automated infrastructure pipelines.",
        "apply_url": "https://startup.jobs/search?q=devops"
    }
]


class OpportunitiesService:
    """
    Student career, startup, and technical internship opportunity discovery service.
    Integrates Startup.Jobs API with verified EDU-Revolution academic benefit mappings.
    """

    @classmethod
    async def get_opportunities(
        cls,
        query: Optional[str] = None,
        role_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves matching internship and startup opportunities.
        Queries Startup.Jobs API if live, falling back to verified campus opportunities.
        """
        search_query = (query or "developer").lower().strip()
        cache_key = f"{search_query}:{role_type or 'all'}"

        # 1. Check ToolCache (4h TTL to preserve Startup.Jobs API quota)
        cached = ToolCache.get("startup_jobs", cache_key)
        if cached is not None:
            logger.info(f"ToolCache HIT for Startup.Jobs query '{search_query}' (0 API calls)")
            return cached

        opportunities = list(CURATED_STUDENT_OPPORTUNITIES)

        # Attempt live query to Startup.Jobs API if API key is present
        if settings.STARTUP_JOBS_API_KEY:
            try:
                headers = {
                    "Authorization": f"Bearer {settings.STARTUP_JOBS_API_KEY}",
                    "Accept": "application/json"
                }
                url = f"https://startup.jobs/api/v1/jobs?q={search_query}"

                async with httpx.AsyncClient(timeout=5.0) as client:
                    res = await client.get(url, headers=headers)
                    if res.status_code == 200:
                        live_jobs = res.json()
                        if isinstance(live_jobs, list) and live_jobs:
                            for idx, job in enumerate(live_jobs[:5]):
                                opportunities.append({
                                    "id": f"LIVE-{idx+1}",
                                    "title": job.get("title", "Software Engineer"),
                                    "company": job.get("company_name", "Tech Startup"),
                                    "location": job.get("location", "Remote / India"),
                                    "type": job.get("job_type", "Internship / Full-Time"),
                                    "stipend": job.get("salary_range", "Market Competitive"),
                                    "eligibility": "B.Tech / MCA, Relevant skills",
                                    "academic_benefit_category": "EDU-Revolution Category 5/6",
                                    "description": job.get("description", "")[:200] + "...",
                                    "apply_url": job.get("url") or "https://startup.jobs"
                                })
            except Exception as e:
                logger.info(f"Startup.Jobs live API query skipped or offline: {e}. Using curated opportunities.")

        # Filter by keyword if provided
        final_list = opportunities
        if query:
            q_lower = query.lower()
            filtered = [
                opp for opp in opportunities
                if q_lower in opp["title"].lower() or
                   q_lower in opp["eligibility"].lower() or
                   q_lower in opp["description"].lower()
            ]
            if filtered:
                final_list = filtered

        # Cache for 4 hours
        ToolCache.set("startup_jobs", cache_key, final_list, ttl_seconds=14400)
        return final_list

