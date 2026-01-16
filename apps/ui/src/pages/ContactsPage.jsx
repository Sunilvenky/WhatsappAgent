import React, { useState, useEffect } from 'react';
import AdminLayout from '../components/AdminLayout';
import { Card, Button, Modal, Input, Select, LoadingSpinner, Alert, Badge, Table } from '../components/UI';
import { adminAPI } from '../services/api';

const ContactsPage = () => {
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [formData, setFormData] = useState({
    phone_number: '',
    first_name: '',
    last_name: '',
    email: '',
  });

  useEffect(() => {
    loadContacts();
  }, []);

  const loadContacts = async () => {
    try {
      setLoading(true);
      const response = await adminAPI.contacts.getAll();
      setContacts(response.data || response);
      setError(null);
    } catch (err) {
      console.error('Error loading contacts:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateContact = async (e) => {
    e.preventDefault();
    try {
      await adminAPI.contacts.create(formData);
      setSuccess('Contact created successfully');
      setShowModal(false);
      loadContacts();
      setFormData({ phone_number: '', first_name: '', last_name: '', email: '' });
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  };

  const filteredContacts = contacts.filter(contact =>
    contact.first_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    contact.phone_number?.includes(searchTerm)
  );

  const tableRows = filteredContacts.map(contact => ({
    'Name': `${contact.first_name} ${contact.last_name}`,
    'Phone': contact.phone_number,
    'Email': contact.email || 'N/A',
    'Status': <Badge variant={contact.is_active ? 'green' : 'gray'}>{contact.is_active ? 'Active' : 'Inactive'}</Badge>,
  }));

  if (loading) {
    return (
      <AdminLayout title="Contacts">
        <div className="flex items-center justify-center h-96">
          <LoadingSpinner size="lg" />
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout title="Contacts Management">
      {error && <Alert type="error" message={error} onClose={() => setError(null)} />}
      {success && <Alert type="success" message={success} onClose={() => setSuccess(null)} />}

      <div className="mb-6 flex items-center justify-between gap-4">
        <Input
          placeholder="Search by name or phone..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="flex-1"
        />
        <Button onClick={() => setShowModal(true)}>+ Add Contact</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card className="text-center">
          <p className="text-gray-600 text-sm">Total Contacts</p>
          <p className="text-3xl font-bold text-gray-900">{contacts.length}</p>
        </Card>
        <Card className="text-center">
          <p className="text-gray-600 text-sm">Active</p>
          <p className="text-3xl font-bold text-green-600">{contacts.filter(c => c.is_active).length}</p>
        </Card>
        <Card className="text-center">
          <p className="text-gray-600 text-sm">Inactive</p>
          <p className="text-3xl font-bold text-red-600">{contacts.filter(c => !c.is_active).length}</p>
        </Card>
      </div>

      <Card>
        <Table
          headers={['Name', 'Phone', 'Email', 'Status']}
          rows={tableRows}
          actions={(row) => (
            <>
              <Button variant="secondary" size="sm">View</Button>
              <Button variant="secondary" size="sm">Edit</Button>
            </>
          )}
        />
      </Card>

      {/* Add Contact Modal */}
      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title="Add New Contact"
      >
        <form onSubmit={handleCreateContact} className="space-y-4">
          <Input
            label="Phone Number"
            value={formData.phone_number}
            onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
            placeholder="+1234567890"
            required
          />
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="First Name"
              value={formData.first_name}
              onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
              required
            />
            <Input
              label="Last Name"
              value={formData.last_name}
              onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
            />
          </div>
          <Input
            label="Email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            placeholder="contact@example.com"
          />
          <div className="flex gap-3 pt-4">
            <Button type="submit">Add Contact</Button>
            <Button variant="secondary" onClick={() => setShowModal(false)}>
              Cancel
            </Button>
          </div>
        </form>
      </Modal>
    </AdminLayout>
  );
};

export default ContactsPage;
