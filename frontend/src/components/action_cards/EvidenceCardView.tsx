import React from 'react';
import { ShieldCheck, FileCheck, AlertTriangle, Calendar } from 'lucide-react';
import { EvidenceCard } from '../../types';

interface EvidenceCardViewProps {
  card: EvidenceCard;
}

export const EvidenceCardView: React.FC<EvidenceCardViewProps> = ({ card }) => {
  return (
    <div className="mt-3 overflow-hidden rounded-xl border border-slate-200 bg-white p-3.5 shadow-2xs">
      <div className="flex items-center justify-between border-b border-slate-100 pb-2">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-emerald-600" />
          <span className="text-xs font-semibold text-slate-800">{card.source_title}</span>
        </div>
        <div className="flex items-center gap-1.5">
          {card.evidence_status && (
            <span className="text-[9px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200 px-1.5 py-0.5 rounded uppercase">
              {card.evidence_status.replace(/_/g, ' ')}
            </span>
          )}
          <span className="text-[10px] font-medium bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">
            {card.source_type}
          </span>
        </div>
      </div>

      <div className="mt-2.5 grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-slate-600">
        {card.document_name && (
          <div className="flex items-center gap-1.5">
            <FileCheck className="h-3.5 w-3.5 text-slate-400" />
            <span>Document: <strong className="text-slate-800">{card.document_name}</strong></span>
          </div>
        )}

        {card.clause_or_page && (
          <div>
            <span>Reference: <strong className="text-slate-800">{card.clause_or_page}</strong></span>
          </div>
        )}
      </div>

      <div className="mt-2 flex items-center gap-1.5 text-[11px] text-slate-400">
        <Calendar className="h-3 w-3" />
        <span>Verified on: {card.verification_date}</span>
      </div>

      {card.revalidation_advisory && (
        <div className="mt-2.5 rounded-lg bg-amber-50 border border-amber-200/80 p-2 text-xs text-amber-800 flex items-start gap-1.5">
          <AlertTriangle className="h-4 w-4 text-amber-600 shrink-0 mt-0.5" />
          <p>{card.revalidation_advisory}</p>
        </div>
      )}
    </div>
  );
};

