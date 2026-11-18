import React, { useState } from 'react';
import {
  PanelLeft,
  Sparkles,
  BookOpen,
  Briefcase,
  Settings as SettingsIcon,
  ShieldCheck,
  ChevronDown,
  Edit2,
  Check,
  X,
  Zap,
  Brain,
  Search,
  Code2,
  Shield,
  Compass,
  Eye,
} from 'lucide-react';

interface TopBarProps {
  sidebarCollapsed: boolean;
  onToggleSidebar: () => void;
  currentTitle: string;
  onRenameTitle?: (newTitle: string) => void;
  selectedModel: string;
  onSelectModel: (model: string) => void;
  reasoningMode?: string;
  onSelectReasoningMode?: (mode: string) => void;
  thinkingLevel?: string;
  onSelectThinkingLevel?: (level: string) => void;
  onOpenLibrary: () => void;
  onOpenWorkspaces: () => void;
  onOpenSettings: () => void;
  onOpenAdmin: () => void;
  isAdminLoggedIn: boolean;
}

const SPECIALIST_META: Record<
  string,
  { name: string; subtitle: string; icon: React.ReactNode; color: string }
> = {
  auto: {
    name: 'Auto',
    subtitle: 'Dynamic Intelligence',
    icon: <Sparkles className="w-3.5 h-3.5 text-orange-600" />,
    color: 'text-orange-600',
  },
  nova: {
    name: 'NOVA',
    subtitle: 'Everyday Intelligence',
    icon: <Zap className="w-3.5 h-3.5 text-amber-500" />,
    color: 'text-amber-600',
  },
  themis: {
    name: 'THEMIS',
    subtitle: 'University Intelligence',
    icon: <Shield className="w-3.5 h-3.5 text-orange-600" />,
    color: 'text-orange-600',
  },
  athena: {
    name: 'ATHENA',
    subtitle: 'Advanced Intelligence',
    icon: <Brain className="w-3.5 h-3.5 text-indigo-600" />,
    color: 'text-indigo-600',
  },
  oracle: {
    name: 'ORACLE',
    subtitle: 'Research Intelligence',
    icon: <Search className="w-3.5 h-3.5 text-emerald-600" />,
    color: 'text-emerald-600',
  },
  aegis: {
    name: 'Auto',
    subtitle: 'Dynamic Intelligence',
    icon: <Sparkles className="w-3.5 h-3.5 text-orange-600" />,
    color: 'text-orange-600',
  },
};

const SELECTOR_OPTIONS = ['auto', 'nova', 'themis', 'athena', 'oracle'];

