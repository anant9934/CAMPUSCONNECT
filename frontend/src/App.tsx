import React, { useState, useEffect } from 'react';
import { api, getAdminToken } from './services/api';
import {
  Category,
  ChatMessage,
  ConversationSummary,
  AdminUser,
} from './types';
import { Sidebar } from './components/Sidebar';
import { TopBar } from './components/TopBar';
import { WelcomeHero } from './components/WelcomeHero';
import { ChatArea } from './components/ChatArea';
import { MessageComposer } from './components/MessageComposer';
import { LibraryModal } from './components/LibraryModal';
import { WorkspacesModal } from './components/WorkspacesModal';
import { SettingsModal } from './components/SettingsModal';
import { AboutModal } from './components/AboutModal';
import { PrivacyModal } from './components/PrivacyModal';
import { SearchModal } from './components/SearchModal';
import { AdminLoginModal } from './components/admin/AdminLoginModal';
import { AdminDashboard } from './components/admin/AdminDashboard';

export const App: React.FC = () => {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [currentTitle, setCurrentTitle] = useState<string>('New Conversation');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategorySlug, setSelectedCategorySlug] = useState<string | undefined>(undefined);
  const [selectedLandmark, setSelectedLandmark] = useState<string>('Block 32');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Model & Reasoning mode states
  const [selectedModel, setSelectedModel] = useState<string>('aegis');
  const [thinkingLevel, setThinkingLevel] = useState<string>('Medium');
  const [reasoningMode, setReasoningMode] = useState<string>('DeepThink');
  const [webResearchEnabled, setWebResearchEnabled] = useState<boolean>(false);
  const [studentProfile, setStudentProfile] = useState<any>(null);

  // Sidebar responsive & collapsed states
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);
  const [isOpenMobile, setIsOpenMobile] = useState<boolean>(false);

  // Modals state
  const [isLibraryOpen, setIsLibraryOpen] = useState(false);
  const [isWorkspacesOpen, setIsWorkspacesOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isAboutOpen, setIsAboutOpen] = useState(false);
  const [isPrivacyOpen, setIsPrivacyOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isAdminLoginOpen, setIsAdminLoginOpen] = useState(false);
  const [isAdminDashboardOpen, setIsAdminDashboardOpen] = useState(false);
  const [adminUser, setAdminUser] = useState<AdminUser | null>(null);

  useEffect(() => {
    initApp();
  }, []);

  const initApp = async () => {
    try {
      const [cats, convs, dash] = await Promise.all([
        api.getCategories().catch(() => []),
        api.getConversations().catch(() => []),
        api.getDashboard().catch(() => null),
      ]);
      setCategories(cats);
      setConversations(convs);
      if (dash && dash.profile) {
        setStudentProfile(dash.profile);
      }

      // Check for existing admin login
      if (getAdminToken()) {
        try {
          const profile = await api.getAdminDashboard();
          if (profile) {
            setAdminUser({ id: '1', username: 'admin', email: 'admin@lpu.co.in', role: 'admin' });
          }
        } catch {
          // Token expired or invalid
        }
      }
    } catch (e) {
      console.error('App init error:', e);
    }
  };

  const loadConversation = async (id: string) => {
    try {
      setIsLoading(true);
      const detail = await api.getConversationDetail(id);
      setCurrentConversationId(detail.id);
      setCurrentTitle(detail.title || 'Conversation');
      setMessages(detail.messages);
    } catch (err) {
      console.error('Failed to load conversation:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    setCurrentConversationId(null);
    setCurrentTitle('New Conversation');
    setMessages([]);
    setSelectedCategorySlug(undefined);
  };

  const handleDeleteConversation = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await api.deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (currentConversationId === id) {
        handleNewChat();
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    }
  };

  const handleRenameConversation = async (id: string, newTitle: string) => {
    try {
      await api.renameConversation(id, newTitle);
      setConversations((prev) =>
        prev.map((c) => (c.id === id ? { ...c, title: newTitle } : c))
      );
      if (currentConversationId === id) {
        setCurrentTitle(newTitle);
      }
    } catch (err) {
      console.error('Failed to rename conversation:', err);
    }
  };

  const handleRenameCurrentTitle = (newTitle: string) => {
    if (currentConversationId) {
      handleRenameConversation(currentConversationId, newTitle);
    } else {
      setCurrentTitle(newTitle);
    }
  };

  const handleSendMessage = async (userText: string) => {
    if (!userText.trim() || isLoading) return;

    const tempUserMsg: ChatMessage = {
      id: `temp_${Date.now()}`,
      role: 'user',
      content: userText,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, tempUserMsg]);
    setIsLoading(true);

    try {
      const response = await api.sendChatMessage({
        message: userText,
        conversation_id: currentConversationId || undefined,
        category_slug: selectedCategorySlug,
        user_landmark: selectedLandmark,
        provider: selectedModel,
        agent_id: selectedModel,
        thinking_level: thinkingLevel.toLowerCase(),
        reasoning_mode: reasoningMode.toLowerCase(),
        web_research: webResearchEnabled,
      });

      const assistantMsg: ChatMessage = {
        id: response.message_id,
        conversation_id: response.conversation_id,
        role: 'assistant',
        content: response.content,
        action_type: response.action_type,
        thinking_steps: response.thinking_steps,
        citations: response.citations,
        follow_ups: response.follow_ups,
        navigation_card: response.navigation_card,
        booking_card: response.booking_card,
        procedure_checklist: response.procedure_checklist,
        rms_card: response.rms_card,
        personal_record_card: response.personal_record_card,
        campus_place_card: response.campus_place_card,
        food_outlet_card: response.food_outlet_card,
        person_card: response.person_card,
        who_to_meet_card: response.who_to_meet_card,
        academic_benefit_card: response.academic_benefit_card,
        evidence_card: response.evidence_card,
        confidence_score: response.confidence_score,
        latency_ms: response.latency_ms,
        is_ai_generated: response.is_ai_generated,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMsg]);
      setCurrentConversationId(response.conversation_id);
      if (!currentConversationId) {
        // Auto-title from the first user inquiry
        const autoTitle = userText.slice(0, 32).trim() + (userText.length > 32 ? '...' : '');
        setCurrentTitle(autoTitle);
      }

      // Refresh conversation list in sidebar
      api.getConversations().then(setConversations).catch(console.error);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: `err_${Date.now()}`,
        role: 'assistant',
        content: `Notice: ${
          err.message ||
          'Unable to connect to CampusConnect server. Please verify your connection and try again.'
        }`,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEditAndResend = (messageId: string, newText: string) => {
    // Remove the message and subsequent messages, then resend
    const index = messages.findIndex((m) => m.id === messageId);
    if (index !== -1) {
      setMessages((prev) => prev.slice(0, index));
    }
    handleSendMessage(newText);
  };

  const handleRetry = () => {
    const lastUserMsg = [...messages].reverse().find((m) => m.role === 'user');
    if (lastUserMsg) {
      handleSendMessage(lastUserMsg.content);
    }
  };

  const handleFeedback = async (messageId: string, rating: 'helpful' | 'unhelpful') => {
    if (!currentConversationId) return;
    try {
      await api.submitFeedback({
        conversation_id: currentConversationId,
        message_id: messageId,
        rating,
      });
    } catch (err) {
      console.error('Failed to submit feedback:', err);
    }
  };

  const handleOpenWorkspace = (prompt: string, title: string) => {
    handleNewChat();
    setCurrentTitle(title);
    handleSendMessage(prompt);
  };

  return (
    <div className="flex h-screen bg-warm-bg text-slate-800 antialiased overflow-hidden font-sans">
      {/* Collapsible Left Sidebar */}
      <Sidebar
        conversations={conversations}
        currentConversationId={currentConversationId}
        onSelectConversation={loadConversation}
        onNewChat={handleNewChat}
        onDeleteConversation={handleDeleteConversation}
        onRenameConversation={handleRenameConversation}
        onOpenSearch={() => setIsSearchOpen(true)}
        onOpenLibrary={() => setIsLibraryOpen(true)}
        onOpenWorkspaces={() => setIsWorkspacesOpen(true)}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onOpenAdmin={() => {
          if (adminUser) setIsAdminDashboardOpen(true);
          else setIsAdminLoginOpen(true);
        }}
        isAdminLoggedIn={Boolean(adminUser)}
        isOpenMobile={isOpenMobile}
        onCloseMobile={() => setIsOpenMobile(false)}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed((prev) => !prev)}
        studentProfile={studentProfile}
      />

      {/* Main Intelligent Conversational Workspace */}
      <div
        className={`flex-1 flex flex-col h-full overflow-hidden transition-all duration-200 ease-in-out relative ${
          isSidebarCollapsed ? 'lg:pl-[68px]' : 'lg:pl-[260px]'
        }`}
      >
        {/* Compact Top Header */}
        <TopBar
          sidebarCollapsed={isSidebarCollapsed}
          onToggleSidebar={() => {
            // If on mobile, open mobile drawer; on desktop toggle collapsed rail
            if (window.innerWidth < 1024) {
              setIsOpenMobile((prev) => !prev);
            } else {
              setIsSidebarCollapsed((prev) => !prev);
            }
          }}
          currentTitle={currentTitle}
          onRenameTitle={handleRenameCurrentTitle}
          selectedModel={selectedModel}
          onSelectModel={setSelectedModel}
          thinkingLevel={thinkingLevel}
          onSelectThinkingLevel={setThinkingLevel}
          reasoningMode={reasoningMode}
          onSelectReasoningMode={setReasoningMode}
          onOpenLibrary={() => setIsLibraryOpen(true)}
          onOpenWorkspaces={() => setIsWorkspacesOpen(true)}
          onOpenSettings={() => setIsSettingsOpen(true)}
          onOpenAdmin={() => {
            if (adminUser) setIsAdminDashboardOpen(true);
            else setIsAdminLoginOpen(true);
          }}
          isAdminLoggedIn={Boolean(adminUser)}
        />

        {/* Central Conversation Timeline */}
        <main className="flex-1 overflow-y-auto relative scroll-smooth">
          {messages.length === 0 ? (
            <WelcomeHero
              categories={categories}
              onSelectPrompt={handleSendMessage}
              onOpenLibrary={() => setIsLibraryOpen(true)}
              onOpenWorkspaces={() => setIsWorkspacesOpen(true)}
            />
          ) : (
            <ChatArea
              messages={messages}
              isLoading={isLoading}
              onRetry={handleRetry}
              onFeedback={handleFeedback}
              onSelectPrompt={handleSendMessage}
              onEditAndResend={handleEditAndResend}
            />
          )}
        </main>

        {/* Floating Capsule Composer */}
        <footer className="shrink-0 bg-gradient-to-t from-warm-bg via-warm-bg/90 to-transparent pt-2 z-10">
          <MessageComposer
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            onStopStreaming={() => setIsLoading(false)}
            selectedCategorySlug={selectedCategorySlug}
            onClearCategory={() => setSelectedCategorySlug(undefined)}
            selectedLandmark={selectedLandmark}
            onSelectLandmark={setSelectedLandmark}
            selectedModel={selectedModel}
            onSelectModel={setSelectedModel}
            thinkingLevel={thinkingLevel}
            onSelectThinkingLevel={setThinkingLevel}
            reasoningMode={reasoningMode}
            onSelectReasoningMode={setReasoningMode}
            webResearchEnabled={webResearchEnabled}
            onToggleWebResearch={setWebResearchEnabled}
          />
        </footer>
      </div>

      {/* Overlay Modals */}
      <LibraryModal
        isOpen={isLibraryOpen}
        onClose={() => setIsLibraryOpen(false)}
        onSelectPrompt={handleSendMessage}
      />

      <WorkspacesModal
        isOpen={isWorkspacesOpen}
        onClose={() => setIsWorkspacesOpen(false)}
        onSelectWorkspace={handleOpenWorkspace}
      />

      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        selectedModel={selectedModel}
        onSelectModel={setSelectedModel}
        reasoningMode={reasoningMode}
        onSelectReasoningMode={setReasoningMode}
        webResearchEnabled={webResearchEnabled}
        onToggleWebResearch={setWebResearchEnabled}
        selectedLandmark={selectedLandmark}
        onSelectLandmark={setSelectedLandmark}
      />

      <SearchModal
        isOpen={isSearchOpen}
        onClose={() => setIsSearchOpen(false)}
        categories={categories}
        conversations={conversations}
        onSelectPrompt={handleSendMessage}
        onSelectConversation={loadConversation}
      />

      <AboutModal isOpen={isAboutOpen} onClose={() => setIsAboutOpen(false)} />
      <PrivacyModal isOpen={isPrivacyOpen} onClose={() => setIsPrivacyOpen(false)} />

      <AdminLoginModal
        isOpen={isAdminLoginOpen}
        onClose={() => setIsAdminLoginOpen(false)}
        onLoginSuccess={(user) => {
          setAdminUser(user);
          setIsAdminDashboardOpen(true);
        }}
      />

      {isAdminDashboardOpen && adminUser && (
        <AdminDashboard
          user={adminUser}
          onLogout={() => {
            setAdminUser(null);
            setIsAdminDashboardOpen(false);
          }}
          onClose={() => setIsAdminDashboardOpen(false)}
        />
      )}
    </div>
  );
};

export default App;
