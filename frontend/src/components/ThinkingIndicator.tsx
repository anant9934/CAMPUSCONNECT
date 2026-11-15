import React, { useState } from 'react';
import { CheckCircle2, Loader2, Sparkles, ChevronDown, ChevronUp } from 'lucide-react';
import { ThinkingStep } from '../types';

interface ThinkingIndicatorProps {
  steps?: ThinkingStep[];
  isStreaming?: boolean;
  confidenceScore?: number;
  latencyMs?: number;
}

const DEFAULT_STEPS: ThinkingStep[] = [
  { step: 1, title: 'Preparing question', description: 'Normalizing query and checking context', status: 'completed' },
  { step: 2, title: 'Searching LPU knowledge', description: 'Querying approved FAQs and documents', status: 'completed' },
  { step: 3, title: 'Analysing retrieved information', description: 'Calibrating confidence and relevance', status: 'completed' },
  { step: 4, title: 'Generating response', description: 'Synthesizing evidence-based answer', status: 'completed' },
  { step: 5, title: 'Completed', description: 'Verifying factual grounding and citations', status: 'completed' },
];

export const ThinkingIndicator: React.FC<ThinkingIndicatorProps> = ({
  steps = DEFAULT_STEPS,
  isStreaming = false,
  confidenceScore,
  latencyMs,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  // During active loading/streaming
  if (isStreaming) {
    return (
      <div className="rounded-xl border border-orange-100 bg-orange-50/40 p-3 shadow-soft-sm mb-3">
        <div className="flex items-center justify-between text-xs font-medium text-orange-900 mb-2">
          <div className="flex items-center gap-2">
            <Loader2 className="w-4 h-4 text-orange-600 animate-spin" />
            <span>Consulting LPU Knowledge Base...</span>
          </div>
          <span className="text-[11px] text-orange-600 font-mono">Phase 2/4</span>
        </div>

        <div className="space-y-1.5 pl-6">
          <div className="flex items-center gap-2 text-[11px] text-slate-700">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            <span>1. Preparing question & isolating session context</span>
          </div>
          <div className="flex items-center gap-2 text-[11px] text-orange-800 font-semibold">
            <Loader2 className="w-3.5 h-3.5 text-orange-600 animate-spin" />
            <span>2. Searching approved LPU institutional records</span>
          </div>
          <div className="flex items-center gap-2 text-[11px] text-slate-400">
            <span className="w-3.5 h-3.5 rounded-full border border-slate-300 inline-block text-[9px] text-center leading-3">3</span>
            <span>3. Analysing evidence & calibrating confidence</span>
          </div>
          <div className="flex items-center gap-2 text-[11px] text-slate-400">
            <span className="w-3.5 h-3.5 rounded-full border border-slate-300 inline-block text-[9px] text-center leading-3">4</span>
            <span>4. Generating grounded response</span>
          </div>
        </div>
      </div>
    );
  }

  // Completed message accordion view
  return (
    <div className="rounded-xl border border-warm-border bg-warm-50/50 p-2.5 mb-3 transition-colors hover:bg-warm-100/40">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between text-xs font-medium text-slate-600 hover:text-slate-900 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Sparkles className="w-3.5 h-3.5 text-orange-600" />
          <span>Institutional Verification Steps</span>
          {confidenceScore !== undefined && (
            <span className="px-1.5 py-0.2 rounded-md bg-white border border-warm-border text-[10px] text-slate-600 font-mono">
              Score: {confidenceScore.toFixed(2)}
            </span>
          )}
          {latencyMs !== undefined && latencyMs > 0 && (
            <span className="text-[10px] text-slate-400 font-mono">
              {latencyMs}ms
            </span>
          )}
        </div>
        <div className="flex items-center gap-1 text-[11px] text-slate-400">
          <span>{isOpen ? 'Hide trace' : 'View trace'}</span>
          {isOpen ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </div>
      </button>

      {isOpen && (
        <div className="mt-2.5 pt-2 border-t border-slate-200/60 space-y-2 pl-2">
          {steps.map((st) => (
            <div key={st.step} className="flex items-start gap-2.5 text-xs">
              <div className="mt-0.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
              </div>
              <div>
                <div className="font-semibold text-slate-800">
                  {st.step}. {st.title}
                </div>
                <div className="text-[11px] text-slate-500 leading-snug">
                  {st.description}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

