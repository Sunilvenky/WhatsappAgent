import { useState, useEffect } from 'react'
import axios from 'axios'
import {
  Users,
  Search,
  Plus,
  Upload,
  Download,
  Edit,
  Trash2,
  Mail,
  Phone,
  MapPin,
  Filter,
  X
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function Contacts() {
  const [contacts, setContacts] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [showAddModal, setShowAddModal] = useState(false)
  const [editingContact, setEditingContact] = useState(null)

  useEffect(() => {
    fetchContacts()
  }, [])

  const fetchContacts = async () => {
    try {
      const response = await axios.get('/api/v1/contacts')
      setContacts(response.data)
    } catch (error) {
      console.error('Failed to fetch contacts:', error)
      // Mock data for demo
      setContacts([
        { id: 1, name: 'John Doe', phone: '+1234567890', email: 'john@example.com', tags: ['customer', 'premium'], created_at: '2024-01-15' },
        { id: 2, name: 'Jane Smith', phone: '+1234567891', email: 'jane@example.com', tags: ['lead'], created_at: '2024-01-16' },
        { id: 3, name: 'Bob Johnson', phone: '+1234567892', email: 'bob@example.com', tags: ['customer'], created_at: '2024-01-17' },
      ])
    } finally {
      setLoading(false)
    }
  }

  const filteredContacts = contacts.filter(contact =>
    contact.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    contact.phone.includes(searchQuery) ||
    contact.email?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this contact?')) return
    
    try {
      await axios.delete(`/api/v1/contacts/${id}`)
      toast.success('Contact deleted successfully')
      fetchContacts()
    } catch (error) {
      toast.error('Failed to delete contact')
    }
  }

  return (
    <div className="space-y-6 animate-slideIn">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Contacts</h1>
          <p className="text-slate-600 mt-1">Manage your WhatsApp contact list</p>
        </div>
        <div className="flex gap-3">
          <button className="btn-secondary">
            <Upload className="w-4 h-4 mr-2" />
            Import CSV
          </button>
          <button className="btn-secondary">
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="btn-primary"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Contact
          </button>
        </div>
      </div>

      {/* Search & Filter */}
      <div className="card">
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search contacts by name, phone, or email..."
              className="input pl-10 w-full"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <button className="btn-secondary">
            <Filter className="w-4 h-4 mr-2" />
            Filter
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <p className="text-sm text-slate-600">Total Contacts</p>
          <p className="text-2xl font-bold text-slate-900">{contacts.length}</p>
        </div>
        <div className="card">
          <p className="text-sm text-slate-600">Active</p>
          <p className="text-2xl font-bold text-green-600">{contacts.length - 5}</p>
        </div>
        <div className="card">
          <p className="text-sm text-slate-600">Leads</p>
          <p className="text-2xl font-bold text-blue-600">42</p>
        </div>
        <div className="card">
          <p className="text-sm text-slate-600">Customers</p>
          <p className="text-2xl font-bold text-purple-600">156</p>
        </div>
      </div>

      {/* Contacts Table */}
      <div className="card">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-whatsapp"></div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Name</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Phone</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Email</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Tags</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Added</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-slate-700">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredContacts.map((contact) => (
                  <tr key={contact.id} className="border-b border-slate-100 hover:bg-slate-50">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-whatsapp to-green-600 rounded-full flex items-center justify-center text-white font-semibold">
                          {contact.name.charAt(0)}
                        </div>
                        <span className="font-medium text-slate-900">{contact.name}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-slate-600">{contact.phone}</td>
                    <td className="py-3 px-4 text-slate-600">{contact.email || '-'}</td>
                    <td className="py-3 px-4">
                      <div className="flex gap-1">
                        {contact.tags?.map((tag, idx) => (
                          <span key={idx} className="badge-primary text-xs">{tag}</span>
                        ))}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-slate-600">{contact.created_at}</td>
                    <td className="py-3 px-4">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => setEditingContact(contact)}
                          className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(contact.id)}
                          className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add/Edit Modal */}
      {(showAddModal || editingContact) && (
        <ContactModal
          contact={editingContact}
          onClose={() => {
            setShowAddModal(false)
            setEditingContact(null)
          }}
          onSave={() => {
            fetchContacts()
            setShowAddModal(false)
            setEditingContact(null)
          }}
        />
      )}
    </div>
  )
}

function ContactModal({ contact, onClose, onSave }) {
  const [formData, setFormData] = useState(contact || {
    name: '',
    phone: '',
    email: '',
    tags: '',
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    try {
      if (contact) {
        await axios.put(`/api/v1/contacts/${contact.id}`, formData)
        toast.success('Contact updated successfully')
      } else {
        await axios.post('/api/v1/contacts', formData)
        toast.success('Contact created successfully')
      }
      onSave()
    } catch (error) {
      toast.error('Failed to save contact')
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-slate-200">
          <h2 className="text-xl font-bold text-slate-900">
            {contact ? 'Edit Contact' : 'Add New Contact'}
          </h2>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Full Name *
            </label>
            <input
              type="text"
              required
              className="input w-full"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Phone Number *
            </label>
            <input
              type="tel"
              required
              className="input w-full"
              placeholder="+1234567890"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Email
            </label>
            <input
              type="email"
              className="input w-full"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Tags (comma-separated)
            </label>
            <input
              type="text"
              className="input w-full"
              placeholder="customer, premium, lead"
              value={formData.tags}
              onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary flex-1"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-primary flex-1"
            >
              {contact ? 'Update' : 'Create'} Contact
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
