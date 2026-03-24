/**
 * API service for communicating with the backend
 */
import axios from 'axios';

const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL ||
  import.meta.env.VITE_API_BASE_URL ||
  'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  register: (email, name, password) =>
    api.post('/auth/register', { email, name, password }),
  login: (email, password) =>
    api.post('/auth/login', { email, password }),
};

export const documentService = {
  uploadDocument: (file, title, description) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    formData.append('description', description);
    return api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getDocuments: (skip = 0, limit = 100) =>
    api.get('/documents', { params: { skip, limit } }),
  getDocument: (id) =>
    api.get(`/documents/${id}`),
  updateDocument: (id, data) =>
    api.put(`/documents/${id}`, data),
  deleteDocument: (id) =>
    api.delete(`/documents/${id}`),
  searchDocuments: (query, skip = 0, limit = 100) =>
    api.get('/documents/search/query', { params: { q: query, skip, limit } }),
};

export const queryService = {
  askQuestion: (question, relevantDocuments = null) =>
    api.post('/queries/ask', { question, relevant_documents: relevantDocuments }),
  getQueryHistory: (skip = 0, limit = 50) =>
    api.get('/queries/history', { params: { skip, limit } }),
  getQuery: (id) =>
    api.get(`/queries/${id}`),
};

export const adminService = {
  getDashboardStats: () =>
    api.get('/admin/dashboard/stats'),
  getUsers: (skip = 0, limit = 100) =>
    api.get('/admin/users', { params: { skip, limit } }),
  getDocumentStats: () =>
    api.get('/admin/documents/stats'),
  getQueryStats: () =>
    api.get('/admin/queries/stats'),
};

export default api;
