"""
Campus Pedestrian Navigation and Geospatial Routing Engine for Lovely Professional University.
Implements a graph-based pedestrian walkway network using Dijkstra shortest path algorithm,
verified building entrance coordinates, walkway junctions, turn-by-turn instructions,
accessibility routing, and strict fallback when pedestrian graph data is unavailable.
"""

import math
import heapq
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Verification status enums
VERIFIED_PEDESTRIAN_PATH = "VERIFIED_PEDESTRIAN_PATH"
ESTIMATED_STRAIGHT_LINE = "ESTIMATED_STRAIGHT_LINE"

# Average student walking speed: 1.2 meters per second (approx 72 meters per minute / 4.3 km/h)
AVERAGE_WALKING_SPEED_MPS = 1.2


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
    """
    Calculates great-circle straight-line distance between two coordinates in meters.
    Strictly used as straight-line baseline, never as walking distance.
    """
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return int(round(R * c))


# Verified Graph Nodes: Building Entrances, Campus Gates, and Walkway Junctions
CAMPUS_GRAPH_NODES: Dict[str, Dict[str, Any]] = {
    # Building Entrances
    "ENT_BLK_32": {
        "name": "Block 32 Main Entrance (School of CSE / Admin)",
        "block_number": "32",
        "node_type": "entrance",
        "lat": 31.2548,
        "lon": 75.7032,
        "wheelchair_accessible": True,
        "has_verified_entrance": True
    },
    "ENT_BLK_14": {
        "name": "Block 14 Main Entrance (Central Library / Business)",
        "block_number": "14",
        "node_type": "entrance",
        "lat": 31.2540,
        "lon": 75.7052,
        "wheelchair_accessible": True,
        "has_verified_entrance": True
    },
    "ENT_BLK_15": {
        "name": "Block 15 Main Entrance (Lovely Mall / UniMall)",
        "block_number": "15",
        "node_type": "entrance",
        "lat": 31.2535,
        "lon": 75.7035,
        "wheelchair_accessible": True,
        "has_verified_entrance": True
    },
    "ENT_BLK_08": {
        "name": "Block 08 Main Entrance (UniHospital Emergency)",
        "block_number": "08",
        "node_type": "entrance",
        "lat": 31.2505,
        "lon": 75.7028,
        "wheelchair_accessible": True,
        "has_verified_entrance": True
    },
    "ENT_BLK_30": {
        "name": "Block 30 Entrance (Chancellor Office)",
        "block_number": "30",
        "node_type": "entrance",
        "lat": 31.2546,
        "lon": 75.7028,
        "wheelchair_accessible": True,
        "has_verified_entrance": True
    },
    "ENT_BLK_34": {
        "name": "Block 34 Entrance (Examination Wing Helpdesk)",
        "block_number": "34",
        "node_type": "entrance",
        "lat": 31.2552,
        "lon": 75.7038,
        "wheelchair_accessible": True,
        "has_verified_entrance": True
    },
    "ENT_BLK_27": {
        "name": "Block 27 Entrance (EDU-Revolution Cell Room 102)",
        "block_number": "27",
        "node_type": "entrance",
        "lat": 31.2536,
        "lon": 75.7039,
        "wheelchair_accessible": True,
        "has_verified_entrance": True
    },
    "ENT_BLK_19": {
        "name": "Block 19 Entrance (School of Films / Auditorium)",
        "block_number": "19",
        "node_type": "entrance",
        "lat": 31.2548,
        "lon": 75.7045,
        "wheelchair_accessible": True,
        "has_verified_entrance": True
    },
    "ENT_BLK_20": {
        "name": "Block 20 Entrance (Lovely School of Business)",
        "block_number": "20",
        "node_type": "entrance",
        "lat": 31.2552,
        "lon": 75.7050,
        "wheelchair_accessible": True,
        "has_verified_entrance": True
    },
    "ENT_BLK_21": {
        "name": "Block 21 Entrance (School of Law)",
        "block_number": "21",
        "node_type": "entrance",
        "lat": 31.2555,
        "lon": 75.7052,
        "wheelchair_accessible": True,
        "has_verified_entrance": True
    },
    "ENT_BLK_53": {
        "name": "Block 53 Entrance (Academic Block 1 - Agriculture)",
        "block_number": "53",
        "node_type": "entrance",
        "lat": 31.2588,
        "lon": 75.7020,
        "wheelchair_accessible": True,
        "has_verified_entrance": True
    },
    "ENT_BLK_01": {
        "name": "Block 01 Entrance (LIM)",
        "block_number": "01",
        "node_type": "entrance",
        "lat": 31.2475,
        "lon": 75.7038,
        "wheelchair_accessible": True,
        "has_verified_entrance": True
    },
    "ENT_BLK_02": {
        "name": "Block 02 Entrance (Campus Cafe)",
        "block_number": "02",
        "node_type": "entrance",
        "lat": 31.2482,
        "lon": 75.7036,
        "wheelchair_accessible": True,
        "has_verified_entrance": True
    },
    "ENT_BOYS_HOSTEL_4": {
        "name": "Boys Hostel 4 Main Security Gate",
        "block_number": "46",
        "node_type": "entrance",
        "lat": 31.2578,
        "lon": 75.7048,
        "wheelchair_accessible": True,
        "has_verified_entrance": True
    },
    "ENT_GIRLS_HOSTEL_1": {
        "name": "Girls Hostel 1 Entrance Gate",
        "block_number": "09",
        "node_type": "entrance",
        "lat": 31.2515,
        "lon": 75.7046,
        "wheelchair_accessible": True,
        "has_verified_entrance": True
    },
    "ENT_STADIUM": {
        "name": "Shanti Devi Mittal Indoor Stadium Entrance",
        "block_number": None,
        "node_type": "entrance",
        "lat": 31.2562,
        "lon": 75.7060,
        "wheelchair_accessible": True,
        "has_verified_entrance": True
    },
    "ENT_UNIPOLIS": {
        "name": "Baldev Raj Mittal Unipolis Concourse",
        "block_number": None,
        "node_type": "entrance",
        "lat": 31.2550,
        "lon": 75.7045,
        "wheelchair_accessible": True,
        "has_verified_entrance": True
    },
    # Campus Gates
    "GATE_MAIN": {
        "name": "Main Campus Gate (NH1 Grand Trunk Road)",
        "block_number": None,
        "node_type": "gate",
        "lat": 31.2462,
        "lon": 75.7042,
        "wheelchair_accessible": True,
        "has_verified_entrance": True
    },
    "GATE_UNIMALL": {
        "name": "UniMall Pedestrian Boulevard Gate",
        "block_number": None,
        "node_type": "gate",
        "lat": 31.2530,
        "lon": 75.7038,
        "wheelchair_accessible": True,
        "has_verified_entrance": True
    },
    "GATE_HOSPITAL": {
        "name": "UniHospital Emergency Access Gate",
        "block_number": None,
        "node_type": "gate",
        "lat": 31.2500,
        "lon": 75.7025,
        "wheelchair_accessible": True,
        "has_verified_entrance": True
    },
    "GATE_BOYS_HOSTEL": {
        "name": "North Boys Hostel Security Gate",
        "block_number": None,
        "node_type": "gate",
        "lat": 31.2568,
        "lon": 75.7042,
        "wheelchair_accessible": True,
        "has_verified_entrance": True
    },
    # Walkway Junctions & Intersections
    "JUNC_MAIN_GATE_PLAZA": {
        "name": "Main Gate Entry Plaza & Bus Bay",
        "block_number": None,
        "node_type": "junction",
        "lat": 31.2468,
        "lon": 75.7040,
        "wheelchair_accessible": True,
        "has_verified_entrance": False
    },
    "JUNC_SOUTH_AVENUE": {
        "name": "South Promenade Junction (near LIM & Cafe)",
        "block_number": None,
        "node_type": "junction",
        "lat": 31.2485,
        "lon": 75.7038,
        "wheelchair_accessible": True,
        "has_verified_entrance": False
    },
    "JUNC_HOSPITAL_CROSS": {
        "name": "Hospital Boulevard & Pharmacy Crossroads",
        "block_number": None,
        "node_type": "junction",
        "lat": 31.2505,
        "lon": 75.7032,
        "wheelchair_accessible": True,
        "has_verified_entrance": False
    },
    "JUNC_GIRLS_HOSTEL_CORRIDOR": {
        "name": "Girls Hostel Avenue & Block 13 Junction",
        "block_number": None,
        "node_type": "junction",
        "lat": 31.2518,
        "lon": 75.7042,
        "wheelchair_accessible": True,
        "has_verified_entrance": False
    },
    "JUNC_MALL_ESPLANADE": {
        "name": "UniMall Esplanade & Boulevard Crossing",
        "block_number": None,
        "node_type": "junction",
        "lat": 31.2532,
        "lon": 75.7035,
        "wheelchair_accessible": True,
        "has_verified_entrance": False
    },
    "JUNC_CENTRAL_SPINE_SOUTH": {
        "name": "Central Spine South (between Block 14, 15, and 27)",
        "block_number": None,
        "node_type": "junction",
        "lat": 31.2538,
        "lon": 75.7040,
        "wheelchair_accessible": True,
        "has_verified_entrance": False
    },
    "JUNC_CENTRAL_PROMENADE": {
        "name": "Central Academic Promenade Junction (near Unipolis)",
        "block_number": None,
        "node_type": "junction",
        "lat": 31.2545,
        "lon": 75.7042,
        "wheelchair_accessible": True,
        "has_verified_entrance": False
    },
    "JUNC_ENGG_PLAZA": {
        "name": "Engineering Plaza Crossroads (connecting Block 25-29 & 32-35)",
        "block_number": None,
        "node_type": "junction",
        "lat": 31.2546,
        "lon": 75.7034,
        "wheelchair_accessible": True,
        "has_verified_entrance": False
    },
    "JUNC_ADMIN_COURTYARD": {
        "name": "Administrative Courtyard (Block 30, 31, and 32)",
        "block_number": None,
        "node_type": "junction",
        "lat": 31.2547,
        "lon": 75.7029,
        "wheelchair_accessible": True,
        "has_verified_entrance": False
    },
    "JUNC_EXAM_AVENUE": {
        "name": "Avenue between Block 33 and Examination Block 34",
        "block_number": None,
        "node_type": "junction",
        "lat": 31.2551,
        "lon": 75.7037,
        "wheelchair_accessible": True,
        "has_verified_entrance": False
    },
    "JUNC_NORTH_SPINE": {
        "name": "North Spine Junction towards Hostels & Stores",
        "block_number": None,
        "node_type": "junction",
        "lat": 31.2562,
        "lon": 75.7035,
        "wheelchair_accessible": True,
        "has_verified_entrance": False
    },
    "JUNC_NORTH_ACADEMIC": {
        "name": "North Academic Crossroads (Block 53-55 & Gurudwara)",
        "block_number": None,
        "node_type": "junction",
        "lat": 31.2582,
        "lon": 75.7022,
        "wheelchair_accessible": True,
        "has_verified_entrance": False
    },
    "JUNC_BOYS_HOSTEL_QUAD": {
        "name": "Boys Hostel Central Quadrangle",
        "block_number": None,
        "node_type": "junction",
        "lat": 31.2575,
        "lon": 75.7045,
        "wheelchair_accessible": True,
        "has_verified_entrance": False
    }
}

# Verified Walkway Edges: Distance in real walking meters, surface, wheelchair accessibility
CAMPUS_GRAPH_EDGES: List[Dict[str, Any]] = [
    # Main Gate to South Promenade
    {"u": "GATE_MAIN", "v": "JUNC_MAIN_GATE_PLAZA", "meters": 70, "wheelchair": True, "surface": "paved_concrete", "instr": "Head north through Main Gate security plaza"},
    {"u": "JUNC_MAIN_GATE_PLAZA", "v": "ENT_BLK_01", "meters": 80, "wheelchair": True, "surface": "paved_granite", "instr": "Follow the western paved path to Block 01 LIM entrance"},
    {"u": "JUNC_MAIN_GATE_PLAZA", "v": "JUNC_SOUTH_AVENUE", "meters": 180, "wheelchair": True, "surface": "interlocking_pavers", "instr": "Walk north along South Boulevard past LIM"},
    {"u": "JUNC_SOUTH_AVENUE", "v": "ENT_BLK_02", "meters": 35, "wheelchair": True, "surface": "paved_concrete", "instr": "Turn slightly left to Campus Cafe entrance"},

    # South Promenade to Hospital Crossroads
    {"u": "JUNC_SOUTH_AVENUE", "v": "JUNC_HOSPITAL_CROSS", "meters": 220, "wheelchair": True, "surface": "asphalt_walkway", "instr": "Continue north along South Boulevard towards Hospital zone"},
    {"u": "JUNC_HOSPITAL_CROSS", "v": "GATE_HOSPITAL", "meters": 65, "wheelchair": True, "surface": "asphalt_walkway", "instr": "Turn left towards Hospital Emergency Access Gate"},
    {"u": "GATE_HOSPITAL", "v": "ENT_BLK_08", "meters": 45, "wheelchair": True, "surface": "smooth_stretcher_ramp", "instr": "Follow the continuous stretcher ramp into UniHospital Emergency Reception"},
    {"u": "JUNC_HOSPITAL_CROSS", "v": "ENT_BLK_08", "meters": 75, "wheelchair": True, "surface": "smooth_stretcher_ramp", "instr": "Follow the dedicated hospital pedestrian walkway into UniHospital OPD lobby"},

    # Hospital Crossroads to Girls Hostel / UniMall
    {"u": "JUNC_HOSPITAL_CROSS", "v": "JUNC_GIRLS_HOSTEL_CORRIDOR", "meters": 150, "wheelchair": True, "surface": "interlocking_pavers", "instr": "Walk north-east along the tree-lined corridor"},
    {"u": "JUNC_GIRLS_HOSTEL_CORRIDOR", "v": "ENT_GIRLS_HOSTEL_1", "meters": 55, "wheelchair": True, "surface": "paved_walkway", "instr": "Enter the gated Girls Hostel 1 quadrangle"},
    {"u": "JUNC_GIRLS_HOSTEL_CORRIDOR", "v": "JUNC_MALL_ESPLANADE", "meters": 160, "wheelchair": True, "surface": "interlocking_pavers", "instr": "Continue north towards UniMall concourse"},

    # UniMall Plaza
    {"u": "JUNC_MALL_ESPLANADE", "v": "GATE_UNIMALL", "meters": 40, "wheelchair": True, "surface": "paved_granite", "instr": "Pass through UniMall east pedestrian gate"},
    {"u": "JUNC_MALL_ESPLANADE", "v": "ENT_BLK_15", "meters": 45, "wheelchair": True, "surface": "level_granite", "instr": "Walk directly onto UniMall ground floor plaza entrance"},
    {"u": "JUNC_MALL_ESPLANADE", "v": "JUNC_CENTRAL_SPINE_SOUTH", "meters": 95, "wheelchair": True, "surface": "granite_promenade", "instr": "Walk north-east along Central Commercial Concourse"},

    # Central Spine South (connecting Block 14, Block 27, Central Promenade)
    {"u": "JUNC_CENTRAL_SPINE_SOUTH", "v": "ENT_BLK_14", "meters": 85, "wheelchair": True, "surface": "paved_granite", "instr": "Take the eastern promenade path to Block 14 Central Library entrance"},
    {"u": "JUNC_CENTRAL_SPINE_SOUTH", "v": "ENT_BLK_27", "meters": 50, "wheelchair": True, "surface": "paved_concrete", "instr": "Walk north-west to Block 27 entrance (Room 102 EDU-Revolution Helpdesk)"},
    {"u": "JUNC_CENTRAL_SPINE_SOUTH", "v": "JUNC_CENTRAL_PROMENADE", "meters": 80, "wheelchair": True, "surface": "granite_promenade", "instr": "Walk north along Central Promenade towards Unipolis"},

    # Central Promenade to Unipolis, Block 19, Block 20, Block 21, Stadium
    {"u": "JUNC_CENTRAL_PROMENADE", "v": "ENT_UNIPOLIS", "meters": 40, "wheelchair": True, "surface": "paved_granite", "instr": "Step onto Baldev Raj Mittal Unipolis concourse"},
    {"u": "JUNC_CENTRAL_PROMENADE", "v": "ENT_BLK_19", "meters": 60, "wheelchair": True, "surface": "paved_concrete", "instr": "Walk east to Block 19 School of Films & Auditorium entrance"},
    {"u": "ENT_BLK_19", "v": "ENT_BLK_20", "meters": 70, "wheelchair": True, "surface": "paved_concrete", "instr": "Continue east to Block 20 Lovely School of Business entrance"},
    {"u": "ENT_BLK_20", "v": "ENT_BLK_21", "meters": 55, "wheelchair": True, "surface": "paved_concrete", "instr": "Walk northeast to Block 21 School of Law entrance"},
    {"u": "JUNC_CENTRAL_PROMENADE", "v": "ENT_STADIUM", "meters": 210, "wheelchair": True, "surface": "interlocking_pavers", "instr": "Walk northeast along sports promenade to Shanti Devi Mittal Indoor Stadium"},

    # Central Promenade to Engineering Plaza & Central Spine Crossings
    {"u": "JUNC_CENTRAL_PROMENADE", "v": "JUNC_ENGG_PLAZA", "meters": 75, "wheelchair": True, "surface": "interlocking_pavers", "instr": "Turn west towards Engineering Plaza"},
    {"u": "JUNC_CENTRAL_SPINE_SOUTH", "v": "JUNC_ENGG_PLAZA", "meters": 85, "wheelchair": True, "surface": "interlocking_pavers", "instr": "Walk northwest along covered corridor to Engineering Plaza"},

    # Engineering Plaza to Block 32, Block 30, Block 34
    {"u": "JUNC_ENGG_PLAZA", "v": "JUNC_ADMIN_COURTYARD", "meters": 55, "wheelchair": True, "surface": "paved_concrete", "instr": "Walk west through the archway into Administrative Courtyard"},
    {"u": "JUNC_ADMIN_COURTYARD", "v": "ENT_BLK_32", "meters": 35, "wheelchair": True, "surface": "paved_granite", "instr": "Take the main accessible ramp into Block 32 (School of CSE / Admin)"},
    {"u": "JUNC_ADMIN_COURTYARD", "v": "ENT_BLK_30", "meters": 40, "wheelchair": True, "surface": "paved_granite", "instr": "Walk west to Block 30 Chancellor Office portico"},
    {"u": "JUNC_ENGG_PLAZA", "v": "JUNC_EXAM_AVENUE", "meters": 70, "wheelchair": True, "surface": "paved_concrete", "instr": "Walk north along Engineering Avenue"},
    {"u": "JUNC_EXAM_AVENUE", "v": "ENT_BLK_34", "meters": 35, "wheelchair": True, "surface": "paved_granite", "instr": "Enter Block 34 ground floor Examination Wing helpdesk"},
    {"u": "ENT_BLK_32", "v": "JUNC_EXAM_AVENUE", "meters": 75, "wheelchair": True, "surface": "paved_concrete", "instr": "Walk northeast past Block 33 towards Block 34"},

    # North Spine & Hostels
    {"u": "JUNC_EXAM_AVENUE", "v": "JUNC_NORTH_SPINE", "meters": 130, "wheelchair": True, "surface": "interlocking_pavers", "instr": "Continue north along the primary pedestrian spine"},
    {"u": "JUNC_NORTH_SPINE", "v": "GATE_BOYS_HOSTEL", "meters": 90, "wheelchair": True, "surface": "paved_concrete", "instr": "Walk northeast to North Boys Hostel security gate"},
    {"u": "GATE_BOYS_HOSTEL", "v": "JUNC_BOYS_HOSTEL_QUAD", "meters": 85, "wheelchair": True, "surface": "paved_concrete", "instr": "Enter the central Boys Hostel quadrangle"},
    {"u": "JUNC_BOYS_HOSTEL_QUAD", "v": "ENT_BOYS_HOSTEL_4", "meters": 50, "wheelchair": True, "surface": "paved_concrete", "instr": "Walk to Boys Hostel 4 entrance lobby"},

    # North Spine to Academic Blocks 53, 54, 55 & Gurudwara
    {"u": "JUNC_NORTH_SPINE", "v": "JUNC_NORTH_ACADEMIC", "meters": 240, "wheelchair": True, "surface": "paved_concrete", "instr": "Follow the north-west academic boulevard towards School of Agriculture"},
    {"u": "JUNC_NORTH_ACADEMIC", "v": "ENT_BLK_53", "meters": 75, "wheelchair": True, "surface": "paved_concrete", "instr": "Take the entrance ramp into Block 53 (Academic Block 1 - Agriculture)"}
]


class CampusRoutingEngine:
    """
    Pedestrian wayfinding and spatial shortest-path routing engine.
    Computes exact walking routes using Dijkstra algorithm over verified walkway edges,
    generates step-by-step turn-by-turn navigation instructions, and enforces strict
    distinction between straight-line distance and pedestrian walking distance.
    """

    _adjacency: Optional[Dict[str, List[Dict[str, Any]]]] = None

    @classmethod
    def _build_adjacency(cls):
        if cls._adjacency is not None:
            return cls._adjacency

        adj: Dict[str, List[Dict[str, Any]]] = {node_id: [] for node_id in CAMPUS_GRAPH_NODES}

        for edge in CAMPUS_GRAPH_EDGES:
            u = edge["u"]
            v = edge["v"]
            meters = edge["meters"]
            wheelchair = edge["wheelchair"]
            surface = edge["surface"]
            instr = edge["instr"]

            if u in adj and v in adj:
                # Bidirectional pedestrian walkway
                adj[u].append({
                    "to": v,
                    "meters": meters,
                    "wheelchair": wheelchair,
                    "surface": surface,
                    "instr": instr
                })
                # Reverse instruction hint
                rev_instr = f"Follow the walkway from {CAMPUS_GRAPH_NODES[v]['name']} towards {CAMPUS_GRAPH_NODES[u]['name']}"
                adj[v].append({
                    "to": u,
                    "meters": meters,
                    "wheelchair": wheelchair,
                    "surface": surface,
                    "instr": rev_instr
                })

        cls._adjacency = adj
        return cls._adjacency

    @classmethod
    def find_node_by_block(cls, block_num: str) -> Optional[str]:
        """Maps a block number (e.g. '32', '14', '08', '53') to its entrance node ID."""
        clean = block_num.strip().lower().replace("block", "").replace("blk", "").strip()
        # Direct entrance check
        for nid, data in CAMPUS_GRAPH_NODES.items():
            bn = data.get("block_number")
            if bn and (bn.lower() == clean or bn.lower() == clean.zfill(2) or bn.lstrip("0") == clean.lstrip("0")):
                return nid
        return None

    @classmethod
    def find_node_by_name_or_keyword(cls, query: str) -> Optional[str]:
        """Resolves natural language queries to an entrance or gate node."""
        q = query.lower().strip()

        # Check block numbers first
        import re
        bmatch = re.search(r"\b(?:block|blk)?\s*([0-9]{1,2})\b", q)
        if bmatch:
            bnum = bmatch.group(1)
            bnode = cls.find_node_by_block(bnum)
            if bnode:
                return bnode

        # Semantic keywords
        if "main gate" in q or "nh1" in q or "gt road" in q or "entrance" in q and "campus" in q:
            return "GATE_MAIN"
        if "hospital" in q or "emergency" in q or "unihospital" in q:
            return "ENT_BLK_08"
        if "mall" in q or "unimall" in q:
            return "ENT_BLK_15"
        if "library" in q or "central library" in q:
            return "ENT_BLK_14"
        if "chancellor" in q or "vc office" in q:
            return "ENT_BLK_30"
        if "exam" in q or "coe" in q or "admit card" in q:
            return "ENT_BLK_34"
        if "edu-revolution" in q or "edurev" in q or "102" in q:
            return "ENT_BLK_27"
        if "films" in q or "journalism" in q or "film school" in q:
            return "ENT_BLK_19"
        if "law" in q or "moot court" in q:
            return "ENT_BLK_21"
        if "stadium" in q or "swimming" in q:
            return "ENT_STADIUM"
        if "unipolis" in q or "amphitheatre" in q:
            return "ENT_UNIPOLIS"
        if "boys hostel 4" in q or "bh4" in q or "bh 4" in q:
            return "ENT_BOYS_HOSTEL_4"
        if "girls hostel 1" in q or "gh1" in q or "gh 1" in q:
            return "ENT_GIRLS_HOSTEL_1"
        if "agriculture" in q or "block 53" in q or "academic block 1" in q:
            return "ENT_BLK_53"
        if "lim" in q or "block 1" in q:
            return "ENT_BLK_01"
        if "cafe" in q or "coffee" in q:
            return "ENT_BLK_02"

        return None

    @classmethod
    def calculate_route(
        cls,
        origin_id: str,
        destination_id: str,
        wheelchair_only: bool = False
    ) -> Dict[str, Any]:
        """
        Calculates pedestrian route between two nodes using Dijkstra's algorithm.
        Enforces strict validation: if either node is unverified or no path exists,
        it explicitly rejects turn-by-turn route generation and falls back to
        straight-line distance estimation with clear disclaimers.
        """
        adj = cls._build_adjacency()

        orig_node = CAMPUS_GRAPH_NODES.get(origin_id)
        dest_node = CAMPUS_GRAPH_NODES.get(destination_id)

        # 1. Reject if either node is not in verified pedestrian graph
        if not orig_node or not dest_node:
            logger.warning("Routing rejected: origin '%s' or destination '%s' not in verified graph", origin_id, destination_id)
            return {
                "turn_by_turn_available": False,
                "is_pedestrian_path_verified": False,
                "origin_name": orig_node["name"] if orig_node else origin_id,
                "destination_name": dest_node["name"] if dest_node else destination_id,
                "walking_distance_meters": None,
                "estimated_duration_minutes": None,
                "straight_line_distance_meters": None,
                "turn_by_turn_steps": [],
                "route_coordinates": [],
                "accessibility_notes": "Pedestrian path graph is not available for unverified or off-grid locations.",
                "route_confidence": "REJECTED_UNVERIFIED_NODE",
                "data_limitations": "Turn-by-turn pedestrian path is not available for this unverified location. Only approximate map positions can be shown."
            }

        # Calculate straight-line distance as separate baseline
        straight_line_meters = haversine_distance_meters(
            orig_node["lat"], orig_node["lon"],
            dest_node["lat"], dest_node["lon"]
        )

        if origin_id == destination_id:
            return {
                "turn_by_turn_available": True,
                "is_pedestrian_path_verified": True,
                "origin_name": orig_node["name"],
                "destination_name": dest_node["name"],
                "walking_distance_meters": 0,
                "estimated_duration_minutes": 0,
                "straight_line_distance_meters": 0,
                "turn_by_turn_steps": [{
                    "step": 1,
                    "instruction": "You are already at your destination.",
                    "distance_meters": 0,
                    "landmark": dest_node["name"],
                    "wheelchair_accessible": True
                }],
                "route_coordinates": [[orig_node["lat"], orig_node["lon"]]],
                "accessibility_notes": "Step-free level access",
                "route_confidence": "EXACT_LOCATION",
                "data_limitations": None
            }

        # 2. Dijkstra shortest path algorithm
        # Priority queue stores tuples: (cumulative_distance, current_node, path, edges_used)
        pq: List[Tuple[int, str, List[str], List[Dict[str, Any]]]] = [(0, origin_id, [origin_id], [])]
        visited: Dict[str, int] = {}

        best_distance: Optional[int] = None
        best_path: List[str] = []
        best_edges: List[Dict[str, Any]] = []

        while pq:
            dist, curr, path, edges = heapq.heappop(pq)

            if curr in visited and visited[curr] <= dist:
                continue
            visited[curr] = dist

            if curr == destination_id:
                best_distance = dist
                best_path = path
                best_edges = edges
                break

            for edge in adj.get(curr, []):
                nxt = edge["to"]
                if wheelchair_only and not edge["wheelchair"]:
                    continue

                new_dist = dist + edge["meters"]
                if nxt not in visited or new_dist < visited[nxt]:
                    heapq.heappush(pq, (new_dist, nxt, path + [nxt], edges + [edge]))

        # 3. Handle disconnected graph / no valid pedestrian path
        if best_distance is None:
            return {
                "turn_by_turn_available": False,
                "is_pedestrian_path_verified": False,
                "origin_name": orig_node["name"],
                "destination_name": dest_node["name"],
                "walking_distance_meters": None,
                "estimated_duration_minutes": None,
                "straight_line_distance_meters": straight_line_meters,
                "turn_by_turn_steps": [],
                "route_coordinates": [
                    [orig_node["lat"], orig_node["lon"]],
                    [dest_node["lat"], dest_node["lon"]]
                ],
                "accessibility_notes": "No accessible connected pedestrian walkway found between these locations.",
                "route_confidence": "NO_CONNECTED_PATH",
                "data_limitations": "Turn-by-turn pedestrian path is not available for this route. Only straight-line distance is estimated."
            }

        # 4. Construct verified turn-by-turn steps & coordinates
        steps: List[Dict[str, Any]] = []
        route_coords: List[List[float]] = [[orig_node["lat"], orig_node["lon"]]]

        for i, edge in enumerate(best_edges):
            to_node = CAMPUS_GRAPH_NODES[edge["to"]]
            route_coords.append([to_node["lat"], to_node["lon"]])
            steps.append({
                "step": i + 1,
                "instruction": edge["instr"],
                "distance_meters": edge["meters"],
                "landmark": to_node["name"],
                "surface": edge["surface"],
                "wheelchair_accessible": edge["wheelchair"]
            })

        # Calculate estimated duration in minutes based on average walking pace (1.2 m/s)
        duration_minutes = max(1, int(round(best_distance / (AVERAGE_WALKING_SPEED_MPS * 60.0))))

        all_accessible = all(e["wheelchair"] for e in best_edges)
        access_note = "Route is fully wheelchair-accessible with ramps and level paving." if all_accessible else "Route includes sections with stairs or uneven pavers."

        return {
            "turn_by_turn_available": True,
            "is_pedestrian_path_verified": True,
            "origin_name": orig_node["name"],
            "destination_name": dest_node["name"],
            "walking_distance_meters": best_distance,
            "estimated_duration_minutes": duration_minutes,
            "straight_line_distance_meters": straight_line_meters,
            "turn_by_turn_steps": steps,
            "route_coordinates": route_coords,
            "accessibility_notes": access_note,
            "route_confidence": "VERIFIED_PEDESTRIAN_PATH",
            "data_limitations": "Walking distance calculated along verified pedestrian walkways at 1.2 m/s average pace."
        }
