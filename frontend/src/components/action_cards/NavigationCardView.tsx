import React from 'react';
import { Compass, ExternalLink, ChevronRight, ShieldCheck } from 'lucide-react';
import { NavigationCard } from '../../types';

interface Props {
  card: NavigationCard;
}

export const NavigationCardView: React.FC<Props> = ({ card }) => {
  const breadcrumbSegments = card.breadcrumb
    ? card.breadcrumb.split('>').map((s) => s.trim()).filter(Boolean)
    : [];

  return (
    <div className="my-4 rounded-xl border border-blue-100 bg-gradient-to-br from-blue-50/50 via-white to-blue-50/20 p-4 shadow-sm transition-all hover:shadow">
      <div className="flex items-center justify-between gap-2 border-b border-blue-100/70 pb-2.5">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-600 text-white shadow-xs">
            <Compass className="h-4 w-4" />
          </div>
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-blue-700">
              UMS Navigation Path
            </span>
            <span className="mx-2 text-xs text-neutral-300">•</span>
            <span className="text-xs font-medium text-neutral-600">{card.module}</span>
          </div>
        </div>
        <span className="inline-flex items-center gap-1 rounded-full bg-blue-100/70 px-2 py-0.5 text-[11px] font-medium text-blue-800">
          <ShieldCheck className="h-3 w-3" />
          Verified UMS Module
        </span>
      </div>

      <div className="mt-3">
        <h4 className="text-sm font-semibold text-neutral-900">{card.service_title}</h4>
        {card.instruction && (
          <p className="mt-1 text-xs text-neutral-600 leading-relaxed">{card.instruction}</p>
        )}
      </div>

      {breadcrumbSegments.length > 0 && (
        <div className="mt-3 flex flex-wrap items-center gap-1.5 rounded-lg bg-neutral-100/80 p-2.5">
          {breadcrumbSegments.map((seg, idx) => (
            <React.Fragment key={idx}>
              <span
                className={`rounded px-2 py-0.5 text-xs font-medium ${
                  idx === breadcrumbSegments.length - 1
                    ? 'bg-blue-600 text-white shadow-xs font-semibold'
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

      <div className="mt-3.5 flex items-center justify-between pt-2 border-t border-blue-100/50">
        <span className="text-[11px] text-neutral-500">
          Sign in to LPU UMS to access this service directly.
        </span>
        <a
          href={card.handoff_url || 'https://ums.lpu.in/lpuums/'}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 rounded-lg bg-blue-600 px-3.5 py-1.5 text-xs font-medium text-white shadow-xs transition-colors hover:bg-blue-700"
        >
          <span>{card.button_label || 'Open Official UMS'}</span>
          <ExternalLink className="h-3.5 w-3.5" />
        </a>
      </div>
    </div>
  );
};

