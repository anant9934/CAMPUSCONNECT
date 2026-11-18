import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Square,
  Sparkles,
  Paperclip,
  FileText,
  Image as ImageIcon,
  X,
  Plus,
  Mic,
  MicOff,
  ChevronDown,
  ChevronUp,
  Zap,
  Scale,
  Brain,
  Search,
  Globe,
  MapPin,
  Check,
  AudioWaveform,
  Shield,
  Compass,
  Code2,
  Eye,
  SlidersHorizontal,
} from 'lucide-react';
import { api } from '../services/api';

interface SpecialistOption {
  id: string;
  name: string;
  badge: string;
  subtitle: string;
  description: string;
  icon: React.ReactNode;
  supportedThinking: ('Low' | 'Balanced' | 'High')[];
  defaultThinking: 'Low' | 'Balanced' | 'High';
}

const SPECIALIST_INTELLIGENCES: SpecialistOption[] = [
  {
    id: 'auto',
    name: 'Auto',
    badge: 'Router',
    subtitle: 'Dynamic Intelligence',
    description: 'Autonomous orchestration; automatically selects and routes to the best intelligence.',
    icon: <Sparkles className="w-4 h-4 text-orange-600" />,
    supportedThinking: ['Low', 'Balanced', 'High'],
    defaultThinking: 'Balanced',
  },
  {
    id: 'nova',
    name: 'NOVA',
    badge: 'Everyday',
    subtitle: 'Everyday Intelligence',
    description: 'General student conversation, Hindi/Hinglish, FAQs, campus living, transit & hospital emergency.',
    icon: <Zap className="w-4 h-4 text-amber-500" />,
    supportedThinking: ['Low', 'Balanced'],
    defaultThinking: 'Low',
  },
  {
    id: 'themis',
    name: 'THEMIS',
    badge: 'University',
    subtitle: 'University Intelligence',
    description: 'LPU academic policies, attendance condonation (65% floor / 75% rule), EDU-Revolution & UMS pathways.',
    icon: <Shield className="w-4 h-4 text-orange-600" />,
    supportedThinking: ['Low', 'Balanced', 'High'],
    defaultThinking: 'Balanced',
  },
  {
    id: 'athena',
    name: 'ATHENA',
    badge: 'Advanced',
    subtitle: 'Advanced Intelligence',
    description: 'Complex technical reasoning, computer science, mathematics, programming, debugging & architecture.',
    icon: <Brain className="w-4 h-4 text-indigo-600" />,
    supportedThinking: ['Balanced', 'High'],
    defaultThinking: 'High',
  },
  {
    id: 'oracle',
    name: 'ORACLE',
    badge: 'Research',
    subtitle: 'Research Intelligence',
    description: 'Primary source discovery, web research, research papers, SIH hackathons & citation verification.',
    icon: <Search className="w-4 h-4 text-emerald-600" />,
    supportedThinking: ['Balanced', 'High'],
    defaultThinking: 'High',
  },
];

interface ThinkingOption {
  id: 'Low' | 'Balanced' | 'High';
  label: string;
  badge: string;
  description: string;
  icon: React.ReactNode;
}

const ALL_THINKING_LEVELS: ThinkingOption[] = [
  {
    id: 'Low',
    label: 'Low',
    badge: 'Fast',
    description: 'Lower reasoning budget, minimal model calls, fast execution.',
    icon: <Zap className="w-3.5 h-3.5 text-amber-500" />,
  },
  {
    id: 'Balanced',
    label: 'Balanced',
    badge: 'Standard',
    description: 'Moderate reasoning, relevant retrieval, selective delegation.',
    icon: <Scale className="w-3.5 h-3.5 text-blue-500" />,
  },
  {
    id: 'High',
    label: 'High',
    badge: 'Thorough',
    description: 'Increased reasoning effort, extensive retrieval, multi-agent verification.',
    icon: <Brain className="w-3.5 h-3.5 text-purple-500" />,
  },
];

interface MessageComposerProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  onStopStreaming?: () => void;
  selectedCategorySlug?: string;
  onClearCategory?: () => void;
  selectedLandmark?: string;
  onSelectLandmark?: (landmark: string) => void;
  selectedModel?: string;
  onSelectModel?: (model: string) => void;
  thinkingLevel?: string;
  onSelectThinkingLevel?: (level: string) => void;
  reasoningMode?: string;
  onSelectReasoningMode?: (mode: string) => void;
  webResearchEnabled?: boolean;
  onToggleWebResearch?: (enabled: boolean) => void;
}

