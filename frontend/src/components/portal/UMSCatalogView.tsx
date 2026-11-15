import React, { useState, useEffect } from 'react';
import {
  Compass,
  Search,
  ExternalLink,
  ShieldCheck,
  ArrowRight,
  Filter,
} from 'lucide-react';
import { api } from '../../services/api';

interface UMSCatalogViewProps {
  onAskAI: (query: string) => void;
}

export const UMSCatalogView: React.FC<UMSCatalogViewProps> = ({ onAskAI }) => {
  const [catalog, setCatalog] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedModule, setSelectedModule] = useState<string>('All');
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const modules = [
    'All',
    'Academics',
    'Examination',
    'Fee Management',
    'Hostel Management',
    'Health Services',
    'Relationship Management System',
    'Library Services',
    'Placement Services',
  ];

  useEffect(() => {
    loadCatalog();
  }, []);

  const loadCatalog = async () => {
    try {
      setIsLoading(true);
      const data = await api.getAdminUMSCatalog();
      setCatalog(data || []);
    } catch (err) {
      console.error('Failed to load UMS catalog:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const filtered = catalog.filter((item) => {
    const matchesSearch =
      item.service_label.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.navigation_path.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.module.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesModule =
      selectedModule === 'All' || item.module.toLowerCase().includes(selectedModule.toLowerCase());

    return matchesSearch && matchesModule;
  });

  return (
    <div className="flex-1 overflow-y-auto bg-warm-bg p-4 sm:p-6 lg:p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-2xl border border-warm-border p-6 shadow-xs space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700 text-xs font-semibold mb-2">
                <Compass className="w-3.5 h-3.5" />
                <span>234 Verified UMS Menu Entries</span>
              </div>
              <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
                UMS Action Centre & Service Navigator
              </h1>
              <p className="text-xs sm:text-sm text-slate-500 max-w-2xl mt-1">
                Natural-language discovery, verified navigation breadcrumbs, and authenticated portal handoff links across all official LPU University Management System modules.
              </p>
            </div>

            <div className="text-right">
              <span className="text-2xl font-black text-slate-900">{filtered.length}</span>
              <span className="text-xs text-slate-500 block">Services Listed</span>
            </div>
          </div>

          {/* Search Input */}
          <div className="flex flex-col sm:flex-row gap-3 pt-2 border-t border-slate-100">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
              <input
                type="text"
                placeholder="Search by service name, module, or task (e.g. datesheet, fee receipt, hostel leave)..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs sm:text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500"
              />
            </div>
          </div>

          {/* Module Filter Pills */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 no-scrollbar">
            {modules.map((mod) => (
              <button
                key={mod}
                onClick={() => setSelectedModule(mod)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
                  selectedModule === mod
                    ? 'bg-orange-600 text-white shadow-xs'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200/80 hover:text-slate-900'
                }`}
              >
                {mod}
              </button>
            ))}
          </div>
        </div>

        {/* Services List */}
        {isLoading ? (
          <div className="py-12 flex justify-center">
            <div className="w-8 h-8 border-3 border-orange-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="bg-white rounded-2xl border border-warm-border p-8 text-center space-y-2">
            <p className="text-sm font-semibold text-slate-700">No UMS services matched your query.</p>
            <p className="text-xs text-slate-500">Try searching with a broader keyword or resetting the module filter.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
            {filtered.map((item) => (
              <div
                key={item.id}
                className="bg-white rounded-2xl border border-warm-border p-4 shadow-xs hover:border-orange-300 transition-all space-y-3 flex flex-col justify-between"
              >
                <div className="space-y-1.5">
                  <div className="flex items-start justify-between gap-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-600 bg-slate-100 px-2 py-0.5 rounded">
                      {item.module}
                    </span>
                    <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200">
                      {item.verification_status}
                    </span>
                  </div>

                  <h3 className="text-xs font-bold text-slate-900 leading-snug">{item.service_label}</h3>

                  <div className="p-2 rounded-lg bg-slate-50 border border-slate-100 text-[11px] font-mono text-slate-700 break-words">
                    {item.navigation_path}
                  </div>
                </div>

                <div className="pt-2.5 border-t border-slate-100 flex items-center justify-between gap-2">
                  <a
                    href={item.deep_link_url || 'https://ums.lpu.in/lpuums/'}
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs text-orange-600 hover:text-orange-700 font-semibold flex items-center gap-1"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                    Open UMS
                  </a>

                  <button
                    onClick={() => onAskAI(`Explain the step-by-step procedure and requirements for ${item.service_label} (${item.navigation_path}) in UMS.`)}
                    className="text-[11px] text-slate-500 hover:text-slate-800 font-medium"
                  >
                    Explain Steps
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
