'use client';

import { useAppStore } from '@/store';
import { Search, Plus, Bell, Command } from 'lucide-react';
import { useState } from 'react';
import { cn } from '@/lib/utils';

export function TopBar() {
  const { sidebarOpen, setCurrentPage } = useAppStore();
  const [searchFocused, setSearchFocused] = useState(false);
  const [showNewMenu, setShowNewMenu] = useState(false);

  return (
    <header className={cn(
      'fixed top-0 right-0 h-14 bg-bg-base border-b border-border flex items-center px-4 gap-4 z-30 transition-all duration-200',
      sidebarOpen ? 'left-[220px]' : 'left-[60px]'
    )}>
      {/* Search */}
      <div className="flex-1 max-w-md">
        <div className={cn(
          'flex items-center gap-2 px-3 py-1.5 rounded-full bg-bg-input border transition-colors',
          searchFocused ? 'border-accent-blue' : 'border-border'
        )}>
          <Search className="w-4 h-4 text-text-muted" />
          <input
            type="text"
            placeholder="Search..."
            className="flex-1 bg-transparent text-sm text-text-primary placeholder:text-text-muted outline-none"
            onFocus={() => setSearchFocused(true)}
            onBlur={() => setSearchFocused(false)}
          />
          <kbd className="hidden sm:flex items-center gap-0.5 px-1.5 py-0.5 text-[10px] font-mono text-text-muted bg-bg-card rounded border border-border">
            <Command className="w-3 h-3" />K
          </kbd>
        </div>
      </div>

      {/* New Button */}
      <div className="relative">
        <button
          onClick={() => setShowNewMenu(!showNewMenu)}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-accent-blue hover:bg-accent-blue/90 text-white rounded-lg text-sm font-medium transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span className="hidden sm:inline">New</span>
        </button>

        {showNewMenu && (
          <div className="absolute right-0 top-full mt-1 w-48 bg-bg-card border border-border rounded-lg shadow-lg py-1 z-50">
            {[
              { label: 'New Note', action: () => { setCurrentPage('notes'); setShowNewMenu(false); } },
              { label: 'New Bookmark', action: () => { setCurrentPage('bookmarks'); setShowNewMenu(false); } },
              { label: 'Upload Document', action: () => { setCurrentPage('documents'); setShowNewMenu(false); } },
              { label: 'Ask AI', action: () => { setCurrentPage('chat'); setShowNewMenu(false); } },
            ].map((item) => (
              <button
                key={item.label}
                onClick={item.action}
                className="w-full px-3 py-2 text-left text-sm text-text-secondary hover:bg-bg-card-hover hover:text-text-primary transition-colors"
              >
                {item.label}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Notifications */}
      <button className="relative p-2 rounded-lg hover:bg-bg-card-hover text-text-secondary transition-colors">
        <Bell className="w-5 h-5" />
        <span className="absolute top-1 right-1 w-2 h-2 bg-accent-orange rounded-full" />
      </button>

      {/* Avatar */}
      <div className="w-8 h-8 rounded-full bg-accent-purple/20 flex items-center justify-center text-xs font-bold text-accent-purple">
        P
      </div>
    </header>
  );
}