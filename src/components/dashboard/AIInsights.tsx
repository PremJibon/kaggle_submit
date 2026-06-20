'use client';

import { useAppStore } from '@/store';
import { Sparkles, Zap } from 'lucide-react';
import { motion } from 'framer-motion';

export function AIInsights() {
  const { notes, tags } = useAppStore();

  const totalNotes = notes.length;
  const taggedNotes = notes.filter(n => n.tags.length > 0).length;
  const score = totalNotes > 0 ? Math.round((taggedNotes / totalNotes) * 100) : 0;

  const topTags = tags.slice(0, 5);
  const unsummarized = notes.filter(n => !n.aiSummary).length;

  return (
    <div className="bg-bg-card rounded-xl border border-accent-purple/20 p-4">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="w-4 h-4 text-accent-purple animate-pulse" />
        <h3 className="text-sm font-semibold text-text-primary">AI Insights</h3>
      </div>

      {/* Knowledge Score */}
      <div className="flex items-center gap-4 mb-4 p-3 bg-bg-base rounded-lg">
        <div className="relative w-16 h-16">
          <svg className="w-16 h-16 -rotate-90" viewBox="0 0 36 36">
            <path
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              fill="none"
              stroke="#252A3D"
              strokeWidth="3"
            />
            <motion.path
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              fill="none"
              stroke="#8B6FFF"
              strokeWidth="3"
              strokeLinecap="round"
              initial={{ strokeDasharray: '0, 100' }}
              animate={{ strokeDasharray: `${score}, 100` }}
              transition={{ duration: 1, ease: 'easeOut' }}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="font-mono text-sm font-bold text-text-primary">{score}%</span>
          </div>
        </div>
        <div>
          <div className="text-xs text-text-secondary">Knowledge Score</div>
          <div className="text-[10px] text-text-muted">{taggedNotes}/{totalNotes} items tagged</div>
        </div>
      </div>

      {/* Suggested Tags */}
      <div className="mb-4">
        <div className="text-xs text-text-secondary mb-2">Suggested Tags</div>
        <div className="flex flex-wrap gap-1.5">
          {topTags.map((tag) => (
            <span
              key={tag.id}
              className="inline-flex items-center gap-1 px-2 py-1 rounded-md text-[11px] font-medium bg-bg-base border border-border hover:border-accent-purple/50 cursor-pointer transition-colors"
              style={{ color: tag.color }}
            >
              {tag.name}
              <span className="text-text-muted text-[9px]">+ Add</span>
            </span>
          ))}
        </div>
      </div>

      {/* Unread Summary */}
      {unsummarized > 0 && (
        <div className="p-3 bg-bg-base rounded-lg border border-border">
          <div className="text-xs text-text-secondary mb-2">
            You have <span className="text-accent-purple font-medium">{unsummarized}</span> unsummarized notes
          </div>
          <button className="flex items-center gap-1.5 px-3 py-1.5 bg-accent-purple/15 text-accent-purple rounded-lg text-xs font-medium hover:bg-accent-purple/25 transition-colors">
            <Zap className="w-3 h-3" />
            Summarize All
          </button>
        </div>
      )}
    </div>
  );
}