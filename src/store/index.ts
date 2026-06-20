import { create } from 'zustand';
import { generateId } from '@/lib/utils';

export interface Note {
  id: string;
  title: string;
  content: string;
  tags: string[];
  wordCount: number;
  aiSummary?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface Bookmark {
  id: string;
  url: string;
  title: string;
  description: string;
  domain: string;
  tags: string[];
  aiSummary?: string;
  createdAt: Date;
}

export interface Document {
  id: string;
  filename: string;
  fileType: string;
  content: string;
  aiSummary?: string;
  tags: string[];
  status: 'uploading' | 'parsing' | 'indexing' | 'ready' | 'error';
  createdAt: Date;
}

export interface Tag {
  id: string;
  name: string;
  color: string;
  count: number;
}

export interface Activity {
  id: string;
  type: 'note' | 'bookmark' | 'document' | 'ai';
  action: 'added' | 'edited' | 'deleted' | 'summarized';
  title: string;
  timestamp: Date;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface AppState {
  notes: Note[];
  bookmarks: Bookmark[];
  documents: Document[];
  tags: Tag[];
  activities: Activity[];
  chatMessages: ChatMessage[];
  sidebarOpen: boolean;
  currentPage: string;

  addNote: (note: Omit<Note, 'id' | 'createdAt' | 'updatedAt'>) => void;
  updateNote: (id: string, updates: Partial<Note>) => void;
  deleteNote: (id: string) => void;
  addBookmark: (bookmark: Omit<Bookmark, 'id' | 'createdAt'>) => void;
  deleteBookmark: (id: string) => void;
  addDocument: (doc: Omit<Document, 'id' | 'createdAt'>) => void;
  addTag: (tag: Omit<Tag, 'id'>) => void;
  addActivity: (activity: Omit<Activity, 'id' | 'timestamp'>) => void;
  addChatMessage: (msg: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  setSidebarOpen: (open: boolean) => void;
  setCurrentPage: (page: string) => void;
}

export const useAppStore = create<AppState>((set) => ({
  notes: [
    { id: '1', title: 'Project Kickoff Meeting', content: 'Discussed timeline and deliverables for Q3...', tags: ['meeting', 'project'], wordCount: 245, createdAt: new Date(Date.now() - 86400000 * 2), updatedAt: new Date(Date.now() - 86400000) },
    { id: '2', title: 'API Design Notes', content: 'REST endpoints for the knowledge graph...', tags: ['api', 'technical'], wordCount: 180, createdAt: new Date(Date.now() - 86400000 * 5), updatedAt: new Date(Date.now() - 86400000 * 3) },
    { id: '3', title: 'Research: Multi-Agent Systems', content: 'Key concepts from the Google ADK course...', tags: ['research', 'ai'], wordCount: 320, createdAt: new Date(Date.now() - 86400000 * 7), updatedAt: new Date(Date.now() - 86400000 * 4) },
    { id: '4', title: 'Design System Tokens', content: 'Color palette, typography, spacing...', tags: ['design', 'ui'], wordCount: 150, createdAt: new Date(Date.now() - 86400000 * 3), updatedAt: new Date(Date.now() - 86400000 * 1) },
    { id: '5', title: 'Sprint Retrospective', content: 'What went well, what to improve...', tags: ['meeting', 'agile'], wordCount: 200, createdAt: new Date(Date.now() - 86400000 * 6), updatedAt: new Date(Date.now() - 86400000 * 2) },
  ],
  bookmarks: [
    { id: '1', url: 'https://cloud.google.com/agent-builder', title: 'Google ADK Documentation', description: 'Official docs for Agent Development Kit', domain: 'cloud.google.com', tags: ['reference', 'ai'], createdAt: new Date(Date.now() - 86400000 * 4) },
    { id: '2', url: 'https://github.com/vercel/ai', title: 'Vercel AI SDK', description: 'Build AI-powered applications with React', domain: 'github.com', tags: ['reference', 'sdk'], createdAt: new Date(Date.now() - 86400000 * 3) },
    { id: '3', url: 'https://tailwindcss.com', title: 'Tailwind CSS', description: 'Utility-first CSS framework', domain: 'tailwindcss.com', tags: ['reference', 'css'], createdAt: new Date(Date.now() - 86400000 * 2) },
  ],
  documents: [
    { id: '1', filename: 'project-spec.pdf', fileType: 'pdf', content: 'Project specification document...', tags: ['spec'], status: 'ready', createdAt: new Date(Date.now() - 86400000 * 10) },
  ],
  tags: [
    { id: '1', name: 'meeting', color: '#4F6FFF', count: 12 },
    { id: '2', name: 'project', color: '#2ECC8A', count: 8 },
    { id: '3', name: 'ai', color: '#8B6FFF', count: 15 },
    { id: '4', name: 'reference', color: '#1DC8CD', count: 6 },
    { id: '5', name: 'design', color: '#FF7B4F', count: 4 },
  ],
  activities: [
    { id: '1', type: 'note', action: 'added', title: 'Project Kickoff Meeting', timestamp: new Date(Date.now() - 86400000) },
    { id: '2', type: 'bookmark', action: 'added', title: 'Google ADK Documentation', timestamp: new Date(Date.now() - 86400000 * 2) },
    { id: '3', type: 'ai', action: 'summarized', title: 'Research: Multi-Agent Systems', timestamp: new Date(Date.now() - 86400000 * 3) },
    { id: '4', type: 'note', action: 'edited', title: 'API Design Notes', timestamp: new Date(Date.now() - 86400000 * 3) },
    { id: '5', type: 'document', action: 'added', title: 'project-spec.pdf', timestamp: new Date(Date.now() - 86400000 * 5) },
  ],
  chatMessages: [],
  sidebarOpen: true,
  currentPage: 'dashboard',

  addNote: (note) => set((state) => ({
    notes: [{ ...note, id: generateId(), createdAt: new Date(), updatedAt: new Date() }, ...state.notes],
    activities: [{ id: generateId(), type: 'note', action: 'added', title: note.title, timestamp: new Date() }, ...state.activities]
  })),
  updateNote: (id, updates) => set((state) => ({
    notes: state.notes.map(n => n.id === id ? { ...n, ...updates, updatedAt: new Date() } : n)
  })),
  deleteNote: (id) => set((state) => ({
    notes: state.notes.filter(n => n.id !== id)
  })),
  addBookmark: (bookmark) => set((state) => ({
    bookmarks: [{ ...bookmark, id: generateId(), createdAt: new Date() }, ...state.bookmarks],
    activities: [{ id: generateId(), type: 'bookmark', action: 'added', title: bookmark.title, timestamp: new Date() }, ...state.activities]
  })),
  deleteBookmark: (id) => set((state) => ({
    bookmarks: state.bookmarks.filter(b => b.id !== id)
  })),
  addDocument: (doc) => set((state) => ({
    documents: [{ ...doc, id: generateId(), createdAt: new Date() }, ...state.documents],
    activities: [{ id: generateId(), type: 'document', action: 'added', title: doc.filename, timestamp: new Date() }, ...state.activities]
  })),
  addTag: (tag) => set((state) => ({
    tags: [...state.tags, { ...tag, id: generateId() }]
  })),
  addActivity: (activity) => set((state) => ({
    activities: [{ ...activity, id: generateId(), timestamp: new Date() }, ...state.activities]
  })),
  addChatMessage: (msg) => set((state) => ({
    chatMessages: [...state.chatMessages, { ...msg, id: generateId(), timestamp: new Date() }]
  })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setCurrentPage: (page) => set({ currentPage: page }),
}));