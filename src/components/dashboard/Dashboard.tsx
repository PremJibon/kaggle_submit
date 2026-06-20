'use client';

import { useAppStore } from '@/store';
import { StatCard } from '@/components/ui/StatCard';
import { ActivityFeed } from '@/components/dashboard/ActivityFeed';
import { AIInsights } from '@/components/dashboard/AIInsights';
import { QuickActions } from '@/components/dashboard/QuickActions';
import { RecentNotes } from '@/components/dashboard/RecentNotes';
import { TagCloud } from '@/components/dashboard/TagCloud';
import { FileText, Bookmark, Tag, FileSearch } from 'lucide-react';

export function Dashboard() {
  const { notes, bookmarks, tags, documents } = useAppStore();

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={FileText}
          label="Notes"
          value={notes.length}
          color="text-accent-blue"
          bgColor="bg-accent-blue/15"
          trend={12}
        />
        <StatCard
          icon={Bookmark}
          label="Bookmarks"
          value={bookmarks.length}
          color="text-accent-green"
          bgColor="bg-accent-green/15"
          trend={8}
        />
        <StatCard
          icon={Tag}
          label="Tags"
          value={tags.length}
          color="text-accent-purple"
          bgColor="bg-accent-purple/15"
          trend={5}
        />
        <StatCard
          icon={FileSearch}
          label="Documents"
          value={documents.length}
          color="text-accent-teal"
          bgColor="bg-accent-teal/15"
          trend={3}
        />
      </div>

      {/* Activity + AI Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
        <div className="lg:col-span-3">
          <ActivityFeed />
        </div>
        <div className="lg:col-span-2">
          <AIInsights />
        </div>
      </div>

      {/* Quick Actions */}
      <QuickActions />

      {/* Recent Notes + Tags */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <RecentNotes />
        </div>
        <div>
          <TagCloud />
        </div>
      </div>
    </div>
  );
}