"""
Acceptance Test Suite for Campus Block Discovery & Pedestrian Navigation (Section L).
Covers all 14 Acceptance Criteria:
1. Search Block 32 by number.
2. Search Block 32 by alternate name.
3. Find all hostel blocks.
4. Find Academic Block 1.
5. Search for Chancellor Office.
6. Navigate from Block 32 Entrance to Block 14 Entrance via pedestrian graph.
7. Reject route generation when path graph is unavailable.
8. Distinguish straight-line distance from pedestrian walking distance.
9. Detect duplicate block numbers and conflicting names.
10. Handle unverified and outdated campus records.
11. Handle GPS denial (fallback to landmark or map-tap).
12. Render map and location cards on mobile.
13. Preserve conversation context during map interactions.
14. Prevent invented room numbers and facilities.
"""

import pytest
import math
from starlette.testclient import TestClient
from app.main import app
from app.services.campus_place_directory import CampusPlaceDirectory, MASTER_CAMPUS_PLACES
from app.services.campus_routing_engine import CampusRoutingEngine, haversine_distance_meters, CAMPUS_GRAPH_NODES
from app.services.campus_map_service import CampusMapService
from app.schemas.campus_navigation import CampusPlaceCard, CampusRouteCard, CampusBlockDirectoryCard


@pytest.fixture
def client():
    return TestClient(app)


# -------------------------------------------------------------------------
# Test 1: Search Block 32 by number
# -------------------------------------------------------------------------
def test_01_search_block_32_by_number():
    place = CampusPlaceDirectory.get_by_block_number("32")
    assert place is not None, "Block 32 must exist in master directory"
    assert place["block_number"] == "32"
    assert "Computer Science" in place["official_name"] or "Administrative" in place["official_name"]
    assert place["verification_status"] == "RECONCILED_UNIVERSITY_RECORD"
    assert place["category"] == "Academic"


# -------------------------------------------------------------------------
# Test 2: Search Block 32 by alternate name
# -------------------------------------------------------------------------
def test_02_search_block_32_by_alternate_name():
    # Search by 'Central Administrative Block'
    results_admin = CampusPlaceDirectory.search_places("Central Administrative Block")
    assert len(results_admin) > 0
    assert results_admin[0]["block_number"] == "32"

    # Search by 'School of Computer Science & Engineering'
    results_cse = CampusPlaceDirectory.search_places("School of Computer Science & Engineering")
    assert len(results_cse) > 0
    assert results_cse[0]["block_number"] == "32"


# -------------------------------------------------------------------------
# Test 3: Find all hostel blocks
# -------------------------------------------------------------------------
def test_03_find_all_hostel_blocks():
    hostels = CampusPlaceDirectory.get_by_category("Hostel")
    assert len(hostels) >= 15, "Must find all boys and girls hostels (BH 1-10 and GH 1-6)"

    # Verify presence of Girls Hostels
    gh_names = [h["official_name"] for h in hostels if "Girls" in h["official_name"]]
    assert len(gh_names) >= 4, "Must contain multiple Girls Hostel blocks"

    # Verify presence of Boys Hostels
    bh_names = [h["official_name"] for h in hostels if "Boys" in h["official_name"]]
    assert len(bh_names) >= 6, "Must contain multiple Boys Hostel blocks"


# -------------------------------------------------------------------------
# Test 4: Find Academic Block 1
# -------------------------------------------------------------------------
def test_04_find_academic_block_1():
    # Direct block number lookup for Block 53
    place = CampusPlaceDirectory.get_by_block_number("53")
    assert place is not None
    assert place["block_number"] == "53"
    assert "Academic Block 1" in place["official_name"]

    # Search query lookup
    results = CampusPlaceDirectory.search_places("Academic Block 1")
    assert len(results) > 0
    assert results[0]["block_number"] == "53"


# -------------------------------------------------------------------------
# Test 5: Search for Chancellor Office
# -------------------------------------------------------------------------
def test_05_search_for_chancellor_office():
    results = CampusPlaceDirectory.search_places("Chancellor Office")
    assert len(results) > 0
    top_match = results[0]
    assert top_match["block_number"] == "30"
    assert "Chancellor" in top_match["official_name"]
    assert top_match["category"] == "Administration"
    assert top_match["verification_status"] == "RECONCILED_UNIVERSITY_RECORD"


# -------------------------------------------------------------------------
# Test 6: Navigate from Block 32 Entrance to Block 14 Entrance via pedestrian graph
# -------------------------------------------------------------------------
def test_06_navigate_block_32_to_block_14():
    route = CampusRoutingEngine.calculate_route("ENT_BLK_32", "ENT_BLK_14")
    assert route["turn_by_turn_available"] is True
    assert route["is_pedestrian_path_verified"] is True
    assert route["walking_distance_meters"] > 0
    assert route["walking_distance_meters"] >= 200, "Walkway distance between Block 32 and 14 should be ~250-270m"
    assert route["estimated_duration_minutes"] is not None
    assert route["estimated_duration_minutes"] >= 3, "Walking duration should be ~3-4 minutes"
    assert len(route["turn_by_turn_steps"]) >= 3, "Route must provide multi-step navigation guidance"
    assert "Block 14" in route["destination_name"]


# -------------------------------------------------------------------------
# Test 7: Reject route generation when path graph is unavailable
# -------------------------------------------------------------------------
def test_07_reject_route_generation_when_graph_unavailable():
    # Routing to an unverified off-graph node
    route = CampusRoutingEngine.calculate_route("ENT_BLK_32", "NON_EXISTENT_BUILDING_99")
    assert route["turn_by_turn_available"] is False
    assert route["is_pedestrian_path_verified"] is False
    assert route["walking_distance_meters"] is None
    assert route["estimated_duration_minutes"] is None
    assert "not available" in route["data_limitations"].lower()


# -------------------------------------------------------------------------
# Test 8: Distinguish straight-line distance from pedestrian walking distance
# -------------------------------------------------------------------------
def test_08_distinguish_straight_line_from_walking_distance():
    route = CampusRoutingEngine.calculate_route("ENT_BLK_32", "ENT_BLK_14")
    walking_dist = route["walking_distance_meters"]
    straight_line_dist = route["straight_line_distance_meters"]

    assert walking_dist is not None
    assert straight_line_dist is not None
    # Crucial acceptance rule: Walking distance along paved walkways must be strictly greater than Euclidean air distance
    assert walking_dist > straight_line_dist, (
        f"Walking distance ({walking_dist}m) must strictly exceed straight-line air distance ({straight_line_dist}m)"
    )


# -------------------------------------------------------------------------
# Test 9: Detect duplicate block numbers and conflicting names
# -------------------------------------------------------------------------
def test_09_detect_duplicate_and_conflicting_names():
    discrepancies = CampusPlaceDirectory.get_discrepancies()
    assert len(discrepancies) > 0, "Must detect discrepancies between site plan and current university records"

    discrepancy_pids = {d["place_id"] for d in discrepancies}

    # Verify Block 19 (Auditorium vs School of Films)
    assert "BLK-19" in discrepancy_pids
    blk19 = CampusPlaceDirectory.get_by_place_id("BLK-19")
    assert "Auditorium" in blk19["legend_name"]
    assert "Films" in blk19["discrepancy_note"] or "Films" in blk19["official_name"]

    # Verify Block 21 (Girls Hostel 5 vs School of Law)
    assert "BLK-21" in discrepancy_pids
    blk21 = CampusPlaceDirectory.get_by_place_id("BLK-21")
    assert "Girls Hostel 5" in blk21["legend_name"]
    assert "Law" in blk21["discrepancy_note"] or "Law" in blk21["official_name"]

    # Verify Boys Hostel sequence discrepancy
    assert "BLK-44" in discrepancy_pids or "BLK-45" in discrepancy_pids


