import React from 'react';
import { MapPin, Clock, Accessibility, ExternalLink, Building2, Tag, Navigation, AlertTriangle, CheckCircle, Info } from 'lucide-react';
import { CampusPlaceCard } from '../../types';

interface Props {
  card: CampusPlaceCard;
  onOpenMap?: (placeId?: string) => void;
  onNavigate?: (destination: string) => void;
}

export const CampusPlaceCardView: React.FC<Props> = ({ card, onOpenMap, onNavigate }) => {
  const isReconciled = card.verification_status === 'RECONCILED_UNIVERSITY_RECORD' || card.verification_status === 'OFFICIAL_CURRENT_VERIFIED';
  const isHistorical = card.verification_status === 'OFFICIAL_HISTORICAL';
  const isPending = card.verification_status === 'USER_SUPPLIED_MAP_PENDING_VERIFICATION';

  const badgeColor = isReconciled
    ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
    : isHistorical
    ? 'bg-amber-50 text-amber-800 border-amber-200'
    : 'bg-blue-50 text-blue-800 border-blue-200';

  const badgeLabel = isReconciled
    ? 'Verified University Record'
    : isHistorical
    ? 'Historical Record (Confirm Seating)'
    : 'Site Plan (Pending Field Check)';

  return (
    <div className="my-4 rounded-xl border border-sky-200/90 bg-gradient-to-br from-white via-sky-50/20 to-indigo-50/10 p-4 shadow-sm transition-all hover:shadow-md">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-sky-100 pb-2.5">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-sky-600 text-white shadow-xs">
            <MapPin className="h-4 w-4" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="text-xs font-semibold uppercase tracking-wider text-sky-700">
                {card.category || 'Campus Place'}
              </span>
              {card.block_number && (
                <span className="rounded bg-sky-100 px-1.5 py-0.2 text-[11px] font-bold text-sky-800">
                  Block {card.block_number}
                </span>
              )}
            </div>
            <span className="text-[11px] text-neutral-500">{card.campus_zone}</span>
          </div>
        </div>
        <span className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-[11px] font-medium ${badgeColor}`}>
          {isReconciled ? <CheckCircle className="h-3 w-3" /> : <Info className="h-3 w-3" />}
          {badgeLabel}
        </span>
      </div>

      {/* Discrepancy Alert */}
      {card.discrepancy_note && (
        <div className="mt-2.5 flex items-start gap-2 rounded-lg border border-amber-200 bg-amber-50/70 p-2.5 text-xs text-amber-900">
          <AlertTriangle className="h-4 w-4 shrink-0 text-amber-600 mt-0.5" />
          <div>
            <span className="font-semibold">Provenance Notice: </span>
            {card.discrepancy_note}
          </div>
        </div>
      )}

      {/* Title & Description */}
      <div className="mt-3">
        <h4 className="text-sm font-bold text-neutral-900">{card.name}</h4>
        <p className="mt-1 text-xs text-neutral-600 leading-relaxed">
          {card.building_description || card.description}
        </p>
      </div>

      {/* Metadata Grid */}
      <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
        {card.floor_room && (
          <div className="flex items-center gap-2 rounded-lg bg-neutral-50 p-2 border border-neutral-200/70">
            <Building2 className="h-3.5 w-3.5 text-neutral-500 shrink-0" />
            <span className="text-neutral-700 font-medium">{card.floor_room}</span>
          </div>
        )}
        {card.opening_hours && (
          <div className="flex items-center gap-2 rounded-lg bg-neutral-50 p-2 border border-neutral-200/70">
            <Clock className="h-3.5 w-3.5 text-neutral-500 shrink-0" />
            <span className="text-neutral-700">{card.opening_hours}</span>
          </div>
        )}
        {(card.accessibility_information || card.accessibility) && (
          <div className="flex items-center gap-2 rounded-lg bg-neutral-50 p-2 border border-neutral-200/70 sm:col-span-2">
            <Accessibility className="h-3.5 w-3.5 text-emerald-600 shrink-0" />
            <span className="text-neutral-700">{card.accessibility_information || card.accessibility}</span>
          </div>
        )}
      </div>

      {/* Verified Rooms (Strictly displayed only if verified) */}
      {card.rooms && card.rooms.length > 0 && (
        <div className="mt-3 rounded-lg border border-neutral-200/80 bg-neutral-50/60 p-2.5 text-xs">
          <span className="font-semibold text-neutral-800 block mb-1">
            Verified Office Desks / Cells:
          </span>
          <div className="space-y-1">
            {card.rooms.map((rm, idx) => (
              <div key={idx} className="flex items-start gap-1.5 text-neutral-700">
                <span className="font-semibold text-sky-700">{rm.room_number}:</span>
                <span>{rm.purpose || rm.service}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Facilities & Services */}
      {(card.verified_facilities?.length > 0 || card.services?.length > 0) && (
        <div className="mt-3">
          <span className="text-xs font-semibold text-neutral-800 block mb-1.5">
            Key Facilities & Services:
          </span>
          <div className="flex flex-wrap gap-1.5">
            {(card.verified_facilities?.length ? card.verified_facilities : card.services).map((svc, idx) => (
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

      {/* Action Footer */}
      <div className="mt-4 flex flex-wrap items-center justify-between gap-2 pt-2.5 border-t border-sky-100/80">
        <span className="text-[11px] text-neutral-500">
          Source: {card.source_attribution || 'Official LPU Campus Directory'}
        </span>
        <div className="flex items-center gap-2">
          {onNavigate && (
            <button
              type="button"
              onClick={() => onNavigate(card.block_number ? `Block ${card.block_number}` : card.name)}
              className="inline-flex items-center gap-1 rounded-lg border border-sky-300 bg-white px-3 py-1.5 text-xs font-medium text-sky-700 shadow-xs hover:bg-sky-50 transition-colors"
            >
              <Navigation className="h-3.5 w-3.5 text-sky-600" />
              <span>Get Directions</span>
            </button>
          )}
          <button
            type="button"
            onClick={() => onOpenMap ? onOpenMap(card.place_id) : window.open('https://scholix.app/lpu/campus/map', '_blank')}
            className="inline-flex items-center gap-1.5 rounded-lg bg-sky-600 px-3.5 py-1.5 text-xs font-medium text-white shadow-xs transition-colors hover:bg-sky-700"
          >
            <span>Interactive Map</span>
            <ExternalLink className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
