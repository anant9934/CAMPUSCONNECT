import time
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.multi_llm import EvaluationRun, EvaluationResult
from app.ai.cost_controller import CostController

logger = logging.getLogger(__name__)


# Domain-specific evaluation benchmark test cases
BENCHMARK_SUITE: Dict[str, List[Dict[str, Any]]] = {
    "nova": [
        {
            "id": "nova_case_01",
            "prompt": "Uni-Hospital ambulance ka number kya hai and timings kya hai?",
            "expected_keywords": ["unihospital", "ambulance", "+91-1824-517100", "24x7", "block 30"],
            "category": "campus_emergency_faq"
        },
        {
            "id": "nova_case_02",
            "prompt": "Central library open kab tak rehti hai weekend pe?",
            "expected_keywords": ["library", "timings", "block"],
            "category": "general_timing"
        }
    ],
    "themis": [
        {
            "id": "themis_case_01",
            "prompt": "My attendance is 63%, can I get medical condonation for final exams?",
            "expected_keywords": ["65%", "floor", "cannot", "debar", "mandatory 75%"],
            "category": "attendance_statutory_boundary"
        },
        {
            "id": "themis_case_02",
            "prompt": "I built an AI startup generating revenue, what EDU-Rev benefit can I claim?",
            "expected_keywords": ["cat-", "edu-revolution", "attendance", "course", "ums"],
            "category": "edurev_project_benefits"
        }
    ],
    "athena": [
        {
            "id": "athena_case_01",
            "prompt": "Write a Python function to compute the longest palindromic substring in O(N^2) time.",
            "expected_keywords": ["def", "palindrome", "expand", "o(n^2)", "return"],
            "category": "code_reasoning"
        },
        {
            "id": "athena_case_02",
            "prompt": "Explain the difference between optimistic and pessimistic locking in PostgreSQL.",
            "expected_keywords": ["optimistic", "pessimistic", "concurrency", "lock", "version"],
            "category": "system_architecture"
        }
    ],
    "oracle": [
        {
            "id": "oracle_case_01",
            "prompt": "What are the official Smart India Hackathon (SIH) 2026 eligibility guidelines for college teams?",
            "expected_keywords": ["smart india hackathon", "eligibility", "team", "college"],
            "category": "external_research_verification"
        },
        {
            "id": "oracle_case_02",
            "prompt": "Compare IEEE and ACM citation formats for a research paper on RAG systems.",
            "expected_keywords": ["ieee", "acm", "citation", "reference", "format"],
            "category": "citation_analysis"
        }
    ]
}


class EvaluationEngine:
    """
    LAYER 9 — EVALUATION ENGINE
    Tracks runtime telemetry, latency, token consumption, routing decisions,
    and runs domain-specific evaluation benchmark suites.
    """

    @classmethod
    async def run_benchmark_for_intelligence(
        cls,
        intelligence_id: str,
        system_invoker_fn,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Executes domain-specific benchmark test suite measuring correctness,
        latency, and cost attribution across test cases.
        """
        intel_key = intelligence_id.lower()
        test_cases = BENCHMARK_SUITE.get(intel_key, [])
        if not test_cases:
            return {"status": "skipped", "reason": f"No test cases for {intelligence_id}"}

        start_time = time.time()
        results: List[Dict[str, Any]] = []
        passed_count = 0
        total_latency = 0.0
        total_cost = 0.0

        for tc in test_cases:
            tc_start = time.time()
            try:
                out = await system_invoker_fn(
                    query=tc["prompt"],
                    intelligence_id=intel_key,
                    thinking_level="Balanced"
                )
                text = out.get("content", "").lower()
                latency_ms = int((time.time() - tc_start) * 1000)
                cost_usd = out.get("cost_usd", 0.0005)

                # Check keyword presence
                matched = [kw for kw in tc["expected_keywords"] if kw.lower() in text]
                score = round((len(matched) / len(tc["expected_keywords"])) * 100.0, 1)
                is_pass = score >= 50.0

                if is_pass:
                    passed_count += 1
                total_latency += latency_ms
                total_cost += cost_usd

                results.append({
                    "test_case_id": tc["id"],
                    "prompt": tc["prompt"],
                    "score": score,
                    "is_pass": is_pass,
                    "matched_keywords": matched,
                    "latency_ms": latency_ms,
                    "cost_usd": cost_usd,
                })
            except Exception as e:
                logger.error(f"Benchmark error for {tc['id']}: {e}")
                results.append({
                    "test_case_id": tc["id"],
                    "prompt": tc["prompt"],
                    "score": 0.0,
                    "is_pass": False,
                    "error": str(e),
                })

        avg_score = round(sum(r.get("score", 0.0) for r in results) / len(results), 1) if results else 0.0
        avg_latency = round(total_latency / len(results), 1) if results else 0.0

        summary = {
            "intelligence_id": intel_key,
            "total_cases": len(test_cases),
            "passed_cases": passed_count,
            "pass_rate_percent": round((passed_count / len(test_cases)) * 100.0, 1) if test_cases else 0.0,
            "avg_score": avg_score,
            "avg_latency_ms": avg_latency,
            "total_cost_usd": round(total_cost, 6),
            "results": results
        }

        # Persist EvaluationRun if db session available
        if db:
            try:
                run_rec = EvaluationRun(
                    run_name=f"bench_{intel_key}_{int(time.time())}",
                    intelligence_id=intel_key,
                    status="completed",
                    total_cases=len(test_cases),
                    passed_cases=passed_count,
                    avg_score=avg_score,
                    avg_latency_ms=avg_latency,
                    total_cost_usd=total_cost
                )
                db.add(run_rec)
                await db.flush()

                for r in results:
                    res_rec = EvaluationResult(
                        run_id=run_rec.id,
                        test_case_id=r["test_case_id"],
                        prompt=r["prompt"],
                        expected_behavior=str(r.get("matched_keywords", [])),
                        actual_output=r.get("error", "Passed"),
                        score=r.get("score", 0.0),
                        is_pass=r.get("is_pass", False),
                        latency_ms=r.get("latency_ms", 0),
                        cost_usd=r.get("cost_usd", 0.0)
                    )
                    db.add(res_rec)
                await db.commit()
            except Exception as e:
                logger.warning(f"Could not persist EvaluationRun: {e}")

        return summary

