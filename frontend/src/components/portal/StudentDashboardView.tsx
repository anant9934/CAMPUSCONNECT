import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  Calendar,
  AlertCircle,
  ExternalLink,
  BookOpen,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Clock,
  Compass,
  Award,
  Users,
  MapPin,
  UtensilsCrossed,
} from 'lucide-react';
import { api } from '../../services/api';

interface StudentDashboardViewProps {
  onAskAI: (query: string) => void;
  onNavigateTab: (tab: any) => void;
}

export const StudentDashboardView: React.FC<StudentDashboardViewProps> = ({
  onAskAI,
  onNavigateTab,
}) => {
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setIsLoading(true);
      const data = await api.getDashboard();
      setDashboardData(data);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading || !dashboardData) {
    return (
      <div className="flex-1 flex items-center justify-center p-8 bg-slate-50/50">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-3 border-orange-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-xs text-slate-500 font-medium">Loading LPU Student Hub...</p>
        </div>
      </div>
    );
  }

  const { profile, welcome_message, important_deadlines, verified_notices, recommended_services } = dashboardData;

  const quickPrompts = [
    { label: 'Attendance Low Problem', query: 'My attendance is very low. Can I do something to get attendance benefits?', icon: <AlertCircle className="w-3.5 h-3.5 text-rose-600" /> },
    { label: 'CA Exemption via Project', query: 'I have built an AI cybersecurity platform. Can I get CA exemption?', icon: <Award className="w-3.5 h-3.5 text-amber-600" /> },
    { label: 'Startup Revenue Benefits', query: 'I want to build a startup. Can I earn revenue and receive academic benefits?', icon: <Award className="w-3.5 h-3.5 text-emerald-600" /> },
    { label: 'Cybersecurity Faculty Guide', query: 'Who can guide me with cybersecurity at LPU?', icon: <Users className="w-3.5 h-3.5 text-blue-600" /> },
    { label: 'Meet University Leadership', query: 'How can I meet the Pro Chancellor?', icon: <ShieldCheck className="w-3.5 h-3.5 text-indigo-600" /> },
    { label: 'Disciplinary & Proctorial Help', query: 'I have an indiscipline case. How should I approach the university?', icon: <AlertCircle className="w-3.5 h-3.5 text-amber-600" /> },
    { label: 'Best Soya Chaap in LPU', query: 'Find the best soya chaap near me inside LPU', icon: <UtensilsCrossed className="w-3.5 h-3.5 text-orange-600" /> },
    { label: 'Who is AI & ML HOD?', query: 'Who is the AI & ML HOD and where is his office located?', icon: <Users className="w-3.5 h-3.5 text-blue-600" /> },
    { label: 'Where is Block 32?', query: 'Where is Block 32 and what facilities are available there?', icon: <MapPin className="w-3.5 h-3.5 text-emerald-600" /> },
  ];

  return (
    <div className="flex-1 overflow-y-auto bg-warm-bg p-4 sm:p-6 lg:p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Welcome & Student Profile Header Card */}
        <div className="bg-white rounded-2xl border border-warm-border p-6 shadow-xs relative overflow-hidden">
          <div className="absolute top-0 right-0 w-80 h-80 bg-gradient-to-bl from-orange-100/50 via-amber-50/30 to-transparent rounded-full blur-2xl -mr-20 -mt-20 pointer-events-none" />

          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
            <div className="space-y-2">
              <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-orange-100/80 text-orange-800 text-xs font-semibold">
                <Sparkles className="w-3.5 h-3.5 text-orange-600" />
                <span>Academic Session {profile.academic_session}</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
                Welcome, {profile.full_name} 👋
              </h1>
              <p className="text-sm text-slate-600 max-w-2xl leading-relaxed">
                {welcome_message}
              </p>
            </div>

            {/* Profile Snapshot Badge */}
            <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-4 min-w-[280px] space-y-2 text-xs">
              <div className="flex justify-between items-center pb-2 border-b border-slate-200/60">
                <span className="text-slate-500 font-medium">Programme</span>
                <span className="font-semibold text-slate-800">{profile.programme}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-500 font-medium">Specialisation</span>
                <span className="font-semibold text-orange-700">{profile.specialisation}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-500 font-medium">Semester</span>
                <span className="font-semibold text-slate-800">Semester {profile.current_semester}</span>
              </div>
              <div className="flex justify-between items-center pt-2 border-t border-slate-200/60">
                <span className="text-slate-500 font-medium">Private Records</span>
                <span className="inline-flex items-center gap-1 text-[11px] text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200 font-medium">
                  <ShieldCheck className="w-3 h-3" />
                  Protected in UMS
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Quick AI Assistance Hub */}
        <div className="bg-white rounded-2xl border border-warm-border p-5 shadow-xs">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-orange-600" />
              Ask AI Campus Assistant
            </h2>
            <span className="text-xs text-slate-500">Tap to start query</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
            {quickPrompts.map((item, idx) => (
              <button
                key={idx}
                onClick={() => onAskAI(item.query)}
                className="flex items-center gap-3 p-3 rounded-xl border border-slate-200/80 hover:border-orange-300 hover:bg-orange-50/40 text-left transition-all group"
              >
                <div className="p-2 rounded-lg bg-slate-100 group-hover:bg-white group-hover:shadow-xs transition-colors">
                  {item.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-xs font-semibold text-slate-800 group-hover:text-orange-700 truncate">
                    {item.label}
                  </div>
                  <div className="text-[11px] text-slate-500 truncate">
                    {item.query}
                  </div>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-orange-600 group-hover:translate-x-0.5 transition-transform" />
              </button>
            ))}
          </div>
        </div>

        {/* Main Grid: Deadlines + Verified Notices */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Important Deadlines Card */}
          <div className="bg-white rounded-2xl border border-warm-border p-5 shadow-xs space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Clock className="w-4 h-4 text-rose-600" />
                Critical Academic Deadlines
              </h2>
              <span className="text-xs font-medium text-slate-500">Official Calendar</span>
            </div>

            <div className="space-y-3">
              {important_deadlines.map((dl: any, idx: number) => (
                <div
                  key={idx}
                  className="p-3.5 rounded-xl border border-slate-100 bg-slate-50/70 hover:bg-slate-100/60 transition-colors flex items-start justify-between gap-3"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-200 text-slate-700">
                        {dl.category}
                      </span>
                      {dl.is_critical && (
                        <span className="text-[10px] font-bold px-1.5 py-0.2 rounded bg-rose-100 text-rose-700">
                          Active
                        </span>
                      )}
                    </div>
                    <h3 className="text-xs font-semibold text-slate-800">{dl.title}</h3>
                    <p className="text-[11px] text-slate-500">{dl.action_url}</p>
                  </div>

                  <div className="text-right whitespace-nowrap">
                    <span className="text-xs font-bold text-rose-700 block">{dl.deadline_date}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Verified Institutional Notices */}
          <div className="bg-white rounded-2xl border border-warm-border p-5 shadow-xs space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-orange-600" />
                Verified University Notices
              </h2>
              <span className="text-xs font-medium text-emerald-700 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                Audited Nov 2026
              </span>
            </div>

            <div className="space-y-3">
              {verified_notices.map((ntc: any, idx: number) => (
                <div
                  key={idx}
                  className="p-3.5 rounded-xl border border-slate-100 bg-slate-50/70 hover:bg-slate-100/60 transition-colors space-y-1.5"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-orange-100 text-orange-800">
                      {ntc.category}
                    </span>
                    <span className="text-[11px] text-slate-400">{ntc.date}</span>
                  </div>
                  <h3 className="text-xs font-semibold text-slate-800">{ntc.title}</h3>
                  <p className="text-[11px] text-slate-600 leading-relaxed">{ntc.snippet}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recommended UMS Services Navigation Grid */}
        <div className="bg-white rounded-2xl border border-warm-border p-5 shadow-xs space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Compass className="w-4 h-4 text-indigo-600" />
                Recommended UMS Services & Pathways
              </h2>
              <p className="text-xs text-slate-500">Verified official breadcrumbs across 234 UMS catalogue items</p>
            </div>
            <button
              onClick={() => onNavigateTab('ums')}
              className="text-xs text-orange-600 hover:text-orange-700 font-semibold flex items-center gap-1"
            >
              Browse All 234 Services <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {recommended_services.map((svc: any, idx: number) => (
              <div
                key={idx}
                className="p-3 rounded-xl border border-slate-200/80 bg-slate-50/50 hover:bg-white hover:shadow-xs transition-all space-y-2"
              >
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold text-slate-800">{svc.name}</h3>
                  <a
                    href={svc.url}
                    target="_blank"
                    rel="noreferrer"
                    className="p-1 rounded text-slate-400 hover:text-orange-600"
                    title="Open official UMS"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
                <div className="text-[11px] text-slate-600 font-mono bg-white p-1.5 rounded border border-slate-200 truncate">
                  {svc.breadcrumb}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
