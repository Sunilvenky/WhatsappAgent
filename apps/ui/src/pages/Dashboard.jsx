import { useState, useEffect } from 'react'
import axios from 'axios'
import {
  Users,
  MessageSquare,
  TrendingUp,
  Target,
  Send,
  BarChart3,
  Zap,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardStats()
  }, [])

  const fetchDashboardStats = async () => {
    try {
      const response = await axios.get('/api/v1/analytics/dashboard')
      setStats(response.data)
    } catch (error) {
      console.error('Failed to fetch stats:', error)
      // Use mock data for demo
      setStats({
        total_contacts: 1247,
        total_messages: 5834,
        total_campaigns: 12,
        active_campaigns: 3,
        total_leads: 324,
        hot_leads: 45,
        messages_sent_today: 142,
        messages_sent_this_week: 856,
        delivery_rate: 98.5,
        read_rate: 76.3,
        response_rate: 34.8,
        avg_lead_score: 67.5
      })
    } finally {
      setLoading(false)
    }
  }

  // Mock data for charts
  const messageData = [
    { day: 'Mon', sent: 120, delivered: 118, read: 95 },
    { day: 'Tue', sent: 150, delivered: 148, read: 112 },
    { day: 'Wed', sent: 180, delivered: 176, read: 145 },
    { day: 'Thu', sent: 140, delivered: 138, read: 108 },
    { day: 'Fri', sent: 200, delivered: 198, read: 165 },
    { day: 'Sat', sent: 90, delivered: 89, read: 72 },
    { day: 'Sun', sent: 76, delivered: 75, read: 58 },
  ]

  const leadData = [
    { name: 'Hot', value: 45, color: '#22c55e' },
    { name: 'Warm', value: 128, color: '#eab308' },
    { name: 'Cold', value: 98, color: '#3b82f6' },
    { name: 'Unqualified', value: 53, color: '#94a3b8' },
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-whatsapp"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8 animate-slideIn">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Dashboard Overview</h1>
        <p className="text-slate-600 mt-1">Real-time insights into your WhatsApp marketing performance</p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Contacts"
          value={stats.total_contacts?.toLocaleString()}
          icon={Users}
          color="blue"
          trend="+12.5%"
        />
        <StatCard
          title="Messages Sent"
          value={stats.total_messages?.toLocaleString()}
          icon={MessageSquare}
          color="green"
          trend="+8.3%"
        />
        <StatCard
          title="Active Campaigns"
          value={stats.active_campaigns}
          icon={Target}
          color="purple"
          subtitle={`${stats.total_campaigns} total`}
        />
        <StatCard
          title="Hot Leads"
          value={stats.hot_leads}
          icon={TrendingUp}
          color="orange"
          subtitle={`${stats.total_leads} total leads`}
        />
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard
          title="Delivery Rate"
          value={`${stats.delivery_rate}%`}
          icon={CheckCircle}
          color="green"
          description="Messages successfully delivered"
        />
        <MetricCard
          title="Read Rate"
          value={`${stats.read_rate}%`}
          icon={Clock}
          color="blue"
          description="Messages opened by recipients"
        />
        <MetricCard
          title="Response Rate"
          value={`${stats.response_rate}%`}
          icon={Zap}
          color="purple"
          description="Recipients who replied"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Message Activity */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-bold text-slate-900">Message Activity</h3>
              <p className="text-sm text-slate-600">Last 7 days</p>
            </div>
            <BarChart3 className="w-5 h-5 text-slate-400" />
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={messageData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="day" stroke="#64748b" />
              <YAxis stroke="#64748b" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'white', 
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                }}
              />
              <Line type="monotone" dataKey="sent" stroke="#22c55e" strokeWidth={2} dot={{ fill: '#22c55e', r: 4 }} />
              <Line type="monotone" dataKey="delivered" stroke="#3b82f6" strokeWidth={2} dot={{ fill: '#3b82f6', r: 4 }} />
              <Line type="monotone" dataKey="read" stroke="#a855f7" strokeWidth={2} dot={{ fill: '#a855f7', r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
          <div className="flex items-center justify-center gap-6 mt-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-whatsapp rounded-full"></div>
              <span className="text-sm text-slate-600">Sent</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <span className="text-sm text-slate-600">Delivered</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
              <span className="text-sm text-slate-600">Read</span>
            </div>
          </div>
        </div>

        {/* Lead Distribution */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-bold text-slate-900">Lead Distribution</h3>
              <p className="text-sm text-slate-600">By quality tier</p>
            </div>
            <Target className="w-5 h-5 text-slate-400" />
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={leadData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" stroke="#64748b" />
              <YAxis stroke="#64748b" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'white', 
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                }}
              />
              <Bar dataKey="value" fill="#22c55e" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
          <div className="grid grid-cols-2 gap-4 mt-6">
            {leadData.map((item) => (
              <div key={item.name} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
                  <span className="text-sm font-medium text-slate-700">{item.name}</span>
                </div>
                <span className="text-sm font-bold text-slate-900">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h3 className="text-lg font-bold text-slate-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <ActionButton
            icon={Send}
            title="Create Campaign"
            description="Start a new marketing campaign"
            to="/campaigns"
          />
          <ActionButton
            icon={Users}
            title="Add Contacts"
            description="Import or create new contacts"
            to="/contacts"
          />
          <ActionButton
            icon={BarChart3}
            title="View Analytics"
            description="Deep dive into your metrics"
            to="/analytics"
          />
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h3 className="text-lg font-bold text-slate-900 mb-4">Recent Activity</h3>
        <div className="space-y-4">
          <ActivityItem
            icon={Send}
            title="Campaign 'Product Launch' started"
            time="2 minutes ago"
            status="success"
          />
          <ActivityItem
            icon={Users}
            title="50 new contacts imported from CSV"
            time="1 hour ago"
            status="success"
          />
          <ActivityItem
            icon={AlertCircle}
            title="Campaign 'Weekly Newsletter' paused - high ban risk"
            time="3 hours ago"
            status="warning"
          />
          <ActivityItem
            icon={TrendingUp}
            title="12 leads scored as 'Hot' by ML model"
            time="5 hours ago"
            status="info"
          />
        </div>
      </div>
    </div>
  )
}

function StatCard({ title, value, icon: Icon, color, trend, subtitle }) {
  const colors = {
    blue: 'bg-blue-50 text-blue-600 border-blue-200',
    green: 'bg-green-50 text-green-600 border-green-200',
    purple: 'bg-purple-50 text-purple-600 border-purple-200',
    orange: 'bg-orange-50 text-orange-600 border-orange-200',
  }

  return (
    <div className="card hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-600 mb-1">{title}</p>
          <p className="text-3xl font-bold text-slate-900">{value}</p>
          {trend && <span className="text-sm text-green-600 font-medium">{trend}</span>}
          {subtitle && <span className="text-sm text-slate-500">{subtitle}</span>}
        </div>
        <div className={`p-3 rounded-xl border ${colors[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  )
}

function MetricCard({ title, value, icon: Icon, color, description }) {
  const colors = {
    green: 'text-green-600',
    blue: 'text-blue-600',
    purple: 'text-purple-600',
  }

  return (
    <div className="card hover:shadow-md transition-shadow">
      <Icon className={`w-8 h-8 mb-3 ${colors[color]}`} />
      <h4 className="text-sm font-medium text-slate-600 mb-1">{title}</h4>
      <p className="text-2xl font-bold text-slate-900 mb-1">{value}</p>
      <p className="text-xs text-slate-500">{description}</p>
    </div>
  )
}

function ActionButton({ icon: Icon, title, description, to }) {
  return (
    <a
      href={to}
      className="flex items-start gap-4 p-4 rounded-lg border-2 border-dashed border-slate-200 hover:border-whatsapp hover:bg-green-50 transition-all group"
    >
      <div className="p-3 bg-whatsapp/10 rounded-lg group-hover:bg-whatsapp group-hover:text-white transition-colors">
        <Icon className="w-5 h-5 text-whatsapp group-hover:text-white" />
      </div>
      <div>
        <h4 className="font-semibold text-slate-900 mb-1">{title}</h4>
        <p className="text-sm text-slate-600">{description}</p>
      </div>
    </a>
  )
}

function ActivityItem({ icon: Icon, title, time, status }) {
  const statusColors = {
    success: 'bg-green-100 text-green-700',
    warning: 'bg-yellow-100 text-yellow-700',
    info: 'bg-blue-100 text-blue-700',
  }

  return (
    <div className="flex items-start gap-4 p-4 bg-slate-50 rounded-lg">
      <div className={`p-2 rounded-lg ${statusColors[status]}`}>
        <Icon className="w-4 h-4" />
      </div>
      <div className="flex-1">
        <p className="font-medium text-slate-900">{title}</p>
        <p className="text-sm text-slate-500">{time}</p>
      </div>
    </div>
  )
}
