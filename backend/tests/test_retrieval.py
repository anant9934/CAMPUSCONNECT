import pytest
from app.core.database import AsyncSessionLocal
from app.services.rag.hybrid_search import hybrid_search_engine
from app.services.rag.confidence import ConfidenceLevel
from app.services.seed_service import seed_database


@pytest.mark.asyncio
async def test_retrieval_exact_match():
    async with AsyncSessionLocal() as session:
        await seed_database(session)
        await hybrid_search_engine.build_index(session)

        query = "How do I download my examination date sheet at LPU?"
        res = await hybrid_search_engine.search(query, session)

        assert len(res["candidates"]) > 0
        assert res["confidence"].level in (ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM)
        assert res["confidence"].should_generate_ai is True
        assert "date sheet" in res["candidates"][0]["canonical_question"].lower()


@pytest.mark.asyncio
async def test_retrieval_paraphrase():
    async with AsyncSessionLocal() as session:
        # Paraphrase that uses different wording
        query = "Where can residential students apply for night leave pass?"
        res = await hybrid_search_engine.search(query, session)

        assert len(res["candidates"]) > 0
        top = res["candidates"][0]
        assert "hostel" in top["canonical_question"].lower() or "night leave" in top["canonical_question"].lower()
        assert res["confidence"].score >= 0.45


@pytest.mark.asyncio
async def test_retrieval_lpu_keywords():
    async with AsyncSessionLocal() as session:
        # Acronym & campus landmark queries
        query = "Block 34"
        res = await hybrid_search_engine.search(query, session)
        assert len(res["candidates"]) > 0
        assert any("block 34" in c["answer"].lower() or "examination" in c["canonical_question"].lower() for c in res["candidates"])

        query_hospital = "UniHospital emergency contact"
        res_hosp = await hybrid_search_engine.search(query_hospital, session)
        assert len(res_hosp["candidates"]) > 0
        assert "unihospital" in res_hosp["candidates"][0]["canonical_question"].lower() or "medical" in res_hosp["candidates"][0]["canonical_question"].lower()


@pytest.mark.asyncio
async def test_retrieval_low_confidence_and_no_match():
    async with AsyncSessionLocal() as session:
        # Query having zero connection to LPU campus
        query = "Quantum warp drive navigation equations for starships"
        res = await hybrid_search_engine.search(query, session)


        # Either no candidates or confidence score is below threshold
        assert res["confidence"].should_generate_ai is False
        assert res["confidence"].level in (ConfidenceLevel.LOW, ConfidenceLevel.NONE)

