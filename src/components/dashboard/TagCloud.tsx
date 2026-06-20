'use client';

import { useAppStore } from '@/store';
import { motion } from 'framer-motion';

export function TagCloud() {
  const { tags } = useAppStore();
  const maxCount = Math.max(...tags.map(t => t.count), 1);

  return (
    <div className="bg-bg-card rounded-xl border border-border p-4">
      <h3 className="text-sm font-semibold text-text-primary mb-4">Tags</h3>

      <div className="flex flex-wrap gap-2">
        {tags.map((tag, i) => {
          const size = 0.7 + (tag.count / maxCount) * 0.5;
          return (
            <motion.button
              key={tag.id}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.05 }}
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg border border-border hover:border-accent-purple/50 transition-colors"
              style={{ fontSize: `${size}rem` }}
            >
              <span
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: tag.color }}
              />
              <span className="text-text-primary">{tag.name}</span>
              <span className="font-mono text-[10px] text-text-muted ml-1">{tag.count}</span>
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}