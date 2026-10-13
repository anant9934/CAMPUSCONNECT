import React from "react";

interface SkillGapProps {
  targetRole: string;
  fitPercentage: number;
  acquiredSkills: string[];
  missingSkills: string[];
  recommendedCourses: string[];
}

export const SkillGapReportView: React.FC<SkillGapProps> = ({
  targetRole, fitPercentage, acquiredSkills, missingSkills, recommendedCourses
}) => {
  return (
    <div className="bg-slate-50 rounded-xl border border-slate-200 p-4">
      <h4 className="font-semibold text-slate-800 text-sm mb-1">Career Readiness: {targetRole}</h4>
      <p className="text-xs text-slate-500 mb-3">Overall Profile Readiness: {fitPercentage}%</p>
      <div className="grid grid-cols-2 gap-2 text-xs mb-3">
        <div className="bg-white p-2 rounded border border-emerald-100">
          <span className="font-medium text-emerald-700">Acquired Skills ({acquiredSkills.length})</span>
          <p className="text-slate-600 mt-1">{acquiredSkills.join(", ")}</p>
        </div>
        <div className="bg-white p-2 rounded border border-rose-100">
          <span className="font-medium text-rose-700">Missing Skills ({missingSkills.length})</span>
          <p className="text-slate-600 mt-1">{missingSkills.join(", ") || "None!"}</p>
        </div>
      </div>
    </div>
  );
};
