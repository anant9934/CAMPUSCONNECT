import React from 'react';
import { UserCheck, Building, DoorOpen, Mail, AlertTriangle, Info, CheckCircle2 } from 'lucide-react';
import { PersonCard } from '../../types';

interface PersonCardViewProps {
  card: PersonCard;
}

export const PersonCardView: React.FC<PersonCardViewProps> = ({ card }) => {
  const isRoomUnpublished = card.room_cabin.toLowerCase().includes('not published');

  return (
    <div className="mt-3 overflow-hidden rounded-xl border border-sky-100 bg-gradient-to-br from-sky-50/30 via-white to-slate-50/50 p-4 shadow-sm transition-all hover:shadow-md">
      {/* Header with Name & Role */}
      <div className="flex items-start justify-between gap-2 border-b border-sky-100/60 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-sky-600 text-white shadow-sm">
            <UserCheck className="h-5 w-5" />
          </div>
          <div>
            <h4 className="font-semibold text-slate-900 text-base flex items-center gap-1.5">
              {card.full_name}
            </h4>
            <p className="text-xs font-medium text-sky-800">{card.designation}</p>
            <p className="text-[11px] text-slate-500">{card.school_division}</p>
          </div>
        </div>

        <div className="flex flex-col items-end gap-1">
          <div className="inline-flex items-center gap-1 rounded-full bg-sky-100 px-2 py-0.5 text-[10px] font-semibold text-sky-800 border border-sky-200">
            <CheckCircle2 className="h-3 w-3 text-sky-600" />
            <span>{card.evidence_status ? card.evidence_status.replace(/_/g, ' ') : 'Verified Roster'}</span>
          </div>
          {card.office_seating_verified === false && (
            <span className="rounded bg-amber-100 px-1.5 py-0.5 text-[9px] font-semibold text-amber-800 border border-amber-200">
              Seating Unverified
            </span>
          )}
        </div>
      </div>

      {/* Location & Office Details */}
      <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
        <div className="flex items-center gap-2 text-slate-700 bg-slate-50/70 p-2 rounded-lg border border-slate-100">
          <Building className="h-4 w-4 text-sky-600 shrink-0" />
          <span>Building: <strong className="text-slate-900">{card.building_block}</strong></span>
        </div>

        <div className={`flex items-start gap-2 p-2 rounded-lg border ${
          isRoomUnpublished 
            ? 'bg-amber-50/60 border-amber-200/70 text-amber-900' 
            : 'bg-slate-50/70 border-slate-100 text-slate-700'
        }`}>
          <DoorOpen className={`h-4 w-4 shrink-0 mt-0.5 ${isRoomUnpublished ? 'text-amber-600' : 'text-sky-600'}`} />
          <div>
            <span className="font-medium">Cabin / Office:</span>
            <span className="block font-semibold mt-0.5">{card.room_cabin}</span>
          </div>
        </div>
      </div>

      {/* Official Email */}
      {card.email && (
        <div className="mt-2.5 flex items-center gap-2 text-xs text-slate-600">
          <Mail className="h-3.5 w-3.5 text-sky-600 shrink-0" />
          <span>Official Email:</span>
          <a
            href={`mailto:${card.email}`}
            className="font-medium text-sky-700 hover:underline hover:text-sky-900"
          >
            {card.email}
          </a>
        </div>
      )}

      {/* Grounding Notes & Designation Distinction */}
      {card.notes && (
        <div className="mt-3 rounded-lg bg-sky-50/60 border border-sky-200/60 p-2.5 text-xs text-slate-700 flex items-start gap-2">
          <Info className="h-4 w-4 text-sky-600 shrink-0 mt-0.5" />
          <p className="leading-relaxed">{card.notes}</p>
        </div>
      )}

      {/* Revalidation Warning if applicable */}
      {card.revalidation_advisory && (
        <div className="mt-2.5 rounded-lg bg-amber-50 border border-amber-200 p-2 text-xs text-amber-800 flex items-start gap-2">
          <AlertTriangle className="h-4 w-4 text-amber-600 shrink-0 mt-0.5" />
          <p>{card.revalidation_advisory}</p>
        </div>
      )}

      {/* Footer / Attribution */}
      <div className="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
        <span>Source: {card.profile_source}</span>
        <span>Verified: {card.verification_date}</span>
      </div>
    </div>
  );
};

