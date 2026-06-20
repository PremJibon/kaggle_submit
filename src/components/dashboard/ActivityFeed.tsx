'use client';

import { useAppStore, Activity } from '@/store';
import { cn, timeAgo } from '@/lib/utils';
import { FileText, Bookmark, FileSearch, Sparkles, Plus, Pencil, Trash2 } from 'lucide-react';

const typeConfig: Record<string, { icon: typeof FileText; color: string }> = {
  note: { icon: FileText, color: 'text-accent-blue' },
  bookmark: { icon: Bookmark, color: 'text-accent-green' },
  document: { icon: FileSearch, color: 'text-accent-teal' },
  ai: { icon: Sparkles, color: 'text-accent-purple' },
};

const actionConfig: Record<string, { icon: typeof Plus; label: string; color: string }> = {
  added: { icon: Plus, label: 'added', color: 'bg-accent-green/15 text-accent-green' },
  edited: { icon: Pencil, label: 'edited', color: 'bg-accent-blue/15 text-accent-blue' },
  deleted: { icon: Trash2, label: 'deleted', color: 'bg-accent-orange/15 text-accent-orange' },
  summarized: { icon: Sparkles, label: 'AI summarized', color: 'bg-accent-purple/15 text-accent-purple' },
};

export function ActivityFeed() {
  const { activities } = useAppStore();
  const recent = activities.slice(0, 8);

  return (
    <div className="bg-bg-card rounded-xl border border-border p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-text-primary">Recent Activity</h3>
        <button className="text-xs text-accent-blue hover:underline">View All →</button>
      </div>

      {recent.length === 0 ? (
        <div className="text-center py-8 text-text-muted text-sm">
          No activity yet — start adding notes or bookmarks
        </div>
      ) : (
        <div className="space-y-3">
          {recent.map((activity) => {
            const typeConf = typeConfig[activity.type] || typeConfig.note;
            const actionConf = actionConfig[activity.action] || actionConfig.added;
            const TypeIcon = typeConf.icon;
            const ActionIcon = actionConf.icon;

            return (
              <div key={activity.id} className="flex items-center gap-3 p-2 rounded-lg hover:bg-bg-card-hover transition-colors">
                <div className={cn('w-8 h-8 rounded-lg bg-bg-base flex items-center justify-center flex-shrink-0')}>
                  <TypeIcon className={cn('w-4 h-4', typeConf.color)} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm text-text-primary truncate">{activity.title}</div>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className={cn('inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium', actionConf.color)}>
                      <ActionIcon className="w-2.5 h-2.5" />
                      {actionConf.label}
                    </span>
                    <span className="text-[10px] text-text-muted font-mono">{timeAgo(activity.timestamp)}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}