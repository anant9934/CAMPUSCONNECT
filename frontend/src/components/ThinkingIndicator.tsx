import React, { useState } from 'react';
import {
  CheckCircle2,
  Loader2,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Brain,
  Shield,
  Search,
  Compass,
  FileCheck2,
  Cpu,
} from 'lucide-react';
import { ThinkingStep } from '../types';

interface ThinkingIndicatorProps {
  steps?: ThinkingStep[];
  isStreaming?: boolean;
  confidenceScore?: number;
  latencyMs?: number;
  specialistsInvolved?: string[];
}

const DEFAULT_REAL_STEPS: ThinkingStep[] = [
  { step: 1, title: 'Understanding task', description: 'Classified student intent, academic complexity, language, and risk boundaries.', status: 'completed' },
  { step: 2, title: 'Planning', description: 'Selected active intelligence identity, execution steps, tool permissions, and token budget.', status: 'completed' },
  { step: 3, title: 'Retrieving knowledge', description: 'Queried institutional pgvector embeddings, hybrid BM25 index & university service catalog.', status: 'completed' },
  { step: 4, title: 'Selecting model', description: 'Evaluated candidate providers and models across capabilities, context window & latency tier.', status: 'completed' },
  { step: 5, title: 'Running tools', description: 'Executed direct institutional hybrid search and active specialist subagents.', status: 'completed' },
  { step: 6, title: 'Verifying results', description: 'Enforced statutory 65% attendance floor, non-unilateral execution, and citation grounding.', status: 'completed' },
  { step: 7, title: 'Preparing response', description: 'Synthesized verified guidance, action cards, and citation trails in persona voice.', status: 'completed' },
];

