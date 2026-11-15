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
  Lightbulb,
  Search,
  Globe,
  MapPin,
  Check,
  AudioWaveform,
  Leaf,
  Layers,
} from 'lucide-react';
import { api } from '../services/api';

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
  reasoningMode?: string;
  onSelectReasoningMode?: (mode: string) => void;
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
  reasoningMode = 'DeepThink',
  onSelectReasoningMode,
}) => {
  const [input, setInput] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedDocName, setUploadedDocName] = useState<string | null>(null);
  const [isListening, setIsListening] = useState(false);
  const [isPlusMenuOpen, setIsPlusMenuOpen] = useState(false);
  const [isModeDropdownOpen, setIsModeDropdownOpen] = useState(false);
  const [isNormalDropdownOpen, setIsNormalDropdownOpen] = useState(false);
  const [deepSearchEnabled, setDeepSearchEnabled] = useState(true);
  const [webResearchEnabled, setWebResearchEnabled] = useState(false);
  const [activeTone, setActiveTone] = useState<'Normal' | 'Concise' | 'Academic' | 'Detailed'>('Normal');

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<any>(null);

  // Auto-grow textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [input]);

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

      recognition.onerror = (e: any) => {
        console.error('Speech recognition error:', e);
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
      alert('Speech recognition is not supported in your browser.');
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
    if (activeTone !== 'Normal') {
      finalPrompt = `[Tone: ${activeTone}] ${finalPrompt}`;
    }
    if (webResearchEnabled) {
      finalPrompt = `[Live Web Research Requested] ${finalPrompt}`;
    }

    onSendMessage(finalPrompt);
    setInput('');
    setUploadedDocName(null);
    setIsPlusMenuOpen(false);
    setIsModeDropdownOpen(false);
    setIsNormalDropdownOpen(false);
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

  // Exact 4 reasoning modes from reference UI
  const reasoningModes = [
    {
      id: 'Quick answer',
      label: 'Quick answer',
      icon: <Zap className="w-3.5 h-3.5 text-amber-400" />,
      desc: 'Instant concise factual retrieval',
    },
    {
      id: 'Balanced',
      label: 'Balanced',
      icon: <Scale className="w-3.5 h-3.5 text-blue-400" />,
      desc: 'Standard grounded response',
    },
    {
      id: 'DeepThink',
      label: 'DeepThink',
      icon: <Lightbulb className="w-3.5 h-3.5 text-purple-400" />,
      desc: 'Multi-step policy analysis & deduction',
    },
    {
      id: 'Research',
      label: 'Research',
      icon: <Search className="w-3.5 h-3.5 text-emerald-400" />,
      desc: 'Comprehensive evidence verification',
    },
  ];

  const agentOptions = [
    { id: 'aegis', label: 'AEGIS — Auto Intelligence', badge: 'Orchestrator', desc: 'Master orchestrator, dynamically coordinates specialists' },
    { id: 'themis', label: 'THEMIS — Policy & Benefits', badge: 'Policy', desc: 'Attendance condonation, EDU-Rev & eligibility' },
    { id: 'hermes', label: 'HERMES — UMS Navigator', badge: 'UMS', desc: '234 UMS pathways, RMS & procedures' },
    { id: 'argus', label: 'ARGUS — Campus & Faculty', badge: 'Campus', desc: 'Faculty cabins, hours & pure-veg dining' },
    { id: 'athena', label: 'ATHENA — Academic Reasoning', badge: 'Academic', desc: 'Course equivalence & credit substitution' },
    { id: 'mnemos', label: 'MNEMOS — Knowledge RAG', badge: 'Memory', desc: '1,035 institutional facts & memory' },
    { id: 'oracle', label: 'ORACLE — Web Research', badge: 'Research', desc: 'Tavily live search & SIH hackathons' },
    { id: 'forge', label: 'FORGE — Tech Projects', badge: 'Code', desc: 'Technical projects & startup internships' },
    { id: 'vision', label: 'VISION — Multimodal', badge: 'Vision', desc: 'Document, screenshot & syllabus perception' },
  ];

  const activeModeObj = reasoningModes.find((m) => m.id.toLowerCase() === reasoningMode.toLowerCase()) || reasoningModes[2];
  const activeAgentObj = agentOptions.find((a) => a.id === selectedModel) || agentOptions[0];

  return (
    <div className="w-full max-w-3xl mx-auto px-4 pb-4 relative z-20">
      {/* Uploaded File Chip */}
      {uploadedDocName && (
        <div className="mb-2 flex items-center justify-between px-3 py-1.5 bg-blue-950/80 border border-blue-500/30 rounded-xl text-xs text-blue-200 shadow-lg animate-fadeIn">
          <div className="flex items-center gap-2 truncate">
            <FileText className="w-4 h-4 text-blue-400 shrink-0" />
            <span className="font-semibold truncate">Attached: {uploadedDocName}</span>
          </div>
          <button
            onClick={() => setUploadedDocName(null)}
            className="text-blue-400 hover:text-blue-200 p-0.5 rounded"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Active Category Filter Tag if selected */}
      {selectedCategorySlug && (
        <div className="mb-2 flex items-center justify-between px-3 py-1.5 bg-orange-950/80 border border-orange-500/30 rounded-xl text-xs text-orange-200 shadow-lg">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-orange-300">Domain Filter:</span>
            <span className="uppercase text-[11px] font-mono tracking-wider bg-orange-900/60 text-orange-200 px-2 py-0.5 rounded border border-orange-500/30">
              {selectedCategorySlug}
            </span>
          </div>
          {onClearCategory && (
            <button
              onClick={onClearCategory}
              className="text-orange-300 hover:text-orange-100 font-medium text-xs underline"
            >
              Clear filter
            </button>
          )}
        </div>
      )}

      {/* Glowing Neon Capsule Container (Exact match with reference UI) */}
      <div className="relative group">
        {/* Ambient Two-Tone Neon Glow Halo */}
        <div
          className="absolute -inset-1 rounded-[2rem] opacity-75 blur-xl transition-opacity duration-500 pointer-events-none group-hover:opacity-100"
          style={{
            background:
              'radial-gradient(ellipse at 15% 30%, rgba(255, 107, 74, 0.35) 0%, transparent 60%), radial-gradient(ellipse at 85% 70%, rgba(59, 130, 246, 0.35) 0%, transparent 60%)',
          }}
        />

        {/* Inner Capsule Body */}
        <div className="relative rounded-[1.75rem] border border-white/10 bg-[#0f1117]/95 backdrop-blur-2xl text-slate-100 shadow-[0_12px_36px_-6px_rgba(0,0,0,0.6),0_0_24px_-4px_rgba(255,107,74,0.12),0_0_24px_-4px_rgba(59,130,246,0.12)] p-2.5 sm:p-3 transition-all focus-within:border-white/20">
          {/* Top Textarea: "Ask anything..." */}
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything..."
            rows={1}
            disabled={isLoading}
            className="w-full resize-none bg-transparent px-3 py-2 text-[15px] sm:text-base text-slate-100 placeholder-slate-400/80 focus:outline-none max-h-48 leading-relaxed font-sans"
          />

          {/* Bottom Toolbar Row */}
          <div className="flex items-center justify-between pt-1.5 px-1 mt-0.5 gap-2 flex-wrap sm:flex-nowrap">
            {/* Left Controls: [+] [Normal ⌄] [DeepThink ^] */}
            <div className="flex items-center gap-1.5 sm:gap-2 flex-wrap">
              {/* Plus (+) Button & Popover */}
              <div className="relative">
                <button
                  type="button"
                  onClick={() => {
                    setIsPlusMenuOpen((prev) => !prev);
                    setIsModeDropdownOpen(false);
                    setIsNormalDropdownOpen(false);
                  }}
                  className={`w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center transition-all border border-white/10 ${
                    isPlusMenuOpen
                      ? 'bg-white/15 text-white rotate-45'
                      : 'bg-white/5 hover:bg-white/10 text-slate-300 hover:text-white'
                  }`}
                  title="Attach files or toggles"
                >
                  <Plus className="w-4 h-4 transition-transform duration-200" />
                </button>

                {/* Plus Menu Popover */}
                {isPlusMenuOpen && (
                  <div className="absolute left-0 bottom-11 w-64 rounded-2xl bg-[#14151e]/98 backdrop-blur-2xl border border-white/10 shadow-2xl p-2 z-50 text-xs space-y-1 animate-fadeIn">
                    <div className="px-2.5 py-1 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                      Context & Tools
                    </div>

                    <button
                      onClick={() => fileInputRef.current?.click()}
                      disabled={isUploading}
                      className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-xl text-slate-200 hover:bg-white/10 transition-colors text-left"
                    >
                      <Paperclip className="w-4 h-4 text-orange-400" />
                      <div>
                        <div className="font-semibold text-xs">Attach Document</div>
                        <div className="text-[10px] text-slate-400">PDF, TXT, Syllabus, Report</div>
                      </div>
                    </button>

                    <button
                      onClick={() => imageInputRef.current?.click()}
                      disabled={isUploading}
                      className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-xl text-slate-200 hover:bg-white/10 transition-colors text-left"
                    >
                      <ImageIcon className="w-4 h-4 text-purple-400" />
                      <div>
                        <div className="font-semibold text-xs">Attach Image / Screenshot</div>
                        <div className="text-[10px] text-slate-400">UMS error, timetable, gradecard</div>
                      </div>
                    </button>

                    <div className="h-px bg-white/10 my-1" />

                    {/* University KB Deep Search Toggle */}
                    <button
                      onClick={() => setDeepSearchEnabled((prev) => !prev)}
                      className="w-full flex items-center justify-between px-2.5 py-2 rounded-xl text-slate-200 hover:bg-white/10 transition-colors text-left"
                    >
                      <div className="flex items-center gap-2">
                        <Search className="w-3.5 h-3.5 text-blue-400" />
                        <div>
                          <div className="font-semibold text-xs">LPU Deep KB Search</div>
                          <div className="text-[10px] text-slate-400">384-d BGE-small embeddings</div>
                        </div>
                      </div>
                      <div
                        className={`w-8 h-4 rounded-full transition-colors p-0.5 ${
                          deepSearchEnabled ? 'bg-orange-600' : 'bg-white/10'
                        }`}
                      >
                        <div
                          className={`w-3 h-3 rounded-full bg-white transition-transform ${
                            deepSearchEnabled ? 'translate-x-4' : 'translate-x-0'
                          }`}
                        />
                      </div>
                    </button>

                    {/* Web Research Toggle */}
                    <button
                      onClick={() => setWebResearchEnabled((prev) => !prev)}
                      className="w-full flex items-center justify-between px-2.5 py-2 rounded-xl text-slate-200 hover:bg-white/10 transition-colors text-left"
                    >
                      <div className="flex items-center gap-2">
                        <Globe className="w-3.5 h-3.5 text-emerald-400" />
                        <div>
                          <div className="font-semibold text-xs">Live Web Research</div>
                          <div className="text-[10px] text-slate-400">Tavily web discovery</div>
                        </div>
                      </div>
                      <div
                        className={`w-8 h-4 rounded-full transition-colors p-0.5 ${
                          webResearchEnabled ? 'bg-emerald-600' : 'bg-white/10'
                        }`}
                      >
                        <div
                          className={`w-3 h-3 rounded-full bg-white transition-transform ${
                            webResearchEnabled ? 'translate-x-4' : 'translate-x-0'
                          }`}
                        />
                      </div>
                    </button>

                    {/* Landmark selector option */}
                    {onSelectLandmark && (
                      <div className="pt-1 border-t border-white/10 px-2.5 py-1">
                        <div className="text-[10px] text-slate-400 mb-1 flex items-center gap-1 font-semibold">
                          <MapPin className="w-3 h-3 text-orange-400" />
                          <span>Current Landmark:</span>
                        </div>
                        <select
                          value={selectedLandmark}
                          onChange={(e) => onSelectLandmark(e.target.value)}
                          className="w-full bg-[#1e2029] text-slate-200 text-xs rounded-lg px-2 py-1 border border-white/10 focus:outline-none cursor-pointer"
                        >
                          <option value="Block 32">Block 32 (CSE Hub)</option>
                          <option value="Uni-Centre">Uni-Centre Food Court</option>
                          <option value="Block 34">Block 34 (Exam Cell)</option>
                          <option value="Block 27">Block 27 (EDU-Rev)</option>
                          <option value="Block 13">Block 13 (DSA)</option>
                          <option value="Block 30">Block 30 (UniHospital)</option>
                          <option value="Uni-Mall">Uni-Mall</option>
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

              {/* [Normal ⌄] Pill (Persona & Specialist Selector) */}
              <div className="relative">
                <button
                  type="button"
                  onClick={() => {
                    setIsNormalDropdownOpen((prev) => !prev);
                    setIsModeDropdownOpen(false);
                    setIsPlusMenuOpen(false);
                  }}
                  className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 hover:bg-white/10 text-slate-300 hover:text-white text-xs font-medium transition-all border border-white/10"
                  title="Configure response style & agent intelligence"
                >
                  <Leaf className="w-3.5 h-3.5 text-emerald-400" />
                  <span>{selectedModel !== 'aegis' ? activeAgentObj.label.split('—')[0].trim() : activeTone}</span>
                  <ChevronDown className="w-3 h-3 text-slate-400" />
                </button>

                {isNormalDropdownOpen && (
                  <div className="absolute left-0 bottom-11 w-64 max-h-80 overflow-y-auto rounded-2xl bg-[#14151e]/98 backdrop-blur-2xl border border-white/10 shadow-2xl p-1.5 z-50 text-xs">
                    <div className="px-2.5 py-1 text-[10px] font-bold text-slate-400 uppercase tracking-wider border-b border-white/10 flex items-center justify-between">
                      <span>Tone & Depth</span>
                    </div>
                    {(['Normal', 'Concise', 'Academic', 'Detailed'] as const).map((tone) => (
                      <button
                        key={tone}
                        onClick={() => {
                          setActiveTone(tone);
                          setIsNormalDropdownOpen(false);
                        }}
                        className={`w-full text-left px-2.5 py-1.5 rounded-lg flex items-center justify-between hover:bg-white/10 transition-colors ${
                          activeTone === tone ? 'text-emerald-400 font-semibold bg-white/5' : 'text-slate-300'
                        }`}
                      >
                        <span>{tone}</span>
                        {activeTone === tone && <Check className="w-3.5 h-3.5 text-emerald-400" />}
                      </button>
                    ))}

                    <div className="px-2.5 py-1.5 mt-1 text-[10px] font-bold text-slate-400 uppercase tracking-wider border-t border-b border-white/10 flex items-center justify-between">
                      <span>Specialist Intelligence</span>
                      <span className="text-[9px] text-orange-400 font-mono">9 Available</span>
                    </div>
                    {agentOptions.map((opt) => {
                      const isSel = opt.id === selectedModel;
                      return (
                        <button
                          key={opt.id}
                          onClick={() => {
                            if (onSelectModel) onSelectModel(opt.id);
                            setIsNormalDropdownOpen(false);
                          }}
                          className={`w-full text-left px-2.5 py-1.5 rounded-lg flex flex-col hover:bg-white/10 transition-colors ${
                            isSel ? 'text-orange-400 font-semibold bg-white/5' : 'text-slate-300'
                          }`}
                        >
                          <div className="flex items-center justify-between w-full">
                            <span className="font-medium text-xs">{opt.label}</span>
                            <span className="text-[9px] text-slate-400 bg-white/5 px-1.5 py-0.5 rounded border border-white/10">
                              {opt.badge}
                            </span>
                          </div>
                          <div className="text-[10px] text-slate-400 mt-0.5">{opt.desc}</div>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* [DeepThink ^] Pill (Reasoning Mode: Quick answer, Balanced, DeepThink, Research) */}
              <div className="relative">
                <button
                  type="button"
                  onClick={() => {
                    setIsModeDropdownOpen((prev) => !prev);
                    setIsNormalDropdownOpen(false);
                    setIsPlusMenuOpen(false);
                  }}
                  className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 hover:bg-white/10 text-slate-200 hover:text-white text-xs font-medium transition-all border border-white/10"
                >
                  <Lightbulb className="w-3.5 h-3.5 text-purple-400" />
                  <span>{activeModeObj.label}</span>
                  {isModeDropdownOpen ? (
                    <ChevronDown className="w-3 h-3 text-slate-400" />
                  ) : (
                    <ChevronUp className="w-3 h-3 text-slate-400" />
                  )}
                </button>

                {/* Dropdown Menu (Exact match with reference image) */}
                {isModeDropdownOpen && (
                  <div className="absolute left-0 bottom-11 w-48 rounded-2xl bg-[#14151e]/98 backdrop-blur-2xl border border-white/10 shadow-2xl p-1.5 z-50 text-xs space-y-0.5 animate-fadeIn">
                    {reasoningModes.map((mode) => {
                      const isSelected = mode.id.toLowerCase() === reasoningMode.toLowerCase();
                      return (
                        <button
                          key={mode.id}
                          onClick={() => {
                            if (onSelectReasoningMode) onSelectReasoningMode(mode.id);
                            setIsModeDropdownOpen(false);
                          }}
                          className={`w-full text-left px-3 py-2 rounded-xl flex items-center justify-between transition-colors ${
                            isSelected
                              ? 'bg-white/10 text-white font-medium shadow-2xs'
                              : 'text-slate-300 hover:bg-white/5 hover:text-white'
                          }`}
                        >
                          <div className="flex items-center gap-2.5">
                            {mode.icon}
                            <span className="text-xs">{mode.label}</span>
                          </div>
                          {isSelected && <div className="w-1.5 h-1.5 rounded-full bg-purple-400" />}
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>

            {/* Right Controls: [Voice] and Send Button */}
            <div className="flex items-center gap-2 ml-auto">
              {/* Voice Pill Button */}
              <button
                type="button"
                onClick={toggleSpeechRecognition}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium transition-all border border-white/10 ${
                  isListening
                    ? 'bg-rose-500/20 text-rose-300 border-rose-500/40 animate-pulse'
                    : 'bg-white/5 hover:bg-white/10 text-slate-300 hover:text-white'
                }`}
                title={isListening ? 'Stop dictation' : 'Voice input'}
              >
                {isListening ? (
                  <>
                    <MicOff className="w-3.5 h-3.5 text-rose-400" />
                    <span>Listening...</span>
                  </>
                ) : (
                  <>
                    <AudioWaveform className="w-3.5 h-3.5 text-slate-300" />
                    <span>Voice</span>
                  </>
                )}
              </button>

              {/* Send / Stop Circular Gradient Button (Exact match with reference image) */}
              {isLoading ? (
                <button
                  type="button"
                  onClick={onStopStreaming}
                  className="w-9 h-9 rounded-full bg-rose-600 hover:bg-rose-500 text-white flex items-center justify-center transition-all shadow-md shadow-rose-600/30 active:scale-95"
                  title="Stop response"
                >
                  <Square className="w-3.5 h-3.5 fill-current" />
                </button>
              ) : (
                <button
                  type="button"
                  onClick={handleSubmit}
                  disabled={!input.trim()}
                  className={`w-9 h-9 rounded-full flex items-center justify-center transition-all ${
                    input.trim()
                      ? 'bg-gradient-to-tr from-[#6366f1] via-[#8b5cf6] to-[#ec4899] text-white shadow-lg shadow-purple-500/25 hover:opacity-95 active:scale-95'
                      : 'bg-white/5 text-slate-500 border border-white/10 cursor-not-allowed'
                  }`}
                  title="Send query (Enter)"
                >
                  <Send className="w-4 h-4 text-white -translate-x-[0.5px] translate-y-[0.5px]" />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Subtle Footer Disclaimer */}
      <p className="mt-2 text-center text-[10px] text-slate-400">
        CampusConnect AI can make mistakes. Verify critical academic deadlines and grades with official{' '}
        <a
          href="https://ums.lpu.in"
          target="_blank"
          rel="noreferrer"
          className="text-orange-500 hover:text-orange-400 underline"
        >
          LPU UMS
        </a>.
      </p>
    </div>
  );
};
