import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTenant } from '../contexts/TenantContext';

const Sidebar = ({ isOpen, onClose }) => {
  const location = useLocation();
  const { logout } = useAuth();
  const { currentTenant, tenants, switchTenant } = useTenant();

  const menuItems = [
    { label: 'Dashboard', path: '/admin', icon: '📊' },
    { label: 'Tenants', path: '/admin/tenants', icon: '🏢' },
    { label: 'Users', path: '/admin/users', icon: '👥' },
    { label: 'API Keys', path: '/admin/api-keys', icon: '🔑' },
    { label: 'Contacts', path: '/admin/contacts', icon: '📱' },
    { label: 'Campaigns', path: '/admin/campaigns', icon: '📬' },
    { label: 'Orders', path: '/admin/orders', icon: '📦' },
    { label: 'Invoices', path: '/admin/invoices', icon: '💳' },
    { label: 'Analytics', path: '/admin/analytics', icon: '📈' },
    { label: 'Settings', path: '/admin/settings', icon: '⚙️' },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <aside
      className={`fixed inset-y-0 left-0 w-64 bg-gradient-to-b from-gray-900 to-gray-800 text-white transition-transform duration-300 z-40 ${
        isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
      } md:relative md:translate-x-0`}
    >
      <div className="h-full flex flex-col overflow-y-auto">
        {/* Logo */}
        <div className="p-6 border-b border-gray-700">
          <h1 className="text-2xl font-bold">WhatsApp Admin</h1>
          <p className="text-xs text-gray-400 mt-1">SaaS Dashboard</p>
        </div>

        {/* Tenant Selector */}
        {currentTenant && (
          <div className="p-4 border-b border-gray-700">
            <p className="text-xs text-gray-400 mb-2">Current Tenant</p>
            <select
              value={currentTenant.id}
              onChange={(e) => switchTenant(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 text-white rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {tenants.map((tenant) => (
                <option key={tenant.id} value={tenant.id}>
                  {tenant.name}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Menu Items */}
        <nav className="flex-1 px-4 py-6 space-y-2">
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              onClick={onClose}
              className={`flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${
                isActive(item.path)
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-700'
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              <span className="text-sm font-medium">{item.label}</span>
            </Link>
          ))}
        </nav>

        {/* Logout Button */}
        <div className="p-4 border-t border-gray-700">
          <button
            onClick={logout}
            className="w-full px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-medium transition-colors"
          >
            Logout
          </button>
        </div>
      </div>
    </aside>
  );
};

export const AdminLayout = ({ children, title = '', showMobileToggle = true }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user } = useAuth();
  const { currentTenant } = useTenant();

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 shadow-sm">
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center gap-4">
              {showMobileToggle && (
                <button
                  onClick={() => setSidebarOpen(!sidebarOpen)}
                  className="md:hidden text-gray-600 hover:text-gray-900"
                >
                  ☰
                </button>
              )}
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
                {currentTenant && (
                  <p className="text-sm text-gray-600">{currentTenant.name}</p>
                )}
              </div>
            </div>

            {/* User Menu */}
            <div className="flex items-center gap-4">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-medium text-gray-900">{user?.email}</p>
                <p className="text-xs text-gray-600">{user?.role}</p>
              </div>
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white font-bold">
                {user?.email?.charAt(0).toUpperCase()}
              </div>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;
