import React from 'react';
import { X, GraduationCap, MapPin, ShieldCheck, Cpu, Database, CheckCircle2 } from 'lucide-react';

interface AboutModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AboutModal: React.FC<AboutModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fadeIn">
      <div className="w-full max-w-lg rounded-2xl bg-white border border-warm-border p-6 shadow-soft-lg space-y-5 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-orange-600 flex items-center justify-center text-white shadow-soft">
            <GraduationCap className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900 leading-tight">CampusConnect LPU</h2>
            <p className="text-xs text-slate-500">Official AI Campus Assistant — SRS v2.0</p>
          </div>
        </div>

        <div className="space-y-3 text-xs text-slate-600 leading-relaxed">
          <p>
            <strong>CampusConnect</strong> is a purpose-built institutional information assistant designed exclusively for
            <strong> Lovely Professional University (LPU)</strong>, Phagwara, Punjab.
          </p>

          <div className="p-3.5 rounded-xl bg-warm-50 border border-warm-border space-y-2">
            <div className="flex items-center gap-2 text-slate-800 font-semibold text-xs">
              <MapPin className="w-3.5 h-3.5 text-orange-600" />
              <span>Campus Scope & Location</span>
            </div>
            <p className="text-[11px] text-slate-500">
              Lovely Professional University (LPU), Jalandhar - Delhi G.T. Road, Phagwara, Punjab (144411).
            </p>
          </div>

          <div className="grid grid-cols-2 gap-2.5 pt-1">
            <div className="p-3 rounded-xl border border-warm-border bg-white space-y-1">
              <div className="flex items-center gap-1.5 text-slate-800 font-medium text-xs">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                <span>Grounded RAG</span>
              </div>
              <p className="text-[11px] text-slate-500">
                Only answers from approved institutional policies and handbooks. Zero fabricated fees or rules.
              </p>
            </div>

            <div className="p-3 rounded-xl border border-warm-border bg-white space-y-1">
              <div className="flex items-center gap-1.5 text-slate-800 font-medium text-xs">
                <Cpu className="w-4 h-4 text-orange-600" />
                <span>Google Gemini 3.8</span>
              </div>
              <p className="text-[11px] text-slate-500">
                Powered by Google Gen AI Flash models with circuit breakers and instant verified fallbacks.
              </p>
            </div>
          </div>

          <div className="space-y-1.5 pt-1">
            <div className="font-semibold text-slate-800">Core Capabilities:</div>
            <ul className="space-y-1 text-[11px] text-slate-600 pl-1">
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-3 h-3 text-emerald-600 shrink-0" />
                <span>Academics, Attendance (75% rule), and UMS navigation</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-3 h-3 text-emerald-600 shrink-0" />
                <span>Examination date sheets, Block 34 Helpdesk, and re-evaluations</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-3 h-3 text-emerald-600 shrink-0" />
                <span>Hostel outpass approvals, wardens, and mess guidelines</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-3 h-3 text-emerald-600 shrink-0" />
                <span>Bus routes (Jalandhar, Phagwara, Ludhiana) and UniHospital 24x7</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
          <span>Production Build 2.0.0</span>
          <button
            onClick={onClose}
            className="px-3.5 py-1.5 rounded-lg bg-slate-900 text-white font-medium hover:bg-slate-800 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

