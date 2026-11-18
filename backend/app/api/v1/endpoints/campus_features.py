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



# =========================================================================
# CAMPUS BLOCK DISCOVERY & PEDESTRIAN NAVIGATION ENDPOINTS
# =========================================================================
from app.services.campus_place_directory import CampusPlaceDirectory
from app.services.campus_routing_engine import CampusRoutingEngine, CAMPUS_GRAPH_NODES


@router.get("/navigation/places")
async def get_campus_navigation_places(
    q: Optional[str] = Query(None, description="Search keyword for building or block"),
    category: Optional[str] = Query(None, description="Category filter (Academic, Hostel, etc.)")
):
    """
    Returns verified and reconciled campus places covering all 55 site-plan locations,
    university administrative blocks, student hostels, and facilities.
    """
    if q:
        return CampusPlaceDirectory.search_places(query=q, category=category)
    if category:
        return CampusPlaceDirectory.get_by_category(category)
    return CampusPlaceDirectory.get_all_places()


@router.get("/navigation/route")
async def get_campus_pedestrian_route(
    origin: str = Query(..., description="Starting block number, landmark, or graph node ID (e.g. '32', 'ENT_BLK_32', 'Main Gate')"),
    destination: str = Query(..., description="Destination block number, landmark, or graph node ID (e.g. '14', 'ENT_BLK_14', 'Hospital')"),
    wheelchair_only: bool = Query(False, description="Filter for 100% step-free accessible routes")
):
    """
    Calculates pedestrian shortest-path route along verified campus walkways using Dijkstra algorithm.
    Strictly distinguishes walking distance from straight-line distance.
    Rejects turn-by-turn route generation for unverified/off-graph points.
    """
    orig_node = CampusRoutingEngine.find_node_by_name_or_keyword(origin) or CampusRoutingEngine.find_node_by_block(origin) or origin
    dest_node = CampusRoutingEngine.find_node_by_name_or_keyword(destination) or CampusRoutingEngine.find_node_by_block(destination) or destination

    return CampusRoutingEngine.calculate_route(
        origin_id=orig_node,
        destination_id=dest_node,
        wheelchair_only=wheelchair_only
    )


@router.get("/navigation/directory")
async def get_campus_block_directory(
    category: str = Query("all", description="Directory category (Academic, Hostel, Administration, Dining, etc.)")
):
    """
    Returns structured directory cards for category searches.
    """
    places = CampusPlaceDirectory.get_by_category(category)
    return {
        "category": category,
        "total_places": len(places),
        "places": places,
        "provenance_note": "Reconciled from official university directory and 01-55 site plan."
    }


@router.get("/navigation/discrepancies")
async def get_campus_map_discrepancies():
    """
    Returns audit list of verified naming/numbering discrepancies between
    the historical site-plan legend (01-55) and current university records.
    """
    return {
        "total_discrepancies": len(CampusPlaceDirectory.get_discrepancies()),
        "discrepancies": CampusPlaceDirectory.get_discrepancies()
    }


@router.get("/navigation/scholix")
async def get_scholix_3d_walkthrough():
    """
    Provides configuration and embeddability check for the Scholix 3D Walkthrough integration.
    URL: https://scholix.app/lpu/campus/map
    """
    return {
        "embed_url": "https://scholix.app/lpu/campus/map",
        "launch_url": "https://scholix.app/lpu/campus/map",
        "allows_iframe": True,
        "requires_cross_origin_isolation": False,
        "experience_type": "SUPPLEMENTARY_3D_WALKTHROUGH",
        "notice": "Supplementary 3D visual exploration. Map not to scale. For turn-by-turn routing, use verified pedestrian walkway graph."
    }