export const TopBar: React.FC<TopBarProps> = ({
  sidebarCollapsed,
  onToggleSidebar,
  currentTitle,
  onRenameTitle,
  selectedModel,
  onSelectModel,
  onOpenLibrary,
  onOpenWorkspaces,
  onOpenSettings,
  onOpenAdmin,
  isAdminLoggedIn,
}) => {
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [editedTitle, setEditedTitle] = useState(currentTitle);
  const [isModelDropdownOpen, setIsModelDropdownOpen] = useState(false);

  const activeMeta = SPECIALIST_META[selectedModel] || SPECIALIST_META.aegis;

  const handleSaveTitle = () => {
    if (editedTitle.trim() && onRenameTitle) {
      onRenameTitle(editedTitle.trim());
    }
    setIsEditingTitle(false);
  };

  return (
    <header className="h-14 border-b border-warm-border bg-white/90 backdrop-blur-md sticky top-0 z-20 flex items-center justify-between px-3 sm:px-5 shadow-2xs">
      {/* Left: Sidebar Toggle & Conversation Title */}
      <div className="flex items-center gap-2 sm:gap-3 min-w-0">
        <button
          onClick={onToggleSidebar}
          className="p-1.5 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors shrink-0"
          title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <PanelLeft className="w-4 h-4" />
        </button>

        {isEditingTitle ? (
          <div className="flex items-center gap-1.5 min-w-0">
            <input
              type="text"
              value={editedTitle}
              onChange={(e) => setEditedTitle(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleSaveTitle();
                if (e.key === 'Escape') setIsEditingTitle(false);
              }}
              autoFocus
              className="text-xs font-semibold text-slate-800 border border-orange-300 rounded px-2 py-0.5 focus:outline-none bg-orange-50/30"
            />
            <button
              onClick={handleSaveTitle}
              className="p-1 text-emerald-600 hover:bg-emerald-50 rounded"
            >
              <Check className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setIsEditingTitle(false)}
              className="p-1 text-slate-400 hover:bg-slate-100 rounded"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-2 truncate group">
            <span
              onClick={() => {
                setEditedTitle(currentTitle);
                setIsEditingTitle(true);
              }}
              className="text-xs sm:text-sm font-semibold text-slate-800 truncate cursor-pointer hover:text-orange-700 transition-colors"
              title="Click to rename"
            >
              {currentTitle || 'New Conversation'}
            </span>
            <button
              onClick={() => {
                setEditedTitle(currentTitle);
                setIsEditingTitle(true);
              }}
              className="opacity-0 group-hover:opacity-100 p-0.5 text-slate-400 hover:text-slate-600 transition-opacity"
            >
              <Edit2 className="w-3 h-3" />
            </button>
          </div>
        )}
      </div>

      {/* Right: Specialist Intelligence Selector & Quick Tools */}
      <div className="flex items-center gap-2 shrink-0">
        {/* Model Selector Pill Dropdown */}
        <div className="relative">
          <button
            onClick={() => setIsModelDropdownOpen((prev) => !prev)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-50 border border-slate-200/90 hover:bg-slate-100 text-xs font-semibold text-slate-700 transition-all shadow-2xs"
            title="Active Intelligence Specialist"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            {activeMeta.icon}
            <span>{activeMeta.name}</span>
            <span className="text-[11px] font-normal text-slate-400 hidden sm:inline">· {activeMeta.subtitle}</span>
            <ChevronDown className="w-3 h-3 text-slate-400" />
          </button>

          {isModelDropdownOpen && (
            <div className="absolute right-0 mt-1.5 w-72 rounded-2xl border border-warm-border bg-white shadow-xl py-1.5 z-50 text-xs space-y-0.5 animate-fadeIn">
              <div className="px-3 py-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider border-b border-slate-100 flex items-center justify-between">
                <span>Select Intelligence</span>
                <span className="text-[9px] text-orange-600 font-mono">5 Identities</span>
              </div>
              {SELECTOR_OPTIONS.map((id) => {
                const meta = SPECIALIST_META[id];
                const isSelected = selectedModel === id || (id === 'auto' && selectedModel === 'aegis');
                return (
                  <button
                    key={id}
                    onClick={() => {
                      onSelectModel(id);
                      setIsModelDropdownOpen(false);
                    }}
                    className={`w-full text-left px-3 py-2 flex items-center gap-2.5 transition-colors ${
                      isSelected
                        ? 'bg-orange-50 text-orange-950 font-semibold'
                        : 'text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    <div className="shrink-0">{meta.icon}</div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold">{meta.name}</span>
                        {isSelected && <span className="text-[10px] text-orange-600 font-bold">Active</span>}
                      </div>
                      <div className="text-[11px] text-slate-500">{meta.subtitle}</div>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Library Button */}
        <button
          onClick={onOpenLibrary}
          className="hidden md:flex items-center gap-1 px-2.5 py-1 rounded-lg border border-slate-200/80 hover:bg-slate-50 text-[11px] font-medium text-slate-700 transition-colors"
          title="Browse university library and policies"
        >
          <BookOpen className="w-3.5 h-3.5 text-orange-600" />
          <span>Library</span>
        </button>

        {/* Workspaces Button */}
        <button
          onClick={onOpenWorkspaces}
          className="hidden md:flex items-center gap-1 px-2.5 py-1 rounded-lg border border-slate-200/80 hover:bg-slate-50 text-[11px] font-medium text-slate-700 transition-colors"
          title="Open focused workspaces"
        >
          <Briefcase className="w-3.5 h-3.5 text-indigo-600" />
          <span>Workspaces</span>
        </button>

        {/* Settings Button */}
        <button
          onClick={onOpenSettings}
          className="p-1.5 rounded-lg border border-slate-200/80 text-slate-500 hover:text-slate-800 hover:bg-slate-50 transition-colors"
          title="Settings & Quota"
        >
          <SettingsIcon className="w-4 h-4" />
        </button>

        {/* Admin Portal Button */}
        <button
          onClick={onOpenAdmin}
          className={`flex items-center gap-1 px-2.5 py-1 rounded-lg border text-[11px] font-medium transition-colors ${
            isAdminLoggedIn
              ? 'border-orange-300 bg-orange-50 text-orange-700'
              : 'border-slate-200/80 text-slate-600 hover:bg-slate-50'
          }`}
          title="Administrative Management"
        >
          <ShieldCheck className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">{isAdminLoggedIn ? 'Admin Active' : 'Admin'}</span>
        </button>
      </div>
    </header>
  );
};
