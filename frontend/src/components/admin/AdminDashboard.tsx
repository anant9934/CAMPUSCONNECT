import React, { useState, useEffect } from 'react';
import {
  LayoutDashboard,
  FileQuestion,
  FileText,
  FolderTree,
  ExternalLink,
  HelpCircle,
  ThumbsUp,
  BarChart3,
  Settings as SettingsIcon,
  LogOut,
  Plus,
  Trash2,
  Edit,
  CheckCircle2,
  XCircle,
  Upload,
  RefreshCw,
  Search,
  Eye,
  AlertTriangle,
  Clock,
  Sparkles,
  ArrowRight,
  Database,
  ShieldCheck,
  Tag,
  FileCheck,
  Layers,
  Compass,
  ListChecks,
  MapPin,
  Shield,
  Workflow
} from 'lucide-react';
import { api, clearAdminToken } from '../../services/api';
import {
  AdminUser,
  DashboardMetrics,
  FAQ,
  DocumentItem,
  DocumentChunk,
  Category,
  QueryLog,
  KnowledgeRecord,
  UMSServiceItem,
  ActionWorkflowItem,
  CampusPlaceItem
} from '../../types';

interface AdminDashboardProps {
  user: AdminUser;
  onLogout: () => void;
  onClose: () => void;
}

type TabType =
  | 'overview'
  | 'ai_intelligence'
  | 'unified_repository'
  | 'ums_catalog'
  | 'action_workflows'
  | 'campus_places'
  | 'faqs'
  | 'documents'
  | 'categories'
  | 'sources'
  | 'unanswered'
  | 'feedback'
  | 'analytics'
  | 'settings';

