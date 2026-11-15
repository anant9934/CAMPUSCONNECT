import React from 'react';
import { CalendarCheck, CheckCircle2, AlertCircle, ExternalLink, ChevronRight } from 'lucide-react';
import { BookingCard } from '../../types';

interface Props {
  card: BookingCard;
}

export const BookingCardView: React.FC<Props> = ({ card }) => {
  const breadcrumbSegments = card.breadcrumb
    ? card.breadcrumb.split('>').map((s) => s.trim()).filter(Boolean)
    : [];

  return (
    <div className="my-4 rounded-xl border border-emerald-200/80 bg-gradient-to-br from-emerald-50/40 via-white to-emerald-50/10 p-4 shadow-sm transition-all hover:shadow">
      <div className="flex items-center justify-between gap-2 border-b border-emerald-100 pb-2.5">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-600 text-white shadow-xs">
            <CalendarCheck className="h-4 w-4" />
          </div>
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-emerald-700">
              Guided Booking Assistance
            </span>
            <span className="mx-2 text-xs text-neutral-300">•</span>
            <span className="text-xs font-medium text-neutral-600">{card.booking_type}</span>
          </div>
        </div>
        <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100/80 px-2 py-0.5 text-[11px] font-medium text-emerald-800">
          Booking Handoff
        </span>
      </div>

      <div className="mt-3">
        <h4 className="text-sm font-semibold text-neutral-900">{card.service_title}</h4>
      </div>

      {breadcrumbSegments.length > 0 && (
        <div className="mt-2.5 flex flex-wrap items-center gap-1.5 rounded-lg bg-neutral-100/80 p-2">
          {breadcrumbSegments.map((seg, idx) => (
            <React.Fragment key={idx}>
              <span
                className={`rounded px-2 py-0.5 text-xs font-medium ${
                  idx === breadcrumbSegments.length - 1
                    ? 'bg-emerald-600 text-white shadow-xs font-semibold'
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

      {card.prerequisites && card.prerequisites.length > 0 && (
        <div className="mt-3 rounded-lg border border-neutral-200/70 bg-white p-3">
          <span className="text-xs font-semibold text-neutral-800 block mb-1.5">
            Prerequisites & Required Information:
          </span>
          <ul className="space-y-1.5">
            {card.prerequisites.map((req, idx) => (
              <li key={idx} className="flex items-start gap-2 text-xs text-neutral-600">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 mt-0.5 shrink-0" />
                <span>{req}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {card.availability_caveat && (
        <div className="mt-3 flex items-start gap-2 rounded-lg bg-amber-50/80 border border-amber-200/70 p-2.5 text-amber-900">
          <AlertCircle className="h-3.5 w-3.5 text-amber-600 mt-0.5 shrink-0" />
          <p className="text-[11px] leading-relaxed text-amber-800">
            {card.availability_caveat}
          </p>
        </div>
      )}

      <div className="mt-3.5 flex items-center justify-between pt-2 border-t border-emerald-100/70">
        <span className="text-[11px] text-neutral-500">
          Complete your booking securely inside authenticated UMS.
        </span>
        <a
          href={card.handoff_url || 'https://ums.lpu.in/lpuums/'}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 px-3.5 py-1.5 text-xs font-medium text-white shadow-xs transition-colors hover:bg-emerald-700"
        >
          <span>{card.button_label || 'Continue to UMS Booking'}</span>
          <ExternalLink className="h-3.5 w-3.5" />
        </a>
      </div>
    </div>
  );
};

