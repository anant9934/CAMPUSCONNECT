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
  Terminal,
  Calculator,
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
  CampusRouteCardView,
  CampusBlockDirectoryCardView,
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
  onOpenMapWithPlace?: (placeId?: string) => void;
  onOpenMapWithRoute?: (route?: any) => void;
}

export const ChatArea: React.FC<ChatAreaProps> = ({
  messages,
  isLoading,
  onRetry,
  onFeedback,
  onSelectPrompt,
  onEditAndResend,
  onOpenMapWithPlace,
  onOpenMapWithRoute,
}) => {
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [feedbackGiven, setFeedbackGiven] = useState<Record<string, 'helpful' | 'unhelpful'>>({});
  const [editingMessageId, setEditingMessageId] = useState<string | null>(null);
  const [editedContent, setEditedContent] = useState('');
  const [copiedCodeBlockIdx, setCopiedCodeBlockIdx] = useState<string | null>(null);

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleCopyCode = (blockId: string, code: string) => {
    navigator.clipboard.writeText(code);
    setCopiedCodeBlockIdx(blockId);
    setTimeout(() => setCopiedCodeBlockIdx(null), 2000);
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

  // Inline formatting helper (Bold, Italic, Code, Math, Links)
  const renderInlineFormatted = (text: string): React.ReactNode => {
    // Match inline code `code`, bold **text**, math $math$, links [label](url)
    const tokenRegex = /(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*|\$[^$]+\$|\[[^\]]+\]\([^)]+\))/g;
    const parts = text.split(tokenRegex);

    return parts.map((part, idx) => {
      if (!part) return null;

      // Inline Code: `code`
      if (part.startsWith('`') && part.endsWith('`') && part.length > 2) {
        return (
          <code
            key={idx}
            className="px-1.5 py-0.5 rounded-md bg-slate-100 text-orange-700 font-mono text-[13px] border border-slate-200/80 font-medium"
          >
            {part.slice(1, -1)}
          </code>
        );
      }

      // Bold: **text**
      if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
        return (
          <strong key={idx} className="font-semibold text-slate-900">
            {part.slice(2, -2)}
          </strong>
        );
      }

      // Italic: *text*
      if (part.startsWith('*') && part.endsWith('*') && part.length > 2 && !part.startsWith('**')) {
        return (
          <em key={idx} className="italic text-slate-700">
            {part.slice(1, -1)}
          </em>
        );
      }

      // Math: $math$
      if (part.startsWith('$') && part.endsWith('$') && part.length > 2) {
        return (
          <span
            key={idx}
            className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded bg-amber-50 text-amber-900 font-mono text-xs border border-amber-200/60"
          >
            <Calculator className="w-3 h-3 text-amber-600 inline mr-0.5" />
            {part.slice(1, -1)}
          </span>
        );
      }

      // Link: [label](url)
      const linkMatch = part.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
      if (linkMatch) {
        return (
          <a
            key={idx}
            href={linkMatch[2]}
            target="_blank"
            rel="noopener noreferrer"
            className="text-orange-600 hover:text-orange-700 underline font-medium inline-flex items-center gap-0.5"
          >
            <span>{linkMatch[1]}</span>
            <ExternalLink className="w-3 h-3 inline shrink-0" />
          </a>
        );
      }

      return part;
    });
  };

  // Full Rich Markdown Parser (Headings, Code blocks, Tables, Blockquotes, Lists, Math blocks)
  const renderRichMarkdown = (content: string, msgId: string) => {
    const rawLines = content.split('\n');
    const elements: React.ReactNode[] = [];

    let i = 0;
    let blockCount = 0;

    while (i < rawLines.length) {
      const line = rawLines[i];

      // 1. Code Blocks (```lang ... ```)
      if (line.trim().startsWith('```')) {
        const lang = line.trim().replace(/^```/, '').trim() || 'code';
        const codeLines: string[] = [];
        i++;
        while (i < rawLines.length && !rawLines[i].trim().startsWith('```')) {
          codeLines.push(rawLines[i]);
          i++;
        }
        i++; // skip closing ```
        const codeText = codeLines.join('\n');
        const blockKey = `${msgId}_code_${blockCount++}`;
        const isCopied = copiedCodeBlockIdx === blockKey;

        elements.push(
          <div key={blockKey} className="my-3 rounded-xl overflow-hidden border border-slate-700 bg-slate-900 shadow-sm text-xs font-mono">
            {/* Code Block Header */}
            <div className="flex items-center justify-between px-3.5 py-1.5 bg-slate-800/90 border-b border-slate-700 text-slate-300">
              <div className="flex items-center gap-1.5">
                <Terminal className="w-3.5 h-3.5 text-orange-400" />
                <span className="font-semibold uppercase tracking-wider text-[11px] text-slate-300">
                  {lang}
                </span>
              </div>
              <button
                type="button"
                onClick={() => handleCopyCode(blockKey, codeText)}
                className="flex items-center gap-1 px-2 py-0.5 rounded text-[11px] hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                title="Copy code"
              >
                {isCopied ? (
                  <>
                    <Check className="w-3 h-3 text-emerald-400" />
                    <span className="text-emerald-400 font-sans">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3 h-3" />
                    <span className="font-sans">Copy</span>
                  </>
                )}
              </button>
            </div>
            {/* Code Body */}
            <pre className="p-3.5 overflow-x-auto text-slate-100 text-[13px] leading-relaxed">
              <code>{codeText}</code>
            </pre>
          </div>
        );
        continue;
      }

      // 2. Math Formula Blocks ($$ ... $$)
      if (line.trim().startsWith('$$')) {
        const mathLines: string[] = [];
        const isSingleLine = line.trim().endsWith('$$') && line.trim().length > 2;
        if (isSingleLine) {
          mathLines.push(line.trim().slice(2, -2));
          i++;
        } else {
          i++;
          while (i < rawLines.length && !rawLines[i].trim().endsWith('$$')) {
            mathLines.push(rawLines[i]);
            i++;
          }
          i++; // skip closing $$
        }
        elements.push(
          <div
            key={`math_${i}`}
            className="my-3 p-3 rounded-xl bg-amber-50/60 border border-amber-200 text-center font-mono text-sm text-amber-950 overflow-x-auto shadow-2xs"
          >
            <div className="text-[10px] uppercase font-bold text-amber-700 mb-1 flex items-center justify-center gap-1">
              <Calculator className="w-3 h-3" />
              <span>Academic Formula / Calculation</span>
            </div>
            <div>{mathLines.join(' ')}</div>
          </div>
        );
        continue;
      }

      // 3. Tables (| Header | Header | ... and |---|---|)
      if (line.trim().startsWith('|') && line.includes('|')) {
        const tableLines: string[] = [];
        while (i < rawLines.length && rawLines[i].trim().startsWith('|')) {
          tableLines.push(rawLines[i].trim());
          i++;
        }

        if (tableLines.length >= 2) {
          const headerCells = tableLines[0]
            .split('|')
            .filter((_, idx, arr) => idx > 0 && idx < arr.length - 1)
            .map((c) => c.trim());

          const bodyLines = tableLines.slice(1).filter((l) => !l.replace(/[\s|:-]/g, '').length === false);

          elements.push(
            <div key={`table_${i}`} className="my-3 overflow-x-auto rounded-xl border border-slate-200 shadow-2xs">
              <table className="w-full text-left text-xs border-collapse">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-700 font-semibold">
                  <tr>
                    {headerCells.map((h, hIdx) => (
                      <th key={hIdx} className="px-3.5 py-2">
                        {renderInlineFormatted(h)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 bg-white">
                  {bodyLines.map((row, rIdx) => {
                    const cells = row
                      .split('|')
                      .filter((_, idx, arr) => idx > 0 && idx < arr.length - 1)
                      .map((c) => c.trim());
                    return (
                      <tr key={rIdx} className={rIdx % 2 === 1 ? 'bg-slate-50/50' : 'bg-white'}>
                        {cells.map((cell, cIdx) => (
                          <td key={cIdx} className="px-3.5 py-2 text-slate-700">
                            {renderInlineFormatted(cell)}
                          </td>
                        ))}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          );
          continue;
        }
      }

      // 4. Blockquotes (> ...)
      if (line.trim().startsWith('>')) {
        const quoteLines: string[] = [];
        while (i < rawLines.length && rawLines[i].trim().startsWith('>')) {
          quoteLines.push(rawLines[i].replace(/^>\s?/, ''));
          i++;
        }
        elements.push(
          <div
            key={`quote_${i}`}
            className="my-2.5 pl-3.5 py-2 border-l-4 border-orange-500 bg-orange-50/40 rounded-r-xl text-slate-800 text-xs sm:text-sm leading-relaxed"
          >
            {quoteLines.map((ql, qIdx) => (
              <p key={qIdx} className="italic">
                {renderInlineFormatted(ql)}
              </p>
            ))}
          </div>
        );
        continue;
      }

      // 5. Headings
      if (line.startsWith('# ')) {
        elements.push(
          <h1 key={`h1_${i}`} className="text-lg sm:text-xl font-bold text-slate-900 pt-2 pb-1 border-b border-slate-100">
            {renderInlineFormatted(line.replace('# ', ''))}
          </h1>
        );
        i++;
        continue;
      }
      if (line.startsWith('## ')) {
        elements.push(
          <h2 key={`h2_${i}`} className="text-base sm:text-lg font-bold text-slate-900 pt-2 pb-0.5">
            {renderInlineFormatted(line.replace('## ', ''))}
          </h2>
        );
        i++;
        continue;
      }
      if (line.startsWith('### ')) {
        elements.push(
          <h3 key={`h3_${i}`} className="text-sm sm:text-base font-semibold text-slate-900 pt-1.5 pb-0.5">
            {renderInlineFormatted(line.replace('### ', ''))}
          </h3>
        );
        i++;
        continue;
      }
      if (line.startsWith('#### ')) {
        elements.push(
          <h4 key={`h4_${i}`} className="text-xs sm:text-sm font-semibold text-slate-800 pt-1">
            {renderInlineFormatted(line.replace('#### ', ''))}
          </h4>
        );
        i++;
        continue;
      }

      // 6. Bullet lists
      if (line.trim().startsWith('• ') || line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
        const bulletText = line.trim().replace(/^[•\-\*]\s+/, '');
        elements.push(
          <div key={`bullet_${i}`} className="flex items-start gap-2 pl-1 my-1 text-sm text-slate-800">
            <span className="text-orange-600 font-bold mt-1 text-xs shrink-0">•</span>
            <div className="leading-relaxed">{renderInlineFormatted(bulletText)}</div>
          </div>
        );
        i++;
        continue;
      }

      // 7. Numbered lists
      const numMatch = line.trim().match(/^(\d+)\.\s+(.*)/);
      if (numMatch) {
        elements.push(
          <div key={`num_${i}`} className="flex items-start gap-2 pl-1 my-1 text-sm text-slate-800">
            <span className="font-semibold text-orange-600 text-xs mt-0.5 shrink-0">{numMatch[1]}.</span>
            <div className="leading-relaxed">{renderInlineFormatted(numMatch[2])}</div>
          </div>
        );
        i++;
        continue;
      }

      // 8. Horizontal Divider
      if (line.trim() === '---' || line.trim() === '***') {
        elements.push(<hr key={`hr_${i}`} className="border-slate-200 my-3" />);
        i++;
        continue;
      }

      // Empty line spacing
      if (!line.trim()) {
        elements.push(<div key={`sp_${i}`} className="h-1.5" />);
        i++;
        continue;
      }

      // Standard paragraph
      elements.push(
        <p key={`p_${i}`} className="text-sm text-slate-800 leading-relaxed my-1">
          {renderInlineFormatted(line)}
        </p>
      );
      i++;
    }

    return <div className="space-y-1">{elements}</div>;
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
                {renderRichMarkdown(msg.content, msg.id)}

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
                  <CampusPlaceCardView
                    card={msg.campus_place_card}
                    onOpenMap={(placeId) => onOpenMapWithPlace?.(placeId)}
                    onNavigate={(dest) => onSelectPrompt(`Take me to ${dest}`)}
                  />
                )}
                {msg.campus_route_card && (
                  <CampusRouteCardView
                    card={msg.campus_route_card}
                    onOpenMap={() => onOpenMapWithRoute?.(msg.campus_route_card)}
                  />
                )}
                {msg.campus_block_directory_card && (
                  <CampusBlockDirectoryCardView
                    card={msg.campus_block_directory_card}
                    onSelectPlace={(placeId) => onOpenMapWithPlace?.(placeId)}
                  />
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
                        <span className="text-[11px] text-emerald-700 font-medium">Copied</span>
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
                    {msg.is_ai_generated ? 'Frontier Model Synthesis' : 'Direct Verified LPU KB'}
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
