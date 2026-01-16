import React, { useState, useEffect } from 'react';
import AdminLayout from '../components/AdminLayout';
import { Card, Button, Modal, Input, Select, LoadingSpinner, Alert, Badge, Table } from '../components/UI';
import { adminAPI } from '../services/api';

const CampaignsPage = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [steps, setSteps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showStepModal, setShowStepModal] = useState(false);
  const [formData, setFormData] = useState({
    step_number: 1,
    delay_hours: 0,
    delay_type: 'hours',
    message_template: '',
  });

  useEffect(() => {
    loadCampaigns();
  }, []);

  const loadCampaigns = async () => {
    try {
      setLoading(true);
      // Fetch from existing campaigns endpoint
      setError(null);
    } catch (err) {
      console.error('Error loading campaigns:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadSteps = async (campaignId) => {
    try {
      const response = await adminAPI.campaigns.getSteps(campaignId);
      setSteps(response.data || response);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleCreateStep = async (e) => {
    e.preventDefault();
    try {
      await adminAPI.campaigns.createStep(selectedCampaign.id, formData);
      setSuccess('Step created successfully');
      setShowStepModal(false);
      loadSteps(selectedCampaign.id);
      setFormData({ step_number: steps.length + 1, delay_hours: 0, delay_type: 'hours', message_template: '' });
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  };

  const stepsTableRows = steps.map(step => ({
    'Step': step.step_number,
    'Delay': `${step.delay_hours} ${step.delay_type}`,
    'Template': step.message_template.substring(0, 50) + '...',
    'Created': new Date(step.created_at).toLocaleDateString(),
  }));

  if (loading) {
    return (
      <AdminLayout title="Campaigns">
        <div className="flex items-center justify-center h-96">
          <LoadingSpinner size="lg" />
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout title="Drip Campaigns Management">
      {error && <Alert type="error" message={error} onClose={() => setError(null)} />}
      {success && <Alert type="success" message={success} onClose={() => setSuccess(null)} />}

      {!selectedCampaign ? (
        <>
          <div className="mb-6">
            <p className="text-gray-600 mb-4">Manage drip campaign sequences and automations</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card className="text-center">
                <p className="text-gray-600 text-sm">Active Campaigns</p>
                <p className="text-3xl font-bold text-blue-600">0</p>
              </Card>
              <Card className="text-center">
                <p className="text-gray-600 text-sm">Active Enrollments</p>
                <p className="text-3xl font-bold text-green-600">0</p>
              </Card>
              <Card className="text-center">
                <p className="text-gray-600 text-sm">Total Steps</p>
                <p className="text-3xl font-bold text-purple-600">0</p>
              </Card>
            </div>
          </div>

          <Card title="Campaigns">
            <div className="text-center py-8 text-gray-600">
              <p>📬 No campaigns created yet</p>
              <p className="text-sm mt-2">Create campaigns in your main app, then manage them here</p>
            </div>
          </Card>
        </>
      ) : (
        <>
          <Button variant="outline" onClick={() => setSelectedCampaign(null)} className="mb-6">
            ← Back to Campaigns
          </Button>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            <Card>
              <p className="text-sm text-gray-600">Campaign Name</p>
              <p className="text-lg font-semibold">{selectedCampaign.name}</p>
            </Card>
            <Card>
              <p className="text-sm text-gray-600">Status</p>
              <Badge variant="green">Active</Badge>
            </Card>
            <Card>
              <p className="text-sm text-gray-600">Total Steps</p>
              <p className="text-lg font-semibold">{steps.length}</p>
            </Card>
          </div>

          <div className="mb-6 flex items-center justify-between">
            <p className="text-gray-600">Campaign Steps</p>
            <Button onClick={() => setShowStepModal(true)}>+ Add Step</Button>
          </div>

          <Card>
            {steps.length > 0 ? (
              <Table
                headers={['Step', 'Delay', 'Template', 'Created']}
                rows={stepsTableRows}
                actions={() => (
                  <>
                    <Button variant="secondary" size="sm">Edit</Button>
                    <Button variant="danger" size="sm">Delete</Button>
                  </>
                )}
              />
            ) : (
              <div className="text-center py-8 text-gray-600">
                No steps created yet. Create the first step to get started.
              </div>
            )}
          </Card>

          {/* Add Step Modal */}
          <Modal
            isOpen={showStepModal}
            onClose={() => setShowStepModal(false)}
            title="Add Campaign Step"
          >
            <form onSubmit={handleCreateStep} className="space-y-4">
              <Input
                label="Step Number"
                type="number"
                value={formData.step_number}
                onChange={(e) => setFormData({ ...formData, step_number: parseInt(e.target.value) })}
                min="1"
              />
              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Delay"
                  type="number"
                  value={formData.delay_hours}
                  onChange={(e) => setFormData({ ...formData, delay_hours: parseInt(e.target.value) })}
                  min="0"
                />
                <Select
                  label="Delay Type"
                  value={formData.delay_type}
                  onChange={(e) => setFormData({ ...formData, delay_type: e.target.value })}
                  options={[
                    { label: 'Hours', value: 'hours' },
                    { label: 'Days', value: 'days' },
                    { label: 'Weeks', value: 'weeks' },
                  ]}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Message Template</label>
                <textarea
                  value={formData.message_template}
                  onChange={(e) => setFormData({ ...formData, message_template: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows="4"
                  placeholder="Enter the message to send at this step..."
                  required
                />
              </div>
              <div className="flex gap-3 pt-4">
                <Button type="submit">Add Step</Button>
                <Button variant="secondary" onClick={() => setShowStepModal(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          </Modal>
        </>
      )}
    </AdminLayout>
  );
};

export default CampaignsPage;
