/**
 * Admin Route Component
 */
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../store';

export default function AdminRoute({ children }) {
  const user = useAuthStore((state) => state.user);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (user?.role !== 'admin') {
    return <Navigate to="/chat" replace />;
  }

  return children;
}
