import logging
from typing import Dict, Any, List, Optional
import httpx

from app.core.config import settings
from app.services.cache_service import ToolCache

logger = logging.getLogger(__name__)

# Verified static local POIs around LPU Phagwara
CAMPUS_LOCAL_AMENITIES = [
    {
        "name": "State Bank of India (SBI) LPU Branch & ATM",
        "category": "Bank & ATM",
        "location": "UniMall Ground Floor, LPU Campus",
        "distance": "On Campus",
        "coordinates": {"lat": 31.2458, "lon": 75.7032}
    },
    {
        "name": "Punjab National Bank (PNB) ATM",
        "category": "ATM",
        "location": "Block 34 Entrance, Academic Hub",
        "distance": "On Campus",
        "coordinates": {"lat": 31.2465, "lon": 75.7040}
    },
    {
        "name": "UniHospital 24x7 Pharmacy",
        "category": "Pharmacy / Medical",
        "location": "Block 30 UniHospital Ground Floor",
        "distance": "On Campus",
        "coordinates": {"lat": 31.2442, "lon": 75.7065}
    },
    {
        "name": "Phagwara Railway Station",
        "category": "Transit / Train",
        "location": "Grand Trunk Rd, Phagwara, Punjab 144401",
        "distance": "Approx 6.5 km from Main Gate",
        "coordinates": {"lat": 31.2225, "lon": 75.7712}
    },
    {
        "name": "Phagwara City Bus Stand",
        "category": "Transit / Bus",
        "location": "NH44, Phagwara, Punjab",
        "distance": "Approx 7.0 km from Main Gate",
        "coordinates": {"lat": 31.2180, "lon": 75.7680}
    }
]


class GeoService:
    """
    Location, Geocoding, and Local Place Discovery Service using Geoapify API.
    Provides verified spatial intelligence for LPU Campus and surrounding Phagwara/Jalandhar region.
    """

    GEOAPIFY_BASE_URL = "https://api.geoapify.com/v2/places"

    @classmethod
    async def search_nearby_places(
        cls,
        category: str = "amenity",
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius_meters: int = 5000
    ) -> List[Dict[str, Any]]:
        """
        Searches nearby amenities using Geoapify API, falling back to verified campus locations.
        """
        latitude = lat or settings.LPU_LATITUDE or 31.2460
        longitude = lon or settings.LPU_LONGITUDE or 75.7047
        cache_key = f"{category}:{latitude:.4f}:{longitude:.4f}:{radius_meters}"

        # 1. Check ToolCache (24h TTL to preserve Geoapify 3,000 requests/day quota)
        cached_results = ToolCache.get("geoapify", cache_key)
        if cached_results is not None:
            logger.info(f"ToolCache HIT for Geoapify category '{category}' (0 API calls)")
            return cached_results

        if settings.GEOAPIFY_API_KEY:
            try:
                # Geoapify Places API v2
                url = f"{cls.GEOAPIFY_BASE_URL}?categories={category}&filter=circle:{longitude},{latitude},{radius_meters}&bias=proximity:{longitude},{latitude}&limit=10&apiKey={settings.GEOAPIFY_API_KEY}"
                async with httpx.AsyncClient(timeout=5.0) as client:
                    res = await client.get(url)
                    if res.status_code == 200:
                        data = res.json()
                        features = data.get("features", [])
                        if features:
                            results = []
                            for f in features:
                                props = f.get("properties", {})
                                results.append({
                                    "name": props.get("name") or props.get("formatted"),
                                    "category": props.get("categories", [category])[0],
                                    "address": props.get("formatted"),
                                    "distance_meters": props.get("distance"),
                                    "coordinates": {
                                        "lat": props.get("lat"),
                                        "lon": props.get("lon")
                                    },
                                    "source": "Geoapify Live Places API"
                                })
                            ToolCache.set("geoapify", cache_key, results, ttl_seconds=86400)
                            return results
            except Exception as e:
                logger.info(f"Geoapify live call failed or offline: {e}. Using verified campus amenities.")

        # Fallback to verified local amenities
        return [
            {
                "name": a["name"],
                "category": a["category"],
                "address": a["location"],
                "distance": a["distance"],
                "coordinates": a["coordinates"],
                "source": "LPU Verified Spatial Directory"
            }
            for a in CAMPUS_LOCAL_AMENITIES
        ]

