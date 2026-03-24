/**
 * Admin Dashboard
 */
import React, { useState, useEffect, Suspense } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import AdminDocs from '../components/AdminDocs';
import { adminService } from '../services/api';
import { FileUp, MessageSquare, Users, BarChart3, AlertCircle } from 'lucide-react';

function AdminStats() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await adminService.getDashboardStats();
        setStats(response.data);
      } catch (err) {
        setError('Failed to load statistics');
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) {
    return <div className="text-center py-10">Loading statistics...</div>;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-800">Admin Dashboard</h1>

      {error && (
        <div className="p-4 bg-red-100 border border-red-400 rounded-lg flex items-start space-x-3">
          <AlertCircle className="text-red-600 flex-shrink-0" size={20} />
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Documents */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Documents</p>
                <p className="text-3xl font-bold text-gray-800">
                  {stats.documents?.total_documents || 0}
                </p>
              </div>
              <FileUp className="text-blue-600" size={32} />
            </div>
            <p className="text-xs text-gray-500 mt-2">
              {(stats.documents?.total_size_mb || 0).toFixed(2)} MB stored
            </p>
          </div>

          {/* Queries */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Queries</p>
                <p className="text-3xl font-bold text-gray-800">
                  {stats.queries?.total_queries || 0}
                </p>
              </div>
              <MessageSquare className="text-green-600" size={32} />
            </div>
          </div>

          {/* Users */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Users</p>
                <p className="text-3xl font-bold text-gray-800">
                  {stats.users?.total || 0}
                </p>
              </div>
              <Users className="text-purple-600" size={32} />
            </div>
          </div>

          {/* System Status */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">System Status</p>
                <p className="text-lg font-bold text-green-600">
                  {stats.system?.status || 'Unknown'}
                </p>
              </div>
              <BarChart3 className="text-orange-600" size={32} />
            </div>
          </div>
        </div>
      )}

      {/* Recent Queries */}
      {stats?.queries?.recent_queries && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Recent Queries</h2>
          <div className="space-y-3">
            {stats.queries.recent_queries.map((query) => (
              <div key={query.id} className="flex justify-between items-start p-3 border border-gray-200 rounded">
                <div className="flex-1">
                  <p className="text-sm text-gray-800">{query.question}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(query.timestamp).toLocaleString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function AdminDashboard() {
  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <Navbar />
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-7xl mx-auto">
          <Routes>
            <Route path="/" element={<AdminStats />} />
            <Route path="/documents" element={<AdminDocs />} />
          </Routes>
        </div>
      </div>
    </div>
  );
}
