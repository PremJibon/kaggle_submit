'use client';

import { useAppStore } from '@/store';
import { cn, timeAgo } from '@/lib/utils';
import { Tag, MoreHorizontal, Pencil, Sparkles, Trash2, Copy } from 'lucide-react';
import { useState } from 'react';

export function RecentNotes() {
  const { notes, setCurrentPage } = useAppStore();
  const recent = notes.slice(0, 5);

  return (
    <div className="bg-bg-card rounded-xl border border-border p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-text-primary">Recent Notes</h3>
        <button
          onClick={() => setCurrentPage('notes')}
          className="text-xs text-accent-blue hover:underline"
        >
          View All →
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left text-[10px] font-semibold text-text-muted uppercase tracking-wider py-2 px-2">Title</th>
              <th className="text-left text-[10px] font-semibold text-text-muted uppercase tracking-wider py-2 px-2">Tags</th>
              <th className="text-right text-[10px] font-semibold text-text-muted uppercase tracking-wider py-2 px-2">Words</th>
              <th className="text-right text-[10px] font-semibold text-text-muted uppercase tracking-wider py-2 px-2">Updated</th>
              <th className="text-right text-[10px] font-semibold text-text-muted uppercase tracking-wider py-2 px-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {recent.map((note, i) => (
              <tr
                key={note.id}
                className={cn(
                  'border-b border-border/50 hover:bg-bg-card-hover transition-colors',
                  i % 2 === 1 && 'bg-bg-base/30'
                )}
              >
                <td className="py-2.5 px-2">
                  <div className="text-sm text-text-primary truncate max-w-[200px]">{note.title}</div>
                </td>
                <td className="py-2.5 px-2">
                  <div className="flex gap-1 flex-wrap">
                    {note.tags.slice(0, 2).map((tag) => (
                      <span key={tag} className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] bg-accent-blue/10 text-accent-blue">
                        <Tag className="w-2.5 h-2.5" />
                        {tag}
                      </span>
                    ))}
                    {note.tags.length > 2 && (
                      <span className="text-[10px] text-text-muted">+{note.tags.length - 2}</span>
                    )}
                  </div>
                </td>
                <td className="py-2.5 px-2 text-right">
                  <span className="font-mono text-xs text-text-secondary">{note.wordCount}</span>
                </td>
                <td className="py-2.5 px-2 text-right">
                  <span className="font-mono text-[10px] text-text-muted">{timeAgo(note.updatedAt)}</span>
                </td>
                <td className="py-2.5 px-2 text-right">
                  <NoteActions noteId={note.id} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function NoteActions({ noteId }: { noteId: string }) {
  const [open, setOpen] = useState(false);
  const { deleteNote } = useAppStore();

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="p-1 rounded hover:bg-bg-base text-text-muted"
      >
        <MoreHorizontal className="w-4 h-4" />
      </button>
      {open && (
        <div className="absolute right-0 top-full mt-1 w-36 bg-bg-card border border-border rounded-lg shadow-lg py-1 z-10">
          <button className="w-full flex items-center gap-2 px-3 py-1.5 text-xs text-text-secondary hover:bg-bg-card-hover">
            <Pencil className="w-3 h-3" /> Edit
          </button>
          <button className="w-full flex items-center gap-2 px-3 py-1.5 text-xs text-text-secondary hover:bg-bg-card-hover">
            <Sparkles className="w-3 h-3" /> Summarize
          </button>
          <button className="w-full flex items-center gap-2 px-3 py-1.5 text-xs text-text-secondary hover:bg-bg-card-hover">
            <Copy className="w-3 h-3" /> Copy
          </button>
          <button
            onClick={() => { deleteNote(noteId); setOpen(false); }}
            className="w-full flex items-center gap-2 px-3 py-1.5 text-xs text-accent-orange hover:bg-bg-card-hover"
          >
            <Trash2 className="w-3 h-3" /> Delete
          </button>
        </div>
      )}
    </div>
  );
}