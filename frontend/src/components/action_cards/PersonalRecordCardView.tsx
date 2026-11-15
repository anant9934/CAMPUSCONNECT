import React from 'react';
import { Lock, ShieldCheck, ExternalLink, ChevronRight, AlertTriangle } from 'lucide-react';
import { PersonalRecordCard } from '../../types';

interface Props {
  card: PersonalRecordCard;
}

export const PersonalRecordCardView: React.FC<Props> = ({ card }) => {
  const breadcrumbSegments = card.breadcrumb
    ? card.breadcrumb.split('>').map((s) => s.trim()).filter(Boolean)
    : [];

  return (
    <div className="my-4 rounded-xl border border-amber-200/90 bg-gradient-to-br from-amber-50/50 via-white to-amber-50/20 p-4 shadow-sm transition-all hover:shadow">
      <div className="flex items-center justify-between gap-2 border-b border-amber-100 pb-2.5">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-amber-600 text-white shadow-xs">
            <Lock className="h-4 w-4" />
          </div>
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-amber-800">
              Private Student Record Boundary
            </span>
            <span className="mx-2 text-xs text-neutral-300">•</span>
            <span className="text-xs font-medium text-neutral-600">{card.record_type}</span>
          </div>
        </div>
        <span className="inline-flex items-center gap-1 rounded-full bg-amber-100/80 px-2 py-0.5 text-[11px] font-medium text-amber-900">
          Auth Required
        </span>
      </div>

      <div className="mt-3">
        <h4 className="text-sm font-semibold text-neutral-900">{card.title}</h4>
      </div>

      <div className="mt-2.5 flex items-start gap-2 rounded-lg bg-amber-50/80 border border-amber-200/70 p-2.5 text-amber-900">
        <AlertTriangle className="h-4 w-4 text-amber-600 mt-0.5 shrink-0" />
        <p className="text-xs leading-relaxed text-amber-800">
          {card.boundary_explanation ||
            'This record belongs to your private student profile and requires authenticated UMS credentials. CampusConnect is a public campus assistant and never accesses private student records.'}
        </p>
      </div>

      {breadcrumbSegments.length > 0 && (
        <div className="mt-3">
          <span className="text-xs font-semibold text-neutral-800 block mb-1">
            Where to find this in your UMS account:
          </span>
          <div className="flex flex-wrap items-center gap-1.5 rounded-lg bg-neutral-100/80 p-2">
            {breadcrumbSegments.map((seg, idx) => (
              <React.Fragment key={idx}>
                <span
                  className={`rounded px-2 py-0.5 text-xs font-medium ${
                    idx === breadcrumbSegments.length - 1
                      ? 'bg-amber-600 text-white shadow-xs font-semibold'
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
        </div>
      )}

      <div className="mt-3.5 flex items-center justify-between pt-2 border-t border-amber-100/70">
        <span className="text-[11px] text-neutral-500">
          Never share your UMS password or OTP with anyone.
        </span>
        <a
          href={card.handoff_url || 'https://ums.lpu.in/lpuums/'}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 rounded-lg bg-amber-600 px-3.5 py-1.5 text-xs font-medium text-white shadow-xs transition-colors hover:bg-amber-700"
        >
          <span>Sign In to UMS</span>
          <ExternalLink className="h-3.5 w-3.5" />
        </a>
      </div>
    </div>
  );
};

