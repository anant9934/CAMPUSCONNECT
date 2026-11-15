export interface ThinkingStep {
  step: number;
  title: string;
  description: string;
  status: 'pending' | 'running' | 'completed';
}

export interface Citation {
  title: string;
  url: string;
  source_type: string;
  verified: boolean;
  snippet?: string;
  content_owner?: string;
}

export interface ChatMessage {
  id: string;
  conversation_id?: string;
  role: 'user' | 'assistant';
  content: string;
  action_type?: string;
  thinking_steps?: ThinkingStep[];
  citations?: Citation[];
  follow_ups?: string[];
  navigation_card?: NavigationCard;
  booking_card?: BookingCard;
  procedure_checklist?: ProcedureChecklist;
  rms_card?: RMSCard;
  personal_record_card?: PersonalRecordCard;
  campus_place_card?: CampusPlaceCard;
  food_outlet_card?: FoodOutletCard;
  person_card?: PersonCard;
  who_to_meet_card?: WhoToMeetCard;
  academic_benefit_card?: AcademicBenefitAssessmentCard;
  evidence_card?: EvidenceCard;
  confidence_score?: number;
  latency_ms?: number;
  is_ai_generated?: boolean;
  created_at?: string;
}

export interface NavigationCard {
  service_title: string;
  module: string;
  breadcrumb: string;
  instruction: string;
  handoff_url: string;
  button_label: string;
}

export interface BookingCard {
  booking_type: string;
  service_title: string;
  breadcrumb: string;
  prerequisites: string[];
  availability_caveat: string;
  handoff_url: string;
  button_label: string;
}

export interface ProcedureChecklist {
  procedure_name: string;
  steps: string[];
  required_documents: string[];
  deadline_or_fees?: string;
  breadcrumb?: string;
  handoff_url: string;
}

export interface RMSCard {
  title: string;
  submission_path: string;
  tracking_path: string;
  stages: string[];
  privacy_notice: string;
  handoff_url: string;
}

export type EvidenceClassification =
  | 'OFFICIAL_CURRENT_VERIFIED'
  | 'OFFICIAL_HISTORICAL'
  | 'ADMIN_CONFIRMED'
  | 'VENDOR_CONFIRMED'
  | 'USER_REPORTED'
  | 'UNVERIFIED'
  | 'CONFLICTING'
  | 'EXPIRED';

export interface PersonalRecordCard {
  record_type: string;
  title: string;
  breadcrumb: string;
  boundary_explanation: string;
  handoff_url: string;
}

export interface CampusPlaceCard {
  place_id: string;
  name: string;
  building: string;
  floor_room?: string;
  opening_hours?: string;
  accessibility?: string;
  description: string;
  services: string[];
  map_url: string;
  building_purpose?: string;
  actual_office_service?: string;
  room_verification_status?: 'VERIFIED_ROOM' | 'UNVERIFIED_ROOM_HISTORICAL' | 'NOT_APPLICABLE_WHOLE_BLOCK';
  coordinates_verification_status?: 'VERIFIED_MAP_PIN' | 'CAMPUS_CENTROID_ESTIMATE';
  evidence_status?: EvidenceClassification;
}

export interface FoodOutletAlternative {
  outlet_id: string;
  display_name: string;
  location: string;
  specialty: string;
  opening_hours: string;
}

export interface FoodOutletCard {
  outlet_id: string;
  display_name: string;
  outlet_type: string;
  zone: string;
  location_description: string;
  distance_meters?: number;
  walking_minutes?: number;
  estimated_straight_line_distance_meters?: number;
  distance_type?: string;
  open_status: string;
  opening_hours: string;
  matched_items: string[];
  price_sample?: string;
  evidence_type: string;
  evidence_status?: EvidenceClassification;
  verification_notice?: string;
  is_vegetarian: boolean;
  alternatives: FoodOutletAlternative[];
  query_match_status: 'exact' | 'unmatched_alternative' | 'dietary_fallback';
}

export interface PersonCard {
  person_id: string;
  full_name: string;
  designation: string;
  school_division: string;
  building_block: string;
  room_cabin: string;
  email?: string;
  profile_source: string;
  verification_date: string;
  notes?: string;
  revalidation_advisory?: string;
  role_category?: string;
  school_hod?: string;
  department_hod?: string;
  executive_dean?: string;
  senior_dean?: string;
  associate_dean?: string;
  academic_coordinator?: string;
  programme_coordinator?: string;
  course_instructor?: string;
  faculty_mentor?: string;
  office_location?: string;
  office_seating_verified?: boolean;
  verification_timestamp?: string;
  evidence_status?: EvidenceClassification;
}

export interface WhoToMeetCard {
  issue_key: string;
  category_title: string;
  primary_contact_role: string;
  named_contact_person?: string;
  office_location: string;
  room_details: string;
  ums_navigation_path: string;
  prerequisite_action: string;
  required_documents: string[];
  escalation_ladder: string[];
  revalidation_notice?: string;
  evidence_status?: EvidenceClassification;
}

