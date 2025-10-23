import { useState } from 'react'
import { User, Mail, Phone, Save, Bell, Palette, Shield, Trash2, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'

export default function Settings() {
  const [activeTab, setActiveTab] = useState('profile')
  const [profile, setProfile] = useState({
    name: 'Admin User',
    email: 'admin@example.com',
    phone: '+1234567890',
    company: 'My Company'
  })

  const [notifications, setNotifications] = useState({
    emailNotifications: true,
    campaignUpdates: true,
    leadAlerts: true,
    messageNotifications: false,
    weeklyReport: true
  })

  const handleSaveProfile = () => {
    toast.success('Profile updated successfully!')
  }

  const handleSaveNotifications = () => {
    toast.success('Notification preferences saved!')
  }

  const tabs = [
    { id: 'profile', name: 'Profile', icon: User },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'whatsapp', name: 'WhatsApp', icon: Phone },
    { id: 'security', name: 'Security', icon: Shield },
    { id: 'danger', name: 'Danger Zone', icon: AlertCircle },
  ]

  return (
    <div className="space-y-6 animate-slideIn">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Settings</h1>
        <p className="text-slate-600 mt-1">Manage your account and preferences</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200">
        <div className="flex gap-1">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-whatsapp text-whatsapp'
                    : 'border-transparent text-slate-600 hover:text-slate-900'
                }`}
              >
                <Icon className="w-5 h-5" />
                {tab.name}
              </button>
            )
          })}
        </div>
      </div>

      {/* Content */}
      {activeTab === 'profile' && (
        <div className="card">
          <h2 className="text-xl font-bold text-slate-900 mb-6">Profile Information</h2>
          
          <div className="space-y-6">
            {/* Avatar */}
            <div className="flex items-center gap-6">
              <div className="w-24 h-24 bg-gradient-to-br from-whatsapp to-green-600 rounded-full flex items-center justify-center text-white text-3xl font-semibold">
                {profile.name.split(' ').map(n => n[0]).join('')}
              </div>
              <div>
                <button className="btn-secondary mb-2">Change Avatar</button>
                <p className="text-sm text-slate-600">JPG, PNG or GIF. Max 2MB</p>
              </div>
            </div>

            {/* Form */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Full Name
                </label>
                <input
                  type="text"
                  className="input w-full"
                  value={profile.name}
                  onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Email Address
                </label>
                <input
                  type="email"
                  className="input w-full"
                  value={profile.email}
                  onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Phone Number
                </label>
                <input
                  type="tel"
                  className="input w-full"
                  value={profile.phone}
                  onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Company Name
                </label>
                <input
                  type="text"
                  className="input w-full"
                  value={profile.company}
                  onChange={(e) => setProfile({ ...profile, company: e.target.value })}
                />
              </div>
            </div>

            <button onClick={handleSaveProfile} className="btn-primary">
              <Save className="w-4 h-4 mr-2" />
              Save Changes
            </button>
          </div>
        </div>
      )}

      {activeTab === 'notifications' && (
        <div className="card">
          <h2 className="text-xl font-bold text-slate-900 mb-6">Notification Preferences</h2>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
              <div>
                <h4 className="font-semibold text-slate-900">Email Notifications</h4>
                <p className="text-sm text-slate-600">Receive email updates about your account</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={notifications.emailNotifications}
                  onChange={(e) => setNotifications({ ...notifications, emailNotifications: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-slate-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-whatsapp"></div>
              </label>
            </div>

            <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
              <div>
                <h4 className="font-semibold text-slate-900">Campaign Updates</h4>
                <p className="text-sm text-slate-600">Get notified when campaigns start or complete</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={notifications.campaignUpdates}
                  onChange={(e) => setNotifications({ ...notifications, campaignUpdates: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-slate-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-whatsapp"></div>
              </label>
            </div>

            <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
              <div>
                <h4 className="font-semibold text-slate-900">Lead Alerts</h4>
                <p className="text-sm text-slate-600">Instant alerts for hot leads</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={notifications.leadAlerts}
                  onChange={(e) => setNotifications({ ...notifications, leadAlerts: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-slate-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-whatsapp"></div>
              </label>
            </div>

            <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
              <div>
                <h4 className="font-semibold text-slate-900">Message Notifications</h4>
                <p className="text-sm text-slate-600">Push notifications for new messages</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={notifications.messageNotifications}
                  onChange={(e) => setNotifications({ ...notifications, messageNotifications: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-slate-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-whatsapp"></div>
              </label>
            </div>

            <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
              <div>
                <h4 className="font-semibold text-slate-900">Weekly Report</h4>
                <p className="text-sm text-slate-600">Receive weekly performance summary</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={notifications.weeklyReport}
                  onChange={(e) => setNotifications({ ...notifications, weeklyReport: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-slate-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-whatsapp"></div>
              </label>
            </div>

            <button onClick={handleSaveNotifications} className="btn-primary">
              <Save className="w-4 h-4 mr-2" />
              Save Preferences
            </button>
          </div>
        </div>
      )}

      {activeTab === 'whatsapp' && (
        <div className="space-y-6">
          <div className="card">
            <h2 className="text-xl font-bold text-slate-900 mb-4">WhatsApp Connection</h2>
            <div className="flex items-center gap-4 mb-6">
              <div className="p-3 bg-green-100 rounded-lg">
                <Phone className="w-6 h-6 text-green-600" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-semibold text-slate-900">Connected</h3>
                  <span className="badge-success">Active</span>
                </div>
                <p className="text-sm text-slate-600">+1234567890</p>
              </div>
              <button className="btn-secondary">Reconnect</button>
            </div>

            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h4 className="font-semibold text-blue-900 mb-2">QR Code for New Connection</h4>
              <div className="flex items-center justify-center w-48 h-48 bg-white border-4 border-blue-200 rounded-xl">
                <p className="text-slate-400 text-center text-sm px-4">QR Code will appear here</p>
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="text-xl font-bold text-slate-900 mb-4">Message Settings</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Message Delay (seconds)
                </label>
                <input
                  type="number"
                  className="input w-full md:w-64"
                  defaultValue={2}
                  min={1}
                  max={10}
                />
                <p className="text-sm text-slate-600 mt-1">Delay between messages to avoid spam detection</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Daily Message Limit
                </label>
                <input
                  type="number"
                  className="input w-full md:w-64"
                  defaultValue={1000}
                  min={100}
                  max={5000}
                />
                <p className="text-sm text-slate-600 mt-1">Maximum messages per day to prevent blocking</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'security' && (
        <div className="space-y-6">
          <div className="card">
            <h2 className="text-xl font-bold text-slate-900 mb-6">Change Password</h2>
            <div className="space-y-4 max-w-md">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Current Password
                </label>
                <input type="password" className="input w-full" />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  New Password
                </label>
                <input type="password" className="input w-full" />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Confirm New Password
                </label>
                <input type="password" className="input w-full" />
              </div>

              <button className="btn-primary">Update Password</button>
            </div>
          </div>

          <div className="card">
            <h2 className="text-xl font-bold text-slate-900 mb-6">Two-Factor Authentication</h2>
            <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
              <div>
                <h4 className="font-semibold text-slate-900">2FA Status</h4>
                <p className="text-sm text-slate-600">Add an extra layer of security</p>
              </div>
              <button className="btn-secondary">Enable 2FA</button>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'danger' && (
        <div className="space-y-6">
          <div className="card border-red-200">
            <h2 className="text-xl font-bold text-red-900 mb-4">Danger Zone</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-red-50 border border-red-200 rounded-lg">
                <div>
                  <h4 className="font-semibold text-red-900">Clear All Data</h4>
                  <p className="text-sm text-red-700">Delete all contacts, messages, and campaigns</p>
                </div>
                <button className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors">
                  Clear Data
                </button>
              </div>

              <div className="flex items-center justify-between p-4 bg-red-50 border border-red-200 rounded-lg">
                <div>
                  <h4 className="font-semibold text-red-900">Delete Account</h4>
                  <p className="text-sm text-red-700">Permanently delete your account and all data</p>
                </div>
                <button className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2">
                  <Trash2 className="w-4 h-4" />
                  Delete Account
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
