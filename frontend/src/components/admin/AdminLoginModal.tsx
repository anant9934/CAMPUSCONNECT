import React, { useState } from 'react';
import { X, ShieldCheck, Lock, User, AlertCircle, Loader2 } from 'lucide-react';
import { api } from '../../services/api';
import { AdminUser } from '../../types';

interface AdminLoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLoginSuccess: (user: AdminUser) => void;
}

export const AdminLoginModal: React.FC<AdminLoginModalProps> = ({
  isOpen,
  onClose,
  onLoginSuccess,
}) => {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const data = await api.adminLogin(username.trim(), password);
      onLoginSuccess(data.user);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fadeIn">
      <div className="w-full max-w-md rounded-2xl bg-white border border-warm-border p-6 shadow-soft-lg space-y-5 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-orange-600 flex items-center justify-center text-white shadow-soft">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900 leading-tight">Admin Portal Login</h2>
            <p className="text-xs text-slate-500">LPU Knowledge Base Management</p>
          </div>
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-800 flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-700">Username or Email</label>
            <div className="relative">
              <User className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="admin or admin@lpu.co.in"
                required
                className="w-full pl-9 pr-3 py-2 text-sm rounded-xl border border-warm-border focus:border-orange-400 focus:outline-none focus:ring-2 focus:ring-orange-100"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-700">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter admin password"
                required
                className="w-full pl-9 pr-3 py-2 text-sm rounded-xl border border-warm-border focus:border-orange-400 focus:outline-none focus:ring-2 focus:ring-orange-100"
              />
            </div>
          </div>

          <div className="p-3 rounded-xl bg-warm-50 border border-warm-border text-[11px] text-slate-500">
            <span className="font-semibold text-slate-700">Default Demo Credentials:</span>
            <div className="font-mono mt-0.5 text-slate-600">
              User: <span className="text-slate-900 font-semibold">admin</span> | Pass: <span className="text-slate-900 font-semibold">CampusAdmin@2026</span>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 px-4 rounded-xl bg-orange-600 text-white font-semibold text-sm hover:bg-orange-700 active:scale-[0.99] transition-all flex items-center justify-center gap-2 shadow-soft disabled:opacity-50"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ShieldCheck className="w-4 h-4" />}
            <span>Sign In to Admin Panel</span>
          </button>
        </form>
      </div>
    </div>
  );
};