export const AdminDashboard: React.FC<AdminDashboardProps> = ({ user, onLogout, onClose }) => {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [faqs, setFaqs] = useState<FAQ[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [knowledgeRecords, setKnowledgeRecords] = useState<KnowledgeRecord[]>([]);
  const [selectedRecordForDetail, setSelectedRecordForDetail] = useState<KnowledgeRecord | null>(null);
  const [selectedRecordTypeFilter, setSelectedRecordTypeFilter] = useState<string>('all');
  const [filterSensitiveOnly, setFilterSensitiveOnly] = useState<boolean>(false);
  const [searchRecordQuery, setSearchRecordQuery] = useState<string>('');
  const [analyticsData, setAnalyticsData] = useState<any>(null);

  // Multi-LLM Intelligence Architecture State
  const [intelProviders, setIntelProviders] = useState<any[]>([]);
  const [intelCosts, setIntelCosts] = useState<any>(null);
  const [intelIdentities, setIntelIdentities] = useState<any[]>([]);
  const [evalLoading, setEvalLoading] = useState<boolean>(false);
  const [evalResult, setEvalResult] = useState<any>(null);
  const [evalTarget, setEvalTarget] = useState<string>('themis');

  // UMS Catalog & Action Workflows & Places state
  const [umsCatalog, setUmsCatalog] = useState<UMSServiceItem[]>([]);
  const [actionWorkflows, setActionWorkflows] = useState<ActionWorkflowItem[]>([]);
  const [campusPlaces, setCampusPlaces] = useState<CampusPlaceItem[]>([]);
  const [umsSearchQuery, setUmsSearchQuery] = useState<string>('');
  const [umsModuleFilter, setUmsModuleFilter] = useState<string>('all');
  const [isUmsModalOpen, setIsUmsModalOpen] = useState(false);
  const [editingUmsItem, setEditingUmsItem] = useState<UMSServiceItem | null>(null);
  const [umsFormData, setUmsFormData] = useState({
    service_label: '',
    navigation_path: '',
    verification_status: 'menu_label_observed_procedure_not_verified',
    deep_link_status: 'not_verified',
    deep_link_url: 'https://ums.lpu.in/lpuums/',
    notes: '',
    keywords: '',
    is_active: true,
  });

  const [loading, setLoading] = useState(false);
  const [reindexing, setReindexing] = useState(false);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  // FAQ Modal state
  const [isFaqModalOpen, setIsFaqModalOpen] = useState(false);
  const [editingFaq, setEditingFaq] = useState<FAQ | null>(null);
  const [faqFormData, setFaqFormData] = useState({
    category_id: '',
    canonical_question: '',
    alternative_questions: '',
    answer: '',
    keywords: '',
    source_url: 'https://ums.lpu.in',
    source_title: 'LPU Official Portal',
    content_owner: 'Division of Student Affairs',
    is_approved: true,
  });

  // Document Upload State
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadCategoryId, setUploadCategoryId] = useState('');
  const [previewChunks, setPreviewChunks] = useState<DocumentChunk[] | null>(null);
  const [previewDocTitle, setPreviewDocTitle] = useState('');

  const showNotification = (message: string, type: 'success' | 'error' = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3500);
  };

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    setLoading(true);
    try {
      const [
        metricsRes,
        faqsRes,
        docsRes,
        catsRes,
        analyticsRes,
        krRes,
        umsRes,
        wfRes,
        placesRes,
        providersRes,
        costsRes,
        identitiesRes,
      ] = await Promise.all([
        api.getAdminDashboard(),
        api.getAdminFaqs(),
        api.getAdminDocuments(),
        api.getCategories(),
        api.getAdminAnalytics(),
        api.getAdminKnowledgeRecords(),
        api.getAdminUMSCatalog(),
        api.getAdminActionWorkflows(),
        api.getAdminCampusPlaces(),
        api.getAdminIntelligenceProviders().catch(() => []),
        api.getAdminIntelligenceCosts().catch(() => null),
        api.getAdminIntelligenceIdentities().catch(() => []),
      ]);
      setMetrics(metricsRes);
      setFaqs(faqsRes);
      setDocuments(docsRes);
      setCategories(catsRes);
      setAnalyticsData(analyticsRes);
      setKnowledgeRecords(krRes);
      setUmsCatalog(umsRes);
      setActionWorkflows(wfRes);
      setCampusPlaces(placesRes);
      setIntelProviders(providersRes);
      setIntelCosts(costsRes);
      setIntelIdentities(identitiesRes);
      if (catsRes.length > 0 && !faqFormData.category_id) {
        setFaqFormData((prev) => ({ ...prev, category_id: catsRes[0].id }));
      }
    } catch (err: any) {
      showNotification(err.message || 'Error fetching data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleReindex = async () => {
    setReindexing(true);
    try {
      const res = await api.triggerReindex();
      showNotification(`Search engine reindexed successfully! Total active records: ${res.total_indexed}`);
      loadAllData();
    } catch (err: any) {
      showNotification(err.message || 'Reindex failed', 'error');
    } finally {
      setReindexing(false);
    }
  };

  // AI Intelligence operations
  const handleRunEvaluation = async () => {
    setEvalLoading(true);
    setEvalResult(null);
    try {
      const res = await api.runAdminDomainEvaluation(evalTarget);
      setEvalResult(res);
      showNotification(`Benchmark evaluation completed for ${evalTarget.toUpperCase()}!`);
    } catch (err: any) {
      showNotification(err.message || 'Evaluation run failed', 'error');
    } finally {
      setEvalLoading(false);
    }
  };

  const handleToggleModel = async (provider: string, modelId: string, currentAvailable: boolean) => {
    try {
      await api.configureAdminModelSettings({
        provider_name: provider,
        model_id: modelId,
        is_available: !currentAvailable,
      });
      showNotification(`Model ${modelId} ${!currentAvailable ? 'enabled' : 'disabled'}.`);
      const updated = await api.getAdminIntelligenceProviders();
      setIntelProviders(updated);
    } catch (err: any) {
      showNotification(err.message || 'Failed to update model', 'error');
    }
  };

  // FAQ operations
  const handleOpenCreateFaq = (initialQuestion?: string) => {
    setEditingFaq(null);
    setFaqFormData({
      category_id: categories[0]?.id || '',
      canonical_question: initialQuestion || '',
      alternative_questions: '',
      answer: '',
      keywords: '',
      source_url: 'https://ums.lpu.in',
      source_title: 'LPU Official Portal',
      content_owner: 'Division of Student Affairs',
      is_approved: true,
    });
    setIsFaqModalOpen(true);
  };

  const handleOpenEditFaq = (faq: FAQ) => {
    setEditingFaq(faq);
    setFaqFormData({
      category_id: faq.category_id,
      canonical_question: faq.canonical_question,
      alternative_questions: (faq.alternative_questions || []).join('\n'),
      answer: faq.answer,
      keywords: (faq.keywords || []).join(', '),
      source_url: faq.source_url || 'https://ums.lpu.in',
      source_title: faq.source_title || 'LPU Official Portal',
      content_owner: faq.content_owner || 'Division of Student Affairs',
      is_approved: faq.is_approved,
    });
    setIsFaqModalOpen(true);
  };

  const handleSaveFaq = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      category_id: faqFormData.category_id,
      canonical_question: faqFormData.canonical_question.trim(),
      alternative_questions: faqFormData.alternative_questions
        .split('\n')
        .map((s) => s.trim())
        .filter(Boolean),
      answer: faqFormData.answer.trim(),
      keywords: faqFormData.keywords
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean),
      source_url: faqFormData.source_url.trim(),
      source_title: faqFormData.source_title.trim(),
      content_owner: faqFormData.content_owner.trim(),
      is_approved: faqFormData.is_approved,
      approval_status: faqFormData.is_approved ? ('approved' as const) : ('pending' as const),
    };

    try {
      if (editingFaq) {
        await api.updateAdminFaq(editingFaq.id, payload);
        showNotification('FAQ updated successfully!');
      } else {
        await api.createAdminFaq(payload);
        showNotification('New FAQ added to knowledge base!');
      }
      setIsFaqModalOpen(false);
      loadAllData();
    } catch (err: any) {
      showNotification(err.message || 'Failed to save FAQ', 'error');
    }
  };

  const handleDeleteFaq = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this FAQ?')) return;
    try {
      await api.deleteAdminFaq(id);
      showNotification('FAQ removed.');
      loadAllData();
    } catch (err: any) {
      showNotification(err.message || 'Failed to delete FAQ', 'error');
    }
  };

  // Document operations
  const handleUploadDocument = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile || !uploadTitle.trim()) {
      showNotification('Please select a file and enter a title.', 'error');
      return;
    }
    const formData = new FormData();
    formData.append('title', uploadTitle.trim());
    if (uploadCategoryId) formData.append('category_id', uploadCategoryId);
    formData.append('file', uploadFile);

    try {
      await api.uploadAdminDocument(formData);
      showNotification('Document uploaded, parsed, and chunked successfully!');
      setUploadFile(null);
      setUploadTitle('');
      loadAllData();
    } catch (err: any) {
      showNotification(err.message || 'Upload failed', 'error');
    }
  };

  const handleApproveDocument = async (docId: string) => {
    try {
      await api.approveDocument(docId);
      showNotification('Document approved and indexed into active RAG corpus!');
      loadAllData();
    } catch (err: any) {
      showNotification(err.message || 'Failed to approve document', 'error');
    }
  };

  const handleDeleteDocument = async (docId: string) => {
    if (!window.confirm('Delete document and all extracted chunks?')) return;
    try {
      await api.deleteAdminDocument(docId);
      showNotification('Document deleted.');
      loadAllData();
    } catch (err: any) {
      showNotification(err.message || 'Failed to delete document', 'error');
    }
  };

  const handlePreviewChunks = async (doc: DocumentItem) => {
    try {
      const chunks = await api.getDocumentChunks(doc.id);
      setPreviewChunks(chunks);
      setPreviewDocTitle(doc.title);
    } catch (err: any) {
      showNotification('Failed to fetch chunks', 'error');
    }
  };

  const handleApproveRecord = async (recId: string) => {
    try {
      await api.approveAdminKnowledgeRecord(recId);
      showNotification('Institutional record approved and activated for student search!');
      loadAllData();
    } catch (err: any) {
      showNotification(err.message || 'Approval failed', 'error');
    }
  };

  const handleDeleteRecord = async (recId: string) => {
    if (!window.confirm('Delete this record from the knowledge repository?')) return;
    try {
      await api.deleteAdminKnowledgeRecord(recId);
      showNotification('Record deleted.');
      loadAllData();
    } catch (err: any) {
      showNotification(err.message || 'Delete failed', 'error');
    }
  };

  const handleGenerateVariants = async (recId: string) => {
    try {
      const res = await api.generateRecordVariants(recId);
      showNotification(`Generated ${res.searchable_variants.length} question variants without changing facts.`);
      loadAllData();
    } catch (err: any) {
      showNotification(err.message || 'Variant generation failed', 'error');
    }
  };

  const handleOpenEditUms = (item: UMSServiceItem) => {
    setEditingUmsItem(item);
    setUmsFormData({
      service_label: item.service_label,
      navigation_path: item.navigation_path,
      verification_status: item.verification_status,
      deep_link_status: item.deep_link_status,
      deep_link_url: item.deep_link_url || 'https://ums.lpu.in/lpuums/',
      notes: item.notes || '',
      keywords: (item.keywords || []).join(', '),
      is_active: item.is_active,
    });
    setIsUmsModalOpen(true);
  };

  const handleSaveUmsItem = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingUmsItem) return;

    try {
      await api.updateAdminUMSService(editingUmsItem.id, {
        service_label: umsFormData.service_label.trim(),
        navigation_path: umsFormData.navigation_path.trim(),
        verification_status: umsFormData.verification_status,
        deep_link_status: umsFormData.deep_link_status,
        deep_link_url: umsFormData.deep_link_url.trim(),
        notes: umsFormData.notes.trim() || undefined,
        keywords: umsFormData.keywords
          .split(',')
          .map((s) => s.trim())
          .filter(Boolean),
        is_active: umsFormData.is_active,
      });
      showNotification('UMS service entry updated successfully!');
      setIsUmsModalOpen(false);
      loadAllData();
    } catch (err: any) {
      showNotification(err.message || 'Failed to update UMS service', 'error');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex bg-warm-bg overflow-hidden animate-fadeIn">
      {/* Admin Sidebar */}
      <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col border-r border-slate-800 shrink-0">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-orange-600 flex items-center justify-center text-white font-bold text-sm">
              LPU
            </div>
            <div>
              <div className="font-semibold text-white text-sm">CampusConnect</div>
              <div className="text-[11px] text-slate-400">Admin Control Panel</div>
            </div>
          </div>
        </div>

        {/* User Info */}
        <div className="px-4 py-3 bg-slate-950/40 border-b border-slate-800 text-xs">
          <div className="text-slate-400">Signed in as:</div>
          <div className="font-semibold text-white truncate">{user.username} ({user.role})</div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {[
            { id: 'overview', label: 'Overview', icon: <LayoutDashboard className="w-4 h-4" /> },
            { id: 'ai_intelligence', label: 'AI Intelligence & Providers', icon: <Sparkles className="w-4 h-4 text-orange-400" /> },
            { id: 'unified_repository', label: 'Unified Repository (12 Types)', icon: <Database className="w-4 h-4" /> },
            { id: 'ums_catalog', label: `UMS Services (${umsCatalog.length || 234})`, icon: <Compass className="w-4 h-4" /> },
            { id: 'action_workflows', label: `Action Workflows (${actionWorkflows.length || 24})`, icon: <ListChecks className="w-4 h-4" /> },
            { id: 'campus_places', label: `Campus Map & Places (${campusPlaces.length || 10})`, icon: <MapPin className="w-4 h-4" /> },
            { id: 'faqs', label: 'FAQ Management', icon: <FileQuestion className="w-4 h-4" /> },
            { id: 'documents', label: 'Knowledge Documents', icon: <FileText className="w-4 h-4" /> },
            { id: 'categories', label: 'Campus Categories', icon: <FolderTree className="w-4 h-4" /> },
            { id: 'sources', label: 'Source Review', icon: <ExternalLink className="w-4 h-4" /> },
            { id: 'unanswered', label: 'Unanswered Queries', icon: <HelpCircle className="w-4 h-4" /> },
            { id: 'feedback', label: 'Student Feedback', icon: <ThumbsUp className="w-4 h-4" /> },
            { id: 'analytics', label: 'Analytics & Quota', icon: <BarChart3 className="w-4 h-4" /> },
            { id: 'settings', label: 'System Settings', icon: <SettingsIcon className="w-4 h-4" /> },
          ].map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as TabType)}
                className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-orange-600 text-white font-semibold shadow-soft'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
              >
                {tab.icon}
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Reindex & Exit */}
        <div className="p-3 border-t border-slate-800 space-y-2">
          <button
            onClick={handleReindex}
            disabled={reindexing}
            className="w-full py-2 px-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 transition-colors flex items-center justify-center gap-2 border border-slate-700 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${reindexing ? 'animate-spin text-orange-400' : ''}`} />
            <span>{reindexing ? 'Reindexing...' : 'Reindex RAG Corpus'}</span>
          </button>

          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="flex-1 py-1.5 px-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-[11px] text-slate-300 transition-colors text-center"
            >
              Exit to Chat
            </button>
            <button
              onClick={() => {
                clearAdminToken();
                onLogout();
              }}
              className="py-1.5 px-3 rounded-lg bg-rose-950/60 hover:bg-rose-900 text-rose-300 text-[11px] transition-colors flex items-center gap-1"
            >
              <LogOut className="w-3 h-3" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Main Admin Workspace */}
      <main className="flex-1 flex flex-col overflow-hidden bg-warm-bg">
        {/* Top bar */}
        <header className="h-14 bg-white border-b border-warm-border px-6 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <h1 className="font-bold text-slate-900 text-base capitalize">
              {activeTab === 'overview'
                ? 'Institutional Overview'
                : activeTab === 'ai_intelligence'
                ? 'Multi-LLM Intelligence & Provider Management'
                : activeTab === 'unified_repository'
                ? 'Unified Knowledge Repository (12 Data Types)'
                : activeTab === 'ums_catalog'
                ? 'UMS Service Catalog (234 Screenshot Entries)'
                : activeTab === 'action_workflows'
                ? 'Guided Action Workflows (24 Campus Services)'
                : activeTab === 'campus_places'
                ? 'Campus Map & Wayfinding Directory'
                : activeTab.replace('-', ' ')}
            </h1>
            {loading && <RefreshCw className="w-3.5 h-3.5 text-orange-600 animate-spin" />}
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleReindex}
              className="px-3 py-1.5 text-xs font-medium text-slate-700 bg-warm-50 border border-warm-border rounded-lg hover:border-orange-300 hover:text-orange-700 transition-colors flex items-center gap-1.5"
            >
              <RefreshCw className={`w-3 h-3 ${reindexing ? 'animate-spin' : ''}`} />
              <span>Sync Search Index</span>
            </button>
          </div>
        </header>

        {/* Notifications */}
        {notification && (
          <div
            className={`px-6 py-2 text-xs font-medium flex items-center justify-between ${
              notification.type === 'success'
                ? 'bg-emerald-50 text-emerald-800 border-b border-emerald-200'
                : 'bg-rose-50 text-rose-800 border-b border-rose-200'
            }`}
          >
            <span>{notification.message}</span>
            <button onClick={() => setNotification(null)} className="text-slate-400 hover:text-slate-700">
              Dismiss
            </button>
          </div>
        )}

        {/* Tab Contents */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* TAB 1: OVERVIEW */}
          {activeTab === 'overview' && metrics && (
            <div className="space-y-6">
              {/* Metrics Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-2xl bg-white border border-warm-border shadow-soft-sm">
                  <div className="text-xs font-medium text-slate-500">Approved FAQs</div>
                  <div className="text-2xl font-bold text-slate-900 mt-1">{metrics.total_approved_faqs}</div>
                  <div className="text-[11px] text-emerald-600 mt-1 flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" /> Searchable by students
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-white border border-warm-border shadow-soft-sm">
                  <div className="text-xs font-medium text-slate-500">Total Inquiries Logged</div>
                  <div className="text-2xl font-bold text-slate-900 mt-1">{metrics.total_queries}</div>
                  <div className="text-[11px] text-slate-400 mt-1">Real database events</div>
                </div>

                <div className="p-4 rounded-2xl bg-white border border-warm-border shadow-soft-sm">
                  <div className="text-xs font-medium text-slate-500">Unanswered / Low Conf</div>
                  <div className="text-2xl font-bold text-orange-600 mt-1">
                    {metrics.unanswered_queries + metrics.low_confidence_queries}
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1">Safe fallbacks provided</div>
                </div>

                <div className="p-4 rounded-2xl bg-white border border-warm-border shadow-soft-sm">
                  <div className="text-xs font-medium text-slate-500">Student Satisfaction</div>
                  <div className="text-2xl font-bold text-emerald-600 mt-1">
                    {metrics.satisfaction_rate_percent}%
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1">
                    {metrics.feedback_helpful_count} helpful / {metrics.feedback_unhelpful_count} unhelpful
                  </div>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 rounded-2xl bg-white border border-warm-border shadow-soft-sm space-y-3">
                  <div className="font-semibold text-slate-900 text-sm">Add Verified FAQ</div>
                  <p className="text-xs text-slate-500">
                    Create a new canonical institutional question, paraphrases, and official answer.
                  </p>
                  <button
                    onClick={() => handleOpenCreateFaq()}
                    className="w-full py-2 px-3 rounded-xl bg-orange-600 hover:bg-orange-700 text-white font-medium text-xs transition-colors flex items-center justify-center gap-1.5"
                  >
                    <Plus className="w-4 h-4" />
                    <span>Create Knowledge FAQ</span>
                  </button>
                </div>

                <div className="p-4 rounded-2xl bg-white border border-warm-border shadow-soft-sm space-y-3">
                  <div className="font-semibold text-slate-900 text-sm">Upload Campus Document</div>
                  <p className="text-xs text-slate-500">
                    Ingest approved official PDF notices, fee handbooks, or circulars with auto-chunking.
                  </p>
                  <button
                    onClick={() => setActiveTab('documents')}
                    className="w-full py-2 px-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-medium text-xs transition-colors flex items-center justify-center gap-1.5"
                  >
                    <Upload className="w-4 h-4" />
                    <span>Upload Document</span>
                  </button>
                </div>

                <div className="p-4 rounded-2xl bg-white border border-warm-border shadow-soft-sm space-y-3">
                  <div className="font-semibold text-slate-900 text-sm">Review Unanswered Queries</div>
                  <p className="text-xs text-slate-500">
                    Inspect queries where retrieval confidence was low, and convert them to FAQs.
                  </p>
                  <button
                    onClick={() => setActiveTab('unanswered')}
                    className="w-full py-2 px-3 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 font-medium text-xs transition-colors flex items-center justify-center gap-1.5"
                  >
                    <HelpCircle className="w-4 h-4" />
                    <span>Review Unanswered ({metrics.unanswered_queries})</span>
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* TAB: UNIFIED KNOWLEDGE REPOSITORY (12 DATA TYPES) */}
          {activeTab === 'unified_repository' && (
            <div className="space-y-5">
              {/* Top Metrics Row */}
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-2xl bg-white border border-warm-border shadow-soft-sm">
                  <div className="text-xs font-medium text-slate-500">Total Multi-Type Records</div>
                  <div className="text-2xl font-bold text-slate-900 mt-1">{knowledgeRecords.length}</div>
                  <div className="text-[11px] text-slate-400 mt-1">12 Institutional Schemas</div>
                </div>

                <div className="p-4 rounded-2xl bg-white border border-warm-border shadow-soft-sm">
                  <div className="text-xs font-medium text-slate-500">Active & Approved</div>
                  <div className="text-2xl font-bold text-emerald-600 mt-1">
                    {knowledgeRecords.filter((r) => r.is_approved && r.approval_status === 'approved').length}
                  </div>
                  <div className="text-[11px] text-emerald-600 mt-1 flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" /> Indexed for student queries
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-white border border-warm-border shadow-soft-sm">
                  <div className="text-xs font-medium text-slate-500">Sensitive / Admin Review</div>
                  <div className="text-2xl font-bold text-amber-600 mt-1">
                    {knowledgeRecords.filter((r) => r.is_sensitive || r.requires_admin_review).length}
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1">Fees, attendance, exams, policy</div>
                </div>

                <div className="p-4 rounded-2xl bg-white border border-warm-border shadow-soft-sm">
                  <div className="text-xs font-medium text-slate-500">Temporal / Expired Excluded</div>
                  <div className="text-2xl font-bold text-rose-600 mt-1">
                    {
                      knowledgeRecords.filter(
                        (r) =>
                          r.approval_status === 'expired' ||
                          (r.review_expiry_date && new Date(r.review_expiry_date) < new Date())
                      ).length
                    }
                  </div>
                  <div className="text-[11px] text-rose-500 mt-1">Safely withheld from RAG</div>
                </div>
              </div>

              {/* Filters & Search Control Bar */}
              <div className="p-4 rounded-2xl bg-white border border-warm-border shadow-soft-sm space-y-3">
                <div className="flex flex-col md:flex-row gap-3 items-center justify-between">
                  <div className="relative w-full md:w-80">
                    <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input
                      type="text"
                      placeholder="Search record title, ID, clause, or keywords..."
                      value={searchRecordQuery}
                      onChange={(e) => setSearchRecordQuery(e.target.value)}
                      className="w-full pl-9 pr-3 py-1.5 rounded-xl border border-warm-border text-xs focus:outline-none focus:border-orange-500"
                    />
                  </div>

                  <div className="flex items-center gap-3 w-full md:w-auto justify-end">
                    <label className="flex items-center gap-2 text-xs font-medium text-slate-700 cursor-pointer select-none">
                      <input
                        type="checkbox"
                        checked={filterSensitiveOnly}
                        onChange={(e) => setFilterSensitiveOnly(e.target.checked)}
                        className="rounded text-orange-600 focus:ring-orange-500 w-3.5 h-3.5"
                      />
                      <ShieldCheck className="w-3.5 h-3.5 text-amber-600" />
                      <span>Sensitive records requiring review only</span>
                    </label>
                  </div>
                </div>

                {/* 12 Type Pills */}
                <div className="flex flex-wrap gap-1.5 pt-1 border-t border-slate-100">
                  {[
                    { id: 'all', label: `All Types (${knowledgeRecords.length})` },
                    { id: 'policy', label: 'Policies' },
                    { id: 'academic_schedule', label: 'Academic & Exams' },
                    { id: 'contact_directory', label: 'Contact Directory' },
                    { id: 'facility_service', label: 'Campus Facilities' },
                    { id: 'library_resource', label: 'Library & Digital' },
                    { id: 'placement_procedure', label: 'Placements' },
                    { id: 'international_programme', label: 'International' },
                    { id: 'research_facility', label: 'Research & Labs' },
                    { id: 'student_activity', label: 'Student DSA Clubs' },
                    { id: 'grievance_procedure', label: 'Grievances & RMS' },
                    { id: 'official_notice', label: 'Notices & Circulars' },
                    { id: 'faq', label: 'FAQs' },
                  ].map((filterTab) => {
                    const isSelected = selectedRecordTypeFilter === filterTab.id;
                    const count =
                      filterTab.id === 'all'
                        ? knowledgeRecords.length
                        : knowledgeRecords.filter((r) => r.record_type === filterTab.id).length;
                    return (
                      <button
                        key={filterTab.id}
                        onClick={() => setSelectedRecordTypeFilter(filterTab.id)}
                        className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition-all ${
                          isSelected
                            ? 'bg-slate-900 text-white shadow-soft-sm'
                            : 'bg-warm-50 text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                        }`}
                      >
                        {filterTab.label} ({count})
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Records Table */}
              <div className="bg-white rounded-2xl border border-warm-border overflow-hidden shadow-soft-sm">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-warm-50 border-b border-warm-border text-slate-500 uppercase tracking-wider font-semibold">
                      <tr>
                        <th className="py-3 px-4">Record Identifier</th>
                        <th className="py-3 px-4">Type</th>
                        <th className="py-3 px-4">Title & Context</th>
                        <th className="py-3 px-4">Category</th>
                        <th className="py-3 px-4">Governance</th>
                        <th className="py-3 px-4">Status</th>
                        <th className="py-3 px-4 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-warm-border">
                      {knowledgeRecords
                        .filter((rec) => {
                          if (selectedRecordTypeFilter !== 'all' && rec.record_type !== selectedRecordTypeFilter) {
                            return false;
                          }
                          if (filterSensitiveOnly && !rec.is_sensitive && !rec.requires_admin_review) {
                            return false;
                          }
                          if (searchRecordQuery.trim()) {
                            const q = searchRecordQuery.toLowerCase();
                            const matchTitle = rec.title.toLowerCase().includes(q);
                            const matchId = rec.record_id.toLowerCase().includes(q);
                            const matchContent = rec.content.toLowerCase().includes(q);
                            const matchCategory = rec.category_name?.toLowerCase().includes(q);
                            return matchTitle || matchId || matchContent || matchCategory;
                          }
                          return true;
                        })
                        .map((rec) => (
                          <tr key={rec.id} className="hover:bg-warm-50/50 transition-colors">
                            <td className="py-3 px-4 font-mono text-[11px] font-semibold text-slate-700">
                              {rec.record_id}
                            </td>
                            <td className="py-3 px-4">
                              <span className="px-2 py-0.5 rounded-md text-[10px] font-semibold uppercase tracking-wider bg-slate-100 text-slate-700 border border-slate-200">
                                {rec.record_type.replace('_', ' ')}
                              </span>
                            </td>
                            <td className="py-3 px-4 max-w-xs">
                              <div className="font-medium text-slate-800 truncate">{rec.title}</div>
                              <div className="text-[10px] text-slate-400 truncate">
                                {rec.clause_reference && `Clause: ${rec.clause_reference} • `}
                                {rec.source_page && `Page: ${rec.source_page} • `}
                                {rec.last_verified_date && `Verified: ${rec.last_verified_date.slice(0, 10)}`}
                              </div>
                            </td>
                            <td className="py-3 px-4 text-slate-600">
                              <span className="px-2 py-0.5 rounded-md bg-slate-100 text-[10px]">
                                {rec.category_name || 'General'}
                              </span>
                            </td>
                            <td className="py-3 px-4">
                              {rec.is_sensitive ? (
                                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 text-[10px] font-semibold border border-amber-200">
                                  <ShieldCheck className="w-2.5 h-2.5" />
                                  Sensitive Policy
                                </span>
                              ) : (
                                <span className="text-slate-400 text-[11px]">Standard</span>
                              )}
                            </td>
                            <td className="py-3 px-4">
                              {rec.is_approved ? (
                                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-[10px] font-semibold border border-emerald-200">
                                  <CheckCircle2 className="w-2.5 h-2.5" /> Approved
                                </span>
                              ) : (
                                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 text-[10px] font-semibold border border-amber-200">
                                  <Clock className="w-2.5 h-2.5" /> Pending
                                </span>
                              )}
                            </td>
                            <td className="py-3 px-4 text-right space-x-1">
                              <button
                                onClick={() => setSelectedRecordForDetail(rec)}
                                className="p-1.5 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors"
                                title="Inspect Complete Record, Metadata & Variants"
                              >
                                <Eye className="w-3.5 h-3.5" />
                              </button>
                              {!rec.is_approved && (
                                <button
                                  onClick={() => handleApproveRecord(rec.record_id)}
                                  className="p-1.5 rounded-lg text-emerald-600 hover:bg-emerald-50 transition-colors"
                                  title="Approve for Student Retrieval"
                                >
                                  <CheckCircle2 className="w-3.5 h-3.5" />
                                </button>
                              )}
                              <button
                                onClick={() => handleGenerateVariants(rec.record_id)}
                                className="p-1.5 rounded-lg text-purple-600 hover:bg-purple-50 transition-colors"
                                title="Generate Searchable Variants via Gemini"
                              >
                                <Sparkles className="w-3.5 h-3.5" />
                              </button>
                              <button
                                onClick={() => handleDeleteRecord(rec.record_id)}
                                className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                                title="Delete Record"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB: UMS SERVICE CATALOG (234 ENTRIES) */}
          {activeTab === 'ums_catalog' && (
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <h3 className="text-sm font-bold text-slate-900">
                    UMS Service Catalog ({umsCatalog.length} Authenticated Screenshot Entries)
                  </h3>
                  <p className="text-xs text-slate-500">
                    Transcribed from student screenshots across 24 modules with navigation breadcrumbs.
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <div className="relative">
                    <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
                    <input
                      type="text"
                      placeholder="Search label, path, ID..."
                      value={umsSearchQuery}
                      onChange={(e) => setUmsSearchQuery(e.target.value)}
                      className="pl-8 pr-3 py-1.5 text-xs rounded-xl border border-warm-border bg-white focus:outline-none focus:border-orange-400 w-48 sm:w-64"
                    />
                  </div>

                  <select
                    value={umsModuleFilter}
                    onChange={(e) => setUmsModuleFilter(e.target.value)}
                    className="px-2.5 py-1.5 text-xs rounded-xl border border-warm-border bg-white text-slate-700 focus:outline-none focus:border-orange-400"
                  >
                    <option value="all">All Modules ({Array.from(new Set(umsCatalog.map((i) => i.module))).length})</option>
                    {Array.from(new Set(umsCatalog.map((i) => i.module)))
                      .sort()
                      .map((mod) => (
                        <option key={mod} value={mod}>
                          {mod}
                        </option>
                      ))}
                  </select>
                </div>
              </div>

              {/* Table */}
              <div className="rounded-2xl bg-white border border-warm-border overflow-hidden shadow-soft-sm">
                <div className="overflow-x-auto max-h-[650px]">
                  <table className="w-full text-left border-collapse text-xs">
                    <thead className="bg-slate-50 border-b border-warm-border sticky top-0 z-10">
                      <tr>
                        <th className="py-2.5 px-3 font-semibold text-slate-700">Catalog ID</th>
                        <th className="py-2.5 px-3 font-semibold text-slate-700">Module</th>
                        <th className="py-2.5 px-3 font-semibold text-slate-700">Service Label</th>
                        <th className="py-2.5 px-3 font-semibold text-slate-700">Navigation Breadcrumb</th>
                        <th className="py-2.5 px-3 font-semibold text-slate-700">Action Type</th>
                        <th className="py-2.5 px-3 font-semibold text-slate-700">Verification Status</th>
                        <th className="py-2.5 px-3 font-semibold text-slate-700 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-warm-border">
                      {umsCatalog
                        .filter((item) => {
                          const matchesMod = umsModuleFilter === 'all' || item.module === umsModuleFilter;
                          const matchesQ =
                            !umsSearchQuery.trim() ||
                            item.service_label.toLowerCase().includes(umsSearchQuery.toLowerCase()) ||
                            item.catalog_id.toLowerCase().includes(umsSearchQuery.toLowerCase()) ||
                            item.navigation_path.toLowerCase().includes(umsSearchQuery.toLowerCase()) ||
                            (item.keywords || []).some((k) => k.toLowerCase().includes(umsSearchQuery.toLowerCase()));
                          return matchesMod && matchesQ;
                        })
                        .map((item) => (
                          <tr key={item.id} className="hover:bg-slate-50/70 transition-colors">
                            <td className="py-2.5 px-3 font-mono font-semibold text-orange-700 text-[11px]">
                              {item.catalog_id}
                            </td>
                            <td className="py-2.5 px-3">
                              <span className="inline-block rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-700">
                                {item.module}
                              </span>
                            </td>
                            <td className="py-2.5 px-3 font-semibold text-slate-900 max-w-[180px] truncate" title={item.service_label}>
                              {item.service_label}
                            </td>
                            <td className="py-2.5 px-3 font-mono text-[11px] text-slate-600 max-w-[280px] truncate" title={item.navigation_path}>
                              {item.navigation_path}
                            </td>
                            <td className="py-2.5 px-3 text-[11px] text-slate-500">
                              {item.action_type}
                            </td>
                            <td className="py-2.5 px-3">
                              <span
                                className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                                  item.verification_status === 'verified'
                                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                                    : 'bg-blue-50 text-blue-700 border border-blue-200'
                                }`}
                              >
                                {item.verification_status === 'verified' ? 'Verified' : 'Menu Observed'}
                              </span>
                            </td>
                            <td className="py-2.5 px-3 text-right">
                              <button
                                onClick={() => handleOpenEditUms(item)}
                                className="p-1 rounded-lg text-slate-500 hover:text-orange-600 hover:bg-orange-50 transition-colors"
                                title="Edit Breadcrumbs & Status"
                              >
                                <Edit className="w-3.5 h-3.5" />
                              </button>
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB: ACTION WORKFLOWS (24 WORKFLOWS) */}
          {activeTab === 'action_workflows' && (
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900">
                  Campus Action Workflows ({actionWorkflows.length} Guided Standard Operating Procedures)
                </h3>
                <p className="text-xs text-slate-500">
                  Doctor appointments, Hostel bookings, Mental health counselling, Library discussion rooms, RMS grievances, and academic procedures.
                </p>
              </div>

              <div className="rounded-2xl bg-white border border-warm-border overflow-hidden shadow-soft-sm">
                <div className="overflow-x-auto max-h-[650px]">
                  <table className="w-full text-left border-collapse text-xs">
                    <thead className="bg-slate-50 border-b border-warm-border sticky top-0 z-10">
                      <tr>
                        <th className="py-2.5 px-3 font-semibold text-slate-700">Action ID</th>
                        <th className="py-2.5 px-3 font-semibold text-slate-700">Target System</th>
                        <th className="py-2.5 px-3 font-semibold text-slate-700">User Intent</th>
                        <th className="py-2.5 px-3 font-semibold text-slate-700">Action Mode</th>
                        <th className="py-2.5 px-3 font-semibold text-slate-700">UMS Navigation Path</th>
                        <th className="py-2.5 px-3 font-semibold text-slate-700">Steps & Prereqs</th>
                        <th className="py-2.5 px-3 font-semibold text-slate-700">Security Guardrail</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-warm-border">
                      {actionWorkflows.map((wf) => (
                        <tr key={wf.id} className="hover:bg-slate-50/70 transition-colors">
                          <td className="py-2.5 px-3 font-mono font-semibold text-purple-700 text-[11px]">
                            {wf.action_id}
                          </td>
                          <td className="py-2.5 px-3">
                            <span className="inline-block rounded-md bg-purple-50 border border-purple-200 px-2 py-0.5 text-[11px] font-semibold text-purple-800">
                              {wf.target_system}
                            </span>
                          </td>
                          <td className="py-2.5 px-3 font-semibold text-slate-900">
                            {wf.user_intent}
                          </td>
                          <td className="py-2.5 px-3">
                            <span
                              className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                                wf.action_mode === 'BOOK_HANDOFF'
                                  ? 'bg-emerald-100 text-emerald-800'
                                  : wf.action_mode === 'PREPARE'
                                  ? 'bg-indigo-100 text-indigo-800'
                                  : wf.action_mode === 'PERSONAL_RECORD'
                                  ? 'bg-amber-100 text-amber-800'
                                  : wf.action_mode === 'ESCALATE'
                                  ? 'bg-rose-100 text-rose-800'
                                  : 'bg-blue-100 text-blue-800'
                              }`}
                            >
                              {wf.action_mode}
                            </span>
                          </td>
                          <td className="py-2.5 px-3 font-mono text-[11px] text-slate-600 max-w-[260px] truncate" title={wf.ums_navigation_path}>
                            {wf.ums_navigation_path}
                          </td>
                          <td className="py-2.5 px-3 text-[11px] text-slate-600">
                            {(wf.steps || []).length} steps, {(wf.prerequisites || []).length} prereqs
                          </td>
                          <td className="py-2.5 px-3 text-[11px] text-slate-500 max-w-[240px] truncate" title={wf.execution_guardrail}>
                            {wf.execution_guardrail}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB: CAMPUS PLACES & WAYFINDING (10 LOCATIONS) */}
          {activeTab === 'campus_places' && (
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900">
                  LPU Verified Campus Wayfinding Directory ({campusPlaces.length} Locations)
                </h3>
                <p className="text-xs text-slate-500">
                  Verified blocks, rooms, opening hours, accessibility notes, and health facilities.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {campusPlaces.map((place) => (
                  <div
                    key={place.id}
                    className="rounded-2xl bg-white border border-warm-border p-4 shadow-soft-sm space-y-2 hover:shadow transition-all"
                  >
                    <div className="flex items-center justify-between border-b border-warm-border pb-2">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-sky-700 bg-sky-50 px-2 py-0.5 rounded">
                          {place.place_id}
                        </span>
                        <span className="text-xs font-semibold text-slate-800">{place.building}</span>
                      </div>
                      <span className="text-[11px] text-slate-500">{place.category}</span>
                    </div>

                    <h4 className="text-sm font-bold text-slate-900">{place.name}</h4>
                    <p className="text-xs text-slate-600 leading-relaxed">{place.description}</p>

                    <div className="grid grid-cols-2 gap-2 text-xs pt-1">
                      {place.floor_room && (
                        <div className="text-slate-700 bg-slate-50 p-1.5 rounded">
                          <strong>Floor:</strong> {place.floor_room}
                        </div>
                      )}
                      {place.opening_hours && (
                        <div className="text-slate-700 bg-slate-50 p-1.5 rounded">
                          <strong>Hours:</strong> {place.opening_hours}
                        </div>
                      )}
                    </div>

                    {place.accessibility && (
                      <div className="text-[11px] text-sky-800 bg-sky-50/70 p-1.5 rounded border border-sky-100">
                        <strong>Accessibility:</strong> {place.accessibility}
                      </div>
                    )}

                    {place.services_available && place.services_available.length > 0 && (
                      <div className="flex flex-wrap gap-1 pt-1">
                        {place.services_available.map((svc, sIdx) => (
                          <span
                            key={sIdx}
                            className="bg-slate-100 text-slate-700 text-[10px] px-1.5 py-0.5 rounded font-medium"
                          >
                            {svc}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 2: FAQ MANAGEMENT */}
          {activeTab === 'faqs' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="text-sm text-slate-500">
                  Total Approved Knowledge FAQs: <strong className="text-slate-900">{faqs.length}</strong>
                </div>
                <button
                  onClick={() => handleOpenCreateFaq()}
                  className="py-2 px-3.5 rounded-xl bg-orange-600 hover:bg-orange-700 text-white text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-soft"
                >
                  <Plus className="w-4 h-4" />
                  <span>New FAQ</span>
                </button>
              </div>

              <div className="bg-white rounded-2xl border border-warm-border overflow-hidden shadow-soft-sm">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-warm-50 border-b border-warm-border text-slate-500 uppercase tracking-wider font-semibold">
                      <tr>
                        <th className="py-3 px-4">Canonical Question</th>
                        <th className="py-3 px-4">Category</th>
                        <th className="py-3 px-4">Source</th>
                        <th className="py-3 px-4">Status</th>
                        <th className="py-3 px-4 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-warm-border">
                      {faqs.map((f) => (
                        <tr key={f.id} className="hover:bg-warm-50/50 transition-colors">
                          <td className="py-3 px-4 max-w-xs font-medium text-slate-800 truncate">
                            {f.canonical_question}
                          </td>
                          <td className="py-3 px-4 text-slate-600">
                            <span className="px-2 py-0.5 rounded-md bg-slate-100 border border-slate-200">
                              {f.category_name || 'General'}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-slate-500 truncate max-w-xs">
                            <a
                              href={f.source_url}
                              target="_blank"
                              rel="noreferrer"
                              className="text-orange-600 hover:underline flex items-center gap-1 truncate"
                            >
                              <span className="truncate">{f.source_title || 'Portal'}</span>
                              <ExternalLink className="w-3 h-3 shrink-0" />
                            </a>
                          </td>
                          <td className="py-3 px-4">
                            {f.is_approved ? (
                              <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-[10px] font-semibold border border-emerald-200">
                                Approved
                              </span>
                            ) : (
                              <span className="px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 text-[10px] font-semibold border border-amber-200">
                                Pending
                              </span>
                            )}
                          </td>
                          <td className="py-3 px-4 text-right space-x-1">
                            <button
                              onClick={() => handleOpenEditFaq(f)}
                              className="p-1 rounded-md text-slate-400 hover:text-slate-700 hover:bg-slate-100"
                              title="Edit FAQ"
                            >
                              <Edit className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDeleteFaq(f.id)}
                              className="p-1 rounded-md text-slate-400 hover:text-rose-600 hover:bg-rose-50"
                              title="Delete FAQ"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: KNOWLEDGE DOCUMENTS */}
          {activeTab === 'documents' && (
            <div className="space-y-6">
              {/* Document Upload Card */}
              <div className="p-5 rounded-2xl bg-white border border-warm-border shadow-soft-sm space-y-4">
                <div className="font-semibold text-slate-900 text-sm">Upload Institutional Document</div>
                <p className="text-xs text-slate-500">
                  Upload PDF, DOCX, or TXT handbooks or circulars. The system cleans text, neutralizes injection markers, and chunks into overlapping segments.
                </p>

                <form onSubmit={handleUploadDocument} className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div>
                    <label className="text-[11px] font-semibold text-slate-600 block mb-1">Document Title</label>
                    <input
                      type="text"
                      value={uploadTitle}
                      onChange={(e) => setUploadTitle(e.target.value)}
                      placeholder="e.g. LPU Academic Regulations 2026"
                      required
                      className="w-full text-xs px-3 py-2 rounded-xl border border-warm-border focus:border-orange-400 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="text-[11px] font-semibold text-slate-600 block mb-1">Campus Category</label>
                    <select
                      value={uploadCategoryId}
                      onChange={(e) => setUploadCategoryId(e.target.value)}
                      className="w-full text-xs px-3 py-2 rounded-xl border border-warm-border focus:border-orange-400 focus:outline-none bg-white"
                    >
                      <option value="">General Institutional</option>
                      {categories.map((c) => (
                        <option key={c.id} value={c.id}>{c.name}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="text-[11px] font-semibold text-slate-600 block mb-1">File (PDF, DOCX, TXT)</label>
                    <input
                      type="file"
                      accept=".pdf,.docx,.txt"
                      onChange={(e) => setUploadFile(e.target.files ? e.target.files[0] : null)}
                      required
                      className="w-full text-xs file:mr-2 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:bg-orange-50 file:text-orange-700 file:font-semibold"
                    />
                  </div>

                  <div className="md:col-span-3 pt-1">
                    <button
                      type="submit"
                      className="py-2 px-4 rounded-xl bg-orange-600 hover:bg-orange-700 text-white text-xs font-semibold flex items-center gap-1.5 transition-colors"
                    >
                      <Upload className="w-4 h-4" />
                      <span>Process & Ingest Document</span>
                    </button>
                  </div>
                </form>
              </div>

              {/* Documents List */}
              <div className="bg-white rounded-2xl border border-warm-border overflow-hidden shadow-soft-sm">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-warm-50 border-b border-warm-border text-slate-500 uppercase tracking-wider font-semibold">
                      <tr>
                        <th className="py-3 px-4">Title & Filename</th>
                        <th className="py-3 px-4">Size</th>
                        <th className="py-3 px-4">Chunks</th>
                        <th className="py-3 px-4">Status</th>
                        <th className="py-3 px-4 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-warm-border">
                      {documents.length === 0 ? (
                        <tr>
                          <td colSpan={5} className="py-6 text-center text-slate-400">
                            No documents uploaded yet.
                          </td>
                        </tr>
                      ) : (
                        documents.map((d) => (
                          <tr key={d.id} className="hover:bg-warm-50/50 transition-colors">
                            <td className="py-3 px-4">
                              <div className="font-semibold text-slate-900">{d.title}</div>
                              <div className="text-[11px] text-slate-400">{d.filename}</div>
                            </td>
                            <td className="py-3 px-4 text-slate-500 font-mono">
                              {(d.file_size / 1024).toFixed(1)} KB
                            </td>
                            <td className="py-3 px-4 text-slate-700 font-mono">
                              {d.total_chunks} chunks
                            </td>
                            <td className="py-3 px-4">
                              {d.is_approved ? (
                                <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-[10px] font-semibold border border-emerald-200">
                                  Approved & Indexed
                                </span>
                              ) : (
                                <span className="px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 text-[10px] font-semibold border border-amber-200">
                                  Pending Review
                                </span>
                              )}
                            </td>
                            <td className="py-3 px-4 text-right space-x-1">
                              <button
                                onClick={() => handlePreviewChunks(d)}
                                className="p-1 rounded-md text-slate-400 hover:text-slate-700 hover:bg-slate-100"
                                title="Inspect chunks"
                              >
                                <Eye className="w-4 h-4" />
                              </button>
                              {!d.is_approved && (
                                <button
                                  onClick={() => handleApproveDocument(d.id)}
                                  className="p-1 rounded-md text-emerald-600 hover:bg-emerald-50"
                                  title="Approve & Index"
                                >
                                  <CheckCircle2 className="w-4 h-4" />
                                </button>
                              )}
                              <button
                                onClick={() => handleDeleteDocument(d.id)}
                                className="p-1 rounded-md text-slate-400 hover:text-rose-600 hover:bg-rose-50"
                                title="Delete document"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Chunk Preview Modal */}
              {previewChunks && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fadeIn">
                  <div className="w-full max-w-2xl rounded-2xl bg-white border border-warm-border p-6 shadow-soft-lg space-y-4 max-h-[85vh] flex flex-col">
                    <div className="flex items-center justify-between border-b border-warm-border pb-3">
                      <div>
                        <h3 className="font-bold text-slate-900 text-sm">Chunk Preview: {previewDocTitle}</h3>
                        <p className="text-xs text-slate-500">Total extracted chunks: {previewChunks.length}</p>
                      </div>
                      <button
                        onClick={() => setPreviewChunks(null)}
                        className="p-1 text-slate-400 hover:text-slate-700"
                      >
                        ✕
                      </button>
                    </div>

                    <div className="flex-1 overflow-y-auto space-y-3 pr-2">
                      {previewChunks.map((c) => (
                        <div key={c.id} className="p-3 rounded-xl bg-warm-50 border border-warm-border text-xs">
                          <div className="flex justify-between font-mono text-[10px] text-slate-400 mb-1">
                            <span>Chunk #{c.chunk_index}</span>
                            <span>Page {c.page_number || 1} • {c.token_count} words</span>
                          </div>
                          <div className="text-slate-700 whitespace-pre-wrap leading-relaxed">
                            {c.content}
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="pt-2 border-t border-slate-100 flex justify-end">
                      <button
                        onClick={() => setPreviewChunks(null)}
                        className="py-1.5 px-4 rounded-xl bg-slate-900 text-white text-xs font-medium"
                      >
                        Close Preview
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 4: CATEGORIES */}
          {activeTab === 'categories' && (
            <div className="space-y-4">
              <div className="text-xs text-slate-500">
                Official Lovely Professional University campus categories.
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                {categories.map((c) => (
                  <div key={c.id} className="p-4 rounded-2xl bg-white border border-warm-border shadow-soft-sm space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="font-semibold text-slate-900 text-sm">{c.name}</div>
                      <span className="px-2 py-0.5 rounded-md bg-orange-50 text-orange-700 text-[10px] font-mono">
                        {c.slug}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 leading-relaxed">{c.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 5: SOURCE REVIEW */}
          {activeTab === 'sources' && (
            <div className="space-y-4">
              <div className="text-xs text-slate-500">
                Verified institutional sources, URLs, and freshness tracking.
              </div>
              <div className="bg-white rounded-2xl border border-warm-border overflow-hidden shadow-soft-sm">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-warm-50 border-b border-warm-border text-slate-500 uppercase tracking-wider font-semibold">
                      <tr>
                        <th className="py-3 px-4">Source Title</th>
                        <th className="py-3 px-4">Official URL</th>
                        <th className="py-3 px-4">Content Owner</th>
                        <th className="py-3 px-4">Last Verified</th>
                        <th className="py-3 px-4">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-warm-border">
                      {faqs.map((f) => (
                        <tr key={f.id} className="hover:bg-warm-50/50 transition-colors">
                          <td className="py-3 px-4 font-medium text-slate-800">{f.source_title}</td>
                          <td className="py-3 px-4 text-orange-600 font-mono">
                            <a href={f.source_url} target="_blank" rel="noreferrer" className="hover:underline flex items-center gap-1">
                              <span>{f.source_url}</span>
                              <ExternalLink className="w-3 h-3" />
                            </a>
                          </td>
                          <td className="py-3 px-4 text-slate-600">{f.content_owner}</td>
                          <td className="py-3 px-4 text-slate-400 font-mono">
                            {new Date(f.last_reviewed).toLocaleDateString()}
                          </td>
                          <td className="py-3 px-4">
                            <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-[10px] font-semibold border border-emerald-200">
                              Active & Verified
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB 6: UNANSWERED QUERIES */}
          {activeTab === 'unanswered' && analyticsData && (
            <div className="space-y-4">
              <div className="text-xs text-slate-500">
                Student queries that yielded low confidence or triggered safe fallbacks. Convert them into verified FAQs with one click.
              </div>

              {analyticsData.unanswered_queries.length === 0 ? (
                <div className="p-8 rounded-2xl bg-white border border-warm-border text-center text-xs text-slate-400">
                  No low-confidence queries recorded yet. All inquiries matched with acceptable confidence!
                </div>
              ) : (
                <div className="bg-white rounded-2xl border border-warm-border overflow-hidden shadow-soft-sm">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-warm-50 border-b border-warm-border text-slate-500 uppercase tracking-wider font-semibold">
                      <tr>
                        <th className="py-3 px-4">Student Query</th>
                        <th className="py-3 px-4">Confidence Score</th>
                        <th className="py-3 px-4">System State</th>
                        <th className="py-3 px-4 text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-warm-border">
                      {analyticsData.unanswered_queries.map((u: any) => (
                        <tr key={u.id} className="hover:bg-warm-50/50 transition-colors">
                          <td className="py-3 px-4 font-medium text-slate-800">{u.query_text}</td>
                          <td className="py-3 px-4 font-mono text-orange-600">
                            {u.confidence_score.toFixed(2)}
                          </td>
                          <td className="py-3 px-4 text-slate-500">{u.gemini_status}</td>
                          <td className="py-3 px-4 text-right">
                            <button
                              onClick={() => handleOpenCreateFaq(u.query_text)}
                              className="px-2.5 py-1 rounded-lg bg-orange-50 text-orange-700 border border-orange-200 hover:bg-orange-100 font-semibold text-[11px] flex items-center gap-1 ml-auto"
                            >
                              <Plus className="w-3 h-3" />
                              <span>Create FAQ</span>
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* TAB 7: FEEDBACK */}
          {activeTab === 'feedback' && analyticsData && (
            <div className="space-y-4">
              <div className="text-xs text-slate-500">
                Real student evaluations (helpful / unhelpful) and user comments.
              </div>

              {analyticsData.feedback_logs.length === 0 ? (
                <div className="p-8 rounded-2xl bg-white border border-warm-border text-center text-xs text-slate-400">
                  No feedback recorded yet. Students can rate answers with the thumbs up/down buttons.
                </div>
              ) : (
                <div className="space-y-2">
                  {analyticsData.feedback_logs.map((fb: any) => (
                    <div key={fb.id} className="p-3.5 rounded-xl bg-white border border-warm-border flex items-center justify-between text-xs">
                      <div className="flex items-center gap-3">
                        <span
                          className={`p-1.5 rounded-lg ${
                            fb.rating === 'helpful'
                              ? 'bg-emerald-50 text-emerald-700'
                              : 'bg-rose-50 text-rose-700'
                          }`}
                        >
                          {fb.rating === 'helpful' ? <ThumbsUp className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
                        </span>
                        <div>
                          <div className="font-semibold text-slate-900 capitalize">{fb.rating}</div>
                          {fb.comment && <div className="text-slate-600 mt-0.5">"{fb.comment}"</div>}
                        </div>
                      </div>
                      <div className="text-[11px] text-slate-400 font-mono">
                        {new Date(fb.created_at).toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB 8: ANALYTICS & QUOTA */}
          {activeTab === 'analytics' && analyticsData && (
            <div className="space-y-6">
              {/* Gemini Quota Card */}
              <div className="p-5 rounded-2xl bg-white border border-warm-border shadow-soft-sm space-y-4">
                <div className="flex items-center justify-between">
                  <div className="font-semibold text-slate-900 text-sm flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-orange-600" />
                    <span>Google Gemini API Free Tier Monitor</span>
                  </div>
                  <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                    analyticsData.gemini_quota.is_circuit_open
                      ? 'bg-rose-50 text-rose-700 border border-rose-200'
                      : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                  }`}>
                    {analyticsData.gemini_quota.is_circuit_open ? 'Circuit Breaker Open (Cooldown)' : 'Operational & Ready'}
                  </span>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div className="p-3 rounded-xl bg-warm-50 border border-warm-border">
                    <div className="text-[11px] text-slate-500">Configured Model</div>
                    <div className="font-mono font-bold text-xs text-slate-900 mt-0.5">
                      {analyticsData.gemini_quota.configured_model}
                    </div>
                  </div>
                  <div className="p-3 rounded-xl bg-warm-50 border border-warm-border">
                    <div className="text-[11px] text-slate-500">Successful API Calls</div>
                    <div className="font-mono font-bold text-xs text-emerald-600 mt-0.5">
                      {analyticsData.gemini_quota.successful_requests}
                    </div>
                  </div>
                  <div className="p-3 rounded-xl bg-warm-50 border border-warm-border">
                    <div className="text-[11px] text-slate-500">Rate Limit Errors (429)</div>
                    <div className="font-mono font-bold text-xs text-orange-600 mt-0.5">
                      {analyticsData.gemini_quota.rate_limit_errors}
                    </div>
                  </div>
                  <div className="p-3 rounded-xl bg-warm-50 border border-warm-border">
                    <div className="text-[11px] text-slate-500">Tokens Processed</div>
                    <div className="font-mono font-bold text-xs text-slate-900 mt-0.5">
                      {analyticsData.gemini_quota.total_tokens_consumed}
                    </div>
                  </div>
                </div>
              </div>

              {/* Recent Query Log Table */}
              <div className="bg-white rounded-2xl border border-warm-border overflow-hidden shadow-soft-sm">
                <div className="p-4 border-b border-warm-border font-semibold text-slate-900 text-xs">
                  Recent Student Inquiries Log (Audit Trail)
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-warm-50 border-b border-warm-border text-slate-500 uppercase tracking-wider font-semibold">
                      <tr>
                        <th className="py-3 px-4">Query</th>
                        <th className="py-3 px-4">Confidence</th>
                        <th className="py-3 px-4">Strategy</th>
                        <th className="py-3 px-4">Latency</th>
                        <th className="py-3 px-4">Time</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-warm-border">
                      {analyticsData.recent_queries.slice(0, 15).map((q: any) => (
                        <tr key={q.id} className="hover:bg-warm-50/50 transition-colors">
                          <td className="py-3 px-4 font-medium text-slate-800 max-w-xs truncate">{q.query_text}</td>
                          <td className="py-3 px-4 font-mono">
                            <span className={`px-1.5 py-0.5 rounded ${
                              q.confidence_score >= 0.70 ? 'bg-emerald-50 text-emerald-700' : 'bg-orange-50 text-orange-700'
                            }`}>
                              {q.confidence_score.toFixed(2)}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-slate-600">{q.retrieval_strategy}</td>
                          <td className="py-3 px-4 font-mono text-slate-500">{q.latency_ms} ms</td>
                          <td className="py-3 px-4 text-slate-400 font-mono">
                            {new Date(q.created_at).toLocaleTimeString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB 9: SETTINGS */}
          {activeTab === 'settings' && (
            <div className="max-w-3xl space-y-6">
              <div className="p-5 rounded-2xl bg-white border border-warm-border shadow-soft-sm space-y-4">
                <div className="font-semibold text-slate-900 text-sm">System & Model Parameters</div>
                <div className="space-y-3 text-xs text-slate-600">
                  <div className="flex justify-between py-2 border-b border-slate-100">
                    <span className="font-medium text-slate-800">AI Provider</span>
                    <span>Google Gen AI SDK (google-genai)</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-slate-100">
                    <span className="font-medium text-slate-800">Configured Flash Model</span>
                    <span className="font-mono text-orange-600">gemini-2.5-flash / gemini-3.8-flash</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-slate-100">
                    <span className="font-medium text-slate-800">RAG Keyword Boost Weight</span>
                    <span className="font-mono">0.35</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-slate-100">
                    <span className="font-medium text-slate-800">RAG TF-IDF Vector Weight</span>
                    <span className="font-mono">0.25</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-slate-100">
                    <span className="font-medium text-slate-800">Dense Semantic Cosine Weight</span>
                    <span className="font-mono">0.40</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-slate-100">
                    <span className="font-medium text-slate-800">High Confidence Threshold</span>
                    <span className="font-mono">&gt;= 0.70</span>
                  </div>
                  <div className="flex justify-between py-2">
                    <span className="font-medium text-slate-800">Institutional System Prompt Enforcement</span>
                    <span className="text-emerald-700 font-semibold">Active & Immutable</span>
                  </div>
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-white border border-warm-border shadow-soft-sm space-y-3">
                <div className="font-semibold text-slate-900 text-sm">Synchronize & Clear Cache</div>
                <p className="text-xs text-slate-500">
                  Force a full rebuild of the TF-IDF matrix and dense vector representations from all approved FAQs and document chunks.
                </p>
                <button
                  onClick={handleReindex}
                  disabled={reindexing}
                  className="py-2.5 px-4 rounded-xl bg-orange-600 hover:bg-orange-700 text-white font-medium text-xs transition-colors flex items-center gap-2"
                >
                  <RefreshCw className={`w-4 h-4 ${reindexing ? 'animate-spin' : ''}`} />
                  <span>Re-index Knowledge Base Now</span>
                </button>
              </div>
            </div>
          )}

          {/* TAB: AI INTELLIGENCE & MULTI-LLM PROVIDER ARCHITECTURE */}
          {activeTab === 'ai_intelligence' && (
            <div className="space-y-6 animate-fadeIn">
              {/* Top Overview Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-2xl bg-white border border-warm-border shadow-soft-sm">
                  <div className="text-xs font-medium text-slate-500">Configured Providers</div>
                  <div className="text-2xl font-bold text-slate-900 mt-1">7 Providers</div>
                  <div className="text-[11px] text-emerald-600 mt-1 flex items-center gap-1 font-mono">
                    Gemini, Groq, OpenRouter, Mistral, Cohere, BazaarLink, PEKPIK
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-white border border-warm-border shadow-soft-sm">
                  <div className="text-xs font-medium text-slate-500">Registered Models</div>
                  <div className="text-2xl font-bold text-slate-900 mt-1">{intelProviders.length || 10} Models</div>
                  <div className="text-[11px] text-slate-400 mt-1">Free-tier & Paid Cascade</div>
                </div>

                <div className="p-4 rounded-2xl bg-white border border-warm-border shadow-soft-sm">
                  <div className="text-xs font-medium text-slate-500">Proprietary Identities</div>
                  <div className="text-2xl font-bold text-orange-600 mt-1">4 Identities + Auto</div>
                  <div className="text-[11px] text-slate-400 mt-1">NOVA, THEMIS, ATHENA, ORACLE</div>
                </div>

                <div className="p-4 rounded-2xl bg-white border border-warm-border shadow-soft-sm">
                  <div className="text-xs font-medium text-slate-500">Total AI Cost (Session)</div>
                  <div className="text-2xl font-bold text-emerald-600 mt-1">
                    ${(intelCosts?.attribution_by_intelligence?.reduce((acc: number, c: any) => acc + (c.total_cost_usd || 0), 0) || 0).toFixed(4)}
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1">Controlled by CostController</div>
                </div>
              </div>

              {/* SECTION 1: Registered Models & Capabilities Table */}
              <div className="bg-white rounded-2xl border border-warm-border overflow-hidden shadow-soft-sm">
                <div className="p-4 border-b border-warm-border flex items-center justify-between">
                  <div>
                    <h3 className="font-bold text-slate-900 text-sm">Shared Model Provider Registry</h3>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Centrally managed pool of LLM APIs with real-time capability matching and circuit breakers.
                    </p>
                  </div>
                  <button
                    onClick={async () => {
                      const res = await api.getAdminIntelligenceProviders();
                      setIntelProviders(res);
                      showNotification('Refreshed provider registry.');
                    }}
                    className="p-1.5 rounded-lg border border-slate-200 text-slate-500 hover:text-slate-800 hover:bg-slate-50"
                    title="Refresh Provider Registry"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                  </button>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-warm-50 border-b border-warm-border text-slate-500 uppercase tracking-wider font-semibold">
                      <tr>
                        <th className="py-3 px-4">Provider</th>
                        <th className="py-3 px-4">Model ID</th>
                        <th className="py-3 px-4">Latency Tier</th>
                        <th className="py-3 px-4">Capabilities</th>
                        <th className="py-3 px-4">Pricing (1M tokens)</th>
                        <th className="py-3 px-4">Status</th>
                        <th className="py-3 px-4 text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-warm-border">
                      {intelProviders.map((m: any) => (
                        <tr key={`${m.provider_name}-${m.model_id}`} className="hover:bg-warm-50/50 transition-colors">
                          <td className="py-3 px-4 font-semibold text-slate-800 capitalize">
                            {m.provider_name}
                          </td>
                          <td className="py-3 px-4 font-mono font-medium text-slate-900">
                            {m.model_id}
                          </td>
                          <td className="py-3 px-4">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                              m.latency_tier === 'fast'
                                ? 'bg-emerald-50 text-emerald-700'
                                : m.latency_tier === 'deep_reasoning'
                                ? 'bg-indigo-50 text-indigo-700'
                                : 'bg-amber-50 text-amber-700'
                            }`}>
                              {m.latency_tier}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <div className="flex flex-wrap gap-1">
                              {m.capabilities?.streaming && <span className="px-1.5 py-0.2 bg-slate-100 rounded text-[9px] text-slate-600">stream</span>}
                              {m.capabilities?.structured_output && <span className="px-1.5 py-0.2 bg-slate-100 rounded text-[9px] text-slate-600">json</span>}
                              {m.capabilities?.tools && <span className="px-1.5 py-0.2 bg-blue-50 text-blue-700 rounded text-[9px]">tools</span>}
                              {m.capabilities?.reasoning && <span className="px-1.5 py-0.2 bg-indigo-50 text-indigo-700 rounded text-[9px]">reasoning</span>}
                              {m.capabilities?.vision && <span className="px-1.5 py-0.2 bg-violet-50 text-violet-700 rounded text-[9px]">vision</span>}
                            </div>
                          </td>
                          <td className="py-3 px-4 font-mono text-[11px] text-slate-600">
                            ${m.pricing?.input_usd_per_1m || 0} in / ${m.pricing?.output_usd_per_1m || 0} out
                          </td>
                          <td className="py-3 px-4">
                            {m.is_available ? (
                              <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-[10px] font-semibold border border-emerald-200">
                                Active
                              </span>
                            ) : (
                              <span className="px-2 py-0.5 rounded-full bg-rose-50 text-rose-700 text-[10px] font-semibold border border-rose-200">
                                Disabled / Trip
                              </span>
                            )}
                          </td>
                          <td className="py-3 px-4 text-right">
                            <button
                              onClick={() => handleToggleModel(m.provider_name, m.model_id, m.is_available)}
                              className={`px-2.5 py-1 rounded-md text-[11px] font-medium border transition-colors ${
                                m.is_available
                                  ? 'border-rose-200 bg-rose-50 text-rose-700 hover:bg-rose-100'
                                  : 'border-emerald-200 bg-emerald-50 text-emerald-700 hover:bg-emerald-100'
                              }`}
                            >
                              {m.is_available ? 'Disable' : 'Enable'}
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* SECTION 2: 4 Proprietary Intelligence Systems */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-bold text-slate-900 text-sm">Four Proprietary Intelligence Systems</h3>
                    <p className="text-xs text-slate-500">
                      Independent agentic identities dynamically routed across the shared model provider pool.
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {(intelIdentities.length > 0 ? intelIdentities : [
                    { id: 'nova', name: 'NOVA', subtitle: 'Everyday Intelligence', role: 'General conversation, Hinglish & daily student living', default_thinking_level: 'Low', allowed_subagents: ['hermes', 'argus'], prompt_length_chars: 1420 },
                    { id: 'themis', name: 'THEMIS', subtitle: 'University Intelligence', role: 'LPU academic policies, attendance 65% floor & benefits', default_thinking_level: 'Balanced', allowed_subagents: ['hermes', 'mnemos'], prompt_length_chars: 2150 },
                    { id: 'athena', name: 'ATHENA', subtitle: 'Advanced Intelligence', role: 'Multi-step reasoning, algorithms, coding & system design', default_thinking_level: 'High', allowed_subagents: ['forge', 'mnemos'], prompt_length_chars: 2680 },
                    { id: 'oracle', name: 'ORACLE', subtitle: 'Research Intelligence', role: 'Primary sources, research papers, SIH & evidence synthesis', default_thinking_level: 'High', allowed_subagents: ['vision', 'argus'], prompt_length_chars: 2340 },
                  ]).map((ident: any) => (
                    <div key={ident.id} className="p-4 rounded-2xl bg-white border border-warm-border shadow-soft-sm space-y-3 flex flex-col justify-between">
                      <div className="space-y-1.5">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-slate-900 text-sm">{ident.name}</span>
                          <span className="px-2 py-0.5 rounded-full bg-orange-50 text-orange-700 text-[10px] font-semibold border border-orange-200">
                            {ident.default_thinking_level}
                          </span>
                        </div>
                        <div className="text-xs font-semibold text-orange-800">{ident.subtitle}</div>
                        <p className="text-xs text-slate-600 leading-relaxed">{ident.role}</p>
                      </div>

                      <div className="pt-2 border-t border-slate-100 text-[11px] text-slate-500 space-y-1">
                        <div className="flex justify-between">
                          <span>Allowed Subagents:</span>
                          <span className="font-mono text-slate-800">{ident.allowed_subagents?.join(', ') || 'Direct'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Master Prompt Size:</span>
                          <span className="font-mono text-slate-800">{ident.prompt_length_chars} chars</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* SECTION 3: Token Accounting & Cost Attribution */}
              <div className="bg-white rounded-2xl border border-warm-border overflow-hidden shadow-soft-sm">
                <div className="p-4 border-b border-warm-border">
                  <h3 className="font-bold text-slate-900 text-sm">Real-Time Cost Controller & Token Attribution</h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Continuous token and dollar accounting across intelligence identities.
                  </p>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-warm-50 border-b border-warm-border text-slate-500 uppercase tracking-wider font-semibold">
                      <tr>
                        <th className="py-3 px-4">Intelligence Identity</th>
                        <th className="py-3 px-4">Total Calls</th>
                        <th className="py-3 px-4">Tokens Consumed</th>
                        <th className="py-3 px-4">Total Cost (USD)</th>
                        <th className="py-3 px-4">Max Input Budget</th>
                        <th className="py-3 px-4">Max Output Budget</th>
                        <th className="py-3 px-4">Per-Turn Cost Limit</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-warm-border">
                      {['nova', 'themis', 'athena', 'oracle', 'aegis'].map((intelKey) => {
                        const attr = intelCosts?.attribution_by_intelligence?.find((a: any) => a.intelligence_id === intelKey) || {
                          calls: 0,
                          total_tokens: 0,
                          total_cost_usd: 0,
                        };
                        const cfg = intelCosts?.configured_budgets?.[intelKey] || {};
                        return (
                          <tr key={intelKey} className="hover:bg-warm-50/50 transition-colors">
                            <td className="py-3 px-4 font-bold text-slate-900 uppercase">
                              {intelKey}
                            </td>
                            <td className="py-3 px-4 font-mono">{attr.calls || 0}</td>
                            <td className="py-3 px-4 font-mono">{attr.total_tokens || 0}</td>
                            <td className="py-3 px-4 font-mono font-semibold text-emerald-700">
                              ${(attr.total_cost_usd || 0).toFixed(5)}
                            </td>
                            <td className="py-3 px-4 font-mono text-slate-500">{cfg.max_input_tokens || 4000} toks</td>
                            <td className="py-3 px-4 font-mono text-slate-500">{cfg.max_output_tokens || 1000} toks</td>
                            <td className="py-3 px-4 font-mono text-slate-500">${cfg.max_request_cost_usd || 0.02}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* SECTION 4: Benchmark Evaluation Suite Runner */}
              <div className="bg-white rounded-2xl border border-warm-border p-5 shadow-soft-sm space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-warm-border pb-3">
                  <div>
                    <h3 className="font-bold text-slate-900 text-sm">Automated Benchmark Evaluation Suite</h3>
                    <p className="text-xs text-slate-500">
                      Run automated domain regression benchmarks measuring correctness, statutory compliance (65% floor), latency, and cost.
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <select
                      value={evalTarget}
                      onChange={(e) => setEvalTarget(e.target.value)}
                      className="px-3 py-1.5 rounded-xl border border-warm-border text-xs font-semibold text-slate-800 bg-white focus:outline-none"
                    >
                      <option value="themis">THEMIS (Policy & Attendance Suite)</option>
                      <option value="athena">ATHENA (Reasoning & Code Suite)</option>
                      <option value="nova">NOVA (Everyday Living Suite)</option>
                      <option value="oracle">ORACLE (Research & Citation Suite)</option>
                    </select>
                    <button
                      onClick={handleRunEvaluation}
                      disabled={evalLoading}
                      className="px-4 py-1.5 rounded-xl bg-orange-600 hover:bg-orange-700 text-white font-semibold text-xs transition-colors flex items-center gap-1.5 disabled:opacity-50"
                    >
                      {evalLoading ? (
                        <>
                          <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                          <span>Running Benchmark...</span>
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-3.5 h-3.5" />
                          <span>Run Benchmark</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>

                {/* Evaluation Results Display */}
                {evalResult && (
                  <div className="space-y-4 animate-fadeIn">
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs">
                      <div>
                        <div className="text-slate-400 text-[10px] uppercase font-bold">Passed / Total</div>
                        <div className="text-lg font-bold text-slate-900">
                          {evalResult.passed_cases} / {evalResult.total_cases} ({evalResult.pass_rate_percent}%)
                        </div>
                      </div>
                      <div>
                        <div className="text-slate-400 text-[10px] uppercase font-bold">Avg Latency</div>
                        <div className="text-lg font-bold text-slate-900">{evalResult.average_latency_ms} ms</div>
                      </div>
                      <div>
                        <div className="text-slate-400 text-[10px] uppercase font-bold">Avg Grounding Score</div>
                        <div className="text-lg font-bold text-emerald-600">
                          {(evalResult.average_grounding_score * 100).toFixed(0)}%
                        </div>
                      </div>
                      <div>
                        <div className="text-slate-400 text-[10px] uppercase font-bold">Total Eval Cost</div>
                        <div className="text-lg font-bold text-slate-900 font-mono">
                          ${(evalResult.total_cost_usd || 0).toFixed(5)}
                        </div>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="text-xs font-semibold text-slate-800">Test Case Breakdown:</div>
                      <div className="space-y-1.5 max-h-60 overflow-y-auto pr-1">
                        {evalResult.results?.map((tc: any, idx: number) => (
                          <div
                            key={idx}
                            className={`p-2.5 rounded-xl border text-xs flex items-center justify-between gap-3 ${
                              tc.passed
                                ? 'bg-emerald-50/60 border-emerald-200 text-emerald-950'
                                : 'bg-rose-50/60 border-rose-200 text-rose-950'
                            }`}
                          >
                            <div className="min-w-0 flex-1">
                              <div className="font-semibold truncate">{tc.name || `Test Case #${idx + 1}`}</div>
                              <div className="text-[11px] text-slate-500 truncate mt-0.5 font-mono">"{tc.query}"</div>
                            </div>
                            <div className="flex items-center gap-2 shrink-0">
                              <span className="text-[10px] font-mono text-slate-500">{tc.latency_ms}ms</span>
                              <span
                                className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                  tc.passed
                                    ? 'bg-emerald-600 text-white'
                                    : 'bg-rose-600 text-white'
                                }`}
                              >
                                {tc.passed ? 'PASSED' : 'FAILED'}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>

      {/* DETAILED KNOWLEDGE RECORD INSPECTION DRAWER / MODAL */}
      {selectedRecordForDetail && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fadeIn">
          <div className="w-full max-w-3xl rounded-2xl bg-white border border-warm-border p-6 shadow-soft-lg space-y-4 max-h-[90vh] flex flex-col">
            <div className="flex items-center justify-between border-b border-warm-border pb-3">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-800 font-semibold border border-slate-200">
                    {selectedRecordForDetail.record_id}
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider bg-orange-50 text-orange-700 border border-orange-200">
                    {selectedRecordForDetail.record_type.replace('_', ' ')}
                  </span>
                  {selectedRecordForDetail.is_sensitive && (
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200 flex items-center gap-1">
                      <ShieldCheck className="w-3 h-3" /> Sensitive Policy
                    </span>
                  )}
                  {selectedRecordForDetail.is_approved ? (
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                      Approved
                    </span>
                  ) : (
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200">
                      Pending Review
                    </span>
                  )}
                </div>
                <h3 className="font-bold text-slate-900 text-base">{selectedRecordForDetail.title}</h3>
              </div>
              <button
                onClick={() => setSelectedRecordForDetail(null)}
                className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100"
              >
                ✕
              </button>
            </div>

            <div className="flex-1 overflow-y-auto space-y-4 pr-2 text-xs">
              {/* Provenance & Dates */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 p-3 rounded-xl bg-warm-50 border border-warm-border">
                <div>
                  <div className="text-[10px] text-slate-400 font-medium">Category</div>
                  <div className="font-semibold text-slate-800">{selectedRecordForDetail.category_name || 'General'}</div>
                </div>
                <div>
                  <div className="text-[10px] text-slate-400 font-medium">Last Verified</div>
                  <div className="font-semibold text-slate-800">
                    {selectedRecordForDetail.last_verified_date ? selectedRecordForDetail.last_verified_date.slice(0, 10) : 'N/A'}
                  </div>
                </div>
                <div>
                  <div className="text-[10px] text-slate-400 font-medium">Clause / Section</div>
                  <div className="font-semibold text-slate-800">{selectedRecordForDetail.clause_reference || 'N/A'}</div>
                </div>
                <div>
                  <div className="text-[10px] text-slate-400 font-medium">Document / Page</div>
                  <div className="font-semibold text-slate-800">
                    {selectedRecordForDetail.source_document || 'N/A'} {selectedRecordForDetail.source_page ? `(p. ${selectedRecordForDetail.source_page})` : ''}
                  </div>
                </div>
              </div>

              {/* Source Link */}
              {selectedRecordForDetail.original_source_url && (
                <div className="flex items-center gap-2 p-2.5 rounded-xl bg-slate-50 border border-slate-200">
                  <ExternalLink className="w-3.5 h-3.5 text-orange-600 shrink-0" />
                  <span className="text-[11px] text-slate-500">Official Source:</span>
                  <a
                    href={selectedRecordForDetail.original_source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-[11px] font-medium text-orange-600 hover:underline truncate"
                  >
                    {selectedRecordForDetail.original_source_url}
                  </a>
                </div>
              )}

              {/* Full Content */}
              <div>
                <div className="font-semibold text-slate-800 mb-1">Authoritative Institutional Content:</div>
                <div className="p-3.5 rounded-xl bg-warm-50 border border-warm-border text-slate-700 whitespace-pre-wrap leading-relaxed font-sans">
                  {selectedRecordForDetail.content}
                </div>
              </div>

              {/* Type-Specific Metadata */}
              {selectedRecordForDetail.type_metadata && Object.keys(selectedRecordForDetail.type_metadata).length > 0 && (
                <div>
                  <div className="font-semibold text-slate-800 mb-1">Type-Specific Metadata Attributes:</div>
                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 grid grid-cols-2 gap-2 text-[11px]">
                    {Object.entries(selectedRecordForDetail.type_metadata).map(([k, v]) => (
                      <div key={k} className="p-1.5 rounded bg-white border border-slate-100">
                        <span className="text-slate-400 font-medium capitalize">{k.replace('_', ' ')}: </span>
                        <span className="font-semibold text-slate-700">{typeof v === 'object' ? JSON.stringify(v) : String(v)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Searchable Question Variants */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <div className="font-semibold text-slate-800 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-purple-600" />
                    <span>Searchable Question Variants ({selectedRecordForDetail.searchable_variants?.length || 0}):</span>
                  </div>
                  <button
                    onClick={() => handleGenerateVariants(selectedRecordForDetail.record_id)}
                    className="px-2.5 py-1 rounded-lg bg-purple-50 text-purple-700 hover:bg-purple-100 font-semibold text-[11px] transition-colors"
                  >
                    Generate / Refresh Variants
                  </button>
                </div>
                {selectedRecordForDetail.searchable_variants && selectedRecordForDetail.searchable_variants.length > 0 ? (
                  <ul className="space-y-1 p-2.5 rounded-xl bg-warm-50 border border-warm-border">
                    {selectedRecordForDetail.searchable_variants.map((v, i) => (
                      <li key={i} className="text-[11px] text-slate-600 flex items-start gap-1.5">
                        <span className="text-orange-500 font-bold">•</span>
                        <span>{v}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="p-3 rounded-xl bg-warm-50 border border-warm-border text-slate-400 text-center text-xs">
                    No question variants generated yet. Click above to generate using Gemini without changing facts.
                  </div>
                )}
              </div>

              {/* Audit Trail */}
              {selectedRecordForDetail.audit_trail && selectedRecordForDetail.audit_trail.length > 0 && (
                <div>
                  <div className="font-semibold text-slate-800 mb-1">Audit Trail History:</div>
                  <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                    {selectedRecordForDetail.audit_trail.map((entry: any, i: number) => (
                      <div key={i} className="flex justify-between text-[10px] text-slate-500 font-mono">
                        <span>{entry.action || 'event'} by {entry.actor || 'system'}</span>
                        <span>{entry.timestamp ? entry.timestamp.slice(0, 19).replace('T', ' ') : ''}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Bottom Actions */}
            <div className="pt-3 border-t border-warm-border flex items-center justify-between">
              <div className="text-[11px] text-slate-400 font-mono">
                SHA-256: {selectedRecordForDetail.content_hash.slice(0, 16)}...
              </div>
              <div className="flex items-center gap-2">
                {!selectedRecordForDetail.is_approved && (
                  <button
                    onClick={async () => {
                      await handleApproveRecord(selectedRecordForDetail.record_id);
                      setSelectedRecordForDetail({ ...selectedRecordForDetail, is_approved: true, approval_status: 'approved' });
                    }}
                    className="px-3 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs flex items-center gap-1.5"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Approve Record</span>
                  </button>
                )}
                <button
                  onClick={() => setSelectedRecordForDetail(null)}
                  className="px-3.5 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium text-xs"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* FAQ CREATE / EDIT MODAL */}
      {isFaqModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fadeIn">
          <div className="w-full max-w-lg rounded-2xl bg-white border border-warm-border p-6 shadow-soft-lg space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-warm-border pb-3">
              <h3 className="font-bold text-slate-900 text-sm">
                {editingFaq ? 'Edit Knowledge FAQ' : 'New Knowledge FAQ'}
              </h3>
              <button
                onClick={() => setIsFaqModalOpen(false)}
                className="p-1 text-slate-400 hover:text-slate-700"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSaveFaq} className="space-y-3 text-xs">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Campus Category</label>
                <select
                  value={faqFormData.category_id}
                  onChange={(e) => setFaqFormData({ ...faqFormData, category_id: e.target.value })}
                  required
                  className="w-full px-3 py-2 rounded-xl border border-warm-border focus:border-orange-400 focus:outline-none bg-white"
                >
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Canonical Question</label>
                <input
                  type="text"
                  value={faqFormData.canonical_question}
                  onChange={(e) => setFaqFormData({ ...faqFormData, canonical_question: e.target.value })}
                  placeholder="e.g. How do I download my examination date sheet at LPU?"
                  required
                  className="w-full px-3 py-2 rounded-xl border border-warm-border focus:border-orange-400 focus:outline-none"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Alternative Questions / Paraphrases (one per line)</label>
                <textarea
                  value={faqFormData.alternative_questions}
                  onChange={(e) => setFaqFormData({ ...faqFormData, alternative_questions: e.target.value })}
                  placeholder="Where can I find the exam date sheet?&#10;How to check End Term exam schedule?"
                  rows={3}
                  className="w-full px-3 py-2 rounded-xl border border-warm-border focus:border-orange-400 focus:outline-none"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Verified Official Answer</label>
                <textarea
                  value={faqFormData.answer}
                  onChange={(e) => setFaqFormData({ ...faqFormData, answer: e.target.value })}
                  placeholder="Provide authoritative, step-by-step guidance..."
                  rows={4}
                  required
                  className="w-full px-3 py-2 rounded-xl border border-warm-border focus:border-orange-400 focus:outline-none leading-relaxed"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Keywords (comma-separated)</label>
                  <input
                    type="text"
                    value={faqFormData.keywords}
                    onChange={(e) => setFaqFormData({ ...faqFormData, keywords: e.target.value })}
                    placeholder="date sheet, UMS, Block 34"
                    className="w-full px-3 py-2 rounded-xl border border-warm-border focus:border-orange-400 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Content Owner</label>
                  <input
                    type="text"
                    value={faqFormData.content_owner}
                    onChange={(e) => setFaqFormData({ ...faqFormData, content_owner: e.target.value })}
                    placeholder="Division of Examination"
                    required
                    className="w-full px-3 py-2 rounded-xl border border-warm-border focus:border-orange-400 focus:outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Source Title</label>
                  <input
                    type="text"
                    value={faqFormData.source_title}
                    onChange={(e) => setFaqFormData({ ...faqFormData, source_title: e.target.value })}
                    placeholder="LPU Examination Guidelines"
                    required
                    className="w-full px-3 py-2 rounded-xl border border-warm-border focus:border-orange-400 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Source URL</label>
                  <input
                    type="url"
                    value={faqFormData.source_url}
                    onChange={(e) => setFaqFormData({ ...faqFormData, source_url: e.target.value })}
                    placeholder="https://ums.lpu.in"
                    required
                    className="w-full px-3 py-2 rounded-xl border border-warm-border focus:border-orange-400 focus:outline-none"
                  />
                </div>
              </div>

              <div className="flex items-center gap-2 pt-2">
                <input
                  type="checkbox"
                  id="approveCheckbox"
                  checked={faqFormData.is_approved}
                  onChange={(e) => setFaqFormData({ ...faqFormData, is_approved: e.target.checked })}
                  className="rounded text-orange-600 focus:ring-orange-500"
                />
                <label htmlFor="approveCheckbox" className="font-semibold text-slate-800">
                  Approve immediately for student search index
                </label>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setIsFaqModalOpen(false)}
                  className="px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-orange-600 hover:bg-orange-700 text-white font-semibold shadow-soft"
                >
                  {editingFaq ? 'Save Changes' : 'Create FAQ'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* UMS Service Edit Modal */}
      {isUmsModalOpen && editingUmsItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4 animate-fadeIn">
          <div className="bg-white rounded-3xl max-w-xl w-full p-6 shadow-2xl border border-warm-border max-h-[90vh] overflow-y-auto space-y-4">
            <div className="flex items-center justify-between border-b border-warm-border pb-3">
              <div>
                <h3 className="text-base font-bold text-slate-900">
                  Edit UMS Service: {editingUmsItem.catalog_id}
                </h3>
                <p className="text-xs text-slate-500">Module: {editingUmsItem.module}</p>
              </div>
              <button
                onClick={() => setIsUmsModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100"
              >
                <XCircle className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSaveUmsItem} className="space-y-3.5 text-xs">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Service Label (Menu Name)</label>
                <input
                  type="text"
                  value={umsFormData.service_label}
                  onChange={(e) => setUmsFormData({ ...umsFormData, service_label: e.target.value })}
                  required
                  className="w-full px-3 py-2 rounded-xl border border-warm-border focus:border-orange-400 focus:outline-none font-medium"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">
                  Navigation Breadcrumb Path (e.g. UMS &gt; Module &gt; Submenu)
                </label>
                <input
                  type="text"
                  value={umsFormData.navigation_path}
                  onChange={(e) => setUmsFormData({ ...umsFormData, navigation_path: e.target.value })}
                  required
                  className="w-full px-3 py-2 rounded-xl border border-warm-border focus:border-orange-400 focus:outline-none font-mono text-[11px]"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Verification Status</label>
                  <select
                    value={umsFormData.verification_status}
                    onChange={(e) => setUmsFormData({ ...umsFormData, verification_status: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-warm-border focus:border-orange-400 focus:outline-none"
                  >
                    <option value="menu_label_observed_procedure_not_verified">
                      Menu Observed (Default)
                    </option>
                    <option value="verified">Verified Official Procedure</option>
                    <option value="requires_review">Requires Review</option>
                  </select>
                </div>

                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Deep Link Status</label>
                  <select
                    value={umsFormData.deep_link_status}
                    onChange={(e) => setUmsFormData({ ...umsFormData, deep_link_status: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-warm-border focus:border-orange-400 focus:outline-none"
                  >
                    <option value="not_verified">Not Verified (Use Landing Page)</option>
                    <option value="entry_page_only">Entry Page Only</option>
                    <option value="verified">Verified Deep Link</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Authenticated Handoff URL</label>
                <input
                  type="url"
                  value={umsFormData.deep_link_url}
                  onChange={(e) => setUmsFormData({ ...umsFormData, deep_link_url: e.target.value })}
                  required
                  className="w-full px-3 py-2 rounded-xl border border-warm-border focus:border-orange-400 focus:outline-none font-mono text-[11px]"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">
                  Search Keywords &amp; Synonyms (comma-separated)
                </label>
                <input
                  type="text"
                  value={umsFormData.keywords}
                  onChange={(e) => setUmsFormData({ ...umsFormData, keywords: e.target.value })}
                  placeholder="reappear, exam form, arrear"
                  className="w-full px-3 py-2 rounded-xl border border-warm-border focus:border-orange-400 focus:outline-none"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Administrative Notes / Caveats</label>
                <textarea
                  value={umsFormData.notes}
                  onChange={(e) => setUmsFormData({ ...umsFormData, notes: e.target.value })}
                  placeholder="Additional context or prerequisites..."
                  rows={2}
                  className="w-full px-3 py-2 rounded-xl border border-warm-border focus:border-orange-400 focus:outline-none"
                />
              </div>

              <div className="flex items-center gap-2 pt-1">
                <input
                  type="checkbox"
                  id="umsActiveCheck"
                  checked={umsFormData.is_active}
                  onChange={(e) => setUmsFormData({ ...umsFormData, is_active: e.target.checked })}
                  className="rounded text-orange-600 focus:ring-orange-500"
                />
                <label htmlFor="umsActiveCheck" className="font-semibold text-slate-800">
                  Active in Student Search &amp; Navigation
                </label>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setIsUmsModalOpen(false)}
                  className="px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-orange-600 hover:bg-orange-700 text-white font-semibold shadow-soft"
                >
                  Save UMS Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

