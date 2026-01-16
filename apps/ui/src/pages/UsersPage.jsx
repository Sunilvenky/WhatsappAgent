import React, { useState, useEffect } from 'react';
import AdminLayout from '../components/AdminLayout';
import { Card, Button, Modal, Input, Select, LoadingSpinner, Alert, Badge, Table } from '../components/UI';
import { adminAPI } from '../services/api';
import { useTenant } from '../contexts/TenantContext';

const UsersPage = () => {
  const { currentTenant } = useTenant();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    user_id: '',
    role: 'member',
  });

  useEffect(() => {
    if (currentTenant) {
      loadUsers();
    }
  }, [currentTenant]);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await adminAPI.tenantUsers.getAll(currentTenant.id);
      setUsers(response.data || response);
      setError(null);
    } catch (err) {
      console.error('Error loading users:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAddUser = async (e) => {
    e.preventDefault();
    try {
      await adminAPI.tenantUsers.add(currentTenant.id, formData);
      setSuccess('User added successfully');
      setShowModal(false);
      loadUsers();
      setFormData({ user_id: '', role: 'member' });
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleUpdateRole = async (userId, newRole) => {
    try {
      await adminAPI.tenantUsers.updateRole(currentTenant.id, userId, { role: newRole });
      setSuccess('User role updated');
      loadUsers();
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleRemoveUser = async (userId) => {
    if (window.confirm('Remove this user from the tenant?')) {
      try {
        await adminAPI.tenantUsers.remove(currentTenant.id, userId);
        setSuccess('User removed successfully');
        loadUsers();
        setError(null);
      } catch (err) {
        setError(err.message);
      }
    }
  };

  const tableRows = users.map(user => ({
    'Email': user.email,
    'Role': user.role,
    'Joined': new Date(user.joined_at).toLocaleDateString(),
    'Status': <Badge variant="green">Active</Badge>,
  }));

  if (loading) {
    return (
      <AdminLayout title="Users">
        <div className="flex items-center justify-center h-96">
          <LoadingSpinner size="lg" />
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout title="User Management">
      {error && <Alert type="error" message={error} onClose={() => setError(null)} />}
      {success && <Alert type="success" message={success} onClose={() => setSuccess(null)} />}

      <div className="mb-6 flex items-center justify-between">
        <p className="text-gray-600">Manage users in {currentTenant?.name}</p>
        <Button onClick={() => setShowModal(true)}>+ Add User</Button>
      </div>

      <Card>
        <Table
          headers={['Email', 'Role', 'Joined', 'Status']}
          rows={tableRows}
          actions={(row) => (
            <>
              <Select
                options={[
                  { label: 'Member', value: 'member' },
                  { label: 'Admin', value: 'admin' },
                  { label: 'Owner', value: 'owner' },
                ]}
                value={row.Role}
                onChange={(e) => {
                  const user = users.find(u => u.email === row.Email);
                  handleUpdateRole(user.user_id, e.target.value);
                }}
              />
              <Button
                variant="danger"
                size="sm"
                onClick={() => {
                  const user = users.find(u => u.email === row.Email);
                  handleRemoveUser(user.user_id);
                }}
              >
                Remove
              </Button>
            </>
          )}
        />
      </Card>

      {/* Add User Modal */}
      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title="Add User to Tenant"
      >
        <form onSubmit={handleAddUser} className="space-y-4">
          <Input
            label="User ID or Email"
            value={formData.user_id}
            onChange={(e) => setFormData({ ...formData, user_id: e.target.value })}
            placeholder="user@example.com"
            required
          />
          <Select
            label="Role"
            value={formData.role}
            onChange={(e) => setFormData({ ...formData, role: e.target.value })}
            options={[
              { label: 'Member', value: 'member' },
              { label: 'Admin', value: 'admin' },
              { label: 'Owner', value: 'owner' },
            ]}
          />
          <div className="flex gap-3 pt-4">
            <Button type="submit">Add User</Button>
            <Button variant="secondary" onClick={() => setShowModal(false)}>
              Cancel
            </Button>
          </div>
        </form>
      </Modal>
    </AdminLayout>
  );
};

export default UsersPage;
