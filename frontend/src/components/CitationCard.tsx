import React, { useState } from 'react';
import { ExternalLink, CheckCircle2, ChevronDown, ChevronUp, FileText } from 'lucide-react';
import { Citation } from '../types';

interface CitationCardProps {
  citation: Citation;
  index: number;
}

export const CitationCard: React.FC<CitationCardProps> = ({ citation, index }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="rounded-xl border border-warm-border bg-white p-3 shadow-soft-sm transition-all hover:border-orange-200 hover:shadow-soft">
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start gap-2.5">
          <div className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-lg bg-orange-50 text-orange-600 border border-orange-100">
            <FileText className="h-3.5 w-3.5" />
          </div>
          <div>
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className="text-xs font-semibold text-slate-800 line-clamp-1">
                {citation.title}
              </span>
              {citation.verified && (
                <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-1.5 py-0.2 text-[10px] font-medium text-emerald-700 border border-emerald-200">
                  <CheckCircle2 className="h-2.5 w-2.5" />
                  Verified
                </span>
              )}
            </div>
            <div className="text-[11px] text-slate-500 mt-0.5">
              <span>{citation.source_type}</span>
              {citation.content_owner && (
                <>
                  <span className="mx-1.5 text-slate-300">•</span>
                  <span>{citation.content_owner}</span>
                </>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1 shrink-0">
          <a
            href={citation.url}
            target="_blank"
            rel="noopener noreferrer"
            title="Open official portal reference"
            className="rounded-md p-1 text-slate-400 hover:bg-slate-100 hover:text-orange-600 transition-colors"
          >
            <ExternalLink className="h-3.5 w-3.5" />
          </a>
          {citation.snippet && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="rounded-md p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700 transition-colors"
            >
              {expanded ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
            </button>
          )}
        </div>
      </div>

      {expanded && citation.snippet && (
        <div className="mt-2.5 pt-2 border-t border-slate-100 text-[11px] text-slate-600 bg-warm-50/70 p-2 rounded-lg leading-relaxed font-mono">
          <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1 font-sans">
            Retrieved Excerpt
          </div>
          {citation.snippet}
        </div>
      )}
    </div>
  );
};

