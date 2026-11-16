import React, { useState, useEffect } from 'react';
import {
  X,
  Search,
  BookOpen,
  Award,
  Users,
  Compass,
  MapPin,
  UtensilsCrossed,
  ArrowRight,
  ShieldCheck,
  ExternalLink,
  Clock,
  Sparkles,
} from 'lucide-react';
import { api } from '../services/api';

interface LibraryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectPrompt: (prompt: string) => void;
}

type LibraryTab = 'all' | 'benefits' | 'people' | 'ums' | 'campus';

export const LibraryModal: React.FC<LibraryModalProps> = ({
  isOpen,
  onClose,
  onSelectPrompt,
}) => {
  const [activeTab, setActiveTab] = useState<LibraryTab>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [benefits, setBenefits] = useState<any[]>([]);
  const [people, setPeople] = useState<any[]>([]);
  const [services, setServices] = useState<any[]>([]);
  const [places, setPlaces] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadLibraryData();
    }
  }, [isOpen]);

  const loadLibraryData = async () => {
    try {
      setIsLoading(true);
      const [bData, pData, sData, plData] = await Promise.all([
        api.getAcademicBenefits().catch(() => []),
        api.getPeople().catch(() => []),
        api.getUMSServices().catch(() => []),
        api.getSavedPlaces().catch(() => []),
      ]);
      setBenefits(bData || []);
      setPeople(Array.isArray(pData) ? pData : (pData?.people || []));
      setServices(sData || []);
      setPlaces(plData || []);
    } catch (err) {
      console.error('Failed to load library data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  const handleLaunchQuery = (query: string) => {
    onSelectPrompt(query);
    onClose();
  };

  const filteredBenefits = benefits.filter(
    (b) =>
      b.category_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      b.output_criteria?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredPeople = people.filter(
    (p) =>
      p.full_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.designation?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.department?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredServices = services.filter(
    (s) =>
      s.service_label?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.module?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs animate-fadeIn">
      <div className="bg-white rounded-2xl border border-warm-border w-full max-w-4xl max-h-[85vh] flex flex-col shadow-soft-lg overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-warm-border flex items-center justify-between bg-slate-50/60">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-orange-100 text-orange-700 flex items-center justify-center border border-orange-200 shadow-xs">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                University Knowledge Library
                <span className="text-[10px] font-semibold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full border border-emerald-200">
                  Verified LPU Records
                </span>
              </h2>
              <p className="text-xs text-slate-500">
                Browse verified academic policies, faculty directories, and 234 UMS navigation pathways
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Search & Tabs */}
        <div className="px-6 pt-4 pb-3 border-b border-warm-border space-y-3 bg-white">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search policies, faculty members, UMS services, or campus places..."
              className="w-full pl-9 pr-4 py-2 rounded-xl border border-warm-border bg-slate-50 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-orange-400 focus:bg-white transition-all"
            />
          </div>

          <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar text-xs">
            <button
              onClick={() => setActiveTab('all')}
              className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                activeTab === 'all'
                  ? 'bg-orange-600 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              All Assets
            </button>
            <button
              onClick={() => setActiveTab('benefits')}
              className={`px-3 py-1.5 rounded-lg font-medium flex items-center gap-1.5 transition-colors ${
                activeTab === 'benefits'
                  ? 'bg-orange-600 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              <Award className="w-3.5 h-3.5" />
              EDU-Revolution & Benefits ({benefits.length})
            </button>
            <button
              onClick={() => setActiveTab('people')}
              className={`px-3 py-1.5 rounded-lg font-medium flex items-center gap-1.5 transition-colors ${
                activeTab === 'people'
                  ? 'bg-orange-600 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              <Users className="w-3.5 h-3.5" />
              Faculty & Leadership ({people.length})
            </button>
            <button
              onClick={() => setActiveTab('ums')}
              className={`px-3 py-1.5 rounded-lg font-medium flex items-center gap-1.5 transition-colors ${
                activeTab === 'ums'
                  ? 'bg-orange-600 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              <Compass className="w-3.5 h-3.5" />
              UMS 234 Services ({services.length})
            </button>
            <button
              onClick={() => setActiveTab('campus')}
              className={`px-3 py-1.5 rounded-lg font-medium flex items-center gap-1.5 transition-colors ${
                activeTab === 'campus'
                  ? 'bg-orange-600 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              <MapPin className="w-3.5 h-3.5" />
              Campus Locations
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/40">
          {isLoading ? (
            <div className="py-12 flex flex-col items-center justify-center text-slate-400 gap-2">
              <div className="w-6 h-6 border-2 border-orange-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-xs">Loading verified university library...</p>
            </div>
          ) : (
            <>
              {/* EDU-Revolution Benefits Section */}
              {(activeTab === 'all' || activeTab === 'benefits') && filteredBenefits.length > 0 && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                      <Award className="w-4 h-4 text-orange-600" />
                      EDU-Revolution Academic Benefits (First 4-Week Window)
                    </h3>
                    <span className="text-[11px] text-slate-500">Standing Academic Committee (SAC) Ratified</span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {filteredBenefits.slice(0, activeTab === 'all' ? 4 : 20).map((b, idx) => (
                      <div
                        key={idx}
                        className="bg-white p-4 rounded-xl border border-warm-border hover:border-orange-300 hover:shadow-xs transition-all space-y-2 group"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-orange-100 text-orange-800">
                            {b.category_id || `CAT-${idx + 1}`}
                          </span>
                          <span className="text-[11px] font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                            Up to 100% CA Exemption
                          </span>
                        </div>
                        <h4 className="text-xs font-bold text-slate-900 group-hover:text-orange-700 transition-colors">
                          {b.category_name}
                        </h4>
                        <p className="text-[11px] text-slate-600 leading-relaxed line-clamp-2">
                          {b.output_criteria}
                        </p>
                        <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                          <span className="text-[10px] text-slate-400">Helpdesk: Block 27 Room 102</span>
                          <button
                            onClick={() =>
                              handleLaunchQuery(
                                `What are the eligibility requirements and CA exemption rules for ${b.category_name}?`
                              )
                            }
                            className="text-xs text-orange-600 hover:text-orange-700 font-semibold flex items-center gap-1 group-hover:translate-x-0.5 transition-transform"
                          >
                            <span>Ask AI in Chat</span>
                            <ArrowRight className="w-3 h-3" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Faculty & Leadership Section */}
              {(activeTab === 'all' || activeTab === 'people') && filteredPeople.length > 0 && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                      <Users className="w-4 h-4 text-blue-600" />
                      Faculty & Academic Leadership (Block 32 School Office)
                    </h3>
                    <span className="text-[11px] text-slate-500">Office hours: 3:00 PM – 5:00 PM</span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {filteredPeople.slice(0, activeTab === 'all' ? 4 : 20).map((p, idx) => (
                      <div
                        key={idx}
                        className="bg-white p-4 rounded-xl border border-warm-border hover:border-blue-300 hover:shadow-xs transition-all space-y-2 group"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <h4 className="text-xs font-bold text-slate-900 group-hover:text-blue-700 transition-colors">
                              {p.full_name}
                            </h4>
                            <p className="text-[11px] text-slate-500">{p.designation}</p>
                          </div>
                          <span className="text-[10px] font-semibold bg-slate-100 text-slate-700 px-2 py-0.5 rounded">
                            {p.building_block || 'Block 32'}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-600">
                          {p.department || p.school_division}
                        </p>
                        <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                          <span className="text-[10px] text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded">
                            Consultation at School Office
                          </span>
                          <button
                            onClick={() =>
                              handleLaunchQuery(
                                `How can I meet ${p.full_name} and what is the appointment procedure?`
                              )
                            }
                            className="text-xs text-blue-600 hover:text-blue-700 font-semibold flex items-center gap-1 group-hover:translate-x-0.5 transition-transform"
                          >
                            <span>Ask AI Guide</span>
                            <ArrowRight className="w-3 h-3" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* UMS 234 Services Catalogue Section */}
              {(activeTab === 'all' || activeTab === 'ums') && filteredServices.length > 0 && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                      <Compass className="w-4 h-4 text-indigo-600" />
                      UMS Service Pathways (234 Official Catalogue Items)
                    </h3>
                    <span className="text-[11px] text-slate-500">Direct Navigation Breadcrumbs</span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {filteredServices.slice(0, activeTab === 'all' ? 4 : 20).map((s, idx) => (
                      <div
                        key={idx}
                        className="bg-white p-3.5 rounded-xl border border-warm-border hover:border-indigo-300 hover:shadow-xs transition-all space-y-1.5 group"
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded">
                            {s.module}
                          </span>
                          <span className="text-[10px] text-slate-400">Authenticated UMS</span>
                        </div>
                        <h4 className="text-xs font-bold text-slate-900">{s.service_label}</h4>
                        <div className="bg-slate-50 p-2 rounded-lg text-[11px] font-mono text-slate-700 break-all border border-slate-100">
                          {s.navigation_path}
                        </div>
                        <div className="pt-1 flex items-center justify-end">
                          <button
                            onClick={() =>
                              handleLaunchQuery(
                                `How do I navigate to ${s.service_label} on UMS and what are the prerequisites?`
                              )
                            }
                            className="text-xs text-indigo-600 hover:text-indigo-800 font-semibold flex items-center gap-1"
                          >
                            <span>Ask AI Navigation</span>
                            <ArrowRight className="w-3 h-3" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Campus Explorer & Pure Veg Food Section */}
              {(activeTab === 'all' || activeTab === 'campus') && (
                <div className="space-y-3">
                  <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-emerald-600" />
                    Key Campus POIs & 100% Pure Vegetarian Dining
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div
                      onClick={() => handleLaunchQuery('Where is Block 32 and what facilities are located there?')}
                      className="bg-white p-3.5 rounded-xl border border-warm-border hover:border-emerald-300 transition-all cursor-pointer space-y-1 group"
                    >
                      <h4 className="text-xs font-bold text-slate-900 group-hover:text-emerald-700">
                        Block 32 (CSE Deanery Hub)
                      </h4>
                      <p className="text-[11px] text-slate-500">Central Academic Zone • Labs & School Office</p>
                    </div>

                    <div
                      onClick={() => handleLaunchQuery('Find verified food outlets near Block 32 inside LPU')}
                      className="bg-white p-3.5 rounded-xl border border-warm-border hover:border-emerald-300 transition-all cursor-pointer space-y-1 group"
                    >
                      <h4 className="text-xs font-bold text-slate-900 group-hover:text-emerald-700">
                        Uni-Centre & Block 34 Food Courts
                      </h4>
                      <p className="text-[11px] text-slate-500">Chhappan Bhog, Dosa Plaza, Pure Veg Stalls</p>
                    </div>

                    <div
                      onClick={() => handleLaunchQuery('Where is Uni-Hospital in Block 30 and how to book doctor appointment?')}
                      className="bg-white p-3.5 rounded-xl border border-warm-border hover:border-emerald-300 transition-all cursor-pointer space-y-1 group"
                    >
                      <h4 className="text-xs font-bold text-slate-900 group-hover:text-emerald-700">
                        Uni-Hospital (Block 30)
                      </h4>
                      <p className="text-[11px] text-slate-500">24x7 Ambulance & OPD Medical Care</p>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

