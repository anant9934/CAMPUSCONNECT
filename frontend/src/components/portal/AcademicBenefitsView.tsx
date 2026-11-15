import React, { useState, useEffect } from 'react';
import {
  Award,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  FileText,
  Clock,
  ArrowRight,
  ShieldCheck,
  ExternalLink,
  Code2,
  HelpCircle,
} from 'lucide-react';
import { api } from '../../services/api';

interface AcademicBenefitsViewProps {
  onAskAI: (query: string) => void;
}

export const AcademicBenefitsView: React.FC<AcademicBenefitsViewProps> = ({ onAskAI }) => {
  const [categories, setCategories] = useState<any[]>([]);
  const [selectedTrack, setSelectedTrack] = useState<string>('CAT-02');
  const [projectText, setProjectText] = useState('');
  const [hasGitHub, setHasGitHub] = useState(false);
  const [hasLiveDemo, setHasLiveDemo] = useState(false);
  const [hasArchDoc, setHasArchDoc] = useState(false);
  const [assessmentResult, setAssessmentResult] = useState<any>(null);
  const [isAssessing, setIsAssessing] = useState(false);

  useEffect(() => {
    loadFramework();
  }, []);

  const loadFramework = async () => {
    try {
      const data = await api.getAcademicBenefits();
      setCategories(data.categories || []);
    } catch (err) {
      console.error('Failed to load academic benefits:', err);
    }
  };

  const handleAssess = async () => {
    if (!projectText.trim()) return;
    try {
      setIsAssessing(true);
      const res = await api.assessBenefit({
        description: projectText,
        has_github: hasGitHub,
        has_live_demo: hasLiveDemo,
        has_architecture_doc: hasArchDoc,
      });
      setAssessmentResult(res);
      setSelectedTrack(res.assessment_card.category_id);
    } catch (err) {
      console.error('Failed to assess project:', err);
    } finally {
      setIsAssessing(false);
    }
  };

  const activeCategory = categories.find((c) => c.category_id === selectedTrack) || categories[1];

  return (
    <div className="flex-1 overflow-y-auto bg-warm-bg p-4 sm:p-6 lg:p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-2xl border border-warm-border p-6 shadow-xs relative overflow-hidden">
          <div className="space-y-2 relative z-10">
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-100 text-amber-800 text-xs font-semibold">
              <Award className="w-3.5 h-3.5 text-amber-700" />
              <span>Division of Academic Affairs</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              EDU-Revolution & Academic Benefits Advisor
            </h1>
            <p className="text-xs sm:text-sm text-slate-600 max-w-3xl leading-relaxed">
              Convert your real-world software platforms, AI applications, hackathon wins, research papers, and startups into academic recognition, Capstone substitution, and Continuous Assessment (CA) exemptions.
            </p>
          </div>
        </div>

        {/* Interactive Eligibility & Readiness Assessment Tool */}
        <div className="bg-white rounded-2xl border border-warm-border p-6 shadow-xs space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-orange-600" />
                Interactive Project Eligibility & Readiness Assessment
              </h2>
              <p className="text-xs text-slate-500">Describe what you built to assess alignment against official LPU policy</p>
            </div>
            <span className="text-xs font-bold text-orange-700 bg-orange-50 px-2.5 py-1 rounded-full border border-orange-200">
              First 4 Weeks of Term
            </span>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Describe your project, achievement, or credential:
              </label>
              <textarea
                rows={3}
                placeholder="e.g. I developed an end-to-end AI disease detection web application using PyTorch, FastAPI, and React with Docker deployment..."
                value={projectText}
                onChange={(e) => setProjectText(e.target.value)}
                className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs sm:text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500"
              />
            </div>

            {/* Evidence Checklist Checkboxes */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <label className="flex items-center gap-2.5 p-3 rounded-xl border border-slate-200 bg-slate-50/60 cursor-pointer hover:bg-white transition-colors">
                <input
                  type="checkbox"
                  checked={hasGitHub}
                  onChange={(e) => setHasGitHub(e.target.checked)}
                  className="rounded text-orange-600 focus:ring-orange-500 w-4 h-4"
                />
                <span className="text-xs text-slate-700 font-medium">Public GitHub Repo</span>
              </label>

              <label className="flex items-center gap-2.5 p-3 rounded-xl border border-slate-200 bg-slate-50/60 cursor-pointer hover:bg-white transition-colors">
                <input
                  type="checkbox"
                  checked={hasLiveDemo}
                  onChange={(e) => setHasLiveDemo(e.target.checked)}
                  className="rounded text-orange-600 focus:ring-orange-500 w-4 h-4"
                />
                <span className="text-xs text-slate-700 font-medium">Live Demo / Working Video</span>
              </label>

              <label className="flex items-center gap-2.5 p-3 rounded-xl border border-slate-200 bg-slate-50/60 cursor-pointer hover:bg-white transition-colors">
                <input
                  type="checkbox"
                  checked={hasArchDoc}
                  onChange={(e) => setHasArchDoc(e.target.checked)}
                  className="rounded text-orange-600 focus:ring-orange-500 w-4 h-4"
                />
                <span className="text-xs text-slate-700 font-medium">Architecture Spec (PDF)</span>
              </label>
            </div>

            <div className="flex justify-end">
              <button
                onClick={handleAssess}
                disabled={isAssessing || !projectText.trim()}
                className="px-5 py-2.5 bg-orange-600 hover:bg-orange-700 disabled:opacity-50 text-white rounded-xl text-xs sm:text-sm font-semibold shadow-xs flex items-center gap-2 transition-all"
              >
                {isAssessing ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Evaluating Against LPU Policy...</span>
                  </>
                ) : (
                  <>
                    <Award className="w-4 h-4" />
                    <span>Evaluate Project Eligibility</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Assessment Output Display */}
          {assessmentResult && (
            <div className="mt-6 pt-5 border-t border-slate-100 space-y-4 animate-in fade-in duration-300">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl bg-orange-50/60 border border-orange-200/80">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-orange-800 bg-orange-100 px-2 py-0.5 rounded">
                    Preliminary Alignment
                  </span>
                  <h3 className="text-base font-extrabold text-slate-900 mt-1">
                    {assessmentResult.assessment_card.category_id}: {assessmentResult.assessment_card.category_name}
                  </h3>
                  <p className="text-xs text-slate-600 mt-0.5">
                    Stage: <span className="font-semibold text-slate-800">{assessmentResult.assessment_card.portal_stage_name}</span>
                  </p>
                </div>

                <div className="text-right">
                  <div className="text-2xl font-black text-orange-700">{assessmentResult.readiness_score}%</div>
                  <div className="text-[11px] text-slate-500 font-medium">Documentation Readiness</div>
                </div>
              </div>

              {/* Potential Benefits */}
              <div className="p-4 rounded-xl bg-white border border-slate-200 text-xs space-y-1.5">
                <h4 className="font-bold text-slate-800 flex items-center gap-1.5">
                  <Award className="w-4 h-4 text-emerald-600" />
                  Potential Eligible Academic Benefits:
                </h4>
                <p className="text-slate-700 leading-relaxed font-medium">
                  {assessmentResult.assessment_card.eligible_academic_benefits}
                </p>
              </div>

              {/* Missing Evidence Warning */}
              {assessmentResult.updated_missing_evidence?.length > 0 && (
                <div className="p-4 rounded-xl bg-amber-50/70 border border-amber-200 text-xs space-y-2">
                  <h4 className="font-bold text-amber-900 flex items-center gap-1.5">
                    <AlertCircle className="w-4 h-4 text-amber-600" />
                    Missing Evidence Required for Final Approval:
                  </h4>
                  <ul className="list-disc list-inside space-y-1 text-amber-800">
                    {assessmentResult.updated_missing_evidence.map((item: string, i: number) => (
                      <li key={i}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Statutory Next Steps */}
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-2">
                <h4 className="font-bold text-slate-800">Statutory Application Workflow:</h4>
                <ol className="list-decimal list-inside space-y-1 text-slate-600">
                  {assessmentResult.next_steps?.map((step: string, i: number) => (
                    <li key={i}>{step}</li>
                  ))}
                </ol>
              </div>

              {/* Policy Disclaimer */}
              <div className="p-3 rounded-xl bg-slate-100 text-[11px] text-slate-500 italic space-y-1">
                <p>⚠️ {assessmentResult.assessment_card.guarantee_disclaimer}</p>
                <p>🔒 {assessmentResult.assessment_card.scrgm_distinction}</p>
              </div>
            </div>
          )}
        </div>

        {/* Explore All 9 Official Tracks */}
        <div className="bg-white rounded-2xl border border-warm-border p-6 shadow-xs space-y-5">
          <div>
            <h2 className="text-base font-bold text-slate-900">Explore All 9 Official EDU-Revolution Tracks</h2>
            <p className="text-xs text-slate-500">Based on LPU Academic Benefits Guidelines (Division of Academic Affairs)</p>
          </div>

          {/* Track selector tabs */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar">
            {categories.map((cat) => (
              <button
                key={cat.category_id}
                onClick={() => setSelectedTrack(cat.category_id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors ${
                  selectedTrack === cat.category_id
                    ? 'bg-orange-600 text-white shadow-xs'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200/80 hover:text-slate-900'
                }`}
              >
                {cat.category_id}: {cat.category_name}
              </button>
            ))}
          </div>

          {/* Active Track Details */}
          {activeCategory && (
            <div className="p-5 rounded-2xl bg-slate-50/80 border border-slate-200 space-y-4 text-xs">
              <div>
                <h3 className="text-base font-bold text-slate-900">
                  {activeCategory.category_id}: {activeCategory.category_name}
                </h3>
                <p className="text-xs text-slate-600 mt-1">{activeCategory.output_criteria}</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-3.5 rounded-xl bg-white border border-slate-200 space-y-1">
                  <span className="font-bold text-slate-800 block">Eligible Academic Benefits</span>
                  <p className="text-slate-600">{activeCategory.eligible_academic_benefits || activeCategory.potential_eligible_benefits}</p>
                </div>

                <div className="p-3.5 rounded-xl bg-white border border-slate-200 space-y-1">
                  <span className="font-bold text-slate-800 block">Required Evidence</span>
                  <p className="text-slate-600">{activeCategory.required_evidence}</p>
                </div>

                <div className="p-3.5 rounded-xl bg-white border border-slate-200 space-y-1">
                  <span className="font-bold text-slate-800 block">Submission Window</span>
                  <p className="text-slate-600">{activeCategory.course_mapping_window}</p>
                </div>

                <div className="p-3.5 rounded-xl bg-white border border-slate-200 space-y-1">
                  <span className="font-bold text-slate-800 block">Physical Helpdesk</span>
                  <p className="text-orange-700 font-semibold">{activeCategory.support_location}</p>
                </div>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-slate-200">
                <span className="text-[11px] text-slate-500">
                  Online Route: <span className="font-mono text-slate-700">{activeCategory.submission_channel}</span>
                </span>

                <button
                  onClick={() => onAskAI(`What are the exact eligibility criteria and benefits for ${activeCategory.category_name} (${activeCategory.category_id}) under LPU EDU-Revolution?`)}
                  className="text-xs text-orange-600 hover:text-orange-700 font-semibold flex items-center gap-1"
                >
                  Ask AI About This Track <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
