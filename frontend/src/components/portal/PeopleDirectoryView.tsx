import React, { useState, useEffect } from 'react';
import {
  Users,
  Search,
  Filter,
  MapPin,
  Mail,
  AlertTriangle,
  CheckCircle2,
  ExternalLink,
  MessageSquare,
  Sparkles,
} from 'lucide-react';
import { api } from '../../services/api';

interface PeopleDirectoryViewProps {
  onAskAI: (query: string) => void;
}

export const PeopleDirectoryView: React.FC<PeopleDirectoryViewProps> = ({ onAskAI }) => {
  const [people, setPeople] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedExpertise, setSelectedExpertise] = useState<string>('All');
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const expertiseCategories = [
    'All',
    'Artificial Intelligence',
    'Machine Learning',
    'Cybersecurity',
    'Web Development',
    'Cloud Computing',
    'Data Science',
    'Robotics',
    'Research & Innovation',
  ];

  useEffect(() => {
    loadPeople();
  }, [selectedExpertise, searchTerm]);

  const loadPeople = async () => {
    try {
      setIsLoading(true);
      const params: any = {};
      if (selectedExpertise !== 'All') {
        params.expertise = selectedExpertise;
      }
      if (searchTerm.trim()) {
        params.search = searchTerm.trim();
      }
      const data = await api.getPeople(params);
      setPeople(data.people || []);
    } catch (err) {
      console.error('Failed to load people:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto bg-warm-bg p-4 sm:p-6 lg:p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-2xl border border-warm-border p-6 shadow-xs space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-semibold mb-2">
                <Users className="w-3.5 h-3.5" />
                <span>Verified Public Directory</span>
              </div>
              <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
                People & Expert Discovery
              </h1>
              <p className="text-xs sm:text-sm text-slate-500 max-w-2xl mt-1">
                Browse verified university leadership, School HODs, Deans, research mentors, and domain experts. Personal cabin numbers are unverified in public records; consult Block 32 reception for appointments.
              </p>
            </div>

            {/* Quick Count Badge */}
            <div className="text-right whitespace-nowrap">
              <span className="text-2xl font-black text-slate-900">{people.length}</span>
              <span className="text-xs text-slate-500 block">Profiles Listed</span>
            </div>
          </div>

          {/* Search & Filter Controls */}
          <div className="flex flex-col sm:flex-row gap-3 pt-2 border-t border-slate-100">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
              <input
                type="text"
                placeholder="Search by faculty name, title, or keywords..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs sm:text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500"
              />
            </div>
          </div>

          {/* Expertise Category Pills */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 no-scrollbar">
            {expertiseCategories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedExpertise(cat)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
                  selectedExpertise === cat
                    ? 'bg-orange-600 text-white shadow-xs'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200/70 hover:text-slate-900'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Directory Cards Grid */}
        {isLoading ? (
          <div className="py-12 flex justify-center">
            <div className="w-8 h-8 border-3 border-orange-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : people.length === 0 ? (
          <div className="bg-white rounded-2xl border border-warm-border p-8 text-center space-y-2">
            <p className="text-sm font-semibold text-slate-700">No faculty members found matching your search.</p>
            <p className="text-xs text-slate-500">Try clearing your search query or selecting 'All' expertise.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {people.map((person) => (
              <div
                key={person.person_id}
                className="bg-white rounded-2xl border border-warm-border p-5 shadow-xs hover:border-orange-300 transition-all space-y-3.5 flex flex-col justify-between"
              >
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h3 className="text-base font-bold text-slate-900 flex items-center gap-1.5">
                        {person.full_name}
                      </h3>
                      <p className="text-xs font-medium text-orange-700">{person.designation}</p>
                      <p className="text-[11px] text-slate-500">{person.school_division}</p>
                    </div>

                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                      {person.evidence_status}
                    </span>
                  </div>

                  {/* Location & Room */}
                  <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100 text-xs space-y-1">
                    <div className="flex items-center gap-1.5 text-slate-700 font-medium">
                      <MapPin className="w-3.5 h-3.5 text-slate-400" />
                      <span>{person.building_block} — {person.room_cabin}</span>
                    </div>

                    {!person.office_seating_verified && (
                      <div className="flex items-start gap-1.5 text-[11px] text-amber-700 pt-1 border-t border-slate-200/50">
                        <AlertTriangle className="w-3.5 h-3.5 text-amber-500 shrink-0 mt-0.5" />
                        <span>Seating unverified in public directory. Consult Ground Floor Reception.</span>
                      </div>
                    )}
                  </div>

                  {/* Notes / Special Distinction */}
                  {person.notes && (
                    <p className="text-xs text-slate-600 bg-orange-50/40 p-2.5 rounded-xl border border-orange-100/70 leading-relaxed">
                      💡 {person.notes}
                    </p>
                  )}
                </div>

                {/* Card Actions */}
                <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                  {person.email ? (
                    <a
                      href={`mailto:${person.email}`}
                      className="text-xs text-slate-600 hover:text-slate-900 flex items-center gap-1 truncate"
                    >
                      <Mail className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span className="truncate">{person.email}</span>
                    </a>
                  ) : (
                    <span className="text-xs text-slate-400 italic">Email not listed</span>
                  )}

                  <button
                    onClick={() => onAskAI(`Tell me about ${person.full_name} (${person.designation}) and how I can meet them for academic guidance.`)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-orange-50 hover:bg-orange-100/80 text-orange-700 text-xs font-semibold transition-colors shrink-0"
                  >
                    <MessageSquare className="w-3.5 h-3.5" />
                    Ask AI
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