export const MessageComposer: React.FC<MessageComposerProps> = ({
  onSendMessage,
  isLoading,
  onStopStreaming,
  selectedCategorySlug,
  onClearCategory,
  selectedLandmark = 'Block 32',
  onSelectLandmark,
  selectedModel = 'aegis',
  onSelectModel,
  thinkingLevel = 'Medium',
  onSelectThinkingLevel,
  reasoningMode = 'DeepThink',
  onSelectReasoningMode,
  webResearchEnabled = false,
  onToggleWebResearch,
}) => {
  const [input, setInput] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedDocName, setUploadedDocName] = useState<string | null>(null);
  const [isListening, setIsListening] = useState(false);

  // Dropdown states
  const [isAgentDropdownOpen, setIsAgentDropdownOpen] = useState(false);
  const [isThinkingDropdownOpen, setIsThinkingDropdownOpen] = useState(false);
  const [isPlusMenuOpen, setIsPlusMenuOpen] = useState(false);

  // Tool states
  const [deepSearchEnabled, setDeepSearchEnabled] = useState(true);
  const [localWebResearch, setLocalWebResearch] = useState(webResearchEnabled);

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);
  const composerContainerRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);

  // Current active specialist
  const activeSpecialist =
    SPECIALIST_INTELLIGENCES.find((s) => s.id === selectedModel) || SPECIALIST_INTELLIGENCES[0];

  // Filter supported thinking levels for the active specialist
  const availableThinkingOptions = ALL_THINKING_LEVELS.filter((lvl) =>
    activeSpecialist.supportedThinking.includes(lvl.id)
  );

  // Current active thinking option (auto-normalize if unsupported)
  const normalizedThinkingLevel: 'Low' | 'Balanced' | 'High' = (
    availableThinkingOptions.some((lvl) => lvl.id.toLowerCase() === thinkingLevel.toLowerCase())
      ? (thinkingLevel.charAt(0).toUpperCase() + thinkingLevel.slice(1).toLowerCase()) as 'Low' | 'Balanced' | 'High'
      : activeSpecialist.defaultThinking
  );

  const activeThinkingOption =
    availableThinkingOptions.find((lvl) => lvl.id === normalizedThinkingLevel) ||
    availableThinkingOptions[0];

  // Auto-grow textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [input]);

  // Sync external web research prop
  useEffect(() => {
    setLocalWebResearch(webResearchEnabled);
  }, [webResearchEnabled]);

  // Close menus on outside click or Escape
  useEffect(() => {
    const handleKeyDownGlobal = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsAgentDropdownOpen(false);
        setIsThinkingDropdownOpen(false);
        setIsPlusMenuOpen(false);
      }
    };

    const handleClickOutside = (e: MouseEvent) => {
      if (
        composerContainerRef.current &&
        !composerContainerRef.current.contains(e.target as Node)
      ) {
        setIsAgentDropdownOpen(false);
        setIsThinkingDropdownOpen(false);
        setIsPlusMenuOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDownGlobal);
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      window.removeEventListener('keydown', handleKeyDownGlobal);
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Web Speech API initialization
  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-IN';

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        if (transcript) {
          setInput((prev) => (prev ? `${prev} ${transcript}` : transcript));
        }
        setIsListening(false);
      };

      recognition.onerror = () => {
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    }
  }, []);

  const toggleSpeechRecognition = () => {
    if (!recognitionRef.current) {
      alert('Speech recognition is not supported in this browser.');
      return;
    }
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      try {
        recognitionRef.current.start();
        setIsListening(true);
      } catch (err) {
        console.error('Failed to start speech recognition:', err);
      }
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>, isImage = false) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setIsUploading(true);
      const res = await api.uploadDocument(file);
      setUploadedDocName(res.filename);
      const docPrompt = `[Uploaded ${isImage ? 'Screenshot/Image' : 'Document'}: ${res.filename} (${res.characters_extracted} characters extracted)]\nDocument Excerpt:\n"${res.summary_preview}"\n\nPlease analyze this against official LPU academic guidelines & UMS workflows.`;
      setInput((prev) => (prev ? `${prev}\n\n${docPrompt}` : docPrompt));
      setIsPlusMenuOpen(false);
    } catch (err: any) {
      alert(`Upload error: ${err.message || 'Failed to upload file'}`);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
      if (imageInputRef.current) imageInputRef.current.value = '';
    }
  };

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isLoading) return;

    let finalPrompt = input.trim();
    if (localWebResearch) {
      finalPrompt = `[Live Web Research Requested] ${finalPrompt}`;
    }

    onSendMessage(finalPrompt);
    setInput('');
    setUploadedDocName(null);
    setIsPlusMenuOpen(false);
    setIsAgentDropdownOpen(false);
    setIsThinkingDropdownOpen(false);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSelectSpecialist = (specialist: SpecialistOption) => {
    if (onSelectModel) {
      onSelectModel(specialist.id);
    }
    // Auto-adjust thinking level if current is unsupported
    if (!specialist.supportedThinking.includes(normalizedThinkingLevel)) {
      if (onSelectThinkingLevel) {
        onSelectThinkingLevel(specialist.defaultThinking);
      }
    }
    setIsAgentDropdownOpen(false);
  };

  const handleSelectThinking = (lvl: 'Low' | 'Balanced' | 'High') => {
    if (onSelectThinkingLevel) {
      onSelectThinkingLevel(lvl);
    }
    if (onSelectReasoningMode) {
      onSelectReasoningMode(lvl === 'Low' ? 'Quick answer' : lvl === 'High' ? 'DeepThink' : 'Balanced');
    }
    setIsThinkingDropdownOpen(false);
  };

  return (
    <div ref={composerContainerRef} className="w-full max-w-3xl mx-auto px-4 pb-4 relative z-20">
      {/* Uploaded File Chip */}
      {uploadedDocName && (
        <div className="mb-2 flex items-center justify-between px-3 py-1.5 bg-orange-50 border border-orange-200/80 rounded-xl text-xs text-orange-900 shadow-xs animate-fadeIn">
          <div className="flex items-center gap-2 truncate">
            <FileText className="w-4 h-4 text-orange-600 shrink-0" />
            <span className="font-semibold truncate">Attached: {uploadedDocName}</span>
          </div>
          <button
            onClick={() => setUploadedDocName(null)}
            className="text-orange-500 hover:text-orange-800 p-0.5 rounded transition-colors"
            title="Remove attachment"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Active Category Filter Tag if selected */}
      {selectedCategorySlug && (
        <div className="mb-2 flex items-center justify-between px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-700 shadow-xs">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-500">Domain:</span>
            <span className="uppercase text-[11px] font-mono tracking-wider bg-white text-orange-700 px-2 py-0.5 rounded border border-orange-200 font-semibold">
              {selectedCategorySlug}
            </span>
          </div>
          {onClearCategory && (
            <button
              onClick={onClearCategory}
              className="text-slate-500 hover:text-slate-800 font-medium text-xs underline transition-colors"
            >
              Clear filter
            </button>
          )}
        </div>
      )}

      {/* Clean Light-Theme Composer Capsule */}
      <div className="relative rounded-2xl bg-white border border-slate-200/90 shadow-[0_8px_30px_rgb(0,0,0,0.06)] transition-all duration-200 focus-within:border-orange-500/50 focus-within:ring-2 focus-within:ring-orange-500/10">
        {/* Top Textarea: "Ask anything..." */}
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={`Ask ${activeSpecialist.name} anything about LPU academics, policies, or campus...`}
          rows={1}
          disabled={isLoading}
          className="w-full resize-none bg-transparent px-4 pt-3.5 pb-2 text-[15px] sm:text-base text-slate-800 placeholder-slate-400 focus:outline-none max-h-48 leading-relaxed font-sans"
        />

        {/* Bottom Toolbar Row */}
        <div className="flex items-center justify-between pt-1 pb-2.5 px-3 gap-2 flex-wrap sm:flex-nowrap border-t border-slate-100/80">
          {/* Left Controls: [+] [Intelligence Selector] [Thinking Level] */}
          <div className="flex items-center gap-1.5 sm:gap-2 flex-wrap">
            {/* Plus (+) Button & Popover */}
            <div className="relative">
              <button
                type="button"
                onClick={() => {
                  setIsPlusMenuOpen((prev) => !prev);
                  setIsAgentDropdownOpen(false);
                  setIsThinkingDropdownOpen(false);
                }}
                className={`w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center transition-all border ${
                  isPlusMenuOpen
                    ? 'bg-orange-50 border-orange-300 text-orange-600 rotate-45'
                    : 'bg-slate-50 hover:bg-slate-100 border-slate-200 text-slate-600 hover:text-slate-900'
                }`}
                title="Attach files or context tools"
              >
                <Plus className="w-4 h-4 transition-transform duration-200" />
              </button>

              {/* Plus Menu Popover */}
              {isPlusMenuOpen && (
                <div className="absolute left-0 bottom-11 w-72 rounded-2xl bg-white border border-slate-200 shadow-xl p-2 z-50 text-xs space-y-1 animate-fadeIn">
                  <div className="px-2.5 py-1 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                    Context & Attachments
                  </div>

                  <button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isUploading}
                    className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-xl text-slate-700 hover:bg-orange-50/60 hover:text-orange-900 transition-colors text-left"
                  >
                    <div className="w-7 h-7 rounded-lg bg-orange-100 text-orange-600 flex items-center justify-center shrink-0">
                      <Paperclip className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="font-semibold text-xs text-slate-800">Attach Document</div>
                      <div className="text-[10px] text-slate-500">PDF, TXT, Syllabus, Report</div>
                    </div>
                  </button>

                  <button
                    onClick={() => imageInputRef.current?.click()}
                    disabled={isUploading}
                    className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-xl text-slate-700 hover:bg-violet-50/60 hover:text-violet-900 transition-colors text-left"
                  >
                    <div className="w-7 h-7 rounded-lg bg-violet-100 text-violet-600 flex items-center justify-center shrink-0">
                      <ImageIcon className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="font-semibold text-xs text-slate-800">Attach Image / Screenshot</div>
                      <div className="text-[10px] text-slate-500">UMS error, timetable, gradecard</div>
                    </div>
                  </button>

                  <div className="h-px bg-slate-100 my-1" />

                  {/* University KB Deep Search Toggle */}
                  <button
                    onClick={() => setDeepSearchEnabled((prev) => !prev)}
                    className="w-full flex items-center justify-between px-2.5 py-2 rounded-xl text-slate-700 hover:bg-slate-50 transition-colors text-left"
                  >
                    <div className="flex items-center gap-2.5">
                      <div className="w-7 h-7 rounded-lg bg-blue-100 text-blue-600 flex items-center justify-center shrink-0">
                        <Search className="w-3.5 h-3.5" />
                      </div>
                      <div>
                        <div className="font-semibold text-xs text-slate-800">LPU Knowledge Search</div>
                        <div className="text-[10px] text-slate-500">384-d BGE hybrid retrieval</div>
                      </div>
                    </div>
                    <div
                      className={`w-8 h-4 rounded-full transition-colors p-0.5 ${
                        deepSearchEnabled ? 'bg-orange-600' : 'bg-slate-200'
                      }`}
                    >
                      <div
                        className={`w-3 h-3 rounded-full bg-white transition-transform ${
                          deepSearchEnabled ? 'translate-x-4' : 'translate-x-0'
                        }`}
                      />
                    </div>
                  </button>

                  {/* Live Web Research Toggle */}
                  <button
                    onClick={() => {
                      const next = !localWebResearch;
                      setLocalWebResearch(next);
                      if (onToggleWebResearch) onToggleWebResearch(next);
                    }}
                    className="w-full flex items-center justify-between px-2.5 py-2 rounded-xl text-slate-700 hover:bg-slate-50 transition-colors text-left"
                  >
                    <div className="flex items-center gap-2.5">
                      <div className="w-7 h-7 rounded-lg bg-emerald-100 text-emerald-600 flex items-center justify-center shrink-0">
                        <Globe className="w-3.5 h-3.5" />
                      </div>
                      <div>
                        <div className="font-semibold text-xs text-slate-800">Live Web Research</div>
                        <div className="text-[10px] text-slate-500">Tavily web discovery & external news</div>
                      </div>
                    </div>
                    <div
                      className={`w-8 h-4 rounded-full transition-colors p-0.5 ${
                        localWebResearch ? 'bg-emerald-600' : 'bg-slate-200'
                      }`}
                    >
                      <div
                        className={`w-3 h-3 rounded-full bg-white transition-transform ${
                          localWebResearch ? 'translate-x-4' : 'translate-x-0'
                        }`}
                      />
                    </div>
                  </button>

                  {/* Landmark selector option */}
                  {onSelectLandmark && (
                    <div className="pt-1 border-t border-slate-100 px-2.5 py-1.5">
                      <div className="text-[10px] text-slate-500 mb-1 flex items-center gap-1 font-semibold">
                        <MapPin className="w-3 h-3 text-orange-600" />
                        <span>Current Campus Landmark:</span>
                      </div>
                      <select
                        value={selectedLandmark}
                        onChange={(e) => onSelectLandmark(e.target.value)}
                        className="w-full bg-slate-50 text-slate-700 text-xs rounded-lg px-2 py-1.5 border border-slate-200 focus:outline-none cursor-pointer"
                      >
                        <option value="Block 32">Block 32 (CSE / Tech Hub)</option>
                        <option value="Uni-Centre">Uni-Centre Food Court</option>
                        <option value="Block 34">Block 34 (Exam Cell & Admin)</option>
                        <option value="Block 27">Block 27 (EDU-Rev & Dean Office)</option>
                        <option value="Block 13">Block 13 (DSA / Student Welfare)</option>
                        <option value="Block 30">Block 30 (UniHospital & Medical)</option>
                        <option value="Uni-Mall">Uni-Mall (Student Services)</option>
                        <option value="BH-4">BH-4 Hostels</option>
                      </select>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Hidden file inputs */}
            <input
              type="file"
              ref={fileInputRef}
              onChange={(e) => handleFileUpload(e, false)}
              accept=".pdf,.txt,.md,.csv,.doc,.docx"
              className="hidden"
            />
            <input
              type="file"
              ref={imageInputRef}
              onChange={(e) => handleFileUpload(e, true)}
              accept=".png,.jpg,.jpeg,.webp"
              className="hidden"
            />

            {/* Intelligence Selector (8 Named Specialists) */}
            <div className="relative">
              <button
                type="button"
                onClick={() => {
                  setIsAgentDropdownOpen((prev) => !prev);
                  setIsThinkingDropdownOpen(false);
                  setIsPlusMenuOpen(false);
                }}
                className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-50 hover:bg-slate-100/90 text-slate-700 hover:text-slate-900 text-xs font-semibold transition-all border border-slate-200 shadow-2xs"
                title="Select Specialist Intelligence"
              >
                {activeSpecialist.icon}
                <span>{activeSpecialist.name}</span>
                <span className="text-[10px] font-normal text-slate-400">· {activeSpecialist.badge}</span>
                <ChevronDown className="w-3 h-3 text-slate-400" />
              </button>

              {/* Intelligence Dropdown Menu */}
              {isAgentDropdownOpen && (
                <div className="absolute left-0 bottom-11 w-80 max-h-96 overflow-y-auto rounded-2xl bg-white border border-slate-200 shadow-2xl p-1.5 z-50 text-xs space-y-0.5 animate-fadeIn">
                  <div className="px-3 py-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider border-b border-slate-100 flex items-center justify-between">
                    <span>Specialist Intelligence</span>
                    <span className="text-[9px] text-orange-600 font-mono">8 Specialists</span>
                  </div>

                  {SPECIALIST_INTELLIGENCES.map((specialist) => {
                    const isSelected = specialist.id === selectedModel;
                    return (
                      <button
                        key={specialist.id}
                        onClick={() => handleSelectSpecialist(specialist)}
                        className={`w-full text-left px-3 py-2 rounded-xl flex items-start gap-2.5 transition-colors ${
                          isSelected
                            ? 'bg-orange-50/70 text-orange-950 font-medium'
                            : 'text-slate-700 hover:bg-slate-50'
                        }`}
                      >
                        <div className="mt-0.5 shrink-0">{specialist.icon}</div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <span className="font-semibold text-xs text-slate-900">
                              {specialist.name} — {specialist.subtitle}
                            </span>
                            {isSelected && (
                              <Check className="w-3.5 h-3.5 text-orange-600 shrink-0" />
                            )}
                          </div>
                          <div className="text-[11px] text-slate-500 leading-snug mt-0.5 line-clamp-2">
                            {specialist.description}
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Thinking Level Selector (Dynamically Filtered per Model) */}
            <div className="relative">
              <button
                type="button"
                onClick={() => {
                  setIsThinkingDropdownOpen((prev) => !prev);
                  setIsAgentDropdownOpen(false);
                  setIsPlusMenuOpen(false);
                }}
                className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-50 hover:bg-slate-100/90 text-slate-700 hover:text-slate-900 text-xs font-medium transition-all border border-slate-200 shadow-2xs"
                title="Adjust reasoning & thinking depth"
              >
                {activeThinkingOption.icon}
                <span>Thinking: {activeThinkingOption.label}</span>
                {isThinkingDropdownOpen ? (
                  <ChevronDown className="w-3 h-3 text-slate-400" />
                ) : (
                  <ChevronUp className="w-3 h-3 text-slate-400" />
                )}
              </button>

              {/* Thinking Level Dropdown */}
              {isThinkingDropdownOpen && (
                <div className="absolute left-0 bottom-11 w-64 rounded-2xl bg-white border border-slate-200 shadow-2xl p-1.5 z-50 text-xs space-y-0.5 animate-fadeIn">
                  <div className="px-3 py-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider border-b border-slate-100 flex items-center justify-between">
                    <span>Thinking Depth ({activeSpecialist.name})</span>
                    <span className="text-[9px] text-slate-400 font-mono">
                      {availableThinkingOptions.length} levels
                    </span>
                  </div>

                  {availableThinkingOptions.map((opt) => {
                    const isSelected = opt.id === activeThinkingOption.id;
                    return (
                      <button
                        key={opt.id}
                        onClick={() => handleSelectThinking(opt.id)}
                        className={`w-full text-left px-3 py-2 rounded-xl flex items-start gap-2.5 transition-colors ${
                          isSelected
                            ? 'bg-orange-50/70 text-orange-950 font-medium'
                            : 'text-slate-700 hover:bg-slate-50'
                        }`}
                      >
                        <div className="mt-0.5 shrink-0">{opt.icon}</div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <span className="font-semibold text-xs text-slate-900">
                              {opt.label} ({opt.badge})
                            </span>
                            {isSelected && (
                              <Check className="w-3.5 h-3.5 text-orange-600 shrink-0" />
                            )}
                          </div>
                          <div className="text-[10px] text-slate-500 leading-snug mt-0.5">
                            {opt.description}
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          {/* Right Controls: [Voice] and Send/Stop Button */}
          <div className="flex items-center gap-2 ml-auto">
            {/* Voice Pill Button */}
            <button
              type="button"
              onClick={toggleSpeechRecognition}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium transition-all border ${
                isListening
                  ? 'bg-rose-50 text-rose-700 border-rose-300 animate-pulse'
                  : 'bg-slate-50 hover:bg-slate-100 text-slate-600 hover:text-slate-900 border-slate-200'
              }`}
              title={isListening ? 'Stop dictation' : 'Voice input'}
            >
              {isListening ? (
                <>
                  <MicOff className="w-3.5 h-3.5 text-rose-600" />
                  <span className="font-semibold">Listening...</span>
                </>
              ) : (
                <>
                  <AudioWaveform className="w-3.5 h-3.5 text-slate-500" />
                  <span>Voice</span>
                </>
              )}
            </button>

            {/* Send / Stop Circular Button */}
            {isLoading ? (
              <button
                type="button"
                onClick={onStopStreaming}
                className="w-8 h-8 rounded-full bg-rose-600 hover:bg-rose-700 text-white flex items-center justify-center transition-all shadow-md shadow-rose-600/20 active:scale-95"
                title="Stop generation"
              >
                <Square className="w-3.5 h-3.5 fill-current" />
              </button>
            ) : (
              <button
                type="button"
                onClick={handleSubmit}
                disabled={!input.trim()}
                className={`w-8 h-8 rounded-full flex items-center justify-center transition-all ${
                  input.trim()
                    ? 'bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-700 hover:to-amber-700 text-white shadow-md shadow-orange-600/20 active:scale-95'
                    : 'bg-slate-100 text-slate-400 border border-slate-200 cursor-not-allowed'
                }`}
                title="Send query (Enter)"
              >
                <Send className="w-4 h-4 text-current -translate-x-[0.5px] translate-y-[0.5px]" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Subtle Footer Disclaimer */}
      <p className="mt-2 text-center text-[10px] text-slate-400">
        CampusConnect AI grounds responses in verified institutional regulations. Confirm academic deadlines and marks in official{' '}
        <a
          href="https://ums.lpu.in"
          target="_blank"
          rel="noreferrer"
          className="text-orange-600 hover:text-orange-700 underline font-medium"
        >
          LPU UMS
        </a>.
      </p>
    </div>
  );
};
