import React, { useState, useEffect } from 'react';
import {
  GraduationCap,
  Plus,
  Search,
  MessageSquare,
  Bookmark,
  BookOpen,
  Briefcase,
  Settings as SettingsIcon,
  ShieldCheck,
  PanelLeftClose,
  PanelLeftOpen,
  Trash2,
  Edit2,
  Check,
  X,
  ExternalLink,
  User,
  Star,
  Sparkles,
  Award,
  Users,
  Compass,
  MapPin,
  HelpCircle,
} from 'lucide-react';
import { ConversationSummary } from '../types';

interface SidebarProps {
  conversations: ConversationSummary[];
  currentConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onNewChat: () => void;
  onDeleteConversation: (id: string, e: React.MouseEvent) => void;
  onRenameConversation?: (id: string, newTitle: string) => void;
  onOpenSearch: () => void;
  onOpenLibrary: () => void;
  onOpenWorkspaces: () => void;
  onOpenSettings: () => void;
  onOpenAdmin: () => void;
  isAdminLoggedIn: boolean;
  isOpenMobile: boolean;
  onCloseMobile: () => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  studentProfile?: {
    full_name?: string;
    registration_number?: string;
    programme?: string;
    specialisation?: string;
    current_semester?: number;
    is_connected?: boolean;
  } | null;
}

