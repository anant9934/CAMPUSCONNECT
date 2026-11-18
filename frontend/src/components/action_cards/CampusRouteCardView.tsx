import React, { useState } from 'react';
import { Navigation, Footprints, Clock, Accessibility, MapPin, ChevronDown, ChevronUp, AlertCircle, CheckCircle2, Compass } from 'lucide-react';
import { CampusRouteCard } from '../../types';

interface Props {
  card: CampusRouteCard;
  onOpenMap?: () => void;
}

export const CampusRouteCardView: React.FC<Props> = ({ card, onOpenMap }) => {
  const [showSteps, setShowSteps] = useState(true);

  const isVerified = card.is_pedestrian_path_verified && card.turn_by_turn_available;

  return (
    <div className="my-4 rounded-xl border border-sky-300/80 bg-gradient-to-br from-white via-sky-50/30 to-blue-50/20 p-4 shadow-sm transition-all hover:shadow-md">
      {/* Route Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-sky-100 pb-2.5">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-600 text-white shadow-xs">
            <Navigation className="h-4 w-4" />
          </div>
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-indigo-700">
              Campus Pedestrian Route
            </span>
            <div className="flex items-center gap-1.5 mt-0.5">
              <span className="text-xs font-bold text-neutral-900">{card.origin_name}</span>
              <span className="text-xs text-neutral-400">➔</span>
              <span className="text-xs font-bold text-sky-800">{card.destination_name}</span>
            </div>
          </div>
        </div>
        <span
          className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-[11px] font-medium ${
            isVerified
              ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
              : 'bg-amber-50 text-amber-800 border-amber-200'
          }`}
        >
          {isVerified ? <CheckCircle2 className="h-3 w-3" /> : <AlertCircle className="h-3 w-3" />}
          {isVerified ? 'Verified Pedestrian Walkway' : 'Straight-Line Estimate Only'}
        </span>
      </div>

      {/* Metrics Row: Walking Distance vs Straight Line vs Duration */}
      <div className="mt-3 grid grid-cols-2 sm:grid-cols-3 gap-2.5">
        {card.walking_distance_meters !== null && card.walking_distance_meters !== undefined ? (
          <div className="flex items-center gap-2.5 rounded-lg bg-sky-50/70 border border-sky-100 p-2.5">
            <Footprints className="h-4 w-4 text-sky-700 shrink-0" />
            <div>
              <span className="text-[10px] uppercase font-semibold text-sky-800 block">Walking Distance</span>
              <span className="text-sm font-bold text-sky-950">{card.walking_distance_meters} meters</span>
            </div>
          </div>
        ) : null}

        {card.estimated_duration_minutes !== null && card.estimated_duration_minutes !== undefined ? (
          <div className="flex items-center gap-2.5 rounded-lg bg-indigo-50/70 border border-indigo-100 p-2.5">
            <Clock className="h-4 w-4 text-indigo-700 shrink-0" />
            <div>
              <span className="text-[10px] uppercase font-semibold text-indigo-800 block">Est. Duration</span>
              <span className="text-sm font-bold text-indigo-950">~{card.estimated_duration_minutes} min (1.2 m/s)</span>
            </div>
          </div>
        ) : null}

        {card.straight_line_distance_meters !== null && card.straight_line_distance_meters !== undefined ? (
          <div className="flex items-center gap-2.5 rounded-lg bg-neutral-50 border border-neutral-200 p-2.5 col-span-2 sm:col-span-1">
            <Compass className="h-4 w-4 text-neutral-600 shrink-0" />
            <div>
              <span className="text-[10px] uppercase font-semibold text-neutral-600 block">Straight-Line Air</span>
              <span className="text-sm font-bold text-neutral-800">~{card.straight_line_distance_meters} meters</span>
            </div>
          </div>
        ) : null}
      </div>

      {/* Distinction Note */}
      {card.walking_distance_meters && card.straight_line_distance_meters && (
        <div className="mt-2 text-[11px] text-neutral-500 italic">
          * Walking distance ({card.walking_distance_meters}m) is measured along paved pedestrian paths, avoiding grass lawns and roadways (straight-line air distance is {card.straight_line_distance_meters}m).
        </div>
      )}

      {/* Limitations Notice if Rejected or Unverified */}
      {card.data_limitations && !isVerified && (
        <div className="mt-2.5 flex items-start gap-2 rounded-lg border border-amber-200 bg-amber-50/80 p-2.5 text-xs text-amber-900">
          <AlertCircle className="h-4 w-4 shrink-0 text-amber-600 mt-0.5" />
          <div>
            <span className="font-semibold">Routing Limitation: </span>
            {card.data_limitations}
          </div>
        </div>
      )}

      {/* Accessibility Note */}
      {card.accessibility_notes && (
        <div className="mt-2.5 flex items-center gap-2 rounded-lg bg-emerald-50/60 border border-emerald-100 p-2 text-xs text-emerald-900">
          <Accessibility className="h-3.5 w-3.5 text-emerald-700 shrink-0" />
          <span>{card.accessibility_notes}</span>
        </div>
      )}

      {/* Turn-by-turn Navigation Steps */}
      {card.turn_by_turn_steps && card.turn_by_turn_steps.length > 0 && (
        <div className="mt-3.5 border-t border-sky-100/80 pt-2.5">
          <button
            type="button"
            onClick={() => setShowSteps(!showSteps)}
            className="flex w-full items-center justify-between text-xs font-semibold text-neutral-800 hover:text-sky-700"
          >
            <span>Step-by-Step Directions ({card.turn_by_turn_steps.length} steps)</span>
            {showSteps ? <ChevronUp className="h-4 w-4 text-neutral-500" /> : <ChevronDown className="h-4 w-4 text-neutral-500" />}
          </button>

          {showSteps && (
            <div className="mt-2.5 space-y-2">
              {card.turn_by_turn_steps.map((st) => (
                <div key={st.step} className="flex items-start gap-2.5 rounded-lg bg-neutral-50/80 border border-neutral-200/60 p-2 text-xs">
                  <div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-sky-600 text-[10px] font-bold text-white">
                    {st.step}
                  </div>
                  <div className="flex-1">
                    <p className="text-neutral-800 font-medium">{st.instruction}</p>
                    <div className="mt-0.5 flex flex-wrap items-center gap-2 text-[10px] text-neutral-500">
                      <span>Distance: {st.distance_meters}m</span>
                      {st.surface && <span>• Surface: {st.surface}</span>}
                      {st.wheelchair_accessible && <span className="text-emerald-700 font-semibold">• Step-free</span>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Action Footer */}
      <div className="mt-4 flex items-center justify-between pt-2 border-t border-sky-100/70">
        <span className="text-[11px] text-neutral-500">
          Walkway graph verified with GPS coordinates.
        </span>
        {onOpenMap && (
          <button
            type="button"
            onClick={onOpenMap}
            className="inline-flex items-center gap-1.5 rounded-lg bg-sky-600 px-3.5 py-1.5 text-xs font-medium text-white shadow-xs transition-colors hover:bg-sky-700"
          >
            <MapPin className="h-3.5 w-3.5" />
            <span>View Path on Map</span>
          </button>
        )}
      </div>
    </div>
  );
};