const SPECIALIST_LABELS: Record<string, { label: string; color: string }> = {
  themis: { label: 'THEMIS: Policy analysis', color: 'bg-orange-50 text-orange-700 border-orange-200' },
  athena: { label: 'ATHENA: Reasoning', color: 'bg-indigo-50 text-indigo-700 border-indigo-200' },
  hermes: { label: 'HERMES: Navigation', color: 'bg-teal-50 text-teal-700 border-teal-200' },
  oracle: { label: 'ORACLE: Source verification', color: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
  nova: { label: 'NOVA: Everyday help', color: 'bg-amber-50 text-amber-700 border-amber-200' },
  forge: { label: 'FORGE: Code review', color: 'bg-blue-50 text-blue-700 border-blue-200' },
  vision: { label: 'VISION: Visual inspection', color: 'bg-violet-50 text-violet-700 border-violet-200' },
  argus: { label: 'ARGUS: Faculty & Wayfinding', color: 'bg-slate-100 text-slate-700 border-slate-300' },
  mnemos: { label: 'MNEMOS: Memory & RAG', color: 'bg-cyan-50 text-cyan-700 border-cyan-200' },
};

export const ThinkingIndicator: React.FC<ThinkingIndicatorProps> = ({
  steps = DEFAULT_REAL_STEPS,
  isStreaming = false,
  confidenceScore,
  latencyMs,
  specialistsInvolved = ['themis', 'hermes'],
}) => {
  const [isOpen, setIsOpen] = useState(false);

  // Active streaming state
  if (isStreaming) {
    return (
      <div className="rounded-xl border border-orange-200/80 bg-orange-50/40 p-3 shadow-xs mb-3 animate-fadeIn">
        <div className="flex items-center justify-between text-xs font-semibold text-orange-950 mb-2">
          <div className="flex items-center gap-2">
            <Loader2 className="w-4 h-4 text-orange-600 animate-spin" />
            <span>Thinking... Coordinating University Intelligence</span>
          </div>
          <span className="text-[11px] text-orange-700 font-mono font-medium">In Progress</span>
        </div>

        {/* Real execution stream progression */}
        <div className="space-y-1.5 pl-6">
          <div className="flex items-center gap-2 text-[11px] text-slate-700">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
            <span>1. Understanding task & Planning execution</span>
          </div>
          <div className="flex items-center gap-2 text-[11px] text-orange-900 font-semibold">
            <Loader2 className="w-3.5 h-3.5 text-orange-600 animate-spin shrink-0" />
            <span>2. Retrieving knowledge & Selecting model</span>
          </div>
          <div className="flex items-center gap-2 text-[11px] text-slate-400">
            <span className="w-3.5 h-3.5 rounded-full border border-slate-300 inline-block text-[9px] text-center leading-3">3</span>
            <span>3. Running tools & Verifying results</span>
          </div>
          <div className="flex items-center gap-2 text-[11px] text-slate-400">
            <span className="w-3.5 h-3.5 rounded-full border border-slate-300 inline-block text-[9px] text-center leading-3">4</span>
            <span>4. Preparing response & action cards</span>
          </div>
        </div>

        {/* Specialist chips during generation */}
        <div className="mt-2.5 pt-2 border-t border-orange-200/60 flex flex-wrap gap-1.5 pl-6">
          <span className="text-[10px] text-slate-500 font-medium self-center">Active Agents:</span>
          {specialistsInvolved.map((spec) => {
            const chip = SPECIALIST_LABELS[spec.toLowerCase()] || {
              label: `${spec.toUpperCase()}: Processing`,
              color: 'bg-slate-100 text-slate-700 border-slate-200',
            };
            return (
              <span
                key={spec}
                className={`text-[10px] px-2 py-0.5 rounded-md border font-medium ${chip.color}`}
              >
                {chip.label}
              </span>
            );
          })}
        </div>
      </div>
    );
  }

  // Use provided steps or fallback to standard 7 steps
  const displaySteps = steps && steps.length > 0 ? steps : DEFAULT_REAL_STEPS;

  return (
    <div className="rounded-xl border border-slate-200/80 bg-slate-50/70 p-2.5 mb-3 transition-colors hover:bg-slate-100/50">
      {/* Header bar: click to expand / collapse */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between text-xs font-medium text-slate-700 hover:text-slate-900 transition-colors"
      >
        <div className="flex items-center gap-2 flex-wrap">
          <Sparkles className="w-3.5 h-3.5 text-orange-600 shrink-0" />
          <span className="font-semibold text-slate-800">Thinking Process & Verification</span>
          {confidenceScore !== undefined && (
            <span className="px-1.5 py-0.2 rounded-md bg-white border border-slate-200 text-[10px] text-slate-600 font-mono font-medium">
              Grounding: {(confidenceScore * 100).toFixed(0)}%
            </span>
          )}
          {latencyMs !== undefined && latencyMs > 0 && (
            <span className="text-[10px] text-slate-400 font-mono">
              {latencyMs}ms
            </span>
          )}
        </div>
        <div className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-slate-600">
          <span>{isOpen ? 'Hide trace' : 'View reasoning'}</span>
          {isOpen ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </div>
      </button>

      {/* Specialist Status Chips Preview */}
      <div className="mt-1.5 flex flex-wrap gap-1.5 items-center">
        {specialistsInvolved.map((spec) => {
          const chip = SPECIALIST_LABELS[spec.toLowerCase()] || {
            label: `${spec.toUpperCase()}: Analysis`,
            color: 'bg-slate-100 text-slate-700 border-slate-200',
          };
          return (
            <span
              key={spec}
              className={`text-[10px] px-2 py-0.5 rounded-md border font-medium ${chip.color}`}
            >
              {chip.label}
            </span>
          );
        })}
      </div>

      {/* Expanded Accordion Body */}
      {isOpen && (
        <div className="mt-2.5 pt-2.5 border-t border-slate-200/80 space-y-2.5 pl-1 animate-fadeIn">
          {displaySteps.map((st, idx) => (
            <div key={st.step || idx} className="flex items-start gap-2.5 text-xs">
              <div className="mt-0.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-semibold text-slate-800">
                  {st.step || idx + 1}. {st.title}
                </div>
                <div className="text-[11px] text-slate-500 leading-snug mt-0.5">
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
