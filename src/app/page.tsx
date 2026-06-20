'use client';

import { Sidebar } from '@/components/layout/Sidebar';
import { TopBar } from '@/components/layout/TopBar';
import { Dashboard } from '@/components/dashboard/Dashboard';
import { useAppStore } from '@/store';
import { cn } from '@/lib/utils';

function PageContent() {
  const { currentPage } = useAppStore();

  switch (currentPage) {
    case 'dashboard':
      return <Dashboard />;
    default:
      return (
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <div className="text-4xl mb-4">🚧</div>
            <h2 className="text-xl font-semibold text-text-primary mb-2">Coming Soon</h2>
            <p className="text-sm text-text-secondary">This page is under development</p>
          </div>
        </div>
      );
  }
}

export default function Home() {
  const { sidebarOpen } = useAppStore();

  return (
    <div className="min-h-screen bg-bg-base overflow-x-hidden">
      <Sidebar />
      <TopBar />
      <main
        className={cn(
          'transition-all duration-200 pt-14 min-h-screen',
          sidebarOpen ? 'ml-[220px]' : 'ml-[60px]'
        )}
      >
        <div className="p-6 max-w-[1400px]">
          <PageContent />
        </div>
      </main>
    </div>
  );
}