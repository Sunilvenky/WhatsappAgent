import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Contacts from './pages/Contacts'
import Campaigns from './pages/Campaigns'
import Messages from './pages/Messages'
import Leads from './pages/Leads'
import Analytics from './pages/Analytics'
import Settings from './pages/Settings'
import ApiKeys from './pages/ApiKeys'
import Integrations from './pages/Integrations'
import MLTraining from './pages/MLTraining'
import GettingStarted from './pages/GettingStarted'

function App() {
  return (
    <Router>
      <Toaster position="top-right" />
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="getting-started" element={<GettingStarted />} />
          <Route path="contacts" element={<Contacts />} />
          <Route path="campaigns" element={<Campaigns />} />
          <Route path="messages" element={<Messages />} />
          <Route path="leads" element={<Leads />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="ml-training" element={<MLTraining />} />
          <Route path="api-keys" element={<ApiKeys />} />
          <Route path="integrations" element={<Integrations />} />
          <Route path="settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App
