'use client';

import { useAppStore } from '@/store';
import { cn } from '@/lib/utils';
import {
  Sparkles, Home, Search, MessageSquare, FileText, Bookmark, Tag,
  FileSearch, FolderOpen, BarChart3, Network, Settings, Plug,
  ChevronLeft, ChevronRight
} from 'lucide-react';

const navSections = [
  {
    label: 'WORKSPACE',
    items: [
      { id: 'dashboard', icon: Home, label: 'Dashboard' },
      { id: 'search', icon: Search, label: 'Smart Search' },
      { id: 'chat', icon: MessageSquare, label: 'AI Chat' },
    ]
  },
  {
    label: 'LIBRARY',
    items: [
      { id: 'notes', icon: FileText, label: 'Notes', countKey: 'notes' },
      { id: 'bookmarks', icon: Bookmark, label: 'Bookmarks', countKey: 'bookmarks' },
      { id: 'tags', icon: Tag, label: 'Tags', countKey: 'tags' },
      { id: 'documents', icon: FileSearch, label: 'Documents', countKey: 'documents' },
      { id: 'collections', icon: FolderOpen, label: 'Collections' },
    ]
  },
  {
    label: 'INSIGHTS',
    items: [
      { id: 'analytics', icon: BarChart3, label: 'Analytics' },
      { id: 'graph', icon: Network, label: 'Knowledge Graph' },
    ]
  },
  {
    label: 'SETTINGS',
    items: [
      { id: 'settings', icon: Settings, label: 'Settings' },
      { id: 'integrations', icon: Plug, label: 'Integrations' },
    ]
  }
];

export function Sidebar() {
  const { sidebarOpen, setSidebarOpen, currentPage, setCurrentPage, notes, bookmarks, tags, documents } = useAppStore();

  const counts: Record<string, number> = {
    notes: notes.length,
    bookmarks: bookmarks.length,
    tags: tags.length,
    documents: documents.length,
  };

  return (
    <aside className={cn(
      'fixed left-0 top-0 h-screen bg-bg-surface border-r border-border flex flex-col z-40 transition-all duration-200',
      sidebarOpen ? 'w-[220px]' : 'w-[60px]'
    )}>
      {/* Logo */}
      <div className="h-14 flex items-center px-4 border-b border-border gap-2">
        <div className="w-8 h-8 rounded-lg bg-accent-blue/20 flex items-center justify-center">
          <Sparkles className="w-4 h-4 text-accent-blue" />
        </div>
        {sidebarOpen && (
          <span className="font-bold text-sm text-text-primary truncate">KnowledgeAI</span>
        )}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="ml-auto p-1 rounded hover:bg-bg-card-hover text-text-secondary"
        >
          {sidebarOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </button>
      </div>

      {/* Nav Sections */}
      <nav className="flex-1 overflow-y-auto py-3 px-2">
        {navSections.map((section) => (
          <div key={section.label} className="mb-4">
            {sidebarOpen && (
              <div className="px-2 mb-1 text-[10px] font-semibold text-text-muted tracking-wider uppercase">
                {section.label}
              </div>
            )}
            {section.items.map((item) => {
              const Icon = item.icon;
              const isActive = currentPage === item.id;
              const count = item.countKey ? counts[item.countKey] : undefined;

              return (
                <button
                  key={item.id}
                  onClick={() => setCurrentPage(item.id)}
                  className={cn(
                    'w-full flex items-center gap-2 px-2 py-1.5 rounded-lg text-sm transition-colors mb-0.5',
                    isActive
                      ? 'bg-accent-blue/15 text-text-primary border-l-2 border-accent-blue'
                      : 'text-text-secondary hover:bg-bg-card-hover hover:text-text-primary border-l-2 border-transparent',
                    !sidebarOpen && 'justify-center px-0'
                  )}
                  title={!sidebarOpen ? item.label : undefined}
                >
                  <Icon className="w-4 h-4 flex-shrink-0" />
                  {sidebarOpen && (
                    <>
                      <span className="flex-1 text-left truncate">{item.label}</span>
                      {count !== undefined && (
                        <span className="px-1.5 py-0.5 text-[10px] font-mono bg-bg-card rounded-full text-text-secondary">
                          {count}
                        </span>
                      )}
                    </>
                  )}
                </button>
              );
            })}
          </div>
        ))}
      </nav>

      {/* User */}
      <div className={cn(
        'border-t border-border p-3 flex items-center gap-2',
        !sidebarOpen && 'justify-center'
      )}>
        <div className="w-8 h-8 rounded-full bg-accent-purple/20 flex items-center justify-center text-xs font-bold text-accent-purple">
          P
        </div>
        {sidebarOpen && (
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium text-text-primary truncate">PremJibon</div>
            <div className="text-[10px] text-text-muted">Free Plan</div>
          </div>
        )}
      </div>
    </aside>
  );
}