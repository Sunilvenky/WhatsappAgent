import React, { useState, useEffect } from 'react';
import AdminLayout from '../components/AdminLayout';
import { Card, Button, Modal, Input, LoadingSpinner, Alert, Badge, Table } from '../components/UI';
import { adminAPI } from '../services/api';
import { useTenant } from '../contexts/TenantContext';

const APIKeysPage = () => {
  const { currentTenant } = useTenant();
  const [apiKeys, setApiKeys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [newKey, setNewKey] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    rate_limit: 1000,
  });

  useEffect(() => {
    if (currentTenant) {
      loadApiKeys();
    }
  }, [currentTenant]);

  const loadApiKeys = async () => {
    try {
      setLoading(true);
      const response = await adminAPI.apiKeys.getAll(currentTenant.id);
      setApiKeys(response.data || response);
      setError(null);
    } catch (err) {
      console.error('Error loading API keys:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateKey = async (e) => {
    e.preventDefault();
    try {
      const response = await adminAPI.apiKeys.create(currentTenant.id, formData);
      const result = response.data || response;
      setNewKey(result.raw_key || result.key);
      setApiKeys([result, ...apiKeys]);
      setSuccess('API key created successfully');
      setShowModal(false);
      setFormData({ name: '', rate_limit: 1000 });
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDeleteKey = async (keyId) => {
    if (window.confirm('Delete this API key? This cannot be undone.')) {
      try {
        await adminAPI.apiKeys.delete(currentTenant.id, keyId);
        setApiKeys(apiKeys.filter(k => k.id !== keyId));
        setSuccess('API key deleted successfully');
        setError(null);
      } catch (err) {
        setError(err.message);
      }
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setSuccess('Copied to clipboard!');
  };

  const tableRows = apiKeys.map(key => ({
    'Name': key.name,
    'Created': new Date(key.created_at).toLocaleDateString(),
    'Rate Limit': `${key.rate_limit}/hour`,
    'Last Used': key.last_used ? new Date(key.last_used).toLocaleDateString() : 'Never',
    'Status': <Badge variant={key.is_active ? 'green' : 'gray'}>{key.is_active ? 'Active' : 'Revoked'}</Badge>,
  }));

  if (loading) {
    return (
      <AdminLayout title="API Keys">
        <div className="flex items-center justify-center h-96">
          <LoadingSpinner size="lg" />
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout title="API Keys Management">
      {error && <Alert type="error" message={error} onClose={() => setError(null)} />}
      {success && <Alert type="success" message={success} onClose={() => setSuccess(null)} />}

      {newKey && (
        <Card className="mb-6 bg-yellow-50 border-2 border-yellow-300">
          <div className="space-y-3">
            <div>
              <p className="text-sm font-semibold text-yellow-900">Your API Key (Save this securely!)</p>
              <p className="text-xs text-yellow-800 mt-1">This is the only time you'll see this key. Store it in a safe place.</p>
            </div>
            <div className="flex gap-2">
              <code className="flex-1 px-3 py-2 bg-white rounded font-mono text-sm text-gray-900 break-all">
                {newKey}
              </code>
              <Button onClick={() => copyToClipboard(newKey)} size="sm">
                📋 Copy
              </Button>
            </div>
            <Button variant="success" size="sm" onClick={() => setNewKey(null)}>
              Got it
            </Button>
          </div>
        </Card>
      )}

      <div className="mb-6 flex items-center justify-between">
        <p className="text-gray-600">Manage API keys for {currentTenant?.name}</p>
        <Button onClick={() => setShowModal(true)}>+ Create API Key</Button>
      </div>

      <Card>
        <Table
          headers={['Name', 'Created', 'Rate Limit', 'Last Used', 'Status']}
          rows={tableRows}
          actions={(row) => (
            <>
              <Button variant="secondary" size="sm" onClick={() => copyToClipboard(`sk_${row.Name}`)}>
                📋 Copy
              </Button>
              <Button
                variant="danger"
                size="sm"
                onClick={() => {
                  const key = apiKeys.find(k => k.name === row.Name);
                  handleDeleteKey(key.id);
                }}
              >
                Revoke
              </Button>
            </>
          )}
        />
      </Card>

      {/* Create API Key Modal */}
      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title="Create API Key"
      >
        <form onSubmit={handleCreateKey} className="space-y-4">
          <Input
            label="Key Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="e.g., Production API"
            required
          />
          <Input
            label="Rate Limit (requests/hour)"
            type="number"
            value={formData.rate_limit}
            onChange={(e) => setFormData({ ...formData, rate_limit: parseInt(e.target.value) })}
            min="10"
            max="100000"
          />
          <div className="bg-blue-50 p-3 rounded-lg text-sm text-blue-800">
            ℹ️ API keys will be required for all API requests in the X-API-Key header
          </div>
          <div className="flex gap-3 pt-4">
            <Button type="submit">Create Key</Button>
            <Button variant="secondary" onClick={() => setShowModal(false)}>
              Cancel
            </Button>
          </div>
        </form>
      </Modal>
    </AdminLayout>
  );
};

export default APIKeysPage;
