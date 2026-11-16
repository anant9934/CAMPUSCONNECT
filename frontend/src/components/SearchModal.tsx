import React, { useState, useEffect } from 'react';
import { Search, X, ArrowRight, BookOpen, Clock } from 'lucide-react';
import { ConversationSummary, Category } from '../types';

interface SearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  categories: Category[];
  conversations: ConversationSummary[];
  onSelectPrompt: (prompt: string) => void;
  onSelectConversation: (id: string) => void;
}

const COMMON_TOPICS = [
  'How do I download my examination date sheet?',
  'Where can I find LPU bus routes and timings?',
  'What is the mandatory attendance requirement at LPU?',
  'How do I apply for a hostel night leave or outpass?',
  'Where is the LPU Central Examination Division in Block 34?',
  'What emergency medical facilities are available at UniHospital?',
  'How do I pay semester tuition fees and download receipts on UMS?',
  'Where is the Central Library in Block 37 located?'
];

export const SearchModal: React.FC<SearchModalProps> = ({
  isOpen,
  onClose,
  categories,
  conversations,
  onSelectPrompt,
  onSelectConversation,
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        if (isOpen) onClose();
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const filteredTopics = COMMON_TOPICS.filter((t) =>
    t.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredConversations = conversations.filter((c) =>
    c.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 p-4 bg-slate-900/40 backdrop-blur-sm animate-fadeIn">
      <div className="w-full max-w-xl rounded-2xl bg-white border border-warm-border shadow-soft-lg overflow-hidden space-y-0">
        {/* Search Input Bar */}
        <div className="flex items-center px-4 py-3.5 border-b border-warm-border gap-3">
          <Search className="w-5 h-5 text-slate-400 shrink-0" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search campus topics, FAQs, date sheets, hostel, bus routes..."
            autoFocus
            className="w-full text-sm text-slate-800 placeholder-slate-400 focus:outline-none bg-transparent"
          />
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Results List */}
        <div className="max-h-96 overflow-y-auto p-3 space-y-4">
          {/* Recent Conversations Match */}
          {filteredConversations.length > 0 && (
            <div>
              <div className="px-2 mb-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <Clock className="w-3 h-3" />
                <span>Your Past Conversations</span>
              </div>
              <div className="space-y-1">
                {filteredConversations.slice(0, 4).map((c) => (
                  <button
                    key={c.id}
                    onClick={() => {
                      onSelectConversation(c.id);
                      onClose();
                    }}
                    className="w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs text-slate-700 hover:bg-orange-50 hover:text-orange-900 transition-colors text-left"
                  >
                    <span className="truncate">{c.title}</span>
                    <ArrowRight className="w-3 h-3 text-slate-400 shrink-0" />
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Topics & FAQs Match */}
          <div>
            <div className="px-2 mb-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <BookOpen className="w-3 h-3" />
              <span>Campus Topics & Approved FAQs</span>
            </div>
            {filteredTopics.length === 0 ? (
              <div className="px-3 py-6 text-center text-xs text-slate-400">
                No matching topics found for "{searchTerm}".
              </div>
            ) : (
              <div className="space-y-1">
                {filteredTopics.map((topic, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      onSelectPrompt(topic);
                      onClose();
                    }}
                    className="w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs text-slate-700 hover:bg-orange-50 hover:text-orange-900 transition-colors text-left group"
                  >
                    <span className="truncate pr-2">{topic}</span>
                    <ArrowRight className="w-3 h-3 text-slate-400 group-hover:text-orange-600 transition-colors shrink-0" />
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-4 py-2 border-t border-slate-100 bg-warm-50/70 text-[11px] text-slate-400 flex items-center justify-between">
          <span>Navigate with arrows, Enter to select</span>
          <kbd className="text-[10px] bg-white border border-slate-200 px-1.5 py-0.5 rounded">ESC</kbd>
        </div>
      </div>
    </div>
  );
};

