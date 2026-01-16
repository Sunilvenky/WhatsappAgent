import React, { useState, useEffect } from 'react';
import AdminLayout from '../components/AdminLayout';
import { Card, Button, Modal, Input, Select, LoadingSpinner, Alert, Badge, Table } from '../components/UI';
import { adminAPI } from '../services/api';

const OrdersPage = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [filterStatus, setFilterStatus] = useState('all');
  const [formData, setFormData] = useState({
    order_number: '',
    external_id: '',
    platform: 'shopify',
    total_amount: 0,
  });

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    try {
      setLoading(true);
      const response = await adminAPI.orders.getAll();
      setOrders(response.data || response);
      setError(null);
    } catch (err) {
      console.error('Error loading orders:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateOrder = async (e) => {
    e.preventDefault();
    try {
      await adminAPI.orders.create(formData);
      setSuccess('Order created successfully');
      setShowModal(false);
      loadOrders();
      setFormData({ order_number: '', external_id: '', platform: 'shopify', total_amount: 0 });
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleUpdateStatus = async (orderId, newStatus) => {
    try {
      await adminAPI.orders.update(orderId, { status: newStatus });
      setSuccess('Order status updated');
      loadOrders();
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  };

  const filteredOrders = filterStatus === 'all'
    ? orders
    : orders.filter(o => o.status === filterStatus);

  const getStatusColor = (status) => {
    const colors = {
      pending: 'gray',
      confirmed: 'blue',
      shipped: 'yellow',
      delivered: 'green',
      cancelled: 'red',
    };
    return colors[status] || 'gray';
  };

  const tableRows = filteredOrders.map(order => ({
    'Order #': order.order_number,
    'Platform': order.platform,
    'Amount': `$${order.total_amount.toFixed(2)}`,
    'Status': <Badge variant={getStatusColor(order.status)}>{order.status}</Badge>,
    'Created': new Date(order.created_at).toLocaleDateString(),
  }));

  if (loading) {
    return (
      <AdminLayout title="Orders">
        <div className="flex items-center justify-center h-96">
          <LoadingSpinner size="lg" />
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout title="Orders Management">
      {error && <Alert type="error" message={error} onClose={() => setError(null)} />}
      {success && <Alert type="success" message={success} onClose={() => setSuccess(null)} />}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card className="text-center">
          <p className="text-gray-600 text-sm">Total Orders</p>
          <p className="text-3xl font-bold text-gray-900">{orders.length}</p>
        </Card>
        <Card className="text-center">
          <p className="text-gray-600 text-sm">Pending</p>
          <p className="text-3xl font-bold text-gray-600">{orders.filter(o => o.status === 'pending').length}</p>
        </Card>
        <Card className="text-center">
          <p className="text-gray-600 text-sm">Shipped</p>
          <p className="text-3xl font-bold text-yellow-600">{orders.filter(o => o.status === 'shipped').length}</p>
        </Card>
        <Card className="text-center">
          <p className="text-gray-600 text-sm">Delivered</p>
          <p className="text-3xl font-bold text-green-600">{orders.filter(o => o.status === 'delivered').length}</p>
        </Card>
      </div>

      <div className="mb-6 flex items-center justify-between gap-4">
        <Select
          options={[
            { label: 'All Orders', value: 'all' },
            { label: 'Pending', value: 'pending' },
            { label: 'Confirmed', value: 'confirmed' },
            { label: 'Shipped', value: 'shipped' },
            { label: 'Delivered', value: 'delivered' },
            { label: 'Cancelled', value: 'cancelled' },
          ]}
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="max-w-xs"
        />
        <Button onClick={() => setShowModal(true)}>+ Create Order</Button>
      </div>

      <Card>
        <Table
          headers={['Order #', 'Platform', 'Amount', 'Status', 'Created']}
          rows={tableRows}
          actions={(row) => (
            <>
              <Button variant="secondary" size="sm">View Items</Button>
              <Select
                options={[
                  { label: 'Pending', value: 'pending' },
                  { label: 'Confirmed', value: 'confirmed' },
                  { label: 'Shipped', value: 'shipped' },
                  { label: 'Delivered', value: 'delivered' },
                ]}
                value={row.Status.props.children}
                onChange={(e) => {
                  const order = orders.find(o => o.order_number === row['Order #']);
                  handleUpdateStatus(order.id, e.target.value);
                }}
                className="max-w-xs"
              />
            </>
          )}
        />
      </Card>

      {/* Create Order Modal */}
      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title="Create New Order"
      >
        <form onSubmit={handleCreateOrder} className="space-y-4">
          <Input
            label="Order Number"
            value={formData.order_number}
            onChange={(e) => setFormData({ ...formData, order_number: e.target.value })}
            placeholder="ORD-001"
            required
          />
          <Input
            label="External ID"
            value={formData.external_id}
            onChange={(e) => setFormData({ ...formData, external_id: e.target.value })}
            placeholder="Platform order ID"
            required
          />
          <Select
            label="Platform"
            value={formData.platform}
            onChange={(e) => setFormData({ ...formData, platform: e.target.value })}
            options={[
              { label: 'Shopify', value: 'shopify' },
              { label: 'WooCommerce', value: 'woocommerce' },
              { label: 'Custom', value: 'custom' },
            ]}
          />
          <Input
            label="Total Amount"
            type="number"
            value={formData.total_amount}
            onChange={(e) => setFormData({ ...formData, total_amount: parseFloat(e.target.value) })}
            min="0"
            step="0.01"
            required
          />
          <div className="flex gap-3 pt-4">
            <Button type="submit">Create Order</Button>
            <Button variant="secondary" onClick={() => setShowModal(false)}>
              Cancel
            </Button>
          </div>
        </form>
      </Modal>
    </AdminLayout>
  );
};

export default OrdersPage;
