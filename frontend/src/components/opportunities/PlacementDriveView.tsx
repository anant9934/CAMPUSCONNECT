import React from "react";

interface DriveProps {
  company: string;
  role: string;
  date: string;
  venue: string;
  minCgpa: number;
}

export const PlacementDriveView: React.FC<DriveProps> = ({
  company, role, date, venue, minCgpa
}) => {
  return (
    <div className="p-3 bg-indigo-50 border border-indigo-200 rounded-lg flex items-center justify-between text-xs">
      <div>
        <h5 className="font-bold text-indigo-950">{company} - {role}</h5>
        <p className="text-indigo-700">{venue} • Min CGPA: {minCgpa}</p>
      </div>
      <span className="bg-indigo-600 text-white font-medium px-2 py-1 rounded">{date}</span>
    </div>
  );
};