export interface AcademicBenefitAssessmentCard {
  category_id: string;
  category_name: string;
  portal_stage_name?: string;
  matched_criteria: string;
  eligible_academic_benefits: string;
  missing_evidence?: string[];
  evidence_checklist: string[];
  technical_originality_check?: string;
  limitations_and_caveats: string[];
  course_mapping_window?: string;
  approval_prerequisite?: string;
  submission_route: string;
  physical_helpdesk: string;
  guarantee_disclaimer: string;
  scrgm_distinction: string;
  eligibility_vs_approval_notice?: string;
  evidence_status?: EvidenceClassification;
}

export interface EvidenceCard {
  source_title: string;
  source_type: string;
  document_name?: string;
  clause_or_page?: string;
  verification_date: string;
  is_official: boolean;
  evidence_status?: EvidenceClassification;
  revalidation_advisory?: string;
}

export interface UMSServiceItem {
  id: string;
  catalog_id: string;
  module: string;
  service_label: string;
  action_type: string;
  public_chatbot_support: string;
  execution_boundary: string;
  ums_authentication: string;
  navigation_path: string;
  deep_link_status: string;
  deep_link_url: string;
  source_evidence: string;
  verification_status: string;
  notes?: string;
  keywords: string[];
  is_active: boolean;
}

export interface ActionWorkflowItem {
  id: string;
  action_id: string;
  user_intent: string;
  action_mode: string;
  target_system: string;
  ums_navigation_path: string;
  chatbot_flow: string;
  evidence: string;
  execution_guardrail: string;
  prerequisites: string[];
  steps: string[];
  handoff_url: string;
  is_active: boolean;
}

export interface CampusPlaceItem {
  id: string;
  place_id: string;
  name: string;
  category: string;
  building: string;
  floor_room?: string;
  latitude?: number;
  longitude?: number;
  opening_hours?: string;
  accessibility?: string;
  description: string;
  services_available: string[];
  official_map_url: string;
  verified_at?: string;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  description?: string;
  icon: string;
  display_order: number;
  is_active: boolean;
}

export interface AgentPublicInfo {
  id: string;
  name: string;
  role: string;
  description: string;
  capabilities: string[];
  is_orchestrator: boolean;
  permission_required: string;
}

export interface AgentEngineInfo {
  agent_id: string;
  agent_name: string;
  actual_provider: string;
  actual_model_id: string;
  availability: boolean;
  last_health_check: string;
  execution_mode: string;
  cost_tier: string;
}

export interface ConversationSummary {
  id: string;
  title: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface AdminUser {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  role: string;
}

export interface DashboardMetrics {
  total_approved_faqs: number;
  pending_faqs: number;
  total_documents: number;
  pending_documents: number;
  total_knowledge_records?: number;
  sensitive_records_count?: number;
  records_by_type?: Record<string, number>;
  total_queries: number;
  low_confidence_queries: number;
  unanswered_queries: number;
  gemini_failures: number;
  feedback_helpful_count: number;
  feedback_unhelpful_count: number;
  satisfaction_rate_percent: number;
}

export interface KnowledgeRecord {
  id: string;
  record_id: string;
  record_type: string;
  title: string;
  content: string;
  category_id?: string;
  category_name?: string;
  original_source_url: string;
  source_document?: string;
  source_page?: string;
  clause_reference?: string;
  publication_date?: string;
  last_verified_date: string;
  effective_date?: string;
  review_expiry_date?: string;
  approval_status: 'approved' | 'pending_review' | 'rejected' | 'expired';
  is_approved: boolean;
  is_sensitive: boolean;
  requires_admin_review: boolean;
  version: number;
  content_hash: string;
  searchable_variants: string[];
  type_metadata: Record<string, any>;
  audit_trail: any[];
  created_at: string;
  updated_at: string;
}

export interface FAQ {
  id: string;
  category_id: string;
  category_name?: string;
  canonical_question: string;
  alternative_questions: string[];
  answer: string;
  keywords: string[];
  source_url: string;
  source_title: string;
  source_type: string;
  content_owner: string;
  approval_status: 'approved' | 'pending' | 'rejected';
  is_approved: boolean;
  version: number;
  last_reviewed: string;
  created_at: string;
  updated_at: string;
}

export interface DocumentItem {
  id: string;
  category_id?: string;
  category_name?: string;
  title: string;
  filename: string;
  file_size: number;
  mime_type: string;
  status: string;
  is_approved: boolean;
  total_chunks: number;
  created_at: string;
  updated_at: string;
}

export interface DocumentChunk {
  id: string;
  chunk_index: number;
  content: string;
  page_number?: number;
  token_count: number;
}

export interface QueryLog {
  id: string;
  query_text: string;
  normalized_query: string;
  confidence_score: number;
  retrieval_strategy: string;
  gemini_status: string;
  latency_ms: number;
  created_at: string;
}

