import {
  Category,
  ChatMessage,
  ConversationSummary,
  DashboardMetrics,
  FAQ,
  DocumentItem,
  DocumentChunk,
  AdminUser,
  KnowledgeRecord,
  NavigationCard,
  BookingCard,
  ProcedureChecklist,
  RMSCard,
  PersonalRecordCard,
  CampusPlaceCard,
  CampusRouteCard,
  CampusBlockDirectoryCard,
  FoodOutletCard,
  PersonCard,
  WhoToMeetCard,
  AcademicBenefitAssessmentCard,
  EvidenceCard,
  UMSServiceItem,
  ActionWorkflowItem,
  CampusPlaceItem,
  AgentPublicInfo,
  AgentEngineInfo,
} from '../types';

const API_BASE = '/api/v1';

// Session management
export function getOrCreateSessionToken(): string {
  let token = localStorage.getItem('campusconnect_session_token');
  if (!token) {
    token = `lpu_sess_${Math.random().toString(36).substring(2)}${Date.now().toString(36)}`;
    localStorage.setItem('campusconnect_session_token', token);
  }
  return token;
}

export function getAdminToken(): string | null {
  return localStorage.getItem('campusconnect_admin_token');
}

export function setAdminToken(token: string): void {
  localStorage.setItem('campusconnect_admin_token', token);
}

export function clearAdminToken(): void {
  localStorage.removeItem('campusconnect_admin_token');
}

