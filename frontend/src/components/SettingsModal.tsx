import React, { useState, useEffect } from 'react';
import {
  X,
  Settings,
  Cpu,
  Sparkles,
  Shield,
  Gauge,
  CheckCircle2,
  AlertTriangle,
  Globe,
  MapPin,
  ChevronDown,
  ChevronUp,
  Layers,
} from 'lucide-react';
import { api } from '../services/api';
import { AgentEngineInfo } from '../types';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedModel: string;
  onSelectModel: (model: string) => void;
  reasoningMode: string;
  onSelectReasoningMode: (mode: string) => void;
  webResearchEnabled: boolean;
  onToggleWebResearch: (enabled: boolean) => void;
  selectedLandmark: string;
  onSelectLandmark: (landmark: string) => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  selectedModel,
  onSelectModel,
  reasoningMode,
  onSelectReasoningMode,
  webResearchEnabled,
  onToggleWebResearch,
  selectedLandmark,
  onSelectLandmark,
}) => {
  const [llmUsage, setLlmUsage] = useState<any>(null);
  const [providers, setProviders] = useState<any[]>([]);
  const [agentDiagnostics, setAgentDiagnostics] = useState<AgentEngineInfo[]>([]);
  const [isEngineExpanded, setIsEngineExpanded] = useState<boolean>(false);

  useEffect(() => {
    if (isOpen) {
      api.getLLMUsage().then(setLlmUsage).catch(console.error);
      api.getLLMProviders().then((res) => setProviders(res.providers || [])).catch(console.error);
      api.getAgentDiagnostics().then(setAgentDiagnostics).catch(console.error);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const models = [
    {
      id: 'gemini-2.5-flash',
      name: 'Google Gemini 2.5 Flash',
      provider: 'Google GenAI (Free Tier)',
      tag: 'Fast & Grounded (Default)',
      context: '1,000,000 tokens',
    },
    {
      id: 'gemini-2.5-pro',
      name: 'Google Gemini 2.5 Pro',
      provider: 'Google GenAI (Free Tier)',
      tag: 'Deep Reasoning',
      context: '2,000,000 tokens',
    },
    {
      id: 'meta-llama/llama-3.3-70b-instruct:free',
      name: 'Llama 3.3 70B Instruct',
      provider: 'OpenRouter (Free)',
      tag: 'Open-Source Power',
      context: '131,072 tokens',
    },
    {
      id: 'mistral-small-latest',
      name: 'Mistral Small Latest',
      provider: 'Mistral AI',
      tag: 'Balanced Latency',
      context: '32,768 tokens',
    },
    {
      id: 'grok-beta',
      name: 'xAI Grok Beta',
      provider: 'xAI',
      tag: 'Real-time Dialog',
      context: '131,072 tokens',
    },
    {
      id: 'gpt-4o-mini',
      name: 'OpenAI GPT-4o Mini',
      provider: 'OpenAI Compatible',
      tag: 'Compact Reasoning',
      context: '128,000 tokens',
    },
  ];

  const modes = [
    { id: 'quick', label: 'Quick Answer', icon: '⚡', desc: 'Direct, crisp factual answers with lowest latency.' },
    { id: 'balanced', label: 'Balanced', icon: '⚖️', desc: 'Standard comprehensive university grounding (recommended).' },
    { id: 'deepthink', label: 'DeepThink', icon: '💡', desc: 'In-depth multi-clause regulatory analysis and planning.' },
    { id: 'research', label: 'Research', icon: '🔬', desc: 'Cross-checks external UGC / statutory databases & live web.' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs animate-fadeIn">
      <div className="bg-white rounded-2xl border border-warm-border w-full max-w-2xl max-h-[85vh] flex flex-col shadow-soft-lg overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-warm-border flex items-center justify-between bg-slate-50/60">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-slate-100 text-slate-800 flex items-center justify-center border border-slate-200">
              <Settings className="w-5 h-5 text-slate-700" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900">Workspace Settings & AI Configuration</h2>
              <p className="text-xs text-slate-500">Configure LLM routing, reasoning modes, and campus preferences</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-6 bg-slate-50/20 text-xs">
          {/* AI Model Selection */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="font-bold text-slate-900 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                <Cpu className="w-4 h-4 text-orange-600" />
                Active Conversational LLM Model
              </label>
              <span className="text-[10px] text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded font-medium border border-emerald-200">
                Live Cascade Enabled
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {models.map((m) => {
                const isSelected = selectedModel === m.id;
                return (
                  <div
                    key={m.id}
                    onClick={() => onSelectModel(m.id)}
                    className={`p-3 rounded-xl border cursor-pointer transition-all ${
                      isSelected
                        ? 'border-orange-500 bg-orange-50/40 shadow-xs'
                        : 'border-warm-border bg-white hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-900">{m.name}</span>
                      {isSelected && <CheckCircle2 className="w-4 h-4 text-orange-600" />}
                    </div>
                    <div className="text-[11px] text-slate-500">{m.provider}</div>
                    <div className="mt-1 flex items-center justify-between text-[10px]">
                      <span className="text-orange-700 font-semibold">{m.tag}</span>
                      <span className="text-slate-400">{m.context}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Reasoning / Execution Mode */}
          <div className="space-y-3 pt-2 border-t border-slate-100">
            <label className="font-bold text-slate-900 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-indigo-600" />
              Default Reasoning Mode
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {modes.map((mode) => {
                const isSelected = reasoningMode === mode.id;
                return (
                  <div
                    key={mode.id}
                    onClick={() => onSelectReasoningMode(mode.id)}
                    className={`p-3 rounded-xl border cursor-pointer transition-all ${
                      isSelected
                        ? 'border-indigo-500 bg-indigo-50/40 shadow-xs'
                        : 'border-warm-border bg-white hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-center gap-2 font-bold text-slate-900">
                      <span>{mode.icon}</span>
                      <span>{mode.label}</span>
                    </div>
                    <p className="mt-1 text-[11px] text-slate-600 leading-relaxed">{mode.desc}</p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Web Research & Proximity Preferences */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-slate-100">
            <div className="space-y-2">
              <label className="font-bold text-slate-900 text-[11px] flex items-center gap-1.5">
                <Globe className="w-4 h-4 text-emerald-600" />
                Live Web Research
              </label>
              <p className="text-[11px] text-slate-500">
                Queries official LPU and statutory UGC/AICTE portals for regulatory updates.
              </p>
              <button
                onClick={() => onToggleWebResearch(!webResearchEnabled)}
                className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                  webResearchEnabled
                    ? 'bg-emerald-600 text-white'
                    : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
                }`}
              >
                {webResearchEnabled ? '✓ Enabled' : 'Disabled'}
              </button>
            </div>

            <div className="space-y-2">
              <label className="font-bold text-slate-900 text-[11px] flex items-center gap-1.5">
                <MapPin className="w-4 h-4 text-orange-600" />
                Default Campus Location
              </label>
              <p className="text-[11px] text-slate-500">
                Used for straight-line proximity estimates to food stalls and facilities.
              </p>
              <select
                value={selectedLandmark}
                onChange={(e) => onSelectLandmark(e.target.value)}
                className="w-full p-2 rounded-lg border border-warm-border bg-white text-slate-800 font-medium focus:outline-none focus:border-orange-400"
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
          </div>

          {/* Usage Analytics Snapshot */}
          {llmUsage && (
            <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-800 flex items-center gap-1.5">
                  <Gauge className="w-3.5 h-3.5 text-slate-600" />
                  Free Tier LLM Quota Status
                </span>
                <span className="text-emerald-700 font-semibold bg-emerald-100 px-2 py-0.5 rounded text-[10px]">
                  {llmUsage.status === 'healthy' ? 'Healthy' : 'Circuit Open'}
                </span>
              </div>
              <div className="grid grid-cols-3 gap-2 text-center pt-1">
                <div className="bg-white p-2 rounded-lg border border-slate-200/60">
                  <div className="font-bold text-slate-900 text-sm">{llmUsage.total_llm_requests}</div>
                  <div className="text-[10px] text-slate-400">Total Requests</div>
                </div>
                <div className="bg-white p-2 rounded-lg border border-slate-200/60">
                  <div className="font-bold text-slate-900 text-sm">
                    {llmUsage.total_tokens_consumed.toLocaleString()}
                  </div>
                  <div className="text-[10px] text-slate-400">Tokens Consumed</div>
                </div>
                <div className="bg-white p-2 rounded-lg border border-slate-200/60">
                  <div className="font-bold text-slate-900 text-sm">{llmUsage.average_latency_ms} ms</div>
                  <div className="text-[10px] text-slate-400">Avg Latency</div>
                </div>
              </div>
            </div>
          )}
          {/* Expandable Multi-Agent Engine Information */}
          <div className="pt-2 border-t border-slate-200">
            <button
              type="button"
              onClick={() => setIsEngineExpanded((prev) => !prev)}
              className="w-full flex items-center justify-between p-3 rounded-xl bg-slate-100 hover:bg-slate-150 transition-colors text-left"
            >
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-orange-600" />
                <div>
                  <div className="font-bold text-xs text-slate-800">
                    Engine Information & Agent Registry Diagnostics
                  </div>
                  <div className="text-[10px] text-slate-500">
                    Named Specialist Intelligences, Underlying Providers & Gateway Health
                  </div>
                </div>
              </div>
              {isEngineExpanded ? (
                <ChevronUp className="w-4 h-4 text-slate-500" />
              ) : (
                <ChevronDown className="w-4 h-4 text-slate-500" />
              )}
            </button>

            {isEngineExpanded && (
              <div className="mt-3 space-y-2.5 p-3 rounded-xl border border-slate-200 bg-slate-50/70 animate-fadeIn text-xs">
                <p className="text-[10px] text-slate-500 leading-relaxed italic border-b border-slate-200 pb-2">
                  ℹ️ <strong>System Transparency:</strong> CampusConnect specialists utilize verified foundation model adapters with zero-shot institutional RAG and deterministic safety boundaries. No independent fine-tuning or model retraining is claimed.
                </p>

                <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
                  {agentDiagnostics.map((agent) => (
                    <div
                      key={agent.agent_id}
                      className="p-2.5 rounded-lg bg-white border border-slate-200/80 shadow-2xs space-y-1"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-900 text-xs">{agent.agent_name}</span>
                        <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                          {agent.availability ? 'Active Gateway' : 'Offline'}
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-x-2 gap-y-0.5 text-[10px] text-slate-600">
                        <div>
                          <span className="text-slate-400">Provider:</span>{' '}
                          <span className="font-semibold text-slate-700 uppercase">{agent.actual_provider}</span>
                        </div>
                        <div>
                          <span className="text-slate-400">Model ID:</span>{' '}
                          <span className="font-mono text-slate-700">{agent.actual_model_id}</span>
                        </div>
                        <div>
                          <span className="text-slate-400">Mode:</span>{' '}
                          <span className="text-slate-700">{agent.execution_mode}</span>
                        </div>
                        <div>
                          <span className="text-slate-400">Health Check:</span>{' '}
                          <span className="text-emerald-600 font-medium">{agent.last_health_check}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

