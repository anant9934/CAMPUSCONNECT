import React from 'react';
import { MapPin, Clock, Accessibility, ExternalLink, Building2, Tag } from 'lucide-react';
import { CampusPlaceCard } from '../../types';

interface Props {
  card: CampusPlaceCard;
}

export const CampusPlaceCardView: React.FC<Props> = ({ card }) => {
  return (
    <div className="my-4 rounded-xl border border-sky-200/80 bg-gradient-to-br from-sky-50/40 via-white to-sky-50/10 p-4 shadow-sm transition-all hover:shadow">
      <div className="flex items-center justify-between gap-2 border-b border-sky-100 pb-2.5">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-sky-600 text-white shadow-xs">
            <MapPin className="h-4 w-4" />
          </div>
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-sky-700">
              Campus Wayfinding & Location
            </span>
            <span className="mx-2 text-xs text-neutral-300">•</span>
            <span className="text-xs font-medium text-neutral-600">{card.building}</span>
          </div>
        </div>
        <span className="inline-flex items-center gap-1 rounded-full bg-sky-100/80 px-2 py-0.5 text-[11px] font-medium text-sky-800">
          Verified Location
        </span>
      </div>

      <div className="mt-3">
        <h4 className="text-sm font-semibold text-neutral-900">{card.name}</h4>
        <p className="mt-1 text-xs text-neutral-600 leading-relaxed">{card.description}</p>
      </div>

      <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
        {card.floor_room && (
          <div className="flex items-center gap-2 rounded-lg bg-neutral-50 p-2 border border-neutral-200/70">
            <Building2 className="h-3.5 w-3.5 text-neutral-500 shrink-0" />
            <span className="text-neutral-700">{card.floor_room}</span>
          </div>
        )}
        {card.opening_hours && (
          <div className="flex items-center gap-2 rounded-lg bg-neutral-50 p-2 border border-neutral-200/70">
            <Clock className="h-3.5 w-3.5 text-neutral-500 shrink-0" />
            <span className="text-neutral-700">{card.opening_hours}</span>
          </div>
        )}
        {card.accessibility && (
          <div className="flex items-center gap-2 rounded-lg bg-neutral-50 p-2 border border-neutral-200/70 sm:col-span-2">
            <Accessibility className="h-3.5 w-3.5 text-sky-600 shrink-0" />
            <span className="text-neutral-700">{card.accessibility}</span>
          </div>
        )}
      </div>

      {card.services && card.services.length > 0 && (
        <div className="mt-3">
          <span className="text-xs font-semibold text-neutral-800 block mb-1.5">
            Key Services at this Location:
          </span>
          <div className="flex flex-wrap gap-1.5">
            {card.services.map((svc, idx) => (
              <span
                key={idx}
                className="inline-flex items-center gap-1 rounded-md bg-sky-50 border border-sky-100 px-2 py-0.5 text-[11px] text-sky-800 font-medium"
              >
                <Tag className="h-2.5 w-2.5 text-sky-500" />
                {svc}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="mt-3.5 flex items-center justify-between pt-2 border-t border-sky-100/70">
        <span className="text-[11px] text-neutral-500">
          Find your way around the 600+ acre campus.
        </span>
        <a
          href={card.map_url || 'https://www.lpu.in/about_lpu/campus-tour.php'}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 rounded-lg bg-sky-600 px-3.5 py-1.5 text-xs font-medium text-white shadow-xs transition-colors hover:bg-sky-700"
        >
          <span>View Campus Map</span>
          <ExternalLink className="h-3.5 w-3.5" />
        </a>
      </div>
    </div>
  );
};

