import React, { useState, useEffect } from 'react';
import {
  Briefcase,
  Search,
  ExternalLink,
  Calendar,
  Award,
  Sparkles,
  ArrowRight,
  Filter,
} from 'lucide-react';
import { api } from '../../services/api';

interface OpportunitiesViewProps {
  onAskAI: (query: string) => void;
}

export const OpportunitiesView: React.FC<OpportunitiesViewProps> = ({ onAskAI }) => {
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [selectedType, setSelectedType] = useState<string>('all');
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const types = [
    { id: 'all', label: 'All Opportunities' },
    { id: 'placement', label: 'Placements' },
    { id: 'hackathon', label: 'Hackathons' },
    { id: 'internship', label: 'Research Internships' },
    { id: 'competition', label: 'Incubation & Grants' },
    { id: 'international', label: 'Semester Abroad' },
  ];

  useEffect(() => {
    loadOpps();
  }, [selectedType]);

  const loadOpps = async () => {
    try {
      setIsLoading(true);
      const data = await api.getOpportunities(selectedType === 'all' ? undefined : selectedType);
      setOpportunities(data);
    } catch (err) {
      console.error('Failed to load opportunities:', err);
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
              <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700 text-xs font-semibold mb-2">
                <Briefcase className="w-3.5 h-3.5" />
                <span>Division of Career Services & Innovation</span>
              </div>
              <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
                Campus Opportunities & Career Hub
              </h1>
              <p className="text-xs sm:text-sm text-slate-500 max-w-2xl mt-1">
                Verified placement drives, national hackathons, funded research internships, Startup School grants, and international semester exchange programs.
              </p>
            </div>

            <div className="text-right">
              <span className="text-2xl font-black text-slate-900">{opportunities.length}</span>
              <span className="text-xs text-slate-500 block">Active Listings</span>
            </div>
          </div>

          {/* Type Filter Pills */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar pt-2 border-t border-slate-100">
            {types.map((t) => (
              <button
                key={t.id}
                onClick={() => setSelectedType(t.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors ${
                  selectedType === t.id
                    ? 'bg-orange-600 text-white shadow-xs'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200/80 hover:text-slate-900'
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>

        {/* Opportunities List Grid */}
        {isLoading ? (
          <div className="py-12 flex justify-center">
            <div className="w-8 h-8 border-3 border-orange-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : opportunities.length === 0 ? (
          <div className="bg-white rounded-2xl border border-warm-border p-8 text-center space-y-2">
            <p className="text-sm font-semibold text-slate-700">No active opportunities found in this category.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {opportunities.map((opp) => (
              <div
                key={opp.id}
                className="bg-white rounded-2xl border border-warm-border p-5 shadow-xs hover:border-orange-300 transition-all space-y-3.5 flex flex-col justify-between"
              >
                <div className="space-y-2.5">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200/60">
                        {opp.opportunity_type}
                      </span>
                      <h3 className="text-base font-bold text-slate-900 mt-1">{opp.title}</h3>
                      <p className="text-xs text-slate-500">{opp.organizer}</p>
                    </div>

                    {opp.deadline && (
                      <span className="text-[11px] font-semibold text-rose-700 bg-rose-50 px-2 py-0.5 rounded shrink-0">
                        Deadline: {opp.deadline}
                      </span>
                    )}
                  </div>

                  <p className="text-xs text-slate-600 leading-relaxed">{opp.description}</p>

                  <div className="space-y-1.5 pt-1 text-xs">
                    <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                      <span className="font-bold text-slate-700 block">Eligibility:</span>
                      <p className="text-slate-600">{opp.eligibility}</p>
                    </div>

                    {opp.stipend_or_reward && (
                      <div className="p-2.5 rounded-lg bg-emerald-50/60 border border-emerald-100 text-emerald-900">
                        <span className="font-bold block">Compensation / Benefits:</span>
                        <p>{opp.stipend_or_reward}</p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                  <span className="text-[11px] text-slate-500 font-mono truncate max-w-[200px]">
                    {opp.application_link}
                  </span>

                  <button
                    onClick={() => onAskAI(`How do I apply for ${opp.title} and what are the specific criteria and deadlines on UMS?`)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-orange-50 hover:bg-orange-100/80 text-orange-700 text-xs font-semibold transition-colors shrink-0"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    Apply via AI
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
