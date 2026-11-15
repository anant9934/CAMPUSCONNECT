import React from 'react';
import {
  Sparkles,
  Award,
  Users,
  Compass,
  MapPin,
  Clock,
  Briefcase,
  ArrowRight,
  GraduationCap,
  ChevronRight,
} from 'lucide-react';
import { Category } from '../types';

interface WelcomeHeroProps {
  categories?: Category[];
  onSelectPrompt: (prompt: string) => void;
  onOpenLibrary?: () => void;
  onOpenWorkspaces?: () => void;
}

const PRIMARY_SUGGESTION_PILLS = [
  {
    label: 'Check my academic benefits',
    prompt:
      'I built a full-stack engineering software project. What EDU-Revolution or academic benefit category applies to me?',
    icon: <Award className="w-3.5 h-3.5 text-orange-500" />,
  },
  {
    label: 'Find a faculty expert',
    prompt:
      'Who is the HOD for CSE AI & ML? Where is their seating location and office contact?',
    icon: <Users className="w-3.5 h-3.5 text-blue-500" />,
  },
  {
    label: 'Explore university opportunities',
    prompt:
      'What hackathon opportunities, SIH selections, and incubation grants are available for students?',
    icon: <Briefcase className="w-3.5 h-3.5 text-emerald-500" />,
  },
  {
    label: 'Find a campus location',
    prompt:
      'Where is Block 32 and what food outlets are nearby inside LPU campus?',
    icon: <MapPin className="w-3.5 h-3.5 text-rose-500" />,
  },
  {
    label: 'Understand my attendance',
    prompt:
      'My attendance is currently below 75%. What are my options for duty leave and condonation under LPU policy?',
    icon: <Clock className="w-3.5 h-3.5 text-amber-500" />,
  },
  {
    label: 'Find a university service',
    prompt:
      'How do I book a discussion room in the Central Library or book a doctor appointment at Uni-Hospital?',
    icon: <Compass className="w-3.5 h-3.5 text-indigo-500" />,
  },
];

const CAPABILITY_CARDS = [
  {
    title: 'EDU-Revolution Advisor',
    desc: 'Verify CA exemptions, 9 official SAC categories, and project credit mapping.',
    prompt: 'Guide me step-by-step through LPU EDU-Revolution categories and submission rules.',
    icon: <Award className="w-4 h-4 text-orange-600" />,
    badge: 'SAC Verified',
  },
  {
    title: 'Who to Meet & Issue Resolver',
    desc: 'Find exact offices, HODs, COD appointments, and RMS escalation workflows.',
    prompt: 'Whom should I meet for an attendance biometric issue in Block 32?',
    icon: <Users className="w-4 h-4 text-blue-600" />,
    badge: 'Block 32 & 34',
  },
  {
    title: 'UMS 234 Service Navigator',
    desc: 'Instant click-by-click navigation paths for fee queries, exams, and hostel requests.',
    prompt: 'How do I download my examination date sheet on UMS?',
    icon: <Compass className="w-4 h-4 text-indigo-600" />,
    badge: 'Click Paths',
  },
  {
    title: 'Campus Food & POI Discovery',
    desc: '100% vegetarian verified stalls, operating hours, and distance from your block.',
    prompt: 'Find best pure vegetarian food outlets inside LPU campus near Block 32.',
    icon: <MapPin className="w-4 h-4 text-emerald-600" />,
    badge: 'Inside Campus',
  },
];

export const WelcomeHero: React.FC<WelcomeHeroProps> = ({
  onSelectPrompt,
  onOpenLibrary,
  onOpenWorkspaces,
}) => {
  return (
    <div className="max-w-3xl mx-auto px-4 py-8 sm:py-12 flex flex-col items-center text-center animate-fadeIn">
      {/* Central Glowing Orb & Brand Header (Zyricon / User Image Inspired) */}
      <div className="relative mb-6">
        <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-full bg-gradient-to-tr from-orange-500 via-amber-400 to-purple-600 p-0.5 shadow-soft-lg animate-pulse">
          <div className="w-full h-full rounded-full bg-slate-900 flex items-center justify-center text-white">
            <GraduationCap className="w-8 h-8 sm:w-10 sm:h-10 text-orange-400" />
          </div>
        </div>
        <div className="absolute -top-1 -right-1 w-6 h-6 rounded-full bg-emerald-500 text-white flex items-center justify-center text-[10px] font-bold border-2 border-white shadow-2xs">
          ✓
        </div>
      </div>

      <div className="space-y-2 mb-8">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-orange-50 border border-orange-200/80 text-orange-700 text-xs font-semibold shadow-2xs">
          <Sparkles className="w-3.5 h-3.5 text-orange-600" />
          <span>Lovely Professional University • AI Assistant</span>
        </div>
        <h1 className="text-2xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
          What would you like to know about LPU?
        </h1>
        <p className="text-sm text-slate-600 max-w-lg mx-auto">
          Ask anything about academic benefits, faculty offices, UMS services, attendance condonation, or food inside campus.
        </p>
      </div>

      {/* 6 Clean Suggestion Pills */}
      <div className="w-full mb-8">
        <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-3">
          Popular Inquiries
        </div>
        <div className="flex flex-wrap justify-center gap-2">
          {PRIMARY_SUGGESTION_PILLS.map((pill, idx) => (
            <button
              key={idx}
              onClick={() => onSelectPrompt(pill.prompt)}
              className="flex items-center gap-2 px-3.5 py-2 rounded-full bg-white border border-warm-border hover:border-orange-400 hover:bg-orange-50/40 text-slate-700 hover:text-orange-900 text-xs font-medium transition-all shadow-2xs group"
            >
              {pill.icon}
              <span>{pill.label}</span>
              <ArrowRight className="w-3 h-3 text-slate-400 group-hover:text-orange-600 group-hover:translate-x-0.5 transition-all" />
            </button>
          ))}
        </div>
      </div>

      {/* Quick University Capability Cards Grid */}
      <div className="w-full grid grid-cols-1 sm:grid-cols-2 gap-3 text-left">
        {CAPABILITY_CARDS.map((card, idx) => (
          <div
            key={idx}
            onClick={() => onSelectPrompt(card.prompt)}
            className="p-3.5 rounded-2xl bg-white border border-warm-border hover:border-orange-300 hover:shadow-soft transition-all cursor-pointer group"
          >
            <div className="flex items-center justify-between mb-2">
              <div className="w-8 h-8 rounded-xl bg-slate-50 border border-slate-200/80 flex items-center justify-center text-slate-700 group-hover:bg-orange-50 group-hover:border-orange-200 transition-colors">
                {card.icon}
              </div>
              <span className="text-[10px] font-semibold bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">
                {card.badge}
              </span>
            </div>
            <h3 className="text-xs font-bold text-slate-900 group-hover:text-orange-700 transition-colors flex items-center justify-between">
              <span>{card.title}</span>
              <ChevronRight className="w-3.5 h-3.5 text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity" />
            </h3>
            <p className="text-[11px] text-slate-500 mt-1 leading-relaxed line-clamp-2">
              {card.desc}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
