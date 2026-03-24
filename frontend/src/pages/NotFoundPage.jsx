/**
 * Not Found Page
 */
import React from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../store';

export default function NotFoundPage() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-blue-800 flex items-center justify-center p-4">
      <div className="text-center">
        <h1 className="text-9xl font-bold text-white mb-4">404</h1>
        <p className="text-2xl text-white mb-8">Page Not Found</p>
        <Link
          to={isAuthenticated ? '/chat' : '/login'}
          className="inline-block bg-white text-blue-600 px-8 py-3 rounded-lg font-bold hover:bg-gray-100 transition"
        >
          {isAuthenticated ? 'Back to Chat' : 'Back to Login'}
        </Link>
      </div>
    </div>
  );
}
