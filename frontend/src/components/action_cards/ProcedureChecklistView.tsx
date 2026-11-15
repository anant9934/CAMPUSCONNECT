import React from 'react';
import { ListChecks, FileText, Clock, ExternalLink, ChevronRight } from 'lucide-react';
import { ProcedureChecklist } from '../../types';

interface Props {
  card: ProcedureChecklist;
}

export const ProcedureChecklistView: React.FC<Props> = ({ card }) => {
  const breadcrumbSegments = card.breadcrumb
    ? card.breadcrumb.split('>').map((s) => s.trim()).filter(Boolean)
    : [];

  return (
    <div className="my-4 rounded-xl border border-indigo-200/80 bg-gradient-to-br from-indigo-50/40 via-white to-indigo-50/10 p-4 shadow-sm transition-all hover:shadow">
      <div className="flex items-center justify-between gap-2 border-b border-indigo-100 pb-2.5">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-600 text-white shadow-xs">
            <ListChecks className="h-4 w-4" />
          </div>
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-indigo-700">
              Standard Procedure & Preparation
            </span>
          </div>
        </div>
        <span className="inline-flex items-center gap-1 rounded-full bg-indigo-100/80 px-2 py-0.5 text-[11px] font-medium text-indigo-800">
          Step-by-Step
        </span>
      </div>

      <div className="mt-3">
        <h4 className="text-sm font-semibold text-neutral-900">{card.procedure_name}</h4>
      </div>

      {breadcrumbSegments.length > 0 && (
        <div className="mt-2.5 flex flex-wrap items-center gap-1.5 rounded-lg bg-neutral-100/80 p-2">
          {breadcrumbSegments.map((seg, idx) => (
            <React.Fragment key={idx}>
              <span
                className={`rounded px-2 py-0.5 text-xs font-medium ${
                  idx === breadcrumbSegments.length - 1
                    ? 'bg-indigo-600 text-white shadow-xs font-semibold'
                    : 'bg-white text-neutral-700 border border-neutral-200/80'
                }`}
              >
                {seg}
              </span>
              {idx < breadcrumbSegments.length - 1 && (
                <ChevronRight className="h-3.5 w-3.5 text-neutral-400 shrink-0" />
              )}
            </React.Fragment>
          ))}
        </div>
      )}

      {card.steps && card.steps.length > 0 && (
        <div className="mt-3 rounded-lg border border-neutral-200/70 bg-white p-3">
          <span className="text-xs font-semibold text-neutral-800 block mb-2">
            Execution Steps:
          </span>
          <ol className="space-y-2">
            {card.steps.map((step, idx) => (
              <li key={idx} className="flex items-start gap-2.5 text-xs text-neutral-700">
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-[11px] font-bold text-indigo-700">
                  {idx + 1}
                </span>
                <span className="pt-0.5 leading-relaxed">{step}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {card.required_documents && card.required_documents.length > 0 && (
        <div className="mt-3 flex items-start gap-2 rounded-lg bg-neutral-50 border border-neutral-200/70 p-2.5">
          <FileText className="h-4 w-4 text-neutral-500 mt-0.5 shrink-0" />
          <div>
            <span className="text-xs font-semibold text-neutral-800">Required Documents:</span>
            <div className="mt-1 flex flex-wrap gap-1.5">
              {card.required_documents.map((doc, idx) => (
                <span
                  key={idx}
                  className="rounded-md bg-white border border-neutral-200 px-2 py-0.5 text-[11px] text-neutral-700"
                >
                  {doc}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {card.deadline_or_fees && (
        <div className="mt-3 flex items-start gap-2 rounded-lg bg-amber-50/80 border border-amber-200/70 p-2.5 text-amber-900">
          <Clock className="h-4 w-4 text-amber-600 mt-0.5 shrink-0" />
          <div>
            <span className="text-xs font-semibold text-amber-900">Fees / Timeline Notice:</span>
            <p className="text-[11px] text-amber-800 mt-0.5">{card.deadline_or_fees}</p>
          </div>
        </div>
      )}

      <div className="mt-3.5 flex items-center justify-between pt-2 border-t border-indigo-100/70">
        <span className="text-[11px] text-neutral-500">
          Follow verified procedure in UMS to complete this process.
        </span>
        <a
          href={card.handoff_url || 'https://ums.lpu.in/lpuums/'}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3.5 py-1.5 text-xs font-medium text-white shadow-xs transition-colors hover:bg-indigo-700"
        >
          <span>Open UMS Portal</span>
          <ExternalLink className="h-3.5 w-3.5" />
        </a>
      </div>
    </div>
  );
};

