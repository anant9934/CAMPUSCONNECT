import React, { useState, useEffect, useRef } from 'react';
import {
  X,
  Search,
  Filter,
  Navigation,
  Footprints,
  Clock,
  Compass,
  Accessibility,
  Building2,
  MapPin,
  ExternalLink,
  RotateCcw,
  ZoomIn,
  ZoomOut,
  AlertCircle,
  CheckCircle2,
  Info,
  Maximize2
} from 'lucide-react';
import { CampusRouteCard } from '../types';
import { api } from '../services/api';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  initialPlaceId?: string;
  initialRoute?: CampusRouteCard | null;
  onSelectPlaceForChat?: (placeName: string) => void;
}

export const CampusMapPanel: React.FC<Props> = ({
  isOpen,
  onClose,
  initialPlaceId,
  initialRoute,
  onSelectPlaceForChat,
}) => {
  const [activeTab, setActiveTab] = useState<'2d' | '3d'>('2d');
  const [places, setPlaces] = useState<any[]>([]);
  const [selectedPlace, setSelectedPlace] = useState<any | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(false);

  // Routing State
  const [originId, setOriginId] = useState<string>('GATE_MAIN');
  const [destId, setDestId] = useState<string>('ENT_BLK_32');
  const [activeRoute, setActiveRoute] = useState<CampusRouteCard | null>(initialRoute || null);
  const [isRouting, setIsRouting] = useState(false);
  const [wheelchairOnly, setWheelchairOnly] = useState(false);
  const [locationMode, setLocationMode] = useState<'landmark' | 'gps' | 'tap'>('landmark');
  const [gpsError, setGpsError] = useState<string | null>(null);

  // Map Pan & Zoom State
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const mapContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      loadPlaces();
    }
  }, [isOpen]);

  useEffect(() => {
    if (initialPlaceId && places.length > 0) {
      const match = places.find((p) => p.place_id === initialPlaceId);
      if (match) setSelectedPlace(match);
    }
  }, [initialPlaceId, places]);

  useEffect(() => {
    if (initialRoute) {
      setActiveRoute(initialRoute);
    }
  }, [initialRoute]);

  const loadPlaces = async () => {
    try {
      setIsLoading(true);
      const data = await api.getCampusNavigationPlaces();
      setPlaces(data);
      if (!selectedPlace && data.length > 0) {
        const blk32 = data.find((p) => p.block_number === '32');
        if (blk32) setSelectedPlace(blk32);
      }
    } catch (err) {
      console.error('Failed to load campus places', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCalculateRoute = async (orig = originId, dest = destId) => {
    try {
      setIsRouting(true);
      const route = await api.getCampusPedestrianRoute(orig, dest, wheelchairOnly);
      setActiveRoute(route);
    } catch (err) {
      console.error('Failed to calculate route', err);
    } finally {
      setIsRouting(false);
    }
  };

  const handleRequestGps = () => {
    setGpsError(null);
    if (!navigator.geolocation) {
      setGpsError('Geolocation is not supported by your browser. Please select a starting landmark.');
      setLocationMode('landmark');
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLocationMode('gps');
        setOriginId('GATE_MAIN'); // closest entrance
        handleCalculateRoute('GATE_MAIN', destId);
      },
      (err) => {
        setGpsError('Location access was denied or unavailable. Fallback: select a starting landmark or tap the map.');
        setLocationMode('landmark');
      },
      { timeout: 8000 }
    );
  };

  const handleZoom = (delta: number) => {
    setZoom((prev) => Math.min(Math.max(prev + delta, 0.6), 2.5));
  };

  const handleResetView = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPan({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  if (!isOpen) return null;

  // Filtered places for list/search
  const filteredPlaces = places.filter((p) => {
    const matchesCat =
      selectedCategory === 'all' ||
      p.category.toLowerCase().includes(selectedCategory.toLowerCase());
    const matchesSearch =
      !searchQuery ||
      p.official_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (p.block_number && p.block_number.includes(searchQuery)) ||
      (p.alternative_names && p.alternative_names.some((a: string) => a.toLowerCase().includes(searchQuery.toLowerCase())));
    return matchesCat && matchesSearch;
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-xs p-2 sm:p-4">
      <div className="flex h-full max-h-[96vh] w-full max-w-7xl flex-col overflow-hidden rounded-2xl bg-white shadow-2xl border border-neutral-200">
        {/* Top Header */}
        <div className="flex items-center justify-between border-b border-neutral-200 bg-neutral-900 px-4 py-3 text-white">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-sky-600 text-white shadow-sm">
              <MapPin className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold tracking-wide text-white flex items-center gap-2">
                <span>LPU Campus Navigation & Block Discovery</span>
                <span className="rounded bg-sky-500/20 text-sky-300 text-[10px] font-medium px-2 py-0.5 border border-sky-400/30">
                  Blocks 01–55
                </span>
              </h3>
              <p className="text-[11px] text-neutral-400">
                Verified Pedestrian Walkways • GPS Entrances • Scholix 3D Walkthrough
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* View Mode Toggle */}
            <div className="flex rounded-lg bg-neutral-800 p-0.5 border border-neutral-700">
              <button
                type="button"
                onClick={() => setActiveTab('2d')}
                className={`flex items-center gap-1.5 rounded-md px-3 py-1 text-xs font-semibold transition-colors ${
                  activeTab === '2d' ? 'bg-sky-600 text-white shadow-xs' : 'text-neutral-400 hover:text-white'
                }`}
              >
                <span>2D Campus Map</span>
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('3d')}
                className={`flex items-center gap-1.5 rounded-md px-3 py-1 text-xs font-semibold transition-colors ${
                  activeTab === '3d' ? 'bg-sky-600 text-white shadow-xs' : 'text-neutral-400 hover:text-white'
                }`}
              >
                <span>3D Walkthrough</span>
              </button>
            </div>

            {/* Close Button (Preserves Conversation) */}
            <button
              type="button"
              onClick={onClose}
              title="Return to Chat"
              className="flex h-8 w-8 items-center justify-center rounded-lg bg-neutral-800 text-neutral-300 hover:bg-neutral-700 hover:text-white transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Tab 1: 2D Interactive Map */}
        {activeTab === '2d' && (
          <div className="flex flex-1 flex-col lg:flex-row overflow-hidden bg-neutral-100">
            {/* Left Controls & Search Sidebar */}
            <div className="flex w-full lg:w-96 flex-col border-r border-neutral-200 bg-white">
              {/* Search & Category Filter */}
              <div className="p-3 border-b border-neutral-200 space-y-2">
                <div className="relative">
                  <Search className="absolute left-3 top-2.5 h-4 w-4 text-neutral-400" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search block, department, hostel..."
                    className="w-full rounded-lg border border-neutral-300 bg-neutral-50 pl-9 pr-3 py-1.5 text-xs text-neutral-800 placeholder-neutral-400 focus:bg-white focus:border-sky-600 focus:outline-none"
                  />
                </div>

                {/* Category Filter Chips */}
                <div className="flex flex-wrap gap-1">
                  {[
                    { id: 'all', label: 'All' },
                    { id: 'academic', label: 'Academic' },
                    { id: 'hostel', label: 'Hostels' },
                    { id: 'administration', label: 'Admin' },
                    { id: 'dining', label: 'Dining' },
                    { id: 'healthcare', label: 'Health' },
                    { id: 'auditorium', label: 'Auditoriums' },
                  ].map((cat) => (
                    <button
                      key={cat.id}
                      type="button"
                      onClick={() => setSelectedCategory(cat.id)}
                      className={`rounded-full px-2.5 py-0.5 text-[11px] font-medium transition-colors ${
                        selectedCategory === cat.id
                          ? 'bg-sky-600 text-white'
                          : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
                      }`}
                    >
                      {cat.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Pedestrian Routing Controls Bar */}
              <div className="p-3 border-b border-neutral-200 bg-sky-50/40">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-neutral-900 flex items-center gap-1">
                    <Navigation className="h-3.5 w-3.5 text-sky-600" />
                    <span>Get Walking Directions</span>
                  </span>
                  <button
                    type="button"
                    onClick={handleRequestGps}
                    className="text-[11px] text-sky-700 hover:text-sky-900 font-semibold"
                  >
                    📍 Use GPS
                  </button>
                </div>

                {gpsError && (
                  <div className="mb-2 rounded bg-amber-50 p-1.5 text-[10px] text-amber-800 border border-amber-200">
                    {gpsError}
                  </div>
                )}

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                  <div>
                    <label className="text-[10px] uppercase font-semibold text-neutral-500 block">Origin</label>
                    <select
                      value={originId}
                      onChange={(e) => setOriginId(e.target.value)}
                      className="w-full rounded border border-neutral-300 bg-white p-1 text-xs"
                    >
                      <option value="GATE_MAIN">Main Gate (NH1)</option>
                      <option value="ENT_BLK_32">Block 32 (CSE / Admin)</option>
                      <option value="ENT_BLK_14">Block 14 (Library / Business)</option>
                      <option value="ENT_BLK_15">Block 15 (UniMall)</option>
                      <option value="ENT_BLK_08">Block 08 (UniHospital)</option>
                      <option value="ENT_BLK_30">Block 30 (Chancellor Office)</option>
                      <option value="ENT_BLK_34">Block 34 (Examination Wing)</option>
                      <option value="ENT_BOYS_HOSTEL_4">Boys Hostel 4</option>
                      <option value="ENT_GIRLS_HOSTEL_1">Girls Hostel 1</option>
                      <option value="ENT_BLK_53">Block 53 (Academic 1)</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-[10px] uppercase font-semibold text-neutral-500 block">Destination</label>
                    <select
                      value={destId}
                      onChange={(e) => setDestId(e.target.value)}
                      className="w-full rounded border border-neutral-300 bg-white p-1 text-xs"
                    >
                      <option value="ENT_BLK_14">Block 14 (Library / Business)</option>
                      <option value="ENT_BLK_32">Block 32 (CSE / Admin)</option>
                      <option value="ENT_BLK_15">Block 15 (UniMall)</option>
                      <option value="ENT_BLK_08">Block 08 (UniHospital)</option>
                      <option value="ENT_BLK_30">Block 30 (Chancellor Office)</option>
                      <option value="ENT_BLK_34">Block 34 (Examination Wing)</option>
                      <option value="ENT_BLK_27">Block 27 (EDU-Rev Room 102)</option>
                      <option value="ENT_BLK_19">Block 19 (School of Films)</option>
                      <option value="ENT_BLK_21">Block 21 (School of Law)</option>
                      <option value="ENT_STADIUM">Indoor Stadium</option>
                      <option value="ENT_BOYS_HOSTEL_4">Boys Hostel 4</option>
                      <option value="ENT_BLK_53">Block 53 (Academic 1)</option>
                    </select>
                  </div>
                </div>

                <div className="mt-2.5 flex items-center justify-between">
                  <label className="flex items-center gap-1.5 text-[11px] text-neutral-700 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={wheelchairOnly}
                      onChange={(e) => setWheelchairOnly(e.target.checked)}
                      className="rounded border-neutral-300 text-sky-600 focus:ring-sky-500 h-3.5 w-3.5"
                    />
                    <span>Wheelchair step-free</span>
                  </label>
                  <button
                    type="button"
                    onClick={() => handleCalculateRoute(originId, destId)}
                    disabled={isRouting}
                    className="inline-flex items-center gap-1 rounded bg-sky-600 px-3 py-1 text-xs font-semibold text-white shadow-xs hover:bg-sky-700 transition-colors disabled:opacity-50"
                  >
                    <span>{isRouting ? 'Routing...' : 'Calculate Route'}</span>
                  </button>
                </div>
              </div>

              {/* Calculated Route Panel */}
              {activeRoute && (
                <div className="p-3 border-b border-sky-200 bg-gradient-to-r from-sky-50 to-indigo-50/50">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-sky-950">Active Pedestrian Route</span>
                    <button
                      type="button"
                      onClick={() => setActiveRoute(null)}
                      className="text-[10px] text-neutral-400 hover:text-neutral-600"
                    >
                      Clear
                    </button>
                  </div>
                  <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
                    <div className="flex items-center gap-1.5 rounded bg-white p-2 border border-sky-100 shadow-2xs">
                      <Footprints className="h-4 w-4 text-sky-600" />
                      <div>
                        <span className="text-[10px] text-neutral-500 block">Walking</span>
                        <span className="font-bold text-sky-900">{activeRoute.walking_distance_meters ?? 'N/A'}m</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-1.5 rounded bg-white p-2 border border-sky-100 shadow-2xs">
                      <Clock className="h-4 w-4 text-indigo-600" />
                      <div>
                        <span className="text-[10px] text-neutral-500 block">Time (1.2m/s)</span>
                        <span className="font-bold text-indigo-900">~{activeRoute.estimated_duration_minutes ?? 'N/A'} min</span>
                      </div>
                    </div>
                  </div>
                  {activeRoute.straight_line_distance_meters && (
                    <div className="mt-1.5 text-[10px] text-neutral-500 flex items-center justify-between">
                      <span>Air Distance: ~{activeRoute.straight_line_distance_meters}m</span>
                      <span className="text-emerald-700 font-semibold">• Verified Walkway</span>
                    </div>
                  )}
                </div>
              )}

              {/* Places List */}
              <div className="flex-1 overflow-y-auto p-2 space-y-1.5">
                <span className="text-[10px] font-bold uppercase tracking-wider text-neutral-400 px-2 block">
                  Found Locations ({filteredPlaces.length})
                </span>
                {filteredPlaces.map((p) => {
                  const isSelected = selectedPlace?.place_id === p.place_id;
                  const isReconciled = p.verification_status === 'RECONCILED_UNIVERSITY_RECORD';
                  return (
                    <div
                      key={p.place_id}
                      onClick={() => setSelectedPlace(p)}
                      className={`flex items-center justify-between rounded-lg p-2.5 text-xs transition-all cursor-pointer ${
                        isSelected
                          ? 'bg-sky-600 text-white shadow-xs'
                          : 'bg-neutral-50 hover:bg-neutral-100 text-neutral-800'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <span
                          className={`flex h-6 w-6 items-center justify-center rounded font-bold text-[11px] ${
                            isSelected ? 'bg-white/20 text-white' : 'bg-sky-100 text-sky-800'
                          }`}
                        >
                          {p.block_number || '•'}
                        </span>
                        <div>
                          <p className="font-semibold leading-tight line-clamp-1">{p.official_name}</p>
                          <span
                            className={`text-[10px] ${
                              isSelected ? 'text-sky-100' : 'text-neutral-500'
                            }`}
                          >
                            {p.category} • {p.campus_zone}
                          </span>
                        </div>
                      </div>
                      <MapPin className={`h-4 w-4 shrink-0 ${isSelected ? 'text-white' : 'text-neutral-400'}`} />
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Right Map Canvas & Details Panel */}
            <div className="flex flex-1 flex-col overflow-hidden relative">
              {/* Map Canvas with SVG Rendering */}
              <div
                ref={mapContainerRef}
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                onMouseLeave={handleMouseUp}
                className="flex-1 overflow-hidden bg-slate-900 cursor-grab active:cursor-grabbing relative select-none"
              >
                {/* Floating Map Zoom Controls */}
                <div className="absolute right-4 top-4 z-10 flex flex-col gap-1 rounded-lg bg-neutral-900/90 p-1 text-white border border-neutral-700 shadow-lg">
                  <button
                    type="button"
                    onClick={() => handleZoom(0.2)}
                    title="Zoom In"
                    className="flex h-8 w-8 items-center justify-center rounded hover:bg-neutral-800"
                  >
                    <ZoomIn className="h-4 w-4" />
                  </button>
                  <button
                    type="button"
                    onClick={() => handleZoom(-0.2)}
                    title="Zoom Out"
                    className="flex h-8 w-8 items-center justify-center rounded hover:bg-neutral-800"
                  >
                    <ZoomOut className="h-4 w-4" />
                  </button>
                  <button
                    type="button"
                    onClick={handleResetView}
                    title="Reset View"
                    className="flex h-8 w-8 items-center justify-center rounded hover:bg-neutral-800"
                  >
                    <RotateCcw className="h-4 w-4" />
                  </button>
                </div>

                {/* Map Notice Overlay */}
                <div className="absolute left-4 top-4 z-10 rounded-lg bg-neutral-900/80 px-3 py-1.5 text-[11px] text-neutral-300 border border-neutral-700 shadow-sm backdrop-blur-xs">
                  <span className="font-semibold text-white">LPU Campus Site Plan:</span> 55 Numbered Locations
                  <span className="mx-2 text-neutral-600">|</span>
                  <span className="text-amber-300">Map Not To Scale (Distances from verified graph)</span>
                </div>

                {/* SVG Campus Rendering */}
                <svg
                  className="h-full w-full"
                  viewBox="0 0 1000 800"
                  style={{
                    transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
                    transformOrigin: 'center center',
                    transition: isDragging ? 'none' : 'transform 0.15s ease-out',
                  }}
                >
                  <defs>
                    <linearGradient id="grassGrad" x1="0" y1="0" x2="1" y2="1">
                      <stop offset="0%" stopColor="#1e293b" />
                      <stop offset="100%" stopColor="#0f172a" />
                    </linearGradient>
                    <linearGradient id="roadGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#475569" />
                      <stop offset="100%" stopColor="#334155" />
                    </linearGradient>
                  </defs>

                  {/* Campus Base Terrain */}
                  <rect x="0" y="0" width="1000" height="800" fill="url(#grassGrad)" />

                  {/* National Highway 1 (Grand Trunk Road) at Bottom */}
                  <rect x="0" y="740" width="1000" height="60" fill="#1e293b" />
                  <line x1="0" y1="770" x2="1000" y2="770" stroke="#facc15" strokeWidth="2" strokeDasharray="15,10" />
                  <text x="400" y="765" fill="#94a3b8" fontSize="12" fontWeight="bold">
                    NATIONAL HIGHWAY 1 (GT ROAD) ➔ TOWARDS JALANDHAR / PHAGWARA
                  </text>

                  {/* Campus Boulevard & Pedestrian Spine (Grey roads) */}
                  <path
                    d="M 500 740 L 490 620 L 460 500 L 480 380 L 490 260 L 470 120"
                    stroke="#475569"
                    strokeWidth="16"
                    fill="none"
                    strokeLinecap="round"
                  />
                  {/* West Wing (Engineering & Admin Avenue) */}
                  <path
                    d="M 460 500 L 320 440 L 310 320 L 480 380"
                    stroke="#334155"
                    strokeWidth="10"
                    fill="none"
                    strokeLinecap="round"
                  />
                  {/* East Wing (Central Library, Hostels & UniMall) */}
                  <path
                    d="M 490 620 L 620 580 L 640 440 L 480 380"
                    stroke="#334155"
                    strokeWidth="10"
                    fill="none"
                    strokeLinecap="round"
                  />
                  {/* North Sector (Academic 53-55 & Boys Hostels) */}
                  <path
                    d="M 490 260 L 320 180 L 300 80"
                    stroke="#334155"
                    strokeWidth="10"
                    fill="none"
                    strokeLinecap="round"
                  />
                  <path
                    d="M 490 260 L 650 200 L 680 100"
                    stroke="#334155"
                    strokeWidth="10"
                    fill="none"
                    strokeLinecap="round"
                  />

                  {/* Active Calculated Route Polyline */}
                  {activeRoute && activeRoute.route_coordinates && activeRoute.route_coordinates.length > 1 && (
                    <polyline
                      points={activeRoute.route_coordinates
                        .map(([lat, lon]) => {
                          // Map GPS coords to SVG coordinates
                          const svgX = ((lon - 75.701) / 0.007) * 600 + 200;
                          const svgY = 740 - ((lat - 31.246) / 0.015) * 640;
                          return `${svgX},${svgY}`;
                        })
                        .join(' ')}
                      stroke="#38bdf8"
                      strokeWidth="6"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeDasharray="8,4"
                      fill="none"
                      className="animate-pulse"
                    />
                  )}

                  {/* Campus Gates */}
                  <g transform="translate(500, 725)">
                    <circle r="12" fill="#0284c7" />
                    <text y="4" textAnchor="middle" fill="white" fontSize="9" fontWeight="bold">
                      GATE
                    </text>
                    <text y="24" textAnchor="middle" fill="#38bdf8" fontSize="10" fontWeight="bold">
                      Main Gate (NH1)
                    </text>
                  </g>

                  {/* Render All 55 Buildings on Map Canvas */}
                  {places.map((p) => {
                    if (!p.latitude || !p.longitude) return null;
                    // Project lat/lon to SVG coordinates
                    const x = ((p.longitude - 75.701) / 0.007) * 600 + 200;
                    const y = 740 - ((p.latitude - 31.246) / 0.015) * 640;
                    const isSelected = selectedPlace?.place_id === p.place_id;

                    const catColors: Record<string, string> = {
                      Academic: '#6366f1',
                      Administration: '#f59e0b',
                      Hostel: '#0ea5e9',
                      'Dining & Retail': '#10b981',
                      Healthcare: '#ef4444',
                      Auditorium: '#a855f7',
                      Library: '#3b82f6',
                      Sports: '#14b8a6',
                    };
                    const color = catColors[p.category] || '#64748b';

                    return (
                      <g
                        key={p.place_id}
                        transform={`translate(${x}, ${y})`}
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedPlace(p);
                        }}
                        className="cursor-pointer transition-transform hover:scale-125"
                      >
                        {isSelected && (
                          <circle r="18" fill="none" stroke="#facc15" strokeWidth="3" className="animate-ping" />
                        )}
                        <rect
                          x="-11"
                          y="-11"
                          width="22"
                          height="22"
                          rx="4"
                          fill={isSelected ? '#facc15' : color}
                          stroke="#ffffff"
                          strokeWidth="1.5"
                          shadow-md="true"
                        />
                        <text
                          y="4"
                          textAnchor="middle"
                          fill={isSelected ? '#000000' : '#ffffff'}
                          fontSize="9"
                          fontWeight="bold"
                        >
                          {p.block_number || '•'}
                        </text>
                      </g>
                    );
                  })}
                </svg>
              </div>

              {/* Bottom Selected Building Detail Drawer */}
              {selectedPlace && (
                <div className="border-t border-neutral-200 bg-white p-3.5 shadow-lg">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="flex items-start gap-2.5">
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-sky-600 font-bold text-white text-xs">
                        {selectedPlace.block_number || 'BLK'}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="text-sm font-bold text-neutral-900 leading-tight">
                            {selectedPlace.official_name}
                          </h4>
                          <span className="rounded bg-sky-100 text-sky-800 text-[10px] font-semibold px-2 py-0.5">
                            {selectedPlace.category}
                          </span>
                        </div>
                        <p className="mt-0.5 text-xs text-neutral-600 line-clamp-1">
                          {selectedPlace.building_description}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      <button
                        type="button"
                        onClick={() => {
                          setOriginId(`ENT_BLK_${selectedPlace.block_number || '32'}`);
                          handleCalculateRoute(`ENT_BLK_${selectedPlace.block_number || '32'}`, destId);
                        }}
                        className="rounded-lg border border-neutral-300 px-3 py-1.5 text-xs font-medium text-neutral-700 hover:bg-neutral-50 transition-colors"
                      >
                        Set as Origin
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setDestId(`ENT_BLK_${selectedPlace.block_number || '14'}`);
                          handleCalculateRoute(originId, `ENT_BLK_${selectedPlace.block_number || '14'}`);
                        }}
                        className="rounded-lg bg-sky-600 px-3.5 py-1.5 text-xs font-semibold text-white shadow-xs hover:bg-sky-700 transition-colors"
                      >
                        Navigate Here
                      </button>
                      {onSelectPlaceForChat && (
                        <button
                          type="button"
                          onClick={() => {
                            onSelectPlaceForChat(selectedPlace.official_name);
                            onClose();
                          }}
                          className="rounded-lg border border-sky-300 bg-sky-50 px-3 py-1.5 text-xs font-semibold text-sky-800 hover:bg-sky-100 transition-colors"
                        >
                          Ask in Chat
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Tab 2: Scholix 3D Walkthrough Integration */}
        {activeTab === '3d' && (
          <div className="flex flex-1 flex-col overflow-hidden bg-neutral-900">
            {/* Notice Banner */}
            <div className="flex items-center justify-between border-b border-neutral-800 bg-neutral-950 px-4 py-2 text-xs text-neutral-300">
              <div className="flex items-center gap-2">
                <Info className="h-4 w-4 text-sky-400" />
                <span>
                  <strong>Scholix 3D Visual Walkthrough:</strong> Supplementary 3D exploration experience. Map not to scale.
                </span>
              </div>
              <a
                href="https://scholix.app/lpu/campus/map"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 rounded bg-neutral-800 px-3 py-1 text-xs font-medium text-sky-300 hover:bg-neutral-700 hover:text-white transition-colors"
              >
                <span>Open in New Window</span>
                <ExternalLink className="h-3.5 w-3.5" />
              </a>
            </div>

            {/* Embedded Iframe */}
            <div className="flex-1 relative">
              <iframe
                src="https://scholix.app/lpu/campus/map"
                title="LPU Campus Scholix 3D Walkthrough"
                className="h-full w-full border-0"
                allow="accelerometer; gyroscope; magnetometer; fullscreen"
                sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

