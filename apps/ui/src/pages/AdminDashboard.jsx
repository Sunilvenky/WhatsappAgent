import React, { useState, useEffect } from 'react';
import AdminLayout from '../components/AdminLayout';
import { Card, LoadingSpinner, Badge, Alert } from '../components/UI';
import { adminAPI } from '../services/api';
import { useTenant } from '../contexts/TenantContext';

const AdminDashboard = () => {
  const { currentTenant } = useTenant();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (currentTenant) {
      loadStats();
    }
  }, [currentTenant]);

  const loadStats = async () => {
    try {
      setLoading(true);
      const response = await adminAPI.billing.getStats(currentTenant.id);
      setStats(response.data || response);
      setError(null);
    } catch (err) {
      console.error('Error loading stats:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <AdminLayout title="Dashboard">
        <div className="flex items-center justify-center h-96">
          <LoadingSpinner size="lg" />
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout title="Dashboard">
      {error && <Alert type="error" message={error} />}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Messages Sent */}
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Messages Sent Today</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {stats?.messages_sent_today || 0}
              </p>
            </div>
            <span className="text-4xl">💬</span>
          </div>
          <p className="text-xs text-gray-600 mt-2">
            This month: {stats?.messages_sent_month || 0}
          </p>
        </Card>

        {/* API Calls */}
        <Card className="bg-gradient-to-br from-green-50 to-green-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">API Calls Today</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {stats?.api_calls_today || 0}
              </p>
            </div>
            <span className="text-4xl">⚡</span>
          </div>
          <p className="text-xs text-gray-600 mt-2">
            This month: {stats?.api_calls_month || 0}
          </p>
        </Card>

        {/* Active Contacts */}
        <Card className="bg-gradient-to-br from-purple-50 to-purple-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Active Contacts</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {stats?.contacts_count || 0}
              </p>
            </div>
            <span className="text-4xl">👤</span>
          </div>
          <p className="text-xs text-gray-600 mt-2">Total in account</p>
        </Card>

        {/* Current Plan */}
        <Card className="bg-gradient-to-br from-orange-50 to-orange-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Current Plan</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">
                {currentTenant?.plan ? currentTenant.plan.charAt(0).toUpperCase() + currentTenant.plan.slice(1) : 'Free'}
              </p>
            </div>
            <span className="text-4xl">📊</span>
          </div>
          <p className="text-xs text-gray-600 mt-2">
            {stats?.plan_limits && `Limit: ${stats.plan_limits.monthly_messages}`}
          </p>
        </Card>
      </div>

      {/* Account Info */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Account Information">
          <div className="space-y-4">
            <div>
              <p className="text-xs text-gray-600 font-medium">Tenant Name</p>
              <p className="text-lg text-gray-900 font-semibold">{currentTenant?.name}</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 font-medium">Domain</p>
              <p className="text-lg text-gray-900 font-semibold">{currentTenant?.domain || 'Not configured'}</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 font-medium">Status</p>
              <div className="mt-1">
                <Badge variant={currentTenant?.is_active ? 'green' : 'red'}>
                  {currentTenant?.is_active ? 'Active' : 'Inactive'}
                </Badge>
              </div>
            </div>
            <div>
              <p className="text-xs text-gray-600 font-medium">Billing Customer ID</p>
              <p className="text-sm text-gray-700 font-mono">{currentTenant?.billing_customer_id || 'Not set'}</p>
            </div>
          </div>
        </Card>

        <Card title="Quick Actions">
          <div className="space-y-3">
            <a
              href="/admin/users"
              className="block px-4 py-3 bg-blue-50 hover:bg-blue-100 rounded-lg text-blue-600 font-medium transition-colors"
            >
              👥 Manage Users
            </a>
            <a
              href="/admin/api-keys"
              className="block px-4 py-3 bg-green-50 hover:bg-green-100 rounded-lg text-green-600 font-medium transition-colors"
            >
              🔑 API Keys
            </a>
            <a
              href="/admin/contacts"
              className="block px-4 py-3 bg-purple-50 hover:bg-purple-100 rounded-lg text-purple-600 font-medium transition-colors"
            >
              📱 View Contacts
            </a>
            <a
              href="/admin/analytics"
              className="block px-4 py-3 bg-orange-50 hover:bg-orange-100 rounded-lg text-orange-600 font-medium transition-colors"
            >
              📈 Analytics
            </a>
          </div>
        </Card>
      </div>
    </AdminLayout>
  );
};

export default AdminDashboard;
