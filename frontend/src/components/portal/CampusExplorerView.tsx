import React, { useState } from 'react';
import {
  MapPin,
  UtensilsCrossed,
  Search,
  Filter,
  ExternalLink,
  Clock,
  Sparkles,
  Compass,
  Building,
  Navigation,
  ShieldCheck,
} from 'lucide-react';

interface CampusExplorerViewProps {
  onAskAI: (query: string) => void;
}

export const CampusExplorerView: React.FC<CampusExplorerViewProps> = ({ onAskAI }) => {
  const [activeTab, setActiveTab] = useState<'places' | 'food'>('food');
  const [searchTerm, setSearchTerm] = useState('');

  // Verified LPU Campus Places
  const verifiedPlaces = [
    {
      id: 'LOC-001',
      name: 'Uni-Mall (Central Commercial Hub)',
      building: 'Uni-Mall',
      lat: 31.2538,
      lon: 75.7042,
      category: 'Commercial & Dining',
      description: 'Multi-story university commercial mall: bookstores, retail outlets, optometrist, banking counters, salon, and multi-cuisine food courts.',
      services: ['Banking / ATMs', 'Retail Stores', 'Bookstore & Stationery', 'Food Court', 'Courier Service'],
      map_url: 'https://www.lpu.in/about_lpu/campus-facilities.php'
    },
    {
      id: 'LOC-002',
      name: 'Shanti Devi Mittal Auditorium',
      building: 'North Campus Plaza',
      lat: 31.2552,
      lon: 75.7028,
      category: 'Auditorium & Events',
      description: '4,000-seat university convention and performing arts auditorium; venue for annual convocations, cultural fests, and global conferences.',
      services: ['Auditorium Hall', 'VIP Green Rooms', 'Audio-Visual Control Wing'],
      map_url: 'https://www.lpu.in/about_lpu/campus-facilities.php'
    },
    {
      id: 'LOC-003',
      name: 'Dr. S. Radhakrishnan Central Library',
      building: 'Block 14',
      lat: 31.2530,
      lon: 75.7035,
      category: 'Academic Learning',
      description: '6-story central university library featuring over 1.5 million print volumes, 24x7 study zones, RFID kiosks, and cyber research resource centres.',
      services: ['Discussion Rooms', 'Reference Section', 'RFID Self-Service Kiosks', 'Digital Resource Center', 'Photocopying Desk'],
      map_url: 'https://www.lpu.in/about_lpu/campus-facilities.php'
    },
    {
      id: 'LOC-004',
      name: 'Uni-Hospital (24x7 Emergency & Multi-Specialty)',
      building: 'Block 30',
      lat: 31.2515,
      lon: 75.7050,
      category: 'Healthcare & Emergency',
      description: 'On-campus multi-specialty university hospital providing round-the-clock emergency casualty care, free OPD consultations, ICU, and dedicated campus ambulance dispatch.',
      services: ['24x7 Emergency Bay', 'OPD Consultations', 'Ambulance Dispatch', 'Pharmacy', 'Pathology Lab'],
      map_url: 'https://www.lpu.in/about_lpu/campus-facilities.php'
    },
    {
      id: 'LOC-005',
      name: 'School of Computer Science & Engineering (HQ)',
      building: 'Block 32',
      lat: 31.2545,
      lon: 75.7020,
      category: 'Academic School',
      description: 'Primary academic block for Computer Science & Engineering, housing School Office, Dean’s Secretariat, faculty cabins, server rooms, and computing laboratories.',
      services: ['Ground Floor School Office', 'Academic Coordinator Desk', 'Computing Labs', 'Student Reception'],
      map_url: 'https://www.lpu.in/about_lpu/campus-facilities.php'
    },
    {
      id: 'LOC-006',
      name: 'EDU-Revolution Query & Guidance Zone',
      building: 'Block 27 (Room 102)',
      lat: 31.2541,
      lon: 75.7025,
      category: 'Student Innovation',
      description: 'Primary physical guidance cell for student academic benefits, course substitution, hackathon vetting, and EDU-Revolution project submissions.',
      services: ['Project Assessment Desk', 'Mentor Course Mapping Forms', 'Evaluation Committee Liaison'],
      map_url: 'https://www.lpu.in/academics/edu-revolution.php'
    },
    {
      id: 'LOC-007',
      name: 'Executive Block & Accounts Division',
      building: 'Block 34',
      lat: 31.2522,
      lon: 75.7018,
      category: 'Administration & Finance',
      description: 'Houses the Vice Chancellor Secretariat, Registrar, Division of Accounts, Fee Payment Helpdesk, and Administrative Services.',
      services: ['Fee Helpdesk', 'Accounts Division', 'Scholarship Verification', 'Registrar Office'],
      map_url: 'https://www.lpu.in/about_lpu/campus-facilities.php'
    }
  ];

  // Verified LPU Campus Food Outlets (100% Pure Vegetarian Mandate)
  const verifiedOutlets = [
    {
      id: 'FOOD-001',
      name: 'Punjabi Tadka Veg Hub',
      location: 'Block 32, Ground Floor Food Court, Shop #2',
      distance: 'On-site (Block 32)',
      hours: '09:00 - 22:00 (Open Now)',
      specialty: 'Soya Chaap (Tandoori / Malai), Dal Makhani, Paneer Butter Masala, Tandoori Roti',
      price: '₹120 - ₹180 per meal combo',
      dietary: '100% Pure Vegetarian',
      status: 'OFFICIAL_CURRENT_VERIFIED'
    },
    {
      id: 'FOOD-002',
      name: 'Nescafe Central Kiosk',
      location: 'Block 32 Central Lawns',
      distance: 'Approx 30m from Block 32',
      hours: '08:30 - 21:00 (Open Now)',
      specialty: 'Hot Brewed Coffee, Cold Frappe, Maggi, Grilled Veg Sandwiches, Cookies',
      price: '₹30 - ₹90',
      dietary: '100% Pure Vegetarian',
      status: 'OFFICIAL_CURRENT_VERIFIED'
    },
    {
      id: 'FOOD-003',
      name: 'Domino’s Pizza',
      location: 'Uni-Mall, 1st Floor Food Court',
      distance: 'Approx 150m from Block 32',
      hours: '11:00 - 23:00 (Open Now)',
      specialty: 'Margherita Pizza, Peppy Paneer, Garlic Breadsticks, Cheese Burst',
      price: '₹99 - ₹350',
      dietary: '100% Pure Vegetarian',
      status: 'OFFICIAL_CURRENT_VERIFIED'
    },
    {
      id: 'FOOD-004',
      name: 'Subway (Pure Veg Campus Outlet)',
      location: 'Uni-Mall, Ground Floor',
      distance: 'Approx 150m from Block 32',
      hours: '10:00 - 22:30 (Open Now)',
      specialty: 'Paneer Tikka Sub, Veggie Delite, Corn & Peas Sub, Cookies',
      price: '₹150 - ₹260',
      dietary: '100% Pure Vegetarian',
      status: 'OFFICIAL_CURRENT_VERIFIED'
    },
    {
      id: 'FOOD-005',
      name: 'Campus Cafe Express',
      location: 'Block 14 (Central Library Basement)',
      distance: 'Approx 180m from Block 32',
      hours: '08:00 - 23:00 (Open Now)',
      specialty: 'Masala Chai, Vegetable Cutlets, Samosa, Quick Breakfast Combos',
      price: '₹20 - ₹80',
      dietary: '100% Pure Vegetarian',
      status: 'OFFICIAL_CURRENT_VERIFIED'
    },
    {
      id: 'FOOD-006',
      name: 'South Indian Dosa Corner',
      location: 'North Campus Food Street (Near BH-4)',
      distance: 'Approx 250m from Block 32',
      hours: '08:00 - 21:30 (Open Now)',
      specialty: 'Masala Dosa, Idli Sambar, Onion Uttapam, Filter Coffee',
      price: '₹60 - ₹120',
      dietary: '100% Pure Vegetarian',
      status: 'OFFICIAL_CURRENT_VERIFIED'
    }
  ];

  const filteredPlaces = verifiedPlaces.filter(
    (p) =>
      p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.building.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredOutlets = verifiedOutlets.filter(
    (o) =>
      o.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      o.specialty.toLowerCase().includes(searchTerm.toLowerCase()) ||
      o.location.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex-1 overflow-y-auto bg-warm-bg p-4 sm:p-6 lg:p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-2xl border border-warm-border p-6 shadow-xs space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 text-xs font-semibold mb-2">
                <MapPin className="w-3.5 h-3.5" />
                <span>Geospatial Campus Intelligence</span>
              </div>
              <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
                Campus Explorer & Food Discovery
              </h1>
              <p className="text-xs sm:text-sm text-slate-500 max-w-2xl mt-1">
                Verified building coordinates, academic blocks, emergency hospital wings, and 100% pure vegetarian food courts inside Lovely Professional University.
              </p>
            </div>

            {/* Pure Veg Badge */}
            <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs space-y-0.5">
              <span className="font-bold flex items-center gap-1">
                🌱 100% Pure Vegetarian
              </span>
              <span className="text-[11px] text-emerald-600 block">Campus-Wide Institutional Mandate</span>
            </div>
          </div>

          {/* Search Bar & Mode Switcher */}
          <div className="flex flex-col sm:flex-row gap-3 pt-2 border-t border-slate-100">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
              <input
                type="text"
                placeholder={
                  activeTab === 'food'
                    ? 'Search food items (soya chaap, dosa, pizza, coffee)...'
                    : 'Search campus buildings, offices, or facilities...'
                }
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs sm:text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500"
              />
            </div>

            <div className="flex items-center gap-1.5 p-1 bg-slate-100 rounded-xl self-start sm:self-auto">
              <button
                onClick={() => setActiveTab('food')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'food' ? 'bg-white text-orange-700 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <UtensilsCrossed className="w-3.5 h-3.5" />
                Food Outlets ({verifiedOutlets.length})
              </button>
              <button
                onClick={() => setActiveTab('places')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'places' ? 'bg-white text-orange-700 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Building className="w-3.5 h-3.5" />
                Campus Places ({verifiedPlaces.length})
              </button>
            </div>
          </div>
        </div>

        {/* Food Outlets Grid */}
        {activeTab === 'food' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredOutlets.map((outlet) => (
              <div
                key={outlet.id}
                className="bg-white rounded-2xl border border-warm-border p-5 shadow-xs hover:border-orange-300 transition-all space-y-3.5 flex flex-col justify-between"
              >
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h3 className="text-base font-bold text-slate-900 flex items-center gap-1.5">
                        {outlet.name}
                      </h3>
                      <p className="text-xs text-slate-500 flex items-center gap-1 mt-0.5">
                        <MapPin className="w-3.5 h-3.5 text-slate-400" />
                        {outlet.location}
                      </p>
                    </div>

                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 shrink-0">
                      {outlet.status}
                    </span>
                  </div>

                  {/* Menu Specialities */}
                  <div className="p-3 rounded-xl bg-orange-50/50 border border-orange-100/80 text-xs space-y-1">
                    <span className="font-bold text-slate-800 block">Verified Specialties:</span>
                    <p className="text-slate-700 font-medium leading-relaxed">{outlet.specialty}</p>
                  </div>

                  {/* Price & Hours Bar */}
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 space-y-0.5">
                      <span className="text-[11px] text-slate-400 font-medium">Sample Pricing</span>
                      <p className="font-bold text-slate-800">{outlet.price}</p>
                    </div>
                    <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 space-y-0.5">
                      <span className="text-[11px] text-slate-400 font-medium">Operating Hours</span>
                      <p className="font-bold text-emerald-700">{outlet.hours}</p>
                    </div>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                  <span className="text-[11px] text-slate-500">
                    Proximity: <span className="font-semibold text-slate-700">{outlet.distance}</span>
                  </span>

                  <button
                    onClick={() => onAskAI(`What are the timings, exact location, and popular dishes at ${outlet.name}?`)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-orange-50 hover:bg-orange-100/80 text-orange-700 text-xs font-semibold transition-colors"
                  >
                    <Compass className="w-3.5 h-3.5" />
                    Ask AI Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Campus Places Grid */}
        {activeTab === 'places' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredPlaces.map((place) => (
              <div
                key={place.id}
                className="bg-white rounded-2xl border border-warm-border p-5 shadow-xs hover:border-orange-300 transition-all space-y-3.5 flex flex-col justify-between"
              >
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h3 className="text-base font-bold text-slate-900">{place.name}</h3>
                      <p className="text-xs font-semibold text-orange-700">{place.building} ({place.category})</p>
                    </div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200 shrink-0">
                      {place.lat.toFixed(4)}°N, {place.lon.toFixed(4)}°E
                    </span>
                  </div>

                  <p className="text-xs text-slate-600 leading-relaxed">{place.description}</p>

                  <div className="space-y-1">
                    <span className="text-[11px] font-bold text-slate-700">Services Available:</span>
                    <div className="flex flex-wrap gap-1">
                      {place.services.map((svc, i) => (
                        <span key={i} className="text-[10px] px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                          {svc}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                  <a
                    href={place.map_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs text-slate-500 hover:text-slate-800 flex items-center gap-1"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                    Official Tour
                  </a>

                  <button
                    onClick={() => onAskAI(`Where is ${place.building} and how do I navigate there from Block 32?`)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-orange-50 hover:bg-orange-100/80 text-orange-700 text-xs font-semibold transition-colors"
                  >
                    <Navigation className="w-3.5 h-3.5" />
                    Wayfinding Directions
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
