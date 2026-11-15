import React, { useState } from 'react';
import { Users, MapPin, Compass, FileText, ChevronRight, CheckCircle2, Copy, Check, AlertTriangle } from 'lucide-react';
import { WhoToMeetCard } from '../../types';

interface WhoToMeetCardViewProps {
  card: WhoToMeetCard;
}

export const WhoToMeetCardView: React.FC<WhoToMeetCardViewProps> = ({ card }) => {
  const [copied, setCopied] = useState(false);

  const handleCopyPath = () => {
    navigator.clipboard.writeText(card.ums_navigation_path);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="mt-3 overflow-hidden rounded-xl border border-indigo-100 bg-gradient-to-br from-indigo-50/30 via-white to-slate-50/50 p-4 shadow-sm transition-all hover:shadow-md">
      {/* Header */}
      <div className="flex items-start justify-between gap-2 border-b border-indigo-100/60 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-sm">
            <Users className="h-5 w-5" />
          </div>
          <div>
            <h4 className="font-semibold text-slate-900 text-sm">
              {card.category_title}
            </h4>
            <p className="text-xs font-medium text-indigo-700 mt-0.5">
              First Point of Contact: <strong className="text-slate-900">{card.primary_contact_role}</strong>
              {card.named_contact_person && (
                <span className="block text-[11px] text-slate-600 font-normal mt-0.5">
                  Designated Official: <strong className="text-slate-800">{card.named_contact_person}</strong>
                </span>
              )}
            </p>
          </div>
        </div>

        <div className="inline-flex items-center gap-1 rounded-full bg-indigo-100 px-2 py-0.5 text-[10px] font-semibold text-indigo-800 border border-indigo-200">
          <CheckCircle2 className="h-3 w-3 text-indigo-600" />
          <span>Issue Routing</span>
        </div>
      </div>

      {/* Office & Room Location */}
      <div className="mt-3 flex items-start gap-2 bg-indigo-50/40 p-2.5 rounded-lg border border-indigo-100/80 text-xs text-slate-700">
        <MapPin className="h-4 w-4 text-indigo-600 shrink-0 mt-0.5" />
        <div>
          <span className="font-medium text-slate-500">In-Person Office:</span>
          <span className="block font-semibold text-slate-800 mt-0.5">
            {card.office_location} — {card.room_details}
          </span>
        </div>
      </div>

      {/* UMS Online Path */}
      <div className="mt-2.5 flex items-center justify-between gap-2 bg-slate-50 p-2 rounded-lg border border-slate-200/80 text-xs">
        <div className="flex items-center gap-2 min-w-0">
          <Compass className="h-4 w-4 text-slate-500 shrink-0" />
          <span className="font-mono text-slate-700 truncate">{card.ums_navigation_path}</span>
        </div>
        <button
          onClick={handleCopyPath}
          className="shrink-0 p-1 rounded hover:bg-slate-200 text-slate-600 transition-colors"
          title="Copy UMS Breadcrumb"
        >
          {copied ? <Check className="h-3.5 w-3.5 text-emerald-600" /> : <Copy className="h-3.5 w-3.5" />}
        </button>
      </div>

      {/* Prerequisite Action */}
      <div className="mt-3 p-2.5 rounded-lg bg-amber-50/50 border border-amber-200/60 text-xs text-amber-900">
        <div className="font-semibold flex items-center gap-1.5 mb-1 text-amber-800">
          <CheckCircle2 className="h-3.5 w-3.5 text-amber-600" />
          <span>Prerequisite (Do this first before escalating):</span>
        </div>
        <p className="leading-relaxed text-slate-700">{card.prerequisite_action}</p>
      </div>

      {/* Required Documents */}
      {card.required_documents && card.required_documents.length > 0 && (
        <div className="mt-3">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-700 mb-1.5">
            <FileText className="h-3.5 w-3.5 text-indigo-600" />
            <span>Documents to Bring / Upload:</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {card.required_documents.map((doc, idx) => (
              <span
                key={idx}
                className="rounded-md bg-white border border-slate-200 px-2 py-0.5 text-xs text-slate-600 shadow-2xs"
              >
                {doc}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Escalation Ladder */}
      {card.escalation_ladder && card.escalation_ladder.length > 0 && (
        <div className="mt-3 pt-3 border-t border-indigo-100/60">
          <span className="text-[11px] font-semibold text-slate-500 block mb-1.5 uppercase tracking-wider">
            Escalation Ladder
          </span>
          <div className="flex items-center flex-wrap gap-1 text-xs text-slate-600">
            {card.escalation_ladder.map((step, idx) => (
              <React.Fragment key={idx}>
                <span className={`px-2 py-0.5 rounded-md text-[11px] font-medium ${
                  idx === 0 
                    ? 'bg-indigo-100 text-indigo-800 border border-indigo-200' 
                    : 'bg-slate-100 text-slate-700 border border-slate-200'
                }`}>
                  {step}
                </span>
                {idx < card.escalation_ladder.length - 1 && (
                  <ChevronRight className="h-3.5 w-3.5 text-slate-400 shrink-0" />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>
      )}

      {/* Revalidation Notice */}
      {card.revalidation_notice && (
        <div className="mt-3 rounded-lg bg-amber-50 border border-amber-200 p-2 text-xs text-amber-800 flex items-start gap-2">
          <AlertTriangle className="h-4 w-4 text-amber-600 shrink-0 mt-0.5" />
          <p>{card.revalidation_notice}</p>
        </div>
      )}
    </div>
  );
};