export const Sidebar: React.FC<SidebarProps> = ({
  conversations,
  currentConversationId,
  onSelectConversation,
  onNewChat,
  onDeleteConversation,
  onRenameConversation,
  onOpenSearch,
  onOpenLibrary,
  onOpenWorkspaces,
  onOpenSettings,
  onOpenAdmin,
  isAdminLoggedIn,
  isOpenMobile,
  onCloseMobile,
  isCollapsed,
  onToggleCollapse,
  studentProfile,
}) => {
  const [editingConvId, setEditingConvId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState('');
  const [savedConvIds, setSavedConvIds] = useState<string[]>(() => {
    try {
      const saved = localStorage.getItem('campusconnect_saved_chats');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });
  const [activeTab, setActiveTab] = useState<'recent' | 'saved'>('recent');

  useEffect(() => {
    try {
      localStorage.setItem('campusconnect_saved_chats', JSON.stringify(savedConvIds));
    } catch (e) {
      console.error('Failed to save starred conversations', e);
    }
  }, [savedConvIds]);

  const toggleSaveConversation = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setSavedConvIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const handleStartRename = (conv: ConversationSummary, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingConvId(conv.id);
    setEditingTitle(conv.title);
  };

  const handleSaveRename = (id: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    if (editingTitle.trim() && onRenameConversation) {
      onRenameConversation(id, editingTitle.trim());
    }
    setEditingConvId(null);
  };

  const savedConversations = conversations.filter((c) => savedConvIds.includes(c.id));
  const displayedConversations = activeTab === 'saved' ? savedConversations : conversations;

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpenMobile && (
        <div
          className="fixed inset-0 bg-slate-900/30 backdrop-blur-xs z-40 lg:hidden"
          onClick={onCloseMobile}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 bg-slate-900 text-slate-100 z-50 flex flex-col transition-all duration-200 ease-in-out border-r border-slate-800 ${
          // Mobile state
          isOpenMobile
            ? 'translate-x-0 w-72'
            : '-translate-x-full lg:translate-x-0'
        } ${
          // Desktop collapsed vs expanded
          isCollapsed ? 'lg:w-[68px]' : 'lg:w-[260px]'
        }`}
      >
        {/* Top Header & Brand */}
        <div className="p-3.5 border-b border-slate-800/80 flex items-center justify-between">
          {!isCollapsed ? (
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center text-white shrink-0 shadow-xs">
                <GraduationCap className="w-4 h-4" />
              </div>
              <div className="min-w-0 truncate">
                <div className="font-bold text-sm tracking-tight text-white flex items-center gap-1.5">
                  CampusConnect
                  <span className="px-1 py-0.2 text-[9px] font-bold bg-orange-500/20 text-orange-400 border border-orange-500/30 rounded">
                    LPU
                  </span>
                </div>
                <p className="text-[10px] text-slate-400 font-medium truncate">Lovely Professional Univ</p>
              </div>
            </div>
          ) : (
            <div className="w-full flex justify-center">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center text-white shadow-xs">
                <GraduationCap className="w-5 h-5" />
              </div>
            </div>
          )}

          {/* Toggle sidebar button (desktop only) */}
          <button
            onClick={onToggleCollapse}
            className="hidden lg:flex p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isCollapsed ? (
              <PanelLeftOpen className="w-4 h-4" />
            ) : (
              <PanelLeftClose className="w-4 h-4" />
            )}
          </button>
        </div>

        {/* Collapsed Mode Icon Rail */}
        {isCollapsed ? (
          <div className="flex-1 flex flex-col items-center py-3 gap-2 overflow-y-auto no-scrollbar">
            {/* New Chat Icon */}
            <button
              onClick={() => {
                onNewChat();
                onCloseMobile();
              }}
              className="w-10 h-10 rounded-xl bg-orange-600 hover:bg-orange-500 text-white flex items-center justify-center transition-all shadow-xs group relative"
              title="New Chat"
            >
              <Plus className="w-5 h-5" />
              <span className="absolute left-14 bg-slate-800 text-white text-xs px-2 py-1 rounded shadow-md whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50">
                New Chat
              </span>
            </button>

            {/* Search Icon */}
            <button
              onClick={onOpenSearch}
              className="w-10 h-10 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 flex items-center justify-center transition-all group relative"
              title="Search (⌘K)"
            >
              <Search className="w-5 h-5" />
              <span className="absolute left-14 bg-slate-800 text-white text-xs px-2 py-1 rounded shadow-md whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50">
                Search (⌘K)
              </span>
            </button>

            {/* Library Icon */}
            <button
              onClick={onOpenLibrary}
              className="w-10 h-10 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 flex items-center justify-center transition-all group relative"
              title="University Library"
            >
              <BookOpen className="w-5 h-5" />
              <span className="absolute left-14 bg-slate-800 text-white text-xs px-2 py-1 rounded shadow-md whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50">
                University Library
              </span>
            </button>

            {/* Workspaces Icon */}
            <button
              onClick={onOpenWorkspaces}
              className="w-10 h-10 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 flex items-center justify-center transition-all group relative"
              title="Workspaces"
            >
              <Briefcase className="w-5 h-5" />
              <span className="absolute left-14 bg-slate-800 text-white text-xs px-2 py-1 rounded shadow-md whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50">
                Workspaces
              </span>
            </button>

            {/* Divider */}
            <div className="w-6 h-px bg-slate-800 my-1" />

            {/* Recent chats quick dots */}
            <div className="flex-1 w-full flex flex-col items-center gap-1.5 overflow-y-auto no-scrollbar">
              {conversations.slice(0, 8).map((conv) => {
                const isSelected = currentConversationId === conv.id;
                return (
                  <button
                    key={conv.id}
                    onClick={() => {
                      onSelectConversation(conv.id);
                      onCloseMobile();
                    }}
                    className={`w-9 h-9 rounded-lg flex items-center justify-center transition-all group relative ${
                      isSelected
                        ? 'bg-orange-600/30 text-orange-400 border border-orange-500/50'
                        : 'text-slate-400 hover:text-white hover:bg-slate-800/80'
                    }`}
                  >
                    <MessageSquare className="w-4 h-4" />
                    <span className="absolute left-14 bg-slate-800 text-white text-xs px-2 py-1 rounded shadow-md max-w-[200px] truncate opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50">
                      {conv.title}
                    </span>
                  </button>
                );
              })}
            </div>

            {/* Bottom Rails: Settings & Admin */}
            <div className="mt-auto flex flex-col items-center gap-1.5 pt-2 border-t border-slate-800 w-full">
              <button
                onClick={onOpenSettings}
                className="w-9 h-9 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 flex items-center justify-center group relative"
                title="Settings"
              >
                <SettingsIcon className="w-4 h-4" />
                <span className="absolute left-14 bg-slate-800 text-white text-xs px-2 py-1 rounded shadow-md whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50">
                  Settings
                </span>
              </button>

              <button
                onClick={onOpenAdmin}
                className={`w-9 h-9 rounded-lg flex items-center justify-center group relative ${
                  isAdminLoggedIn
                    ? 'text-orange-400 bg-orange-500/20'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
                title="Admin Control"
              >
                <ShieldCheck className="w-4 h-4" />
                <span className="absolute left-14 bg-slate-800 text-white text-xs px-2 py-1 rounded shadow-md whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50">
                  {isAdminLoggedIn ? 'Admin Active' : 'Admin'}
                </span>
              </button>
            </div>
          </div>
        ) : (
          /* Expanded Mode Full Sidebar */
          <div className="flex-1 flex flex-col min-h-0">
            {/* Primary Action Buttons */}
            <div className="p-3 space-y-2">
              <button
                onClick={() => {
                  onNewChat();
                  onCloseMobile();
                }}
                className="w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl bg-orange-600 hover:bg-orange-500 text-white font-semibold text-xs transition-all shadow-xs group"
              >
                <span className="flex items-center gap-2">
                  <Plus className="w-4 h-4 transition-transform group-hover:rotate-90 duration-200" />
                  <span>New Conversation</span>
                </span>
                <kbd className="text-[9px] bg-orange-700/60 text-orange-200 px-1.5 py-0.5 rounded font-mono">
                  ⌘N
                </kbd>
              </button>

              <button
                onClick={onOpenSearch}
                className="w-full flex items-center justify-between px-3 py-2 rounded-xl bg-slate-800/60 hover:bg-slate-800 text-slate-300 hover:text-white text-xs transition-colors border border-slate-750"
              >
                <span className="flex items-center gap-2.5">
                  <Search className="w-3.5 h-3.5 text-slate-400" />
                  <span>Search Knowledge & Chats</span>
                </span>
                <kbd className="text-[9px] bg-slate-700 text-slate-400 px-1.5 py-0.5 rounded font-mono">
                  ⌘K
                </kbd>
              </button>
            </div>

            {/* University Flyout Navigation Items */}
            <div className="px-3 py-1 space-y-0.5 border-b border-slate-800/80">
              <div className="px-2 pb-1 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                University Hub
              </div>
              <button
                onClick={onOpenLibrary}
                className="w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs text-slate-300 hover:text-white hover:bg-slate-800/70 transition-colors group"
              >
                <span className="flex items-center gap-2">
                  <BookOpen className="w-3.5 h-3.5 text-orange-400" />
                  <span>University Library</span>
                </span>
                <span className="text-[10px] text-slate-500 font-mono">234 UMS</span>
              </button>

              <button
                onClick={onOpenWorkspaces}
                className="w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs text-slate-300 hover:text-white hover:bg-slate-800/70 transition-colors group"
              >
                <span className="flex items-center gap-2">
                  <Briefcase className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Workspaces</span>
                </span>
                <span className="text-[10px] text-indigo-400 bg-indigo-500/10 px-1.5 py-0.2 rounded">
                  Active
                </span>
              </button>
            </div>

            {/* Chat List Tabs: Recent vs Saved */}
            <div className="px-3 pt-3 flex items-center justify-between text-xs border-b border-slate-800/80 pb-2">
              <div className="flex items-center gap-1 bg-slate-800/80 p-0.5 rounded-lg w-full">
                <button
                  onClick={() => setActiveTab('recent')}
                  className={`flex-1 py-1 rounded-md text-[11px] font-medium transition-colors ${
                    activeTab === 'recent'
                      ? 'bg-slate-700 text-white shadow-2xs'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Recent ({conversations.length})
                </button>
                <button
                  onClick={() => setActiveTab('saved')}
                  className={`flex-1 py-1 rounded-md text-[11px] font-medium transition-colors flex items-center justify-center gap-1 ${
                    activeTab === 'saved'
                      ? 'bg-slate-700 text-white shadow-2xs'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Star className="w-3 h-3 text-amber-400" />
                  <span>Starred ({savedConversations.length})</span>
                </button>
              </div>
            </div>

            {/* Scrollable Conversations List */}
            <div className="flex-1 overflow-y-auto px-2 py-2 space-y-1">
              {displayedConversations.length === 0 ? (
                <div className="px-3 py-6 text-center text-xs text-slate-500">
                  {activeTab === 'saved' ? 'No starred conversations yet.' : 'No conversations yet.'}
                </div>
              ) : (
                displayedConversations.map((conv) => {
                  const isSelected = currentConversationId === conv.id;
                  const isSaved = savedConvIds.includes(conv.id);
                  const isEditing = editingConvId === conv.id;

                  if (isEditing) {
                    return (
                      <div
                        key={conv.id}
                        className="p-1.5 rounded-lg bg-slate-800 border border-orange-500/50 flex items-center gap-1.5"
                      >
                        <input
                          type="text"
                          value={editingTitle}
                          onChange={(e) => setEditingTitle(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') handleSaveRename(conv.id);
                            if (e.key === 'Escape') setEditingConvId(null);
                          }}
                          autoFocus
                          className="w-full bg-transparent text-xs text-white px-1.5 py-0.5 rounded focus:outline-none"
                        />
                        <button
                          onClick={(e) => handleSaveRename(conv.id, e)}
                          className="p-1 text-emerald-400 hover:text-emerald-300"
                        >
                          <Check className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setEditingConvId(null);
                          }}
                          className="p-1 text-slate-400 hover:text-slate-300"
                        >
                          <X className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    );
                  }

                  return (
                    <div
                      key={conv.id}
                      onClick={() => {
                        onSelectConversation(conv.id);
                        onCloseMobile();
                      }}
                      className={`group flex items-center justify-between px-2.5 py-2 rounded-xl text-xs cursor-pointer transition-all ${
                        isSelected
                          ? 'bg-slate-800 text-white font-medium border border-slate-700 shadow-2xs'
                          : 'text-slate-300 hover:bg-slate-850 hover:text-white border border-transparent'
                      }`}
                    >
                      <div className="flex items-center gap-2 truncate pr-1">
                        <MessageSquare
                          className={`w-3.5 h-3.5 shrink-0 ${
                            isSelected ? 'text-orange-400' : 'text-slate-500'
                          }`}
                        />
                        <span className="truncate">{conv.title}</span>
                      </div>

                      {/* Action buttons (Star, Rename, Delete) */}
                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                        <button
                          onClick={(e) => toggleSaveConversation(conv.id, e)}
                          title={isSaved ? 'Unstar conversation' : 'Star conversation'}
                          className={`p-1 rounded hover:bg-slate-700 ${
                            isSaved ? 'text-amber-400 opacity-100' : 'text-slate-400 hover:text-amber-300'
                          }`}
                        >
                          <Star className="w-3 h-3 fill-current" />
                        </button>

                        {onRenameConversation && (
                          <button
                            onClick={(e) => handleStartRename(conv, e)}
                            title="Rename"
                            className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-700"
                          >
                            <Edit2 className="w-3 h-3" />
                          </button>
                        )}

                        <button
                          onClick={(e) => onDeleteConversation(conv.id, e)}
                          title="Delete"
                          className="p-1 rounded text-slate-400 hover:text-rose-400 hover:bg-slate-700"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  );
                })
              )}
            </div>

            {/* Student Profile Card (Dynamic Backend Grounded) */}
            <div className="p-3 border-t border-slate-800/80 bg-slate-950/40">
              <div className="rounded-xl bg-slate-800/60 p-2.5 border border-slate-750 flex items-center justify-between">
                <div className="flex items-center gap-2.5 min-w-0">
                  <div className="w-8 h-8 rounded-lg bg-orange-600/20 text-orange-400 border border-orange-500/30 flex items-center justify-center font-bold text-xs shrink-0">
                    {(studentProfile?.full_name || 'LPU Student')
                      .split(' ')
                      .map((w: string) => w[0])
                      .join('')
                      .slice(0, 2)
                      .toUpperCase() || 'ST'}
                  </div>
                  <div className="truncate">
                    <div className="text-xs font-semibold text-white truncate flex items-center gap-1.5">
                      {studentProfile?.full_name || 'LPU Student'}
                      <span
                        className={`w-1.5 h-1.5 rounded-full ${
                          studentProfile?.is_connected ? 'bg-emerald-500' : 'bg-amber-400'
                        }`}
                        title={studentProfile?.is_connected ? 'Authenticated UMS Session' : 'Protected Public Session'}
                      />
                    </div>
                    <div className="text-[10px] text-slate-400 truncate">
                      {studentProfile?.programme || 'B.Tech CSE'} • Sem {studentProfile?.current_semester ?? 6}
                      {studentProfile?.registration_number ? ` • Reg ${studentProfile.registration_number}` : ''}
                    </div>
                  </div>
                </div>

                <button
                  onClick={onOpenSettings}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700 transition-colors"
                  title="Account Settings"
                >
                  <SettingsIcon className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* Bottom Quick Bar */}
              <div className="mt-2 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px] text-slate-500 px-1">
                <span className="flex items-center gap-1 text-slate-400">
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${
                      studentProfile?.is_connected ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'
                    }`}
                  />
                  <span>
                    {studentProfile?.is_connected ? 'Connected to UMS' : 'Protected in UMS'}
                  </span>
                </span>
                <button
                  onClick={onOpenAdmin}
                  className={`hover:text-orange-400 transition-colors flex items-center gap-1 font-semibold ${
                    isAdminLoggedIn ? 'text-orange-400' : 'text-slate-400'
                  }`}
                >
                  <ShieldCheck className="w-3 h-3" />
                  <span>{isAdminLoggedIn ? 'Admin Panel' : 'Admin'}</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </aside>
    </>
  );
};
