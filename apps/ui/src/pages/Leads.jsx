import { useState, useEffect } from 'react'
import axios from 'axios'
import {
  Target,
  TrendingUp,
  TrendingDown,
  Award,
  Filter,
  Download,
  Star,
  Flame,
  Droplet,
  Snowflake
} from 'lucide-react'

export default function Leads() {
  const [leads, setLeads] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    fetchLeads()
  }, [])

  const fetchLeads = async () => {
    try {
      const response = await axios.get('/api/v1/leads')
      setLeads(response.data)
    } catch (error) {
      console.error('Failed to fetch leads:', error)
      // Mock data
      setLeads([
        {
          id: 1,
          contact_name: 'Sarah Williams',
          contact_phone: '+1234567890',
          email: 'sarah@example.com',
          lead_score: 89.5,
          quality: 'hot',
          last_interaction: '2 hours ago',
          engagement_rate: 76.3,
          response_time: '5 min',
          tags: ['premium', 'interested']
        },
        {
          id: 2,
          contact_name: 'Mike Brown',
          contact_phone: '+1234567891',
          email: 'mike@example.com',
          lead_score: 72.8,
          quality: 'warm',
          last_interaction: '1 day ago',
          engagement_rate: 54.2,
          response_time: '15 min',
          tags: ['potential']
        },
        {
          id: 3,
          contact_name: 'Lisa Anderson',
          contact_phone: '+1234567892',
          email: 'lisa@example.com',
          lead_score: 45.2,
          quality: 'cold',
          last_interaction: '5 days ago',
          engagement_rate: 23.1,
          response_time: '2 hours',
          tags: ['follow-up']
        },
        {
          id: 4,
          contact_name: 'David Martinez',
          contact_phone: '+1234567893',
          email: 'david@example.com',
          lead_score: 91.3,
          quality: 'hot',
          last_interaction: '30 min ago',
          engagement_rate: 84.5,
          response_time: '2 min',
          tags: ['premium', 'ready-to-buy']
        },
        {
          id: 5,
          contact_name: 'Emma Wilson',
          contact_phone: '+1234567894',
          email: 'emma@example.com',
          lead_score: 67.4,
          quality: 'warm',
          last_interaction: '3 hours ago',
          engagement_rate: 61.8,
          response_time: '10 min',
          tags: ['interested']
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const getQualityIcon = (quality) => {
    const icons = {
      hot: { icon: Flame, color: 'text-red-600', bg: 'bg-red-100' },
      warm: { icon: Droplet, color: 'text-orange-600', bg: 'bg-orange-100' },
      cold: { icon: Snowflake, color: 'text-blue-600', bg: 'bg-blue-100' },
    }
    return icons[quality] || icons.cold
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-orange-600'
    return 'text-slate-600'
  }

  const filteredLeads = leads.filter(lead => 
    filter === 'all' || lead.quality === filter
  )

  return (
    <div className="space-y-6 animate-slideIn">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Lead Scoring</h1>
          <p className="text-slate-600 mt-1">AI-powered lead quality assessment and prioritization</p>
        </div>
        <button className="btn-secondary">
          <Download className="w-4 h-4 mr-2" />
          Export Leads
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-red-100 rounded-lg">
              <Flame className="w-6 h-6 text-red-600" />
            </div>
            <div>
              <p className="text-sm text-slate-600">Hot Leads</p>
              <p className="text-2xl font-bold text-red-600">
                {leads.filter(l => l.quality === 'hot').length}
              </p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-orange-100 rounded-lg">
              <Droplet className="w-6 h-6 text-orange-600" />
            </div>
            <div>
              <p className="text-sm text-slate-600">Warm Leads</p>
              <p className="text-2xl font-bold text-orange-600">
                {leads.filter(l => l.quality === 'warm').length}
              </p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Snowflake className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-slate-600">Cold Leads</p>
              <p className="text-2xl font-bold text-blue-600">
                {leads.filter(l => l.quality === 'cold').length}
              </p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-purple-100 rounded-lg">
              <Award className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-slate-600">Avg Score</p>
              <p className="text-2xl font-bold text-purple-600">
                {(leads.reduce((sum, l) => sum + l.lead_score, 0) / leads.length).toFixed(1)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filter */}
      <div className="card">
        <div className="flex items-center gap-4">
          <Filter className="w-5 h-5 text-slate-400" />
          <div className="flex gap-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === 'all'
                  ? 'bg-whatsapp text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              All Leads
            </button>
            <button
              onClick={() => setFilter('hot')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === 'hot'
                  ? 'bg-red-600 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              🔥 Hot
            </button>
            <button
              onClick={() => setFilter('warm')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === 'warm'
                  ? 'bg-orange-600 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              💧 Warm
            </button>
            <button
              onClick={() => setFilter('cold')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === 'cold'
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              ❄️ Cold
            </button>
          </div>
        </div>
      </div>

      {/* Leads List */}
      <div className="space-y-4">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-whatsapp"></div>
          </div>
        ) : (
          filteredLeads.map((lead) => {
            const qualityConfig = getQualityIcon(lead.quality)
            const QualityIcon = qualityConfig.icon

            return (
              <div key={lead.id} className="card hover:shadow-lg transition-shadow">
                <div className="flex items-start gap-6">
                  {/* Avatar & Quality */}
                  <div className="flex flex-col items-center gap-2">
                    <div className="w-16 h-16 bg-gradient-to-br from-whatsapp to-green-600 rounded-full flex items-center justify-center text-white text-xl font-semibold">
                      {lead.contact_name.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div className={`p-2 rounded-lg ${qualityConfig.bg}`}>
                      <QualityIcon className={`w-5 h-5 ${qualityConfig.color}`} />
                    </div>
                  </div>

                  {/* Info */}
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="text-xl font-bold text-slate-900">{lead.contact_name}</h3>
                        <p className="text-slate-600">{lead.contact_phone}</p>
                        <p className="text-sm text-slate-500">{lead.email}</p>
                      </div>

                      {/* Lead Score */}
                      <div className="text-right">
                        <div className="flex items-center gap-2 mb-1">
                          <Star className={`w-5 h-5 ${getScoreColor(lead.lead_score)}`} />
                          <span className={`text-3xl font-bold ${getScoreColor(lead.lead_score)}`}>
                            {lead.lead_score}
                          </span>
                        </div>
                        <p className="text-sm text-slate-600">Lead Score</p>
                      </div>
                    </div>

                    {/* Tags */}
                    <div className="flex gap-2 mb-4">
                      {lead.tags.map((tag, idx) => (
                        <span key={idx} className="badge-primary text-xs">{tag}</span>
                      ))}
                    </div>

                    {/* Metrics */}
                    <div className="grid grid-cols-3 gap-4">
                      <div className="bg-slate-50 rounded-lg p-3">
                        <p className="text-xs text-slate-600 mb-1">Engagement Rate</p>
                        <div className="flex items-center gap-2">
                          <p className="text-lg font-bold text-slate-900">{lead.engagement_rate}%</p>
                          {lead.engagement_rate > 60 ? (
                            <TrendingUp className="w-4 h-4 text-green-600" />
                          ) : (
                            <TrendingDown className="w-4 h-4 text-red-600" />
                          )}
                        </div>
                      </div>

                      <div className="bg-slate-50 rounded-lg p-3">
                        <p className="text-xs text-slate-600 mb-1">Response Time</p>
                        <p className="text-lg font-bold text-slate-900">{lead.response_time}</p>
                      </div>

                      <div className="bg-slate-50 rounded-lg p-3">
                        <p className="text-xs text-slate-600 mb-1">Last Interaction</p>
                        <p className="text-lg font-bold text-slate-900">{lead.last_interaction}</p>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-3 mt-4">
                      <button className="btn-primary flex-1">
                        Send Message
                      </button>
                      <button className="btn-secondary flex-1">
                        View History
                      </button>
                      <button className="btn-secondary">
                        More
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )
          })
        )}
      </div>

      {/* ML Info */}
      <div className="card bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-purple-600 rounded-xl">
            <Target className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-bold text-slate-900 mb-2">
              🤖 AI Lead Scoring Powered by Machine Learning
            </h3>
            <p className="text-slate-700 mb-3">
              Our ML model analyzes engagement patterns, response times, conversation sentiment, and interaction history to automatically score and categorize your leads. Focus on hot leads for maximum conversion rates.
            </p>
            <div className="flex gap-4 text-sm">
              <div>
                <span className="font-semibold text-green-700">Hot (80-100):</span>
                <span className="text-slate-700"> Ready to convert</span>
              </div>
              <div>
                <span className="font-semibold text-orange-700">Warm (60-79):</span>
                <span className="text-slate-700"> Needs nurturing</span>
              </div>
              <div>
                <span className="font-semibold text-blue-700">Cold (0-59):</span>
                <span className="text-slate-700"> Long-term follow-up</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
