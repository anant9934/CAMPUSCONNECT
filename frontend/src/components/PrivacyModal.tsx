import React from 'react';
import { X, ShieldCheck, Lock, EyeOff, AlertTriangle, CheckCircle2 } from 'lucide-react';

interface PrivacyModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const PrivacyModal: React.FC<PrivacyModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fadeIn">
      <div className="w-full max-w-lg rounded-2xl bg-white border border-warm-border p-6 shadow-soft-lg space-y-5 relative max-h-[90vh] overflow-y-auto">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-600 flex items-center justify-center text-white shadow-soft">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900 leading-tight">Student Privacy & Disclosure</h2>
            <p className="text-xs text-slate-500">CampusConnect Data Handling Policies</p>
          </div>
        </div>

        <div className="space-y-4 text-xs text-slate-600 leading-relaxed">
          {/* Public & Anonymous Access */}
          <div className="p-3.5 rounded-xl bg-warm-50 border border-warm-border space-y-1.5">
            <div className="flex items-center gap-2 font-semibold text-slate-800 text-xs">
              <EyeOff className="w-4 h-4 text-emerald-600" />
              <span>100% Anonymous & Zero Login</span>
            </div>
            <p className="text-[11px] text-slate-500">
              Students do not log in. Your conversations are linked only to a random cryptographic session token stored locally in your browser. CampusConnect never asks for your LPU Registration Number, student password, or personal phone number.
            </p>
          </div>

          {/* AI Provider Data Handling */}
          <div className="p-3.5 rounded-xl bg-orange-50/60 border border-orange-200/80 space-y-1.5">
            <div className="flex items-center gap-2 font-semibold text-orange-950 text-xs">
              <AlertTriangle className="w-4 h-4 text-orange-600" />
              <span>Google Gemini Developer API Disclosure</span>
            </div>
            <p className="text-[11px] text-orange-900/80">
              In accordance with Google AI Studio Free Tier terms, queries processed by Gemini may be reviewed by human reviewers to train and improve Google products. <strong>Do not submit passwords, payment card details, or personal medical/financial information in chat queries.</strong>
            </p>
          </div>

          {/* Context Minimization */}
          <div className="space-y-1.5">
            <div className="font-semibold text-slate-800">Data Minimization Guarantees:</div>
            <ul className="space-y-1.5 text-[11px] text-slate-600 pl-1">
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                <span><strong>No Account Hijacking:</strong> We cannot and will not ever perform transactions on your behalf (such as paying fees or submitting exam forms).</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                <span><strong>Short Context Window:</strong> Only the immediate question and concise recent turns are sent to the AI engine—never your full conversation archive.</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                <span><strong>Cross-Session Isolation:</strong> Sessions are strictly cryptographically segregated. No student can view another student's conversation history.</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
          <span>SRS v2.0 Compliance</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-900 text-white font-medium hover:bg-slate-800 transition-colors"
          >
            I Understand
          </button>
        </div>
      </div>
    </div>
  );
};

