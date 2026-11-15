import React, { useState } from 'react';
import {
  Copy,
  Check,
  ThumbsUp,
  ThumbsDown,
  RotateCcw,
  Sparkles,
  User,
  GraduationCap,
  ExternalLink,
  CheckCircle2,
  AlertCircle,
  Edit2,
  X,
  Send,
} from 'lucide-react';
import { ChatMessage, Citation } from '../types';
import { ThinkingIndicator } from './ThinkingIndicator';
import { CitationCard } from './CitationCard';
import {
  NavigationCardView,
  BookingCardView,
  ProcedureChecklistView,
  RMSCardView,
  PersonalRecordCardView,
  CampusPlaceCardView,
  FoodOutletCardView,
  PersonCardView,
  WhoToMeetCardView,
  BenefitAssessmentCardView,
  EvidenceCardView,
} from './action_cards';

interface ChatAreaProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onRetry: () => void;
  onFeedback: (messageId: string, rating: 'helpful' | 'unhelpful') => void;
  onSelectPrompt: (prompt: string) => void;
  onEditAndResend?: (messageId: string, newText: string) => void;
}

export const ChatArea: React.FC<ChatAreaProps> = ({
  messages,
  isLoading,
  onRetry,
  onFeedback,
  onSelectPrompt,
  onEditAndResend,
}) => {
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [feedbackGiven, setFeedbackGiven] = useState<Record<string, 'helpful' | 'unhelpful'>>({});
  const [editingMessageId, setEditingMessageId] = useState<string | null>(null);
  const [editedContent, setEditedContent] = useState('');

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleFeedbackClick = (messageId: string, rating: 'helpful' | 'unhelpful') => {
    setFeedbackGiven((prev) => ({ ...prev, [messageId]: rating }));
    onFeedback(messageId, rating);
  };

  const handleStartEdit = (msg: ChatMessage) => {
    setEditingMessageId(msg.id);
    setEditedContent(msg.content);
  };

  const handleSaveEdit = (msgId: string) => {
    if (editedContent.trim() && onEditAndResend) {
      onEditAndResend(msgId, editedContent.trim());
    }
    setEditingMessageId(null);
  };

  // Simple markdown renderer for clean paragraph & bullet formatting
  const renderFormattedContent = (content: string) => {
    const lines = content.split('\n');
    return (
      <div className="space-y-2.5 leading-relaxed text-slate-800 text-sm">
        {lines.map((line, idx) => {
          if (!line.trim()) return <div key={idx} className="h-1" />;

          // Headers
          if (line.startsWith('### ')) {
            return (
              <h4 key={idx} className="font-semibold text-slate-900 pt-1 text-sm">
                {line.replace('### ', '')}
              </h4>
            );
          }
          if (
            line.startsWith('## ') ||
            (line.startsWith('**') && line.endsWith('**') && line.length < 80)
          ) {
            return (
              <h3 key={idx} className="font-bold text-slate-900 pt-1.5 text-base">
                {line.replace(/[\*#]/g, '').trim()}
              </h3>
            );
          }

          // Bullet points
          if (line.startsWith('• ') || line.startsWith('- ') || line.startsWith('* ')) {
            const bulletText = line.replace(/^[•\-\*]\s+/, '');
            return (
              <div key={idx} className="flex items-start gap-2 pl-1">
                <span className="text-orange-500 font-bold mt-1 text-xs">•</span>
                <span>{renderBoldSpans(bulletText)}</span>
              </div>
            );
          }

          // Numbered list
          const numMatch = line.match(/^(\d+)\.\s+(.*)/);
          if (numMatch) {
            return (
              <div key={idx} className="flex items-start gap-2 pl-1">
                <span className="font-semibold text-orange-600 text-xs mt-0.5">{numMatch[1]}.</span>
                <span>{renderBoldSpans(numMatch[2])}</span>
              </div>
            );
          }

          // Horizontal divider
          if (line.trim() === '---') {
            return <hr key={idx} className="border-slate-200 my-2" />;
          }

          // Italic / note line
          if (line.startsWith('*') && line.endsWith('*')) {
            return (
              <p key={idx} className="text-xs text-slate-500 italic">
                {line.replace(/\*/g, '')}
              </p>
            );
          }

          return <p key={idx}>{renderBoldSpans(line)}</p>;
        })}
      </div>
    );
  };

  const renderBoldSpans = (text: string) => {
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return (
          <strong key={i} className="font-semibold text-slate-900">
            {part.slice(2, -2)}
          </strong>
        );
      }
      return part;
    });
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
      {messages.map((msg, index) => {
        const isUser = msg.role === 'user';
        const isLast = index === messages.length - 1;
        const isEditing = editingMessageId === msg.id;

        if (isUser) {
          return (
            <div key={msg.id} className="flex justify-end gap-3 group animate-fadeIn">
              <div className="max-w-[85%] space-y-1">
                {isEditing ? (
                  <div className="rounded-2xl bg-white border border-orange-400 p-3 shadow-soft space-y-2">
                    <textarea
                      value={editedContent}
                      onChange={(e) => setEditedContent(e.target.value)}
                      className="w-full text-xs text-slate-800 bg-transparent focus:outline-none resize-none"
                      rows={3}
                      autoFocus
                    />
                    <div className="flex justify-end gap-1.5 pt-1 border-t border-slate-100">
                      <button
                        onClick={() => setEditingMessageId(null)}
                        className="px-2.5 py-1 text-xs text-slate-500 hover:bg-slate-100 rounded-lg"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={() => handleSaveEdit(msg.id)}
                        className="px-3 py-1 text-xs bg-orange-600 text-white rounded-lg font-semibold hover:bg-orange-700 flex items-center gap-1"
                      >
                        <Send className="w-3 h-3" />
                        <span>Resend</span>
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="relative group/bubble">
                    <div className="rounded-2xl bg-slate-900 text-white px-4 py-3 text-sm shadow-soft-sm font-medium leading-relaxed">
                      {msg.content}
                    </div>

                    {/* Edit prompt button */}
                    {onEditAndResend && (
                      <button
                        onClick={() => handleStartEdit(msg)}
                        className="opacity-0 group-hover/bubble:opacity-100 absolute -left-8 top-1/2 -translate-y-1/2 p-1.5 text-slate-400 hover:text-slate-700 bg-white border border-slate-200 rounded-full shadow-2xs transition-opacity"
                        title="Edit and resend"
                      >
                        <Edit2 className="w-3 h-3" />
                      </button>
                    )}
                  </div>
                )}
              </div>

              <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 shrink-0 mt-0.5">
                <User className="w-4 h-4" />
              </div>
            </div>
          );
        }

        // Assistant message
        const currentFeedback = feedbackGiven[msg.id];
        return (
          <div key={msg.id} className="flex items-start gap-3.5 animate-fadeIn">
            {/* LPU Logo Avatar */}
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center text-white shrink-0 mt-1 shadow-soft">
              <GraduationCap className="w-4 h-4" />
            </div>

            <div className="flex-1 space-y-3 min-w-0">
              {/* Thinking Indicator Accordion */}
              {msg.thinking_steps && msg.thinking_steps.length > 0 && (
                <ThinkingIndicator
                  steps={msg.thinking_steps}
                  confidenceScore={msg.confidence_score}
                  latencyMs={msg.latency_ms}
                />
              )}

              {/* Message Typography */}
              <div className="rounded-2xl bg-white border border-warm-border p-4 shadow-soft-sm">
                {renderFormattedContent(msg.content)}

                {/* Action Cards */}
                {msg.navigation_card && <NavigationCardView card={msg.navigation_card} />}
                {msg.booking_card && <BookingCardView card={msg.booking_card} />}
                {msg.procedure_checklist && (
                  <ProcedureChecklistView card={msg.procedure_checklist} />
                )}
                {msg.rms_card && <RMSCardView card={msg.rms_card} />}
                {msg.personal_record_card && (
                  <PersonalRecordCardView card={msg.personal_record_card} />
                )}
                {msg.campus_place_card && (
                  <CampusPlaceCardView card={msg.campus_place_card} />
                )}
                {msg.food_outlet_card && <FoodOutletCardView card={msg.food_outlet_card} />}
                {msg.person_card && <PersonCardView card={msg.person_card} />}
                {msg.who_to_meet_card && <WhoToMeetCardView card={msg.who_to_meet_card} />}
                {msg.academic_benefit_card && (
                  <BenefitAssessmentCardView card={msg.academic_benefit_card} />
                )}
                {msg.evidence_card && <EvidenceCardView card={msg.evidence_card} />}

                {/* Source Citations */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-slate-100">
                    <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Verified Sources & Citations ({msg.citations.length})</span>
                    </div>
                    <div className="grid grid-cols-1 gap-2">
                      {msg.citations.map((cite, cIdx) => (
                        <CitationCard key={cIdx} citation={cite} index={cIdx} />
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Action Toolbar */}
              <div className="flex items-center justify-between text-xs text-slate-400 px-1">
                <div className="flex items-center gap-1.5">
                  <button
                    onClick={() => handleCopy(msg.id, msg.content)}
                    className="flex items-center gap-1 p-1.5 rounded-lg hover:bg-slate-100 hover:text-slate-700 transition-colors"
                    title="Copy response"
                  >
                    {copiedId === msg.id ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-emerald-600" />
                        <span className="text-[11px] text-emerald-700">Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5" />
                        <span className="text-[11px]">Copy</span>
                      </>
                    )}
                  </button>

                  <div className="h-3 w-px bg-slate-200 mx-1" />

                  <button
                    onClick={() => handleFeedbackClick(msg.id, 'helpful')}
                    className={`flex items-center gap-1 p-1.5 rounded-lg transition-colors ${
                      currentFeedback === 'helpful'
                        ? 'bg-emerald-50 text-emerald-700 font-semibold'
                        : 'hover:bg-slate-100 hover:text-slate-700'
                    }`}
                    title="Helpful response"
                  >
                    <ThumbsUp className="w-3.5 h-3.5" />
                    {currentFeedback === 'helpful' && <span className="text-[11px]">Helpful</span>}
                  </button>

                  <button
                    onClick={() => handleFeedbackClick(msg.id, 'unhelpful')}
                    className={`flex items-center gap-1 p-1.5 rounded-lg transition-colors ${
                      currentFeedback === 'unhelpful'
                        ? 'bg-rose-50 text-rose-700 font-semibold'
                        : 'hover:bg-slate-100 hover:text-slate-700'
                    }`}
                    title="Not helpful"
                  >
                    <ThumbsDown className="w-3.5 h-3.5" />
                    {currentFeedback === 'unhelpful' && (
                      <span className="text-[11px]">Unhelpful</span>
                    )}
                  </button>

                  {isLast && (
                    <>
                      <div className="h-3 w-px bg-slate-200 mx-1" />
                      <button
                        onClick={onRetry}
                        className="flex items-center gap-1 p-1.5 rounded-lg hover:bg-slate-100 hover:text-slate-700 transition-colors"
                        title="Retry response"
                      >
                        <RotateCcw className="w-3.5 h-3.5" />
                        <span className="text-[11px]">Retry</span>
                      </button>
                    </>
                  )}
                </div>

                {msg.is_ai_generated !== undefined && (
                  <span className="text-[11px] text-slate-400">
                    {msg.is_ai_generated ? 'Gemini Pro / Flash' : 'Direct Verified LPU KB'}
                  </span>
                )}
              </div>

              {/* Follow-up Prompts */}
              {isLast && msg.follow_ups && msg.follow_ups.length > 0 && (
                <div className="pt-2 space-y-2">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                    Suggested Follow-ups
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {msg.follow_ups.map((fu, fIdx) => (
                      <button
                        key={fIdx}
                        onClick={() => onSelectPrompt(fu)}
                        className="text-xs px-3 py-1.5 rounded-xl bg-white border border-warm-border text-slate-700 hover:border-orange-300 hover:text-orange-700 hover:bg-orange-50/40 transition-all shadow-soft-sm text-left"
                      >
                        {fu}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        );
      })}

      {/* Live Loading Thinking State */}
      {isLoading && (
        <div className="flex items-start gap-3.5 animate-fadeIn">
          <div className="w-8 h-8 rounded-xl bg-orange-600 flex items-center justify-center text-white shrink-0 mt-1 shadow-soft">
            <GraduationCap className="w-4 h-4" />
          </div>
          <div className="flex-1 min-w-0">
            <ThinkingIndicator isStreaming={true} />
          </div>
        </div>
      )}
    </div>
  );
};
