/**
 * Zustand store for authentication
 */
import { create } from 'zustand';

export const useAuthStore = create((set) => ({
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  
  setAuth: (user, token) => {
    localStorage.setItem('user', JSON.stringify(user));
    localStorage.setItem('token', token);
    set({ user, token, isAuthenticated: true });
  },
  
  logout: () => {
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    set({ user: null, token: null, isAuthenticated: false });
  },
  
  setUser: (user) => {
    localStorage.setItem('user', JSON.stringify(user));
    set({ user });
  },
}));

export const useChatStore = create((set) => ({
  messages: [],
  isLoading: false,
  error: null,
  
  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),
  
  setMessages: (messages) =>
    set({ messages }),
  
  clearMessages: () =>
    set({ messages: [] }),
  
  setLoading: (isLoading) =>
    set({ isLoading }),
  
  setError: (error) =>
    set({ error }),
}));

export const useDocumentStore = create((set) => ({
  documents: [],
  isLoading: false,
  error: null,
  
  setDocuments: (documents) =>
    set({ documents }),
  
  addDocument: (document) =>
    set((state) => ({ documents: [...state.documents, document] })),
  
  removeDocument: (id) =>
    set((state) => ({
      documents: state.documents.filter((doc) => doc.id !== id),
    })),
  
  setLoading: (isLoading) =>
    set({ isLoading }),
  
  setError: (error) =>
    set({ error }),
}));
