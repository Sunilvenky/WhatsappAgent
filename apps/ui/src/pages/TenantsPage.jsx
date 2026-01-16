import React, { useState, useEffect } from 'react';
import AdminLayout from '../components/AdminLayout';
import { Card, Button, Modal, Input, Select, LoadingSpinner, Alert, Badge, Table } from '../components/UI';
import { adminAPI } from '../services/api';
import { useTenant } from '../contexts/TenantContext';

const TenantsPage = () => {
  const { tenants, loading, createTenant, updateTenant, deleteTenant, reloadTenants } = useTenant();
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    domain: '',
    plan: 'free',
  });

  const handleOpenModal = (tenant = null) => {
    if (tenant) {
      setFormData(tenant);
      setEditingId(tenant.id);
    } else {
      setFormData({ name: '', slug: '', domain: '', plan: 'free' });
      setEditingId(null);
    }
    setShowModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await updateTenant(editingId, formData);
        setSuccess('Tenant updated successfully');
      } else {
        await createTenant(formData);
        setSuccess('Tenant created successfully');
      }
      setShowModal(false);
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this tenant?')) {
      try {
        await deleteTenant(id);
        setSuccess('Tenant deleted successfully');
        setError(null);
      } catch (err) {
        setError(err.message);
      }
    }
  };

  const tableRows = tenants.map(tenant => ({
    'Name': tenant.name,
    'Slug': tenant.slug,
    'Plan': <Badge variant={tenant.plan === 'free' ? 'gray' : 'blue'}>{tenant.plan}</Badge>,
    'Status': <Badge variant={tenant.is_active ? 'green' : 'red'}>{tenant.is_active ? 'Active' : 'Inactive'}</Badge>,
  }));

  if (loading) {
    return (
      <AdminLayout title="Tenants">
        <div className="flex items-center justify-center h-96">
          <LoadingSpinner size="lg" />
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout title="Tenants Management">
      {error && <Alert type="error" message={error} onClose={() => setError(null)} />}
      {success && <Alert type="success" message={success} onClose={() => setSuccess(null)} />}

      <div className="mb-6 flex items-center justify-between">
        <p className="text-gray-600">Manage all tenants in the system</p>
        <Button onClick={() => handleOpenModal()}>+ Create Tenant</Button>
      </div>

      <Card>
        <Table
          headers={['Name', 'Slug', 'Plan', 'Status']}
          rows={tableRows}
          actions={(row) => (
            <>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => {
                  const tenant = tenants.find(t => t.name === row.Name);
                  handleOpenModal(tenant);
                }}
              >
                Edit
              </Button>
              <Button
                variant="danger"
                size="sm"
                onClick={() => {
                  const tenant = tenants.find(t => t.name === row.Name);
                  handleDelete(tenant.id);
                }}
              >
                Delete
              </Button>
            </>
          )}
        />
      </Card>

      {/* Modal */}
      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title={editingId ? 'Edit Tenant' : 'Create New Tenant'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Tenant Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="e.g., Acme Corp"
            required
          />
          <Input
            label="Slug"
            value={formData.slug}
            onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
            placeholder="e.g., acme-corp"
            required
          />
          <Input
            label="Domain"
            value={formData.domain}
            onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
            placeholder="e.g., acme.example.com"
          />
          <Select
            label="Plan"
            value={formData.plan}
            onChange={(e) => setFormData({ ...formData, plan: e.target.value })}
            options={[
              { label: 'Free', value: 'free' },
              { label: 'Starter', value: 'starter' },
              { label: 'Pro', value: 'pro' },
              { label: 'Enterprise', value: 'enterprise' },
            ]}
          />
          <div className="flex gap-3 pt-4">
            <Button type="submit">{editingId ? 'Update' : 'Create'}</Button>
            <Button variant="secondary" onClick={() => setShowModal(false)}>
              Cancel
            </Button>
          </div>
        </form>
      </Modal>
    </AdminLayout>
  );
};

export default TenantsPage;
