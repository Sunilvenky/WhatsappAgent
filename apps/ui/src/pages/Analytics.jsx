import { useState } from 'react'
import {
  BarChart3,
  TrendingUp,
  MessageSquare,
  Users,
  Target,
  Clock,
  Calendar
} from 'lucide-react'
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function Analytics() {
  const [timeRange, setTimeRange] = useState('7d')

  // Mock data
  const messageVolumeData = [
    { date: 'Jan 15', sent: 245, delivered: 242, read: 198, replied: 67 },
    { date: 'Jan 16', sent: 312, delivered: 308, read: 254, replied: 89 },
    { date: 'Jan 17', sent: 289, delivered: 285, read: 234, replied: 78 },
    { date: 'Jan 18', sent: 356, delivered: 351, read: 289, replied: 102 },
    { date: 'Jan 19', sent: 423, delivered: 418, read: 345, replied: 125 },
    { date: 'Jan 20', sent: 378, delivered: 374, read: 312, replied: 98 },
    { date: 'Jan 21', sent: 401, delivered: 396, read: 328, replied: 115 },
  ]

  const campaignPerformanceData = [
    { name: 'Product Launch', sent: 1200, delivered: 1185, read: 967, replied: 256 },
    { name: 'Flash Sale', sent: 850, delivered: 842, read: 689, replied: 178 },
    { name: 'Newsletter', sent: 2100, delivered: 2076, read: 1678, replied: 423 },
    { name: 'Follow-up', sent: 450, delivered: 445, read: 362, replied: 89 },
  ]

  const leadDistributionData = [
    { name: 'Hot Leads', value: 45, color: '#ef4444' },
    { name: 'Warm Leads', value: 128, color: '#f97316' },
    { name: 'Cold Leads', value: 98, color: '#3b82f6' },
    { name: 'Unqualified', value: 53, color: '#94a3b8' },
  ]

  const responseTimeData = [
    { time: '0-5 min', count: 245 },
    { time: '5-15 min', count: 189 },
    { time: '15-30 min', count: 123 },
    { time: '30-60 min', count: 78 },
    { time: '1+ hour', count: 45 },
  ]

  return (
    <div className="space-y-6 animate-slideIn">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Analytics & Reports</h1>
          <p className="text-slate-600 mt-1">Deep insights into your WhatsApp marketing performance</p>
        </div>
        <select
          className="input"
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
        >
          <option value="24h">Last 24 Hours</option>
          <option value="7d">Last 7 Days</option>
          <option value="30d">Last 30 Days</option>
          <option value="90d">Last 90 Days</option>
        </select>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          title="Total Messages"
          value="5,834"
          change="+12.5%"
          trend="up"
          icon={MessageSquare}
          color="green"
        />
        <MetricCard
          title="Delivery Rate"
          value="98.7%"
          change="+1.2%"
          trend="up"
          icon={Target}
          color="blue"
        />
        <MetricCard
          title="Response Rate"
          value="34.8%"
          change="+5.3%"
          trend="up"
          icon={TrendingUp}
          color="purple"
        />
        <MetricCard
          title="Active Users"
          value="1,247"
          change="+8.7%"
          trend="up"
          icon={Users}
          color="orange"
        />
      </div>

      {/* Message Volume Chart */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold text-slate-900">Message Volume Trends</h2>
            <p className="text-sm text-slate-600">Daily message activity breakdown</p>
          </div>
          <BarChart3 className="w-6 h-6 text-slate-400" />
        </div>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={messageVolumeData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="date" stroke="#64748b" />
            <YAxis stroke="#64748b" />
            <Tooltip
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
              }}
            />
            <Legend />
            <Line type="monotone" dataKey="sent" stroke="#22c55e" strokeWidth={2} name="Sent" />
            <Line type="monotone" dataKey="delivered" stroke="#3b82f6" strokeWidth={2} name="Delivered" />
            <Line type="monotone" dataKey="read" stroke="#a855f7" strokeWidth={2} name="Read" />
            <Line type="monotone" dataKey="replied" stroke="#f97316" strokeWidth={2} name="Replied" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Campaign Performance & Lead Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Campaign Performance */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-slate-900">Campaign Performance</h2>
              <p className="text-sm text-slate-600">Compare campaign results</p>
            </div>
            <Target className="w-6 h-6 text-slate-400" />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={campaignPerformanceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" stroke="#64748b" angle={-15} textAnchor="end" height={80} />
              <YAxis stroke="#64748b" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                }}
              />
              <Legend />
              <Bar dataKey="sent" fill="#22c55e" radius={[8, 8, 0, 0]} name="Sent" />
              <Bar dataKey="read" fill="#3b82f6" radius={[8, 8, 0, 0]} name="Read" />
              <Bar dataKey="replied" fill="#a855f7" radius={[8, 8, 0, 0]} name="Replied" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Lead Distribution */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-slate-900">Lead Distribution</h2>
              <p className="text-sm text-slate-600">Quality breakdown</p>
            </div>
            <Users className="w-6 h-6 text-slate-400" />
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={leadDistributionData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {leadDistributionData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="grid grid-cols-2 gap-3 mt-4">
            {leadDistributionData.map((item) => (
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

      {/* Response Time Distribution */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold text-slate-900">Response Time Distribution</h2>
            <p className="text-sm text-slate-600">How quickly contacts respond</p>
          </div>
          <Clock className="w-6 h-6 text-slate-400" />
        </div>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={responseTimeData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis type="number" stroke="#64748b" />
            <YAxis dataKey="time" type="category" stroke="#64748b" />
            <Tooltip
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
              }}
            />
            <Bar dataKey="count" fill="#22c55e" radius={[0, 8, 8, 0]} name="Responses" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Export Section */}
      <div className="card bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-slate-900 mb-1">Export Analytics Report</h3>
            <p className="text-slate-700">Download detailed reports in PDF or CSV format</p>
          </div>
          <div className="flex gap-3">
            <button className="btn-secondary">
              Export PDF
            </button>
            <button className="btn-primary">
              Export CSV
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

function MetricCard({ title, value, change, trend, icon: Icon, color }) {
  const colors = {
    green: 'bg-green-50 text-green-600 border-green-200',
    blue: 'bg-blue-50 text-blue-600 border-blue-200',
    purple: 'bg-purple-50 text-purple-600 border-purple-200',
    orange: 'bg-orange-50 text-orange-600 border-orange-200',
  }

  return (
    <div className="card hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className={`p-3 rounded-xl border ${colors[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
        <span className={`text-sm font-medium ${trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
          {change}
        </span>
      </div>
      <p className="text-sm font-medium text-slate-600 mb-1">{title}</p>
      <p className="text-3xl font-bold text-slate-900">{value}</p>
    </div>
  )
}
