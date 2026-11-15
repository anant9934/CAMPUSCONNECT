import React from 'react';
import { Award, CheckCircle2, AlertOctagon, ExternalLink, MapPin, Compass, ShieldAlert } from 'lucide-react';
import { AcademicBenefitAssessmentCard } from '../../types';

interface BenefitAssessmentCardViewProps {
  card: AcademicBenefitAssessmentCard;
}

export const BenefitAssessmentCardView: React.FC<BenefitAssessmentCardViewProps> = ({ card }) => {
  return (
    <div className="mt-3 overflow-hidden rounded-xl border border-purple-100 bg-gradient-to-br from-purple-50/40 via-white to-indigo-50/30 p-4 shadow-sm transition-all hover:shadow-md">
      {/* Header */}
      <div className="flex items-start justify-between gap-2 border-b border-purple-100/60 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-600 text-white shadow-sm">
            <Award className="h-5 w-5" />
          </div>
          <div>
            <span className="text-[11px] font-bold text-purple-700 uppercase tracking-wider block">
              EDU-Revolution Category {card.category_id}
            </span>
            <h4 className="font-semibold text-slate-900 text-sm">
              {card.category_name}
            </h4>
          </div>
        </div>

        <div className="flex flex-col items-end gap-1">
          <div className="inline-flex items-center gap-1 rounded-full bg-purple-100 px-2 py-0.5 text-[10px] font-semibold text-purple-800 border border-purple-200">
            <CheckCircle2 className="h-3 w-3 text-purple-600" />
            <span>Potential Eligibility</span>
          </div>
          {card.portal_stage_name && (
            <span className="text-[10px] text-purple-700 font-medium">
              Stage: {card.portal_stage_name}
            </span>
          )}
        </div>
      </div>

      {/* Eligibility vs Approval Alert */}
      {card.eligibility_vs_approval_notice && (
        <div className="mt-2.5 rounded-lg border border-purple-200 bg-purple-50/70 p-2 text-xs text-purple-900 flex items-start gap-2">
          <AlertOctagon className="h-4 w-4 text-purple-600 shrink-0 mt-0.5" />
          <p className="text-[11px] leading-relaxed font-medium">{card.eligibility_vs_approval_notice}</p>
        </div>
      )}

      {/* Matched Criteria */}
      <div className="mt-3 text-xs text-slate-600 bg-slate-50/80 p-2.5 rounded-lg border border-slate-100">
        <span className="font-semibold text-slate-800 block mb-0.5">Assessed Output Criteria:</span>
        <p>{card.matched_criteria}</p>
        {card.course_mapping_window && (
          <p className="mt-1 text-[11px] text-slate-500 font-medium">
            Course Mapping Window: <strong className="text-slate-700">{card.course_mapping_window}</strong>
          </p>
        )}
      </div>

      {/* Eligible Recognition */}
      <div className="mt-2.5 text-xs text-purple-900 bg-purple-50/50 p-2.5 rounded-lg border border-purple-100">
        <span className="font-semibold text-purple-800 block mb-0.5">Potential Academic Recognition:</span>
        <p className="leading-relaxed">{card.eligible_academic_benefits}</p>
      </div>

      {/* Evidence Checklist */}
      <div className="mt-3">
        <span className="text-xs font-semibold text-slate-800 block mb-1.5 flex items-center gap-1.5">
          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
          <span>Required Evidence Checklist:</span>
        </span>
        <div className="space-y-1">
          {card.evidence_checklist.map((item, idx) => (
            <div key={idx} className="flex items-start gap-2 text-xs text-slate-700 bg-white p-1.5 rounded border border-slate-100 shadow-2xs">
              <span className="inline-block h-1.5 w-1.5 rounded-full bg-purple-500 mt-1.5 shrink-0" />
              <span>{item}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Missing Evidence Alert if identified */}
      {card.missing_evidence && card.missing_evidence.length > 0 && (
        <div className="mt-2.5 rounded-lg border border-amber-200 bg-amber-50/70 p-2 text-xs text-amber-900">
          <span className="font-semibold text-amber-800 block mb-1">
            ⚠️ Missing Evidence Identified for Submission:
          </span>
          <div className="space-y-1">
            {card.missing_evidence.map((m, idx) => (
              <div key={idx} className="flex items-start gap-1.5 text-[11px] text-amber-800">
                <span className="text-amber-600 font-bold">•</span>
                <span>{m}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Submission Channels */}
      <div className="mt-3 pt-3 border-t border-purple-100/60 grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
        <div className="flex items-start gap-2 p-2 rounded-lg bg-indigo-50/50 border border-indigo-100 text-indigo-950">
          <Compass className="h-4 w-4 text-indigo-600 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold block text-[11px] text-indigo-800">Online Submission:</span>
            <span className="font-mono text-[11px] text-slate-700">{card.submission_route}</span>
          </div>
        </div>

        <div className="flex items-start gap-2 p-2 rounded-lg bg-slate-50 border border-slate-200 text-slate-800">
          <MapPin className="h-4 w-4 text-purple-600 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold block text-[11px] text-slate-600">Guidance Desk:</span>
            <span className="font-medium text-[11px] text-slate-900">{card.physical_helpdesk}</span>
          </div>
        </div>
      </div>

      {/* Disclaimers & SCRGM Distinction */}
      <div className="mt-3 p-2.5 rounded-lg bg-amber-50/70 border border-amber-200/80 text-[11px] text-amber-900 space-y-1">
        <div className="flex items-center gap-1.5 font-semibold text-amber-800">
          <ShieldAlert className="h-3.5 w-3.5 text-amber-600 shrink-0" />
          <span>Mandatory University Guidelines:</span>
        </div>
        <p className="text-slate-600 leading-relaxed">• {card.guarantee_disclaimer}</p>
        <p className="text-slate-600 leading-relaxed">• {card.scrgm_distinction}</p>
      </div>

      {/* Action Button */}
      <div className="mt-3 flex justify-end">
        <a
          href="https://ums.lpu.in/lpuums/"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 rounded-lg bg-purple-600 px-3 py-1.5 text-xs font-medium text-white shadow-sm hover:bg-purple-700 transition-colors"
        >
          <span>Open UMS RMS Module</span>
          <ExternalLink className="h-3.5 w-3.5" />
        </a>
      </div>
    </div>
  );
};

