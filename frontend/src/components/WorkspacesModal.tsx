import React from 'react';
import {
  X,
  Sparkles,
  Rocket,
  FileCode2,
  BookCheck,
  Briefcase,
  AlertCircle,
  ArrowRight,
  ShieldCheck,
} from 'lucide-react';

interface WorkspacesModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectWorkspace: (prompt: string, title: string) => void;
}

export const WorkspacesModal: React.FC<WorkspacesModalProps> = ({
  isOpen,
  onClose,
  onSelectWorkspace,
}) => {
  if (!isOpen) return null;

  const workspaces = [
    {
      id: 'edurev-projects',
      title: 'Student Engineering & EDU-Rev Projects',
      tag: 'Academic Benefits & CA Exemption',
      tagColor: 'bg-orange-100 text-orange-800',
      description:
        'Map your GitHub repository, live web app, or IoT prototype to EDU-Revolution categories to seek CA exemptions (up to 100%) or course credit equivalence.',
      icon: <Rocket className="w-5 h-5 text-orange-600" />,
      starterPrompt:
        'I am developing an engineering software project. Guide me step-by-step through the EDU-Revolution benefits, required evidence, and course mapping procedure.',
    },
    {
      id: 'attendance-appeal',
      title: 'Attendance Problem Solver & Condonation',
      tag: 'Exam Eligibility & Condonation',
      tagColor: 'bg-rose-100 text-rose-800',
      description:
        'Evaluate low attendance against the 75% End Term Examination threshold, assess eligible 10% condonation / duty leaves, or review biometric punch errors.',
      icon: <AlertCircle className="w-5 h-5 text-rose-600" />,
      starterPrompt:
        'My attendance is low and I want to understand my options. Explain the legitimate condonation and duty leave rules under LPU regulations.',
    },
    {
      id: 'research-patents',
      title: 'Research Publications, Patents & Grade Upgradation',
      tag: 'Scopus / SCI & Patent Office',
      tagColor: 'bg-blue-100 text-blue-800',
      description:
        'Verify requirements for research paper grade enhancement, Scopus DOI indexing, patent application credits, and Division of Research & Development (DRD) procedures.',
      icon: <BookCheck className="w-5 h-5 text-blue-600" />,
      starterPrompt:
        'I have authored a research paper / patent. What academic grade upgradation or credit equivalence can I claim under university policy?',
    },
    {
      id: 'career-hackathons',
      title: 'Hackathons, Startups & Placements',
      tag: 'SIH 2026, Grants & Incubation',
      tagColor: 'bg-emerald-100 text-emerald-800',
      description:
        'Discover upcoming Smart India Hackathon internal selections, Startup School incubation grants, commercial revenue guidelines (SCRGM), and campus placements.',
      icon: <Briefcase className="w-5 h-5 text-emerald-600" />,
      starterPrompt:
        'What hackathon opportunities, incubation grants, and placement initiatives are currently open for CSE students at LPU?',
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs animate-fadeIn">
      <div className="bg-white rounded-2xl border border-warm-border w-full max-w-2xl max-h-[85vh] flex flex-col shadow-soft-lg overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-warm-border flex items-center justify-between bg-slate-50/60">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-orange-600 text-white flex items-center justify-center shadow-xs">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900">Conversational Workspaces</h2>
              <p className="text-xs text-slate-500">
                Focused AI workspaces for project mapping, attendance problem-solving, and research guidance
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Workspaces List */}
        <div className="p-6 overflow-y-auto space-y-3 bg-slate-50/30">
          {workspaces.map((ws) => (
            <div
              key={ws.id}
              onClick={() => {
                onSelectWorkspace(ws.starterPrompt, ws.title);
                onClose();
              }}
              className="p-4 rounded-xl border border-warm-border bg-white hover:border-orange-300 hover:shadow-xs transition-all cursor-pointer group space-y-2"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded-lg bg-slate-50 group-hover:bg-orange-50 transition-colors">
                    {ws.icon}
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-slate-900 group-hover:text-orange-700 transition-colors">
                      {ws.title}
                    </h3>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${ws.tagColor}`}>
                      {ws.tag}
                    </span>
                  </div>
                </div>
                <div className="w-7 h-7 rounded-lg bg-slate-100 text-slate-400 group-hover:bg-orange-600 group-hover:text-white flex items-center justify-center transition-all shrink-0">
                  <ArrowRight className="w-3.5 h-3.5" />
                </div>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed pl-11">
                {ws.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

