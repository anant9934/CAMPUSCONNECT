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
} from 'lucide-react';

interface TopBarProps {
  sidebarCollapsed: boolean;
  onToggleSidebar: () => void;
  currentTitle: string;
  onRenameTitle?: (newTitle: string) => void;
  selectedModel: string;
  onSelectModel: (model: string) => void;
  reasoningMode: string;
  onSelectReasoningMode: (mode: string) => void;
  onOpenLibrary: () => void;
  onOpenWorkspaces: () => void;
  onOpenSettings: () => void;
  onOpenAdmin: () => void;
  isAdminLoggedIn: boolean;
}

export const TopBar: React.FC<TopBarProps> = ({
  sidebarCollapsed,
  onToggleSidebar,
  currentTitle,
  onRenameTitle,
  selectedModel,
  onSelectModel,
  reasoningMode,
  onSelectReasoningMode,
  onOpenLibrary,
  onOpenWorkspaces,
  onOpenSettings,
  onOpenAdmin,
  isAdminLoggedIn,
}) => {
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [editedTitle, setEditedTitle] = useState(currentTitle);
  const [isModelDropdownOpen, setIsModelDropdownOpen] = useState(false);

  const modelDisplayNames: Record<string, string> = {
    'gemini': 'Gemini 3.5 Flash',
    'bazaarlink': 'BazaarLink Qwen 3.7',
    'pekpik': 'DeepSeek V4 Flash',
    'groq': 'Groq LLaMA 3.3',
    'openrouter': 'OpenRouter Ling 3.2',
    'cohere': 'Cohere Command A',
    'aionlabs': 'Aion Labs',
    'gemini-2.5-flash': 'Gemini 3.5 Flash',
  };

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

      {/* Right: Model Selector & Quick Tools */}
      <div className="flex items-center gap-2 shrink-0">
        {/* Model Selector Pill Dropdown */}
        <div className="relative">
          <button
            onClick={() => setIsModelDropdownOpen((prev) => !prev)}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-50 border border-slate-200/80 hover:bg-slate-100 text-[11px] font-medium text-slate-700 transition-all shadow-2xs"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <Sparkles className="w-3 h-3 text-orange-600" />
            <span>{modelDisplayNames[selectedModel] || 'Gemini 2.5 Flash'}</span>
            <ChevronDown className="w-3 h-3 text-slate-400" />
          </button>

          {isModelDropdownOpen && (
            <div className="absolute right-0 mt-1.5 w-56 rounded-xl border border-warm-border bg-white shadow-soft-lg py-1 z-50 text-xs">
              <div className="px-3 py-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider border-b border-slate-100">
                Select Active LLM
              </div>
              {Object.entries(modelDisplayNames).map(([mId, mLabel]) => {
                const isSelected = selectedModel === mId;
                return (
                  <button
                    key={mId}
                    onClick={() => {
                      onSelectModel(mId);
                      setIsModelDropdownOpen(false);
                    }}
                    className={`w-full text-left px-3 py-2 flex items-center justify-between hover:bg-slate-50 transition-colors ${
                      isSelected ? 'text-orange-700 font-semibold bg-orange-50/50' : 'text-slate-700'
                    }`}
                  >
                    <span>{mLabel}</span>
                    {isSelected && <span className="text-[10px] text-orange-600 font-bold">Active</span>}
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