# -------------------------------------------------------------------------
# Test 10: Handle unverified and outdated campus records
# -------------------------------------------------------------------------
def test_10_handle_unverified_and_outdated_records():
    # Site plan legend items not yet field-surveyed must be flagged pending verification
    unverified_places = [
        p for p in MASTER_CAMPUS_PLACES
        if p["verification_status"] == "USER_SUPPLIED_MAP_PENDING_VERIFICATION"
    ]
    assert len(unverified_places) > 0, "Initial site plan legend entries must retain pending verification status"

    for uv in unverified_places[:5]:
        assert uv["coordinate_verification_status"] == "APPROXIMATE_DIAGRAM_PIN"
        assert uv["coordinate_source"] == "DIAGRAM_IMAGE_ESTIMATE"


# -------------------------------------------------------------------------
# Test 11: Handle GPS denial (fallback to landmark or map-tap)
# -------------------------------------------------------------------------
def test_11_handle_gps_denial_fallback():
    # User denies GPS (lat/lon = None), but provides a landmark or origin name
    route_card = CampusMapService.resolve_campus_navigation(
        query="Take me from Block 32 to Block 14",
        user_lat=None,
        user_lon=None,
        landmark="Block 32"
    )
    assert route_card is not None
    assert route_card.turn_by_turn_available is True
    assert route_card.walking_distance_meters is not None
    assert "Block 32" in route_card.origin_name
    assert "Block 14" in route_card.destination_name


# -------------------------------------------------------------------------
# Test 12: Render map and location cards on mobile
# -------------------------------------------------------------------------
def test_12_render_cards_mobile_payload_compatibility():
    place = CampusPlaceDirectory.get_by_block_number("32")
    place_card = CampusMapService.build_place_card(place)
    data = place_card.model_dump()

    # Verify mobile payload fields
    assert "place_id" in data
    assert "name" in data
    assert "category" in data
    assert "accessibility_information" in data
    assert "navigation_actions" in data
    assert len(data["navigation_actions"]) >= 2

    # Verify route card serialization
    route = CampusRoutingEngine.calculate_route("ENT_BLK_32", "ENT_BLK_14")
    assert isinstance(route["route_coordinates"], list)
    for coord in route["route_coordinates"]:
        assert len(coord) == 2  # [lat, lon]


# -------------------------------------------------------------------------
# Test 13: Preserve conversation context during map interactions
# -------------------------------------------------------------------------
def test_13_preserve_conversation_context(client):
    # Simulate chat query asking for map information
    req_body = {
        "message": "Where is Block 32?",
        "session_token": "sess_test_navigation_context_001",
        "category_slug": "campus_spatial",
        "agent_id": "themis"
    }
    res = client.post("/api/v1/chat", json=req_body)
    assert res.status_code == 200
    res_data = res.json()

    assert "conversation_id" in res_data
    conv_id = res_data["conversation_id"]

    # Verify campus_place_card is returned
    assert res_data.get("campus_place_card") is not None
    assert res_data["campus_place_card"]["block_number"] == "32"

    # Subsequent turn in same conversation preserves thread
    req_body_2 = {
        "message": "How do I reach Block 14 from here?",
        "session_token": "sess_test_navigation_context_001",
        "conversation_id": conv_id,
        "landmark": "Block 32"
    }
    res2 = client.post("/api/v1/chat", json=req_body_2)
    assert res2.status_code == 200
    res2_data = res2.json()
    assert res2_data["conversation_id"] == conv_id


# -------------------------------------------------------------------------
# Test 14: Prevent invented room numbers and facilities
# -------------------------------------------------------------------------
def test_14_prevent_invented_room_numbers_and_facilities():
    # Buildings without verified room records must have empty rooms list
    for p in MASTER_CAMPUS_PLACES:
        if p["block_number"] in ["01", "04", "06", "10", "18", "25", "33", "53"]:
            # These blocks have no officially verified room list in public seed
            assert p["rooms"] == [], f"Block {p['block_number']} must not fabricate fictitious room numbers"

    # Block 27 must only have officially verified Room 102
    blk27 = CampusPlaceDirectory.get_by_block_number("27")
    assert len(blk27["rooms"]) == 1
    assert blk27["rooms"][0]["room_number"] == "Room 102"
    assert blk27["rooms"][0]["verification_status"] == "OFFICIAL_CURRENT_VERIFIED"
