import React from 'react';
import { Utensils, MapPin, Clock, Tag, Leaf, AlertCircle, CheckCircle } from 'lucide-react';
import { FoodOutletCard } from '../../types';

interface FoodOutletCardViewProps {
  card: FoodOutletCard;
}

export const FoodOutletCardView: React.FC<FoodOutletCardViewProps> = ({ card }) => {
  const isUnmatched = card.query_match_status === 'unmatched_alternative';

  return (
    <div className="mt-3 overflow-hidden rounded-xl border border-emerald-100 bg-gradient-to-br from-emerald-50/40 via-white to-amber-50/30 p-4 shadow-sm transition-all hover:shadow-md">
      {/* Top Header */}
      <div className="flex items-start justify-between gap-2 border-b border-emerald-100/60 pb-3">
        <div className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-600 text-white shadow-sm">
            <Utensils className="h-5 w-5" />
          </div>
          <div>
            <h4 className="font-semibold text-slate-800 text-sm flex items-center gap-1.5">
              {card.display_name}
            </h4>
            <div className="flex items-center gap-2 text-xs text-slate-500 mt-0.5">
              <span className="capitalize font-medium text-emerald-800">{card.outlet_type.replace('_', ' ')}</span>
              <span>•</span>
              <span>{card.zone}</span>
            </div>
          </div>
        </div>

        {/* 100% Pure Veg Badge */}
        <div className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2.5 py-0.5 text-[11px] font-semibold text-emerald-800 border border-emerald-200">
          <Leaf className="h-3 w-3 text-emerald-600" />
          <span>Pure Veg</span>
        </div>
      </div>

      {/* Proximity & Location Information */}
      <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
        <div className="flex items-start gap-2 text-slate-600">
          <MapPin className="h-4 w-4 text-emerald-600 mt-0.5 shrink-0" />
          <span>{card.location_description}</span>
        </div>

        {(card.estimated_straight_line_distance_meters !== undefined && card.estimated_straight_line_distance_meters !== null) ? (
          <div className="flex items-center gap-2 text-slate-600">
            <Clock className="h-4 w-4 text-emerald-600 shrink-0" />
            <span>
              Straight-Line Estimate: <strong className="text-slate-800">~{card.estimated_straight_line_distance_meters}m</strong>
            </span>
          </div>
        ) : (card.distance_meters !== undefined && card.distance_meters !== null && (
          <div className="flex items-center gap-2 text-slate-600">
            <Clock className="h-4 w-4 text-emerald-600 shrink-0" />
            <span>
              Approx <strong className="text-slate-800">{card.distance_meters}m</strong> (~{card.walking_minutes} min walk)
            </span>
          </div>
        ))}
      </div>

      {/* Verification Notice / Evidence Status Advisory */}
      {card.verification_notice && (
        <div className="mt-2.5 rounded-lg border border-amber-200 bg-amber-50/80 p-2 text-xs text-amber-900 flex items-start gap-2">
          <AlertCircle className="h-4 w-4 text-amber-600 shrink-0 mt-0.5" />
          <div className="space-y-0.5">
            <div className="font-semibold flex items-center gap-1.5">
              <span>Provenance Advisory:</span>
              <span className="rounded bg-amber-200/80 px-1.5 py-0.2 text-[10px] font-bold text-amber-900">
                {card.evidence_status || 'USER_REPORTED'}
              </span>
            </div>
            <p className="text-[11px] leading-relaxed text-amber-800">{card.verification_notice}</p>
          </div>
        </div>
      )}

      {/* Operating Hours & Status */}
      <div className="mt-2.5 flex items-center gap-2 text-xs text-slate-500">
        <span className="inline-block h-2 w-2 rounded-full bg-emerald-500" />
        <span>Hours: <strong className="text-slate-700">{card.opening_hours}</strong></span>
        {card.price_sample && (
          <>
            <span>•</span>
            <span>Sample: <strong className="text-emerald-700">{card.price_sample}</strong></span>
          </>
        )}
      </div>

      {/* Exact Match Items */}
      {!isUnmatched && card.matched_items && card.matched_items.length > 0 && (
        <div className="mt-3 pt-3 border-t border-emerald-100/60">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-900 mb-1.5">
            <Tag className="h-3.5 w-3.5 text-emerald-600" />
            <span>Verified Menu Matches ({card.evidence_type}):</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {card.matched_items.map((item, idx) => (
              <span
                key={idx}
                className="inline-flex items-center gap-1 rounded-md bg-white border border-emerald-200 px-2 py-0.5 text-xs font-medium text-slate-700 shadow-2xs"
              >
                <CheckCircle className="h-3 w-3 text-emerald-500" />
                {item}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Unmatched Dietary Alternatives */}
      {isUnmatched && card.alternatives && card.alternatives.length > 0 && (
        <div className="mt-3 pt-3 border-t border-amber-200/80 bg-amber-50/50 -mx-4 -mb-4 p-4 rounded-b-xl">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-amber-900 mb-2">
            <AlertCircle className="h-4 w-4 text-amber-600" />
            <span>No exact verified menu match. Verified Nearby Vegetarian Alternatives:</span>
          </div>
          <div className="space-y-1.5">
            {card.alternatives.map((alt) => (
              <div
                key={alt.outlet_id}
                className="rounded-lg bg-white border border-amber-200/60 p-2 text-xs flex items-center justify-between shadow-2xs"
              >
                <div>
                  <span className="font-semibold text-slate-800">{alt.display_name}</span>
                  <span className="text-slate-500 text-[11px] block">{alt.location} • {alt.specialty}</span>
                </div>
                <span className="text-[11px] text-emerald-700 font-medium whitespace-nowrap pl-2">
                  {alt.opening_hours.split(':')[0]}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

