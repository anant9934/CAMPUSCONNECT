import React, { useState } from 'react';
import { Building2, MapPin, ExternalLink, Filter, Search, CheckCircle2 } from 'lucide-react';
import { CampusBlockDirectoryCard } from '../../types';

interface Props {
  card: CampusBlockDirectoryCard;
  onSelectPlace?: (placeId: string) => void;
}

export const CampusBlockDirectoryCardView: React.FC<Props> = ({ card, onSelectPlace }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredPlaces = card.places.filter((p) => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return (
      p.name.toLowerCase().includes(term) ||
      (p.block_number && p.block_number.toLowerCase().includes(term)) ||
      p.campus_zone.toLowerCase().includes(term)
    );
  });

  return (
    <div className="my-4 rounded-xl border border-sky-200/90 bg-white p-4 shadow-sm transition-all hover:shadow-md">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-sky-100 pb-2.5">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-sky-700 text-white shadow-xs">
            <Building2 className="h-4 w-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-sky-800">
                Campus Directory
              </span>
              <span className="rounded-full bg-sky-100 px-2 py-0.5 text-[11px] font-bold text-sky-800">
                {card.total_places} Locations
              </span>
            </div>
            <span className="text-xs text-neutral-600 font-medium">{card.filter_applied}</span>
          </div>
        </div>
      </div>

      {/* Filter / Search Bar */}
      <div className="mt-3 relative">
        <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-neutral-400" />
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder={`Filter ${card.total_places} buildings (e.g. Block 32, Hostel, Agriculture)...`}
          className="w-full rounded-lg border border-neutral-200 bg-neutral-50/70 pl-8 pr-3 py-1.5 text-xs text-neutral-800 placeholder-neutral-400 focus:bg-white focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
        />
      </div>

      {/* Grid of Places */}
      <div className="mt-3 max-h-72 overflow-y-auto space-y-2 pr-1">
        {filteredPlaces.length === 0 ? (
          <div className="py-4 text-center text-xs text-neutral-500">
            No locations matched &ldquo;{searchTerm}&rdquo;
          </div>
        ) : (
          filteredPlaces.map((p) => {
            const isReconciled = p.verification_status === 'RECONCILED_UNIVERSITY_RECORD';
            return (
              <div
                key={p.place_id}
                onClick={() => onSelectPlace && onSelectPlace(p.place_id)}
                className="group flex items-center justify-between gap-2 rounded-lg border border-neutral-200/80 bg-neutral-50/50 p-2.5 hover:bg-sky-50/50 hover:border-sky-300 cursor-pointer transition-all"
              >
                <div className="flex items-start gap-2.5">
                  <div className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded bg-sky-100 font-bold text-[11px] text-sky-800 group-hover:bg-sky-600 group-hover:text-white transition-colors">
                    {p.block_number || '•'}
                  </div>
                  <div>
                    <h5 className="text-xs font-semibold text-neutral-900 group-hover:text-sky-900">
                      {p.name}
                    </h5>
                    <div className="flex flex-wrap items-center gap-2 mt-0.5 text-[10px] text-neutral-500">
                      <span>{p.campus_zone}</span>
                      <span>•</span>
                      <span className={isReconciled ? 'text-emerald-700 font-medium' : 'text-neutral-500'}>
                        {isReconciled ? 'Verified Record' : 'Site Plan'}
                      </span>
                    </div>
                  </div>
                </div>

                <MapPin className="h-4 w-4 text-neutral-400 group-hover:text-sky-600 shrink-0" />
              </div>
            );
          })
        )}
      </div>

      {/* Footer */}
      <div className="mt-3.5 flex items-center justify-between pt-2 border-t border-sky-100 text-[11px] text-neutral-500">
        <span>{card.provenance_note}</span>
      </div>
    </div>
  );
};