export const api = {
  // Public Endpoints
  async getCategories(): Promise<Category[]> {
    const res = await fetch(`${API_BASE}/categories`);
    if (!res.ok) throw new Error('Failed to load campus categories');
    return res.json();
  },

  async sendChatMessage(payload: {
    message: string;
    conversation_id?: string;
    category_slug?: string;
    user_lat?: number;
    user_lon?: number;
    user_landmark?: string;
    provider?: string;
    model?: string;
    reasoning_mode?: string;
    thinking_level?: string;
    web_research?: boolean;
    agent_id?: string;
  }): Promise<{
    conversation_id: string;
    message_id: string;
    role: 'assistant';
    content: string;
    action_type?: string;
    thinking_steps: any[];
    citations: any[];
    follow_ups: string[];
    navigation_card?: NavigationCard;
    booking_card?: BookingCard;
    procedure_checklist?: ProcedureChecklist;
    rms_card?: RMSCard;
    personal_record_card?: PersonalRecordCard;
    campus_place_card?: CampusPlaceCard;
    campus_route_card?: CampusRouteCard;
    campus_block_directory_card?: CampusBlockDirectoryCard;
    food_outlet_card?: FoodOutletCard;
    person_card?: PersonCard;
    who_to_meet_card?: WhoToMeetCard;
    academic_benefit_card?: AcademicBenefitAssessmentCard;
    evidence_card?: EvidenceCard;
    confidence_score: number;
    latency_ms: number;
    is_ai_generated: boolean;
  }> {
    const sessionToken = getOrCreateSessionToken();
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...payload,
        session_token: sessionToken,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to send message');
    }
    return res.json();
  },

  async getConversations(): Promise<ConversationSummary[]> {
    const sessionToken = getOrCreateSessionToken();
    const res = await fetch(`${API_BASE}/conversations`, {
      headers: {
        'X-Session-Token': sessionToken,
      },
    });
    if (!res.ok) return [];
    return res.json();
  },

  async getConversationDetail(id: string): Promise<{
    id: string;
    title: string;
    messages: ChatMessage[];
  }> {
    const sessionToken = getOrCreateSessionToken();
    const res = await fetch(`${API_BASE}/conversations/${id}`, {
      headers: {
        'X-Session-Token': sessionToken,
      },
    });
    if (!res.ok) throw new Error('Failed to load conversation');
    return res.json();
  },

  async deleteConversation(id: string): Promise<void> {
    const sessionToken = getOrCreateSessionToken();
    await fetch(`${API_BASE}/conversations/${id}`, {
      method: 'DELETE',
      headers: {
        'X-Session-Token': sessionToken,
      },
    });
  },

  async submitFeedback(payload: {
    conversation_id: string;
    message_id: string;
    rating: 'helpful' | 'unhelpful';
    comment?: string;
  }): Promise<void> {
    const sessionToken = getOrCreateSessionToken();
    await fetch(`${API_BASE}/feedback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...payload,
        session_token: sessionToken,
      }),
    });
  },

  // Admin Endpoints
  async adminLogin(username: string, password: string): Promise<{ access_token: string; user: AdminUser }> {
    const res = await fetch(`${API_BASE}/admin/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Login failed');
    }
    const data = await res.json();
    setAdminToken(data.access_token);
    return data;
  },

  async getAdminDashboard(): Promise<DashboardMetrics> {
    const token = getAdminToken();
    const res = await fetch(`${API_BASE}/admin/dashboard`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Unauthorized');
    return res.json();
  },

  async getAdminFaqs(params?: { category_id?: string; search?: string }): Promise<FAQ[]> {
    const token = getAdminToken();
    const query = new URLSearchParams(params as any).toString();
    const res = await fetch(`${API_BASE}/admin/faqs?${query}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to load FAQs');
    return res.json();
  },

  async createAdminFaq(data: Partial<FAQ>): Promise<FAQ> {
    const token = getAdminToken();
    const res = await fetch(`${API_BASE}/admin/faqs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create FAQ');
    return res.json();
  },

  async updateAdminFaq(id: string, data: Partial<FAQ>): Promise<FAQ> {
    const token = getAdminToken();
    const res = await fetch(`${API_BASE}/admin/faqs/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to update FAQ');
    return res.json();
  },

  async deleteAdminFaq(id: string): Promise<void> {
    const token = getAdminToken();
    await fetch(`${API_BASE}/admin/faqs/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    });
  },

  async getAdminDocuments(): Promise<DocumentItem[]> {
    const token = getAdminToken();
    const res = await fetch(`${API_BASE}/admin/documents`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to load documents');
    return res.json();
  },

  async uploadAdminDocument(formData: FormData): Promise<DocumentItem> {
    const token = getAdminToken();
    const res = await fetch(`${API_BASE}/admin/documents`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
  },

  async getDocumentChunks(docId: string): Promise<DocumentChunk[]> {
    const token = getAdminToken();
    const res = await fetch(`${API_BASE}/admin/documents/${docId}/chunks`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to load chunks');
    return res.json();
  },

  async approveDocument(docId: string): Promise<void> {
    const token = getAdminToken();
    await fetch(`${API_BASE}/admin/documents/${docId}/approve`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });
  },

  async deleteAdminDocument(docId: string): Promise<void> {
    const token = getAdminToken();
    await fetch(`${API_BASE}/admin/documents/${docId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    });
  },

  // Unified Knowledge Records (12 Types)
  async getAdminKnowledgeRecords(params?: {
    record_type?: string;
    approval_status?: string;
    is_sensitive?: boolean;
    search?: string;
  }): Promise<KnowledgeRecord[]> {
    const token = getAdminToken();
    const query = new URLSearchParams(params as any).toString();
    const res = await fetch(`${API_BASE}/admin/knowledge-records?${query}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to load knowledge records');
    return res.json();
  },

  async createAdminKnowledgeRecord(data: Partial<KnowledgeRecord>): Promise<KnowledgeRecord> {
    const token = getAdminToken();
    const res = await fetch(`${API_BASE}/admin/knowledge-records`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to create knowledge record');
    }
    return res.json();
  },

  async updateAdminKnowledgeRecord(id: string, data: Partial<KnowledgeRecord>): Promise<KnowledgeRecord> {
    const token = getAdminToken();
    const res = await fetch(`${API_BASE}/admin/knowledge-records/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to update knowledge record');
    return res.json();
  },

  async approveAdminKnowledgeRecord(id: string): Promise<void> {
    const token = getAdminToken();
    await fetch(`${API_BASE}/admin/knowledge-records/${id}/approve`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });
  },

  async deleteAdminKnowledgeRecord(id: string): Promise<void> {
    const token = getAdminToken();
    await fetch(`${API_BASE}/admin/knowledge-records/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    });
  },

  async generateRecordVariants(id: string): Promise<{ searchable_variants: string[] }> {
    const token = getAdminToken();
    const res = await fetch(`${API_BASE}/admin/knowledge-records/${id}/generate-variants`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to generate variants');
    return res.json();
  },

  async getAdminAnalytics(): Promise<any> {
    const token = getAdminToken();
    const res = await fetch(`${API_BASE}/admin/analytics`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to load analytics');
    return res.json();
  },

  async triggerReindex(): Promise<{ total_indexed: number }> {
    const token = getAdminToken();
    const res = await fetch(`${API_BASE}/admin/reindex`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Reindex failed');
    return res.json();
  },

  // UMS & Action Workflows & Campus Places
  async getUMSServices(params?: { query?: string; module?: string; action_type?: string }): Promise<UMSServiceItem[]> {
    const searchParams = new URLSearchParams();
    if (params?.query) searchParams.set('query', params.query);
    if (params?.module) searchParams.set('module', params.module);
    if (params?.action_type) searchParams.set('action_type', params.action_type);
    const res = await fetch(`${API_BASE}/ums/services?${searchParams.toString()}`);
    if (!res.ok) throw new Error('Failed to load UMS services');
    return res.json();
  },

  async getUMSServiceDetail(id: string): Promise<UMSServiceItem> {
    const res = await fetch(`${API_BASE}/ums/services/${id}`);
    if (!res.ok) throw new Error('Failed to load UMS service detail');
    return res.json();
  },

  async getActionWorkflows(params?: { intent?: string; action_mode?: string }): Promise<ActionWorkflowItem[]> {
    const searchParams = new URLSearchParams();
    if (params?.intent) searchParams.set('intent', params.intent);
    if (params?.action_mode) searchParams.set('action_mode', params.action_mode);
    const res = await fetch(`${API_BASE}/ums/workflows?${searchParams.toString()}`);
    if (!res.ok) throw new Error('Failed to load action workflows');
    return res.json();
  },

  async getCampusPlaces(params?: { query?: string; category?: string; building?: string }): Promise<CampusPlaceItem[]> {
    const searchParams = new URLSearchParams();
    if (params?.query) searchParams.set('query', params.query);
    if (params?.category) searchParams.set('category', params.category);
    if (params?.building) searchParams.set('building', params.building);
    const res = await fetch(`${API_BASE}/campus/places?${searchParams.toString()}`);
    if (!res.ok) throw new Error('Failed to load campus places');
    return res.json();
  },

  // Admin UMS & Workflows & Campus Directory
  async getAdminUMSCatalog(params?: { module?: string; verification_status?: string; search?: string }): Promise<UMSServiceItem[]> {
    const token = getAdminToken();
    const searchParams = new URLSearchParams();
    if (params?.module) searchParams.set('module', params.module);
    if (params?.verification_status) searchParams.set('verification_status', params.verification_status);
    if (params?.search) searchParams.set('search', params.search);
    const res = await fetch(`${API_BASE}/admin/ums-catalog?${searchParams.toString()}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to load admin UMS catalog');
    return res.json();
  },

  async updateAdminUMSService(id: string, payload: Partial<UMSServiceItem>): Promise<UMSServiceItem> {
    const token = getAdminToken();
    const res = await fetch(`${API_BASE}/admin/ums-catalog/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to update UMS catalog item');
    return res.json();
  },

  async getAdminActionWorkflows(): Promise<ActionWorkflowItem[]> {
    const token = getAdminToken();
    const res = await fetch(`${API_BASE}/admin/action-workflows`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to load admin action workflows');
    return res.json();
  },

  async getAdminCampusPlaces(): Promise<CampusPlaceItem[]> {
    const token = getAdminToken();
    const res = await fetch(`${API_BASE}/admin/campus-places`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to load admin campus places');
    return res.json();
  },

  // Student Portal V7.0 Endpoints
  async getDashboard(): Promise<any> {
    const sessionToken = getOrCreateSessionToken();
    const res = await fetch(`${API_BASE}/portal/dashboard`, {
      headers: { 'X-Session-Token': sessionToken },
    });
    if (!res.ok) throw new Error('Failed to load student dashboard');
    return res.json();
  },

  async getPeople(params?: { expertise?: string; search?: string; school?: string }): Promise<{ total: number; people: any[] }> {
    const searchParams = new URLSearchParams();
    if (params?.expertise) searchParams.set('expertise', params.expertise);
    if (params?.search) searchParams.set('search', params.search);
    if (params?.school) searchParams.set('school', params.school);
    const res = await fetch(`${API_BASE}/portal/people?${searchParams.toString()}`);
    if (!res.ok) throw new Error('Failed to load university people directory');
    return res.json();
  },

  async getOpportunities(type?: string): Promise<any[]> {
    const searchParams = new URLSearchParams();
    if (type) searchParams.set('type', type);
    const res = await fetch(`${API_BASE}/portal/opportunities?${searchParams.toString()}`);
    if (!res.ok) return [];
    return res.json();
  },

  async getEvents(category?: string): Promise<any[]> {
    const searchParams = new URLSearchParams();
    if (category) searchParams.set('category', category);
    const res = await fetch(`${API_BASE}/portal/events?${searchParams.toString()}`);
    if (!res.ok) return [];
    return res.json();
  },

  async getAcademicBenefits(): Promise<any> {
    const res = await fetch(`${API_BASE}/portal/academic-benefits`);
    if (!res.ok) throw new Error('Failed to load academic benefits framework');
    return res.json();
  },

  async assessBenefit(payload: {
    description: string;
    has_github?: boolean;
    has_live_demo?: boolean;
    has_architecture_doc?: boolean;
  }): Promise<any> {
    const res = await fetch(`${API_BASE}/portal/assess-benefit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to assess project');
    return res.json();
  },

  async renameConversation(id: string, title: string): Promise<void> {
    const sessionToken = getOrCreateSessionToken();
    await fetch(`${API_BASE}/conversations/${id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'X-Session-Token': sessionToken,
      },
      body: JSON.stringify({ title }),
    });
  },

  async uploadDocument(file: File): Promise<{
    filename: string;
    size_bytes: number;
    characters_extracted: number;
    summary_preview: string;
    extracted_content: string;
  }> {
    const sessionToken = getOrCreateSessionToken();
    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_token', sessionToken);

    const res = await fetch(`${API_BASE}/chat/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to upload document');
    }
    return res.json();
  },

  async getSavedPlaces(): Promise<any[]> {
    const sessionToken = getOrCreateSessionToken();
    const res = await fetch(`${API_BASE}/portal/saved-places`, {
      headers: { 'X-Session-Token': sessionToken },
    });
    if (!res.ok) return [];
    return res.json();
  },

  async savePlace(loc: { place_id: string; name: string; building_block: string; room_number?: string; notes?: string }): Promise<any> {
    const sessionToken = getOrCreateSessionToken();
    const res = await fetch(`${API_BASE}/portal/saved-places`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Session-Token': sessionToken,
      },
      body: JSON.stringify(loc),
    });
    if (!res.ok) throw new Error('Failed to save location');
    return res.json();
  },

  async deleteSavedPlace(id: string): Promise<void> {
    const sessionToken = getOrCreateSessionToken();
    await fetch(`${API_BASE}/portal/saved-places/${id}`, {
      method: 'DELETE',
      headers: { 'X-Session-Token': sessionToken },
    });
  },

  async getLLMUsage(): Promise<any> {
    const res = await fetch(`${API_BASE}/portal/llm-usage`);
    if (!res.ok) throw new Error('Failed to load LLM usage statistics');
    return res.json();
  },

  // --- V8 Proactive Intelligence & Multi-Provider Endpoints ---
  async getLLMProviders(): Promise<{ default_provider: string; providers: any[] }> {
    const res = await fetch(`${API_BASE}/portal/llm-providers`);
    if (!res.ok) throw new Error('Failed to load LLM providers');
    return res.json();
  },

  async assessAttendance(query: string, attendance_percentage?: number): Promise<any> {
    const res = await fetch(`${API_BASE}/portal/assess-attendance`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, attendance_percentage }),
    });
    if (!res.ok) throw new Error('Failed to evaluate attendance');
    return res.json();
  },

  async assessProjectBenefits(query: string, details?: any): Promise<any> {
    const res = await fetch(`${API_BASE}/portal/assess-project-benefits`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, details }),
    });
    if (!res.ok) throw new Error('Failed to assess project benefits');
    return res.json();
  },

  async getAuthorityGuidance(query: string): Promise<any> {
    const res = await fetch(`${API_BASE}/portal/authority-guidance?query=${encodeURIComponent(query)}`);
    if (!res.ok) throw new Error('Failed to retrieve authority guidance');
    return res.json();
  },

  async getLiveWebResearch(query: string): Promise<any> {
    const res = await fetch(`${API_BASE}/portal/web-research?query=${encodeURIComponent(query)}`);
    if (!res.ok) throw new Error('Failed to execute web research');
    return res.json();
  },

  async listAgents(): Promise<AgentPublicInfo[]> {
    const res = await fetch(`${API_BASE}/agents`);
    if (!res.ok) throw new Error('Failed to load multi-agent registry');
    return res.json();
  },

  async getAgentDiagnostics(): Promise<AgentEngineInfo[]> {
    const res = await fetch(`${API_BASE}/agents/diagnostics`);
    if (!res.ok) throw new Error('Failed to load agent engine diagnostics');
    return res.json();
  },

  // --- Admin Multi-LLM Agentic Intelligence Endpoints ---
  async getAdminIntelligenceProviders(): Promise<any[]> {
    const token = getAdminToken();
    const res = await fetch(`${API_BASE}/admin/intelligence/providers`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to load providers');
    return res.json();
  },

  async getAdminIntelligenceCosts(): Promise<any> {
    const token = getAdminToken();
    const res = await fetch(`${API_BASE}/admin/intelligence/costs`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to load costs and budgets');
    return res.json();
  },

  async getAdminIntelligenceIdentities(): Promise<any[]> {
    const token = getAdminToken();
    const res = await fetch(`${API_BASE}/admin/intelligence/identities`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to load intelligence identities');
    return res.json();
  },

  async runAdminDomainEvaluation(intelligenceId: string): Promise<any> {
    const token = getAdminToken();
    const res = await fetch(`${API_BASE}/admin/intelligence/evaluations/run/${intelligenceId}`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error(`Evaluation failed for ${intelligenceId}`);
    return res.json();
  },

  async configureAdminModelSettings(payload: any): Promise<any> {
    const token = getAdminToken();
    const res = await fetch(`${API_BASE}/admin/intelligence/providers/configure`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to configure model settings');
    return res.json();
  },

  // Campus Navigation & Wayfinding
  async getCampusNavigationPlaces(params?: { q?: string; category?: string }): Promise<any[]> {
    const query = new URLSearchParams();
    if (params?.q) query.append('q', params.q);
    if (params?.category) query.append('category', params.category);
    const res = await fetch(`${API_BASE}/campus/navigation/places?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to load campus places');
    return res.json();
  },

  async getCampusPedestrianRoute(origin: string, destination: string, wheelchairOnly = false): Promise<CampusRouteCard> {
    const query = new URLSearchParams({
      origin,
      destination,
      wheelchair_only: wheelchairOnly ? 'true' : 'false',
    });
    const res = await fetch(`${API_BASE}/campus/navigation/route?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to calculate pedestrian route');
    return res.json();
  },

  async getCampusBlockDirectory(category = 'all'): Promise<any> {
    const res = await fetch(`${API_BASE}/campus/navigation/directory?category=${encodeURIComponent(category)}`);
    if (!res.ok) throw new Error('Failed to load campus directory');
    return res.json();
  },

  async getCampusDiscrepancies(): Promise<any> {
    const res = await fetch(`${API_BASE}/campus/navigation/discrepancies`);
    if (!res.ok) throw new Error('Failed to load campus discrepancies');
    return res.json();
  },

  async getScholixConfig(): Promise<any> {
    const res = await fetch(`${API_BASE}/campus/navigation/scholix`);
    if (!res.ok) throw new Error('Failed to load Scholix configuration');
    return res.json();
  },
};

