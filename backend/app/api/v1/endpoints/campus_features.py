import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, UploadFile, File, Form, HTTPException, Response
from pydantic import BaseModel

from app.services.weather_service import WeatherService
from app.services.voice_service import VoiceService
from app.services.opportunities_service import OpportunitiesService
from app.services.geo_service import GeoService

logger = logging.getLogger(__name__)

router = APIRouter()


class TextToSpeechRequest(BaseModel):
    text: str
    voice_id: Optional[str] = None


@router.get("/weather")
async def get_campus_weather(
    lat: Optional[float] = Query(None, description="Latitude (defaults to LPU Main Campus 31.2460)"),
    lon: Optional[float] = Query(None, description="Longitude (defaults to LPU Main Campus 75.7047)")
):
    """
    Returns real-time weather and campus activity advice for Lovely Professional University.
    Powered by Open-Meteo API.
    """
    return await WeatherService.get_current_weather(lat=lat, lon=lon)


@router.get("/opportunities")
async def get_student_opportunities(
    q: Optional[str] = Query(None, description="Search keyword for internships or roles"),
    type: Optional[str] = Query(None, description="Role type (e.g. Internship, Full-Time)")
):
    """
    Returns student internships, startup roles, and technical project opportunities.
    Integrated with Startup.Jobs API and EDU-Revolution benefit mappings.
    """
    return await OpportunitiesService.get_opportunities(query=q, role_type=type)


@router.get("/amenities")
async def get_campus_amenities(
    category: str = Query("amenity", description="Amenity category: bank, pharmacy, transport, atm"),
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    radius: int = Query(5000, description="Search radius in meters")
):
    """
    Searches spatial amenities and transit hubs around LPU Phagwara campus.
    Powered by Geoapify API.
    """
    return await GeoService.search_nearby_places(
        category=category, lat=lat, lon=lon, radius_meters=radius
    )


@router.post("/voice/transcribe")
async def transcribe_voice_query(
    file: UploadFile = File(...)
):
    """
    Transcribes student voice audio using Deepgram Nova-2 STT.
    """
    content_bytes = await file.read()
    content_type = file.content_type or "audio/wav"
    result = await VoiceService.transcribe_audio(audio_bytes=content_bytes, content_type=content_type)
    if result.get("status") == "error" and not result.get("transcript"):
        raise HTTPException(status_code=502, detail=result.get("error", "Transcription failed"))
    return result


@router.post("/voice/synthesize")
async def synthesize_speech_response(
    req: TextToSpeechRequest
):
    """
    Synthesizes speech audio using ElevenLabs TTS.
    Returns audio/mpeg stream.
    """
    result = await VoiceService.synthesize_speech(text=req.text, voice_id=req.voice_id)
    if result.get("status") == "error" or not result.get("audio_bytes"):
        raise HTTPException(status_code=502, detail=result.get("error", "Speech synthesis failed"))
    return Response(
        content=result["audio_bytes"],
        media_type=result.get("content_type", "audio/mpeg")
    )

