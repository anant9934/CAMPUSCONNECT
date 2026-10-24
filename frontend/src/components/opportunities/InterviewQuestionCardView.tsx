import React from "react";

interface QuestionProps {
  question: string;
  framework: string;
  category: string;
}

export const InterviewQuestionCardView: React.FC<QuestionProps> = ({
  question, framework, category
}) => {
  return (
    <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs mb-2">
      <div className="flex justify-between items-center mb-1">
        <span className="font-bold text-amber-900">{category}</span>
        <span className="text-amber-700 font-medium">{framework}</span>
      </div>
      <p className="text-slate-800">{question}</p>
    </div>
  );
};
