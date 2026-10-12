import React from "react";

interface OpportunityProps {
  jobTitle: string;
  companyName: string;
  location: string;
  salaryText: string;
  matchScore: number;
  isEligible: boolean;
  matchedSkills: string[];
  missingSkills: string[];
  applyUrl?: string;
}

export const OpportunityCardView: React.FC<OpportunityProps> = ({
  jobTitle, companyName, location, salaryText, matchScore, isEligible, matchedSkills, missingSkills, applyUrl
}) => {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-2">
        <div>
          <h3 className="font-semibold text-slate-800 text-base">{jobTitle}</h3>
          <p className="text-sm font-medium text-emerald-600">{companyName} • <span className="text-slate-500">{location}</span></p>
        </div>
        <div className="text-right">
          <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold ${
            matchScore >= 75 ? "bg-emerald-100 text-emerald-800" : "bg-amber-100 text-amber-800"
          }`}>
            {matchScore}% Match
          </span>
        </div>
      </div>
      <p className="text-xs font-semibold text-slate-700 mb-3">{salaryText}</p>
      <div className="flex flex-wrap gap-1 mb-3">
        {matchedSkills.map((s, idx) => (
          <span key={idx} className="bg-slate-100 text-slate-700 text-xs px-2 py-0.5 rounded">{s}</span>
        ))}
      </div>
      {applyUrl && (
        <a href={applyUrl} target="_blank" rel="noreferrer" className="block text-center w-full py-1.5 bg-blue-600 text-white rounded-lg text-xs font-medium hover:bg-blue-700">
          Apply on Naukri.com
        </a>
      )}
    </div>
  );
};
