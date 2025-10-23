import { Outlet, NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Users,
  Megaphone,
  MessageSquare,
  Target,
  BarChart3,
  Brain,
  Key,
  Puzzle,
  Settings,
  Sparkles,
  MessageCircle
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', to: '/dashboard', icon: LayoutDashboard },
  { name: 'Getting Started', to: '/getting-started', icon: Sparkles },
  { name: 'Contacts', to: '/contacts', icon: Users },
  { name: 'Campaigns', to: '/campaigns', icon: Megaphone },
  { name: 'Messages', to: '/messages', icon: MessageSquare },
  { name: 'Leads', to: '/leads', icon: Target },
  { name: 'Analytics', to: '/analytics', icon: BarChart3 },
  { name: 'ML Training', to: '/ml-training', icon: Brain },
  { name: 'API Keys', to: '/api-keys', icon: Key },
  { name: 'Integrations', to: '/integrations', icon: Puzzle },
  { name: 'Settings', to: '/settings', icon: Settings },
]

export default function Layout() {
  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-64 bg-gradient-to-b from-slate-900 to-slate-800 text-white flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b border-slate-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-whatsapp rounded-xl flex items-center justify-center">
              <MessageCircle className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-lg font-bold">WhatsApp Agent</h1>
              <p className="text-xs text-slate-400">Smart Marketing</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {navigation.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                  isActive
                    ? 'bg-whatsapp text-white shadow-lg shadow-whatsapp/30'
                    : 'text-slate-300 hover:bg-slate-700/50 hover:text-white'
                }`
              }
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.name}</span>
            </NavLink>
          ))}
        </nav>

        {/* User Info */}
        <div className="p-4 border-t border-slate-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center text-white font-bold">
              A
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium truncate">Admin User</p>
              <p className="text-xs text-slate-400 truncate">admin@example.com</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Bar */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8">
          <div>
            <h2 className="text-xl font-bold text-slate-900">Welcome back, Admin!</h2>
            <p className="text-sm text-slate-600">Manage your WhatsApp marketing campaigns</p>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="px-4 py-2 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium text-green-700">WhatsApp Connected</span>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-8 bg-slate-50">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
