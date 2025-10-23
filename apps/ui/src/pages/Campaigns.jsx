import { useState, useEffect } from 'react'
import axios from 'axios'
import {
  Megaphone,
  Plus,
  Play,
  Pause,
  Edit,
  Trash2,
  Users,
  MessageSquare,
  TrendingUp,
  Calendar,
  Clock,
  Target,
  Sparkles
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function Campaigns() {
  const [campaigns, setCampaigns] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)

  useEffect(() => {
    fetchCampaigns()
  }, [])

  const fetchCampaigns = async () => {
    try {
      const response = await axios.get('/api/v1/campaigns')
      setCampaigns(response.data)
    } catch (error) {
      console.error('Failed to fetch campaigns:', error)
      // Mock data
      setCampaigns([
        {
          id: 1,
          name: 'Product Launch',
          status: 'active',
          total_contacts: 1200,
          messages_sent: 856,
          delivered: 842,
          read: 678,
          replied: 143,
          created_at: '2024-01-15',
          scheduled_at: '2024-01-20 10:00'
        },
        {
          id: 2,
          name: 'Weekly Newsletter',
          status: 'paused',
          total_contacts: 850,
          messages_sent: 234,
          delivered: 230,
          read: 189,
          replied: 45,
          created_at: '2024-01-10',
          scheduled_at: null
        },
        {
          id: 3,
          name: 'Flash Sale',
          status: 'scheduled',
          total_contacts: 2500,
          messages_sent: 0,
          delivered: 0,
          read: 0,
          replied: 0,
          created_at: '2024-01-18',
          scheduled_at: '2024-01-25 09:00'
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleToggleStatus = async (campaign) => {
    try {
      const newStatus = campaign.status === 'active' ? 'paused' : 'active'
      await axios.patch(`/api/v1/campaigns/${campaign.id}/status`, { status: newStatus })
      toast.success(`Campaign ${newStatus}`)
      fetchCampaigns()
    } catch (error) {
      toast.error('Failed to update campaign status')
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this campaign?')) return
    
    try {
      await axios.delete(`/api/v1/campaigns/${id}`)
      toast.success('Campaign deleted')
      fetchCampaigns()
    } catch (error) {
      toast.error('Failed to delete campaign')
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      active: 'badge-success',
      paused: 'badge-warning',
      scheduled: 'badge-info',
      completed: 'badge-secondary',
    }
    return colors[status] || 'badge-secondary'
  }

  return (
    <div className="space-y-6 animate-slideIn">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Campaigns</h1>
          <p className="text-slate-600 mt-1">Create and manage your WhatsApp marketing campaigns</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary"
        >
          <Plus className="w-4 h-4 mr-2" />
          Create Campaign
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Megaphone className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-slate-600">Total Campaigns</p>
              <p className="text-2xl font-bold text-slate-900">{campaigns.length}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-100 rounded-lg">
              <Play className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-slate-600">Active</p>
              <p className="text-2xl font-bold text-green-600">
                {campaigns.filter(c => c.status === 'active').length}
              </p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-purple-100 rounded-lg">
              <MessageSquare className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-slate-600">Messages Sent</p>
              <p className="text-2xl font-bold text-purple-600">
                {campaigns.reduce((sum, c) => sum + c.messages_sent, 0).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-orange-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-orange-600" />
            </div>
            <div>
              <p className="text-sm text-slate-600">Avg Response Rate</p>
              <p className="text-2xl font-bold text-orange-600">34.8%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Campaigns List */}
      <div className="space-y-4">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-whatsapp"></div>
          </div>
        ) : (
          campaigns.map((campaign) => (
            <div key={campaign.id} className="card hover:shadow-lg transition-shadow">
              <div className="flex items-start gap-6">
                {/* Icon */}
                <div className="p-4 bg-gradient-to-br from-whatsapp to-green-600 rounded-xl">
                  <Megaphone className="w-8 h-8 text-white" />
                </div>

                {/* Info */}
                <div className="flex-1">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="text-xl font-bold text-slate-900">{campaign.name}</h3>
                      <div className="flex items-center gap-3 mt-2">
                        <span className={`badge ${getStatusColor(campaign.status)}`}>
                          {campaign.status}
                        </span>
                        {campaign.scheduled_at && (
                          <span className="text-sm text-slate-600 flex items-center gap-1">
                            <Clock className="w-4 h-4" />
                            Scheduled: {campaign.scheduled_at}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2">
                      {campaign.status !== 'completed' && (
                        <button
                          onClick={() => handleToggleStatus(campaign)}
                          className="p-2 text-slate-400 hover:text-whatsapp hover:bg-green-50 rounded-lg transition-colors"
                        >
                          {campaign.status === 'active' ? (
                            <Pause className="w-5 h-5" />
                          ) : (
                            <Play className="w-5 h-5" />
                          )}
                        </button>
                      )}
                      <button className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                        <Edit className="w-5 h-5" />
                      </button>
                      <button
                        onClick={() => handleDelete(campaign.id)}
                        className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="grid grid-cols-5 gap-4">
                    <StatItem
                      label="Contacts"
                      value={campaign.total_contacts}
                      icon={Users}
                    />
                    <StatItem
                      label="Sent"
                      value={campaign.messages_sent}
                      icon={MessageSquare}
                    />
                    <StatItem
                      label="Delivered"
                      value={campaign.delivered}
                      percent={(campaign.delivered / campaign.messages_sent * 100).toFixed(1)}
                    />
                    <StatItem
                      label="Read"
                      value={campaign.read}
                      percent={(campaign.read / campaign.messages_sent * 100).toFixed(1)}
                    />
                    <StatItem
                      label="Replied"
                      value={campaign.replied}
                      percent={(campaign.replied / campaign.messages_sent * 100).toFixed(1)}
                    />
                  </div>

                  {/* Progress Bar */}
                  {campaign.status === 'active' && campaign.messages_sent > 0 && (
                    <div className="mt-4">
                      <div className="flex items-center justify-between text-sm text-slate-600 mb-1">
                        <span>Progress</span>
                        <span>{Math.round(campaign.messages_sent / campaign.total_contacts * 100)}%</span>
                      </div>
                      <div className="w-full bg-slate-200 rounded-full h-2">
                        <div
                          className="bg-gradient-to-r from-whatsapp to-green-600 h-2 rounded-full transition-all"
                          style={{ width: `${Math.round(campaign.messages_sent / campaign.total_contacts * 100)}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Create Campaign Modal */}
      {showCreateModal && (
        <CreateCampaignModal
          onClose={() => setShowCreateModal(false)}
          onSave={() => {
            fetchCampaigns()
            setShowCreateModal(false)
          }}
        />
      )}
    </div>
  )
}

function StatItem({ label, value, percent, icon: Icon }) {
  return (
    <div className="text-center">
      {Icon && <Icon className="w-4 h-4 text-slate-400 mx-auto mb-1" />}
      <p className="text-lg font-bold text-slate-900">{value}</p>
      <p className="text-xs text-slate-600">{label}</p>
      {percent && <p className="text-xs text-whatsapp font-medium">{percent}%</p>}
    </div>
  )
}

function CreateCampaignModal({ onClose, onSave }) {
  const [formData, setFormData] = useState({
    name: '',
    message: '',
    contacts: 'all',
    schedule_type: 'immediate',
    scheduled_at: '',
  })

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    try {
      await axios.post('/api/v1/campaigns', formData)
      toast.success('Campaign created successfully')
      onSave()
    } catch (error) {
      toast.error('Failed to create campaign')
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-slate-200">
          <h2 className="text-xl font-bold text-slate-900">Create New Campaign</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <Plus className="w-5 h-5 rotate-45" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Campaign Name *
            </label>
            <input
              type="text"
              required
              className="input w-full"
              placeholder="e.g., Summer Sale 2024"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Message *
            </label>
            <textarea
              required
              className="input w-full"
              rows="6"
              placeholder="Your message to customers..."
              value={formData.message}
              onChange={(e) => setFormData({ ...formData, message: e.target.value })}
            />
            <button
              type="button"
              className="text-sm text-whatsapp hover:text-green-700 mt-2 flex items-center gap-1"
            >
              <Sparkles className="w-4 h-4" />
              AI Rewrite Message
            </button>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Target Contacts
            </label>
            <select
              className="input w-full"
              value={formData.contacts}
              onChange={(e) => setFormData({ ...formData, contacts: e.target.value })}
            >
              <option value="all">All Contacts</option>
              <option value="customers">Customers Only</option>
              <option value="leads">Leads Only</option>
              <option value="custom">Custom Selection</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Schedule
            </label>
            <select
              className="input w-full"
              value={formData.schedule_type}
              onChange={(e) => setFormData({ ...formData, schedule_type: e.target.value })}
            >
              <option value="immediate">Send Immediately</option>
              <option value="scheduled">Schedule for Later</option>
            </select>
          </div>

          {formData.schedule_type === 'scheduled' && (
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Schedule Date & Time
              </label>
              <input
                type="datetime-local"
                className="input w-full"
                value={formData.scheduled_at}
                onChange={(e) => setFormData({ ...formData, scheduled_at: e.target.value })}
              />
            </div>
          )}

          <div className="flex gap-3 pt-4">
            <button type="button" onClick={onClose} className="btn-secondary flex-1">
              Cancel
            </button>
            <button type="submit" className="btn-primary flex-1">
              Create Campaign
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
