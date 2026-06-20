'use client';

import { cn } from '@/lib/utils';
import { LucideIcon } from 'lucide-react';
import { motion } from 'framer-motion';

interface StatCardProps {
  icon: LucideIcon;
  label: string;
  value: number;
  color: string;
  bgColor: string;
  trend?: number;
}

export function StatCard({ icon: Icon, label, value, color, bgColor, trend }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-bg-card rounded-xl p-5 border border-border flex flex-col gap-2 hover:border-border/80 transition-colors"
    >
      <div className={cn('w-10 h-10 rounded-lg flex items-center justify-center', bgColor)}>
        <Icon className={cn('w-5 h-5', color)} />
      </div>
      <div className="font-mono text-3xl font-bold text-text-primary animate-count">
        {value}
      </div>
      <div className="text-xs text-text-secondary uppercase tracking-wider font-medium">
        {label}
      </div>
      {trend !== undefined && (
        <div className={cn('text-xs font-mono', trend >= 0 ? 'text-accent-green' : 'text-accent-orange')}>
          {trend >= 0 ? '+' : ''}{trend}% this week
        </div>
      )}
      {/* Mini sparkline */}
      <div className="flex items-end gap-0.5 h-4 mt-1">
        {[3, 5, 2, 7, 4, 6, 5].map((h, i) => (
          <div
            key={i}
            className="flex-1 rounded-sm opacity-40"
            style={{
              height: `${h * 14}%`,
              backgroundColor: color.includes('blue') ? '#4F6FFF' : color.includes('green') ? '#2ECC8A' : color.includes('purple') ? '#8B6FFF' : '#1DC8CD'
            }}
          />
        ))}
      </div>
    </motion.div>
  );
}