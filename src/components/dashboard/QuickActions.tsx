'use client';

import { useAppStore } from '@/store';
import { FileText, Bookmark, Upload, MessageSquare, Network } from 'lucide-react';

const actions = [
  { icon: FileText, label: 'New Note', color: 'text-accent-blue', bg: 'bg-accent-blue/10', page: 'notes' },
  { icon: Bookmark, label: 'Add Bookmark', color: 'text-accent-green', bg: 'bg-accent-green/10', page: 'bookmarks' },
  { icon: Upload, label: 'Import Doc', color: 'text-accent-teal', bg: 'bg-accent-teal/10', page: 'documents' },
  { icon: MessageSquare, label: 'Ask AI', color: 'text-accent-purple', bg: 'bg-accent-purple/10', page: 'chat' },
  { icon: Network, label: 'View Graph', color: 'text-accent-orange', bg: 'bg-accent-orange/10', page: 'graph' },
];

export function QuickActions() {
  const { setCurrentPage } = useAppStore();

  return (
    <div className="flex gap-3 flex-wrap">
      {actions.map((action) => {
        const Icon = action.icon;
        return (
          <button
            key={action.label}
            onClick={() => setCurrentPage(action.page)}
            className="flex flex-col items-center gap-1.5 p-3 bg-bg-card hover:bg-bg-card-hover border border-border rounded-xl transition-all hover:-translate-y-0.5 min-w-[80px]"
          >
            <div className={`w-10 h-10 rounded-lg ${action.bg} flex items-center justify-center`}>
              <Icon className={`w-5 h-5 ${action.color}`} />
            </div>
            <span className="text-xs text-text-secondary">{action.label}</span>
          </button>
        );
      })}
    </div>
  );
}