import React from 'react';
import { LifeBuoy, ShieldAlert, ArrowRight, ExternalLink, ChevronRight, CheckCircle2 } from 'lucide-react';
import { RMSCard } from '../../types';

interface Props {
  card: RMSCard;
}

export const RMSCardView: React.FC<Props> = ({ card }) => {
  const subSegments = card.submission_path
    ? card.submission_path.split('>').map((s) => s.trim()).filter(Boolean)
    : [];

  const trackSegments = card.tracking_path
    ? card.tracking_path.split('>').map((s) => s.trim()).filter(Boolean)
    : [];

  return (
    <div className="my-4 rounded-xl border border-rose-200/80 bg-gradient-to-br from-rose-50/40 via-white to-rose-50/10 p-4 shadow-sm transition-all hover:shadow">
      <div className="flex items-center justify-between gap-2 border-b border-rose-100 pb-2.5">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-rose-600 text-white shadow-xs">
            <LifeBuoy className="h-4 w-4" />
          </div>
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-rose-700">
              LPU Grievance Redressal (RMS)
            </span>
          </div>
        </div>
        <span className="inline-flex items-center gap-1 rounded-full bg-rose-100/80 px-2 py-0.5 text-[11px] font-medium text-rose-800">
          Official Support
        </span>
      </div>

      <div className="mt-3">
        <h4 className="text-sm font-semibold text-neutral-900">{card.title}</h4>
      </div>

      {/* Submission Path */}
      <div className="mt-3">
        <span className="text-xs font-semibold text-neutral-800 block mb-1">
          Submission Path in UMS:
        </span>
        <div className="flex flex-wrap items-center gap-1.5 rounded-lg bg-neutral-100/80 p-2">
          {subSegments.map((seg, idx) => (
            <React.Fragment key={idx}>
              <span
                className={`rounded px-2 py-0.5 text-xs font-medium ${
                  idx === subSegments.length - 1
                    ? 'bg-rose-600 text-white shadow-xs font-semibold'
                    : 'bg-white text-neutral-700 border border-neutral-200/80'
                }`}
              >
                {seg}
              </span>
              {idx < subSegments.length - 1 && (
                <ChevronRight className="h-3.5 w-3.5 text-neutral-400 shrink-0" />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* 5-Stage Hierarchy */}
      {card.stages && card.stages.length > 0 && (
        <div className="mt-3 rounded-lg border border-neutral-200/70 bg-white p-3">
          <span className="text-xs font-semibold text-neutral-800 block mb-2">
            5-Stage Submission Hierarchy:
          </span>
          <div className="space-y-1.5">
            {card.stages.map((stage, idx) => (
              <div key={idx} className="flex items-start gap-2 text-xs text-neutral-700">
                <span className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-rose-100 text-[10px] font-bold text-rose-700 mt-0.5">
                  {idx + 1}
                </span>
                <span>{stage}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tracking Path */}
      {trackSegments.length > 0 && (
        <div className="mt-3">
          <span className="text-xs font-semibold text-neutral-800 block mb-1">
            Tracking Existing Request Status:
          </span>
          <div className="flex flex-wrap items-center gap-1.5 rounded-lg bg-neutral-100/80 p-2">
            {trackSegments.map((seg, idx) => (
              <React.Fragment key={idx}>
                <span
                  className={`rounded px-2 py-0.5 text-xs font-medium ${
                    idx === trackSegments.length - 1
                      ? 'bg-neutral-800 text-white shadow-xs font-semibold'
                      : 'bg-white text-neutral-700 border border-neutral-200/80'
                  }`}
                >
                  {seg}
                </span>
                {idx < trackSegments.length - 1 && (
                  <ChevronRight className="h-3.5 w-3.5 text-neutral-400 shrink-0" />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>
      )}

      {/* Confidentiality Warning */}
      <div className="mt-3 flex items-start gap-2 rounded-lg bg-rose-50 border border-rose-200/70 p-2.5 text-rose-900">
        <ShieldAlert className="h-4 w-4 text-rose-600 mt-0.5 shrink-0" />
        <p className="text-[11px] leading-relaxed text-rose-800">
          {card.privacy_notice ||
            'For your confidentiality and security, do not enter sensitive grievance text in this public chatbot. Submit directly inside authenticated UMS.'}
        </p>
      </div>

      <div className="mt-3.5 flex items-center justify-between pt-2 border-t border-rose-100/70">
        <span className="text-[11px] text-neutral-500">
          Log complaints or track ticket resolution in UMS.
        </span>
        <a
          href={card.handoff_url || 'https://ums.lpu.in/lpuums/'}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 rounded-lg bg-rose-600 px-3.5 py-1.5 text-xs font-medium text-white shadow-xs transition-colors hover:bg-rose-700"
        >
          <span>Open RMS in UMS</span>
          <ExternalLink className="h-3.5 w-3.5" />
        </a>
      </div>
    </div>
  );
};

