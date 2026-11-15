import React from 'react';
import {
  MessageSquare,
  LayoutDashboard,
  Users,
  Award,
  MapPin,
  Compass,
  Briefcase,
  ShieldAlert,
  Sparkles,
  Menu,
} from 'lucide-react';

export type PortalTab =
  | 'chat'
  | 'dashboard'
  | 'people'
  | 'benefits'
  | 'campus'
  | 'ums'
  | 'opportunities';

interface PortalHeaderProps {
  activeTab: PortalTab;
  onSelectTab: (tab: PortalTab) => void;
  onOpenAdmin: () => void;
  onToggleMobileMenu: () => void;
  llmModelName?: string;
}

export const PortalHeader: React.FC<PortalHeaderProps> = ({
  activeTab,
  onSelectTab,
  onOpenAdmin,
  onToggleMobileMenu,
  llmModelName = 'gemini-2.5-flash',
}) => {
  const tabs: { id: PortalTab; label: string; icon: React.ReactNode }[] = [
    { id: 'chat', label: 'AI Assistant', icon: <MessageSquare className="w-4 h-4" /> },
    { id: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
    { id: 'people', label: 'People & Experts', icon: <Users className="w-4 h-4" /> },
    { id: 'benefits', label: 'Academic Benefits', icon: <Award className="w-4 h-4" /> },
    { id: 'campus', label: 'Campus & Food', icon: <MapPin className="w-4 h-4" /> },
    { id: 'ums', label: 'UMS Navigator', icon: <Compass className="w-4 h-4" /> },
    { id: 'opportunities', label: 'Opportunities', icon: <Briefcase className="w-4 h-4" /> },
  ];

  return (
    <header className="bg-white border-b border-warm-border sticky top-0 z-30 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo & Mobile Trigger */}
          <div className="flex items-center gap-3">
            <button
              onClick={onToggleMobileMenu}
              className="md:hidden p-2 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 focus:outline-none"
              aria-label="Toggle Navigation"
            >
              <Menu className="w-5 h-5" />
            </button>

            <div
              onClick={() => onSelectTab('dashboard')}
              className="flex items-center gap-2 cursor-pointer group"
            >
              <div className="w-9 h-9 rounded-xl bg-orange-600 flex items-center justify-center text-white font-bold text-lg shadow-sm group-hover:scale-105 transition-transform">
                L
              </div>
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="font-bold text-slate-900 tracking-tight text-base">CampusConnect</span>
                  <span className="text-[10px] bg-orange-100 text-orange-700 font-semibold px-1.5 py-0.5 rounded-full border border-orange-200">
                    LPU v8.0
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 leading-none">AI University Student Portal</p>
              </div>
            </div>
          </div>

          {/* Navigation Tabs (Desktop) */}
          <nav className="hidden lg:flex items-center gap-1">
            {tabs.map((tab) => {
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => onSelectTab(tab.id)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-orange-50 text-orange-700 shadow-xs border border-orange-200/60 font-semibold'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  <span className={isActive ? 'text-orange-600' : 'text-slate-400'}>{tab.icon}</span>
                  {tab.label}
                </button>
              );
            })}
          </nav>

          {/* Right Tools: LLM Model Status & Admin Access */}
          <div className="flex items-center gap-2">
            {/* Live Model Badge */}
            <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200/70 text-emerald-800 text-[11px] font-medium">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <Sparkles className="w-3 h-3 text-emerald-600" />
              <span>{llmModelName}</span>
            </div>

            {/* Admin Portal Button */}
            <button
              onClick={onOpenAdmin}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-slate-700 hover:text-slate-900 hover:bg-slate-50 text-xs font-medium transition-colors"
              title="Administrator Management Portal"
            >
              <ShieldAlert className="w-3.5 h-3.5 text-slate-500" />
              <span className="hidden sm:inline">Admin</span>
            </button>
          </div>
        </div>
      </div>

      {/* Sub-nav for tablet / medium screens */}
      <div className="lg:hidden flex items-center overflow-x-auto px-4 py-2 border-t border-slate-100 gap-1 bg-slate-50/60 no-scrollbar">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => onSelectTab(tab.id)}
              className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs whitespace-nowrap transition-all ${
                isActive
                  ? 'bg-orange-600 text-white font-medium shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          );
        })}
      </div>
    </header>
  );
};
