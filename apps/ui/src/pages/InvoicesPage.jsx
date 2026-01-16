import React, { useState, useEffect } from 'react';
import AdminLayout from '../components/AdminLayout';
import { Card, Button, Modal, Input, Select, LoadingSpinner, Alert, Badge, Table } from '../components/UI';
import { adminAPI } from '../services/api';

const InvoicesPage = () => {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [filterStatus, setFilterStatus] = useState('all');
  const [formData, setFormData] = useState({
    invoice_number: '',
    amount: 0,
    currency: 'USD',
    due_date: '',
  });

  useEffect(() => {
    loadInvoices();
  }, []);

  const loadInvoices = async () => {
    try {
      setLoading(true);
      const response = await adminAPI.billing.getInvoices();
      setInvoices(response.data || response);
      setError(null);
    } catch (err) {
      console.error('Error loading invoices:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateInvoice = async (e) => {
    e.preventDefault();
    try {
      await adminAPI.billing.createInvoice(formData);
      setSuccess('Invoice created successfully');
      setShowModal(false);
      loadInvoices();
      setFormData({ invoice_number: '', amount: 0, currency: 'USD', due_date: '' });
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleUpdateStatus = async (invoiceId, newStatus) => {
    try {
      await adminAPI.billing.updateInvoice(invoiceId, { status: newStatus });
      setSuccess('Invoice status updated');
      loadInvoices();
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleSendReminder = async (invoiceId) => {
    try {
      await adminAPI.billing.createReminder(invoiceId, {
        reminder_type: 'overdue_1day',
      });
      setSuccess('Reminder sent successfully');
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  };

  const filteredInvoices = filterStatus === 'all'
    ? invoices
    : invoices.filter(i => i.status === filterStatus);

  const getStatusColor = (status) => {
    const colors = {
      pending: 'yellow',
      sent: 'blue',
      paid: 'green',
      overdue: 'red',
      cancelled: 'gray',
    };
    return colors[status] || 'gray';
  };

  const totalAmount = invoices.reduce((sum, inv) => sum + (inv.amount || 0), 0);
  const paidAmount = invoices
    .filter(inv => inv.status === 'paid')
    .reduce((sum, inv) => sum + (inv.amount || 0), 0);
  const unpaidAmount = invoices
    .filter(inv => inv.status !== 'paid' && inv.status !== 'cancelled')
    .reduce((sum, inv) => sum + (inv.amount || 0), 0);

  const tableRows = filteredInvoices.map(invoice => ({
    'Invoice #': invoice.invoice_number,
    'Amount': `$${invoice.amount.toFixed(2)}`,
    'Currency': invoice.currency,
    'Status': <Badge variant={getStatusColor(invoice.status)}>{invoice.status}</Badge>,
    'Due Date': new Date(invoice.due_date).toLocaleDateString(),
    'Created': new Date(invoice.created_at).toLocaleDateString(),
  }));

  if (loading) {
    return (
      <AdminLayout title="Invoices">
        <div className="flex items-center justify-center h-96">
          <LoadingSpinner size="lg" />
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout title="Invoices & Billing">
      {error && <Alert type="error" message={error} onClose={() => setError(null)} />}
      {success && <Alert type="success" message={success} onClose={() => setSuccess(null)} />}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card className="text-center">
          <p className="text-gray-600 text-sm">Total Invoiced</p>
          <p className="text-3xl font-bold text-gray-900">${totalAmount.toFixed(2)}</p>
        </Card>
        <Card className="text-center">
          <p className="text-gray-600 text-sm">Paid</p>
          <p className="text-3xl font-bold text-green-600">${paidAmount.toFixed(2)}</p>
        </Card>
        <Card className="text-center">
          <p className="text-gray-600 text-sm">Unpaid</p>
          <p className="text-3xl font-bold text-red-600">${unpaidAmount.toFixed(2)}</p>
        </Card>
        <Card className="text-center">
          <p className="text-gray-600 text-sm">Total Invoices</p>
          <p className="text-3xl font-bold text-gray-900">{invoices.length}</p>
        </Card>
      </div>

      <div className="mb-6 flex items-center justify-between gap-4">
        <Select
          options={[
            { label: 'All Invoices', value: 'all' },
            { label: 'Pending', value: 'pending' },
            { label: 'Sent', value: 'sent' },
            { label: 'Paid', value: 'paid' },
            { label: 'Overdue', value: 'overdue' },
            { label: 'Cancelled', value: 'cancelled' },
          ]}
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="max-w-xs"
        />
        <Button onClick={() => setShowModal(true)}>+ Create Invoice</Button>
      </div>

      <Card>
        <Table
          headers={['Invoice #', 'Amount', 'Currency', 'Status', 'Due Date', 'Created']}
          rows={tableRows}
          actions={(row) => (
            <>
              <Button variant="secondary" size="sm">View</Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  const invoice = invoices.find(i => i.invoice_number === row['Invoice #']);
                  handleSendReminder(invoice.id);
                }}
              >
                Remind
              </Button>
              <Select
                options={[
                  { label: 'Pending', value: 'pending' },
                  { label: 'Sent', value: 'sent' },
                  { label: 'Paid', value: 'paid' },
                  { label: 'Overdue', value: 'overdue' },
                  { label: 'Cancelled', value: 'cancelled' },
                ]}
                value={row.Status.props.children}
                onChange={(e) => {
                  const invoice = invoices.find(i => i.invoice_number === row['Invoice #']);
                  handleUpdateStatus(invoice.id, e.target.value);
                }}
                className="max-w-xs"
              />
            </>
          )}
        />
      </Card>

      {/* Create Invoice Modal */}
      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title="Create New Invoice"
      >
        <form onSubmit={handleCreateInvoice} className="space-y-4">
          <Input
            label="Invoice Number"
            value={formData.invoice_number}
            onChange={(e) => setFormData({ ...formData, invoice_number: e.target.value })}
            placeholder="INV-001"
            required
          />
          <Input
            label="Amount"
            type="number"
            value={formData.amount}
            onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) })}
            min="0"
            step="0.01"
            required
          />
          <Select
            label="Currency"
            value={formData.currency}
            onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
            options={[
              { label: 'USD ($)', value: 'USD' },
              { label: 'EUR (€)', value: 'EUR' },
              { label: 'GBP (£)', value: 'GBP' },
              { label: 'CAD ($)', value: 'CAD' },
            ]}
          />
          <Input
            label="Due Date"
            type="date"
            value={formData.due_date}
            onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
            required
          />
          <div className="flex gap-3 pt-4">
            <Button type="submit">Create Invoice</Button>
            <Button variant="secondary" onClick={() => setShowModal(false)}>
              Cancel
            </Button>
          </div>
        </form>
      </Modal>
    </AdminLayout>
  );
};

export default InvoicesPage;
