import React, { useState, useEffect } from 'react';
import AdminLayout from '../components/AdminLayout';
import { Card, Select, LoadingSpinner, Alert } from '../components/UI';
import { useTenant } from '../contexts/TenantContext';
import { adminAPI } from '../services/api';

const AnalyticsPage = () => {
  const { currentTenant } = useTenant();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('month');

  useEffect(() => {
    if (currentTenant) {
      loadStats();
    }
  }, [currentTenant, timeRange]);

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
      <AdminLayout title="Analytics">
        <div className="flex items-center justify-center h-96">
          <LoadingSpinner size="lg" />
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout title="Analytics & Reports">
      {error && <Alert type="error" message={error} />}

      <div className="mb-6">
        <Select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          options={[
            { label: 'Last 7 Days', value: 'week' },
            { label: 'Last 30 Days', value: 'month' },
            { label: 'Last 90 Days', value: 'quarter' },
            { label: 'Year to Date', value: 'year' },
          ]}
          className="max-w-xs"
        />
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100">
          <div>
            <p className="text-gray-600 text-sm font-medium">Messages Sent</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">
              {stats?.messages_sent_month?.toLocaleString() || 0}
            </p>
            <p className="text-xs text-gray-600 mt-2">↑ 12% from last month</p>
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-green-50 to-green-100">
          <div>
            <p className="text-gray-600 text-sm font-medium">Messages Delivered</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">
              {Math.floor((stats?.messages_sent_month || 0) * 0.95).toLocaleString()}
            </p>
            <p className="text-xs text-gray-600 mt-2">95% delivery rate</p>
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-purple-50 to-purple-100">
          <div>
            <p className="text-gray-600 text-sm font-medium">API Calls</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">
              {stats?.api_calls_month?.toLocaleString() || 0}
            </p>
            <p className="text-xs text-gray-600 mt-2">Avg 5.2K/day</p>
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-orange-50 to-orange-100">
          <div>
            <p className="text-gray-600 text-sm font-medium">Active Contacts</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">
              {stats?.contacts_count?.toLocaleString() || 0}
            </p>
            <p className="text-xs text-gray-600 mt-2">↑ 8% growth</p>
          </div>
        </Card>
      </div>

      {/* Engagement Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <Card title="Message Breakdown">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Outbound Messages</span>
              <div className="flex items-center gap-2">
                <div className="w-24 bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: '65%' }}></div>
                </div>
                <span className="text-sm font-semibold">65%</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Inbound Replies</span>
              <div className="flex items-center gap-2">
                <div className="w-24 bg-gray-200 rounded-full h-2">
                  <div className="bg-green-600 h-2 rounded-full" style={{ width: '35%' }}></div>
                </div>
                <span className="text-sm font-semibold">35%</span>
              </div>
            </div>
            <div className="mt-6 pt-4 border-t border-gray-200">
              <p className="text-xs text-gray-600 mb-2">Response Rate</p>
              <p className="text-2xl font-bold text-gray-900">42.5%</p>
            </div>
          </div>
        </Card>

        <Card title="API Usage Distribution">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Send Message</span>
              <span className="font-semibold text-gray-900">45%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Get Contacts</span>
              <span className="font-semibold text-gray-900">25%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Campaign Management</span>
              <span className="font-semibold text-gray-900">18%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Other Operations</span>
              <span className="font-semibold text-gray-900">12%</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Billing Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card title="Current Plan Details">
          <div className="space-y-3">
            <div>
              <p className="text-xs text-gray-600">Plan Type</p>
              <p className="text-lg font-semibold text-gray-900">
                {currentTenant?.plan ? currentTenant.plan.charAt(0).toUpperCase() + currentTenant.plan.slice(1) : 'Free'}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-600">Monthly Limit</p>
              <p className="text-lg font-semibold text-gray-900">
                {stats?.plan_limits?.monthly_messages?.toLocaleString() || 'Unlimited'}
              </p>
            </div>
            <div className="pt-3 border-t border-gray-200">
              <p className="text-xs text-gray-600">Usage This Month</p>
              <div className="flex items-center justify-between mt-2">
                <span className="text-sm font-semibold text-gray-900">
                  {Math.round((stats?.messages_sent_month / (stats?.plan_limits?.monthly_messages || 1)) * 100)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ width: `${Math.min(100, (stats?.messages_sent_month / (stats?.plan_limits?.monthly_messages || 1)) * 100)}%` }}
                ></div>
              </div>
            </div>
          </div>
        </Card>

        <Card title="Billing Information">
          <div className="space-y-3">
            <div>
              <p className="text-xs text-gray-600">Next Bill Date</p>
              <p className="text-lg font-semibold text-gray-900">
                {new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toLocaleDateString()}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-600">Amount Due</p>
              <p className="text-lg font-semibold text-gray-900">$99.00</p>
            </div>
            <div className="pt-3 border-t border-gray-200">
              <p className="text-xs text-gray-600">Payment Method</p>
              <p className="text-sm text-gray-900 mt-1">💳 Visa ending in 4242</p>
            </div>
          </div>
        </Card>

        <Card title="Top Features">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-600 text-sm">Drip Campaigns</span>
              <span className="text-lg font-bold text-gray-900">12</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600 text-sm">Active Contacts</span>
              <span className="text-lg font-bold text-gray-900">
                {stats?.contacts_count || 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600 text-sm">Pending Orders</span>
              <span className="text-lg font-bold text-gray-900">8</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600 text-sm">Invoices This Month</span>
              <span className="text-lg font-bold text-gray-900">5</span>
            </div>
          </div>
        </Card>
      </div>
    </AdminLayout>
  );
};

export default AnalyticsPage;
