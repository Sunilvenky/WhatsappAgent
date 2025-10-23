import { useState } from 'react'
import { Key, Plus, Copy, Eye, EyeOff, Trash2, CheckCircle, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'

export default function ApiKeys() {
  const [apiKeys, setApiKeys] = useState([
    {
      id: 1,
      name: 'Production API Key',
      key: 'wa_1234567890abcdefghij',
      created_at: '2024-01-15',
      last_used: '2 hours ago',
      status: 'active',
      requests: 15234
    },
    {
      id: 2,
      name: 'Development Key',
      key: 'wa_0987654321zyxwvutsrq',
      created_at: '2024-01-10',
      last_used: '1 day ago',
      status: 'active',
      requests: 3421
    },
  ])

  const [showNewKeyModal, setShowNewKeyModal] = useState(false)
  const [newKeyName, setNewKeyName] = useState('')
  const [generatedKey, setGeneratedKey] = useState(null)
  const [visibleKeys, setVisibleKeys] = useState({})

  const handleGenerateKey = () => {
    const key = `wa_${Math.random().toString(36).substring(2, 24)}`
    setGeneratedKey(key)
    setApiKeys([...apiKeys, {
      id: apiKeys.length + 1,
      name: newKeyName,
      key: key,
      created_at: new Date().toISOString().split('T')[0],
      last_used: 'Never',
      status: 'active',
      requests: 0
    }])
    setNewKeyName('')
    toast.success('API key generated successfully!')
  }

  const handleCopy = (key) => {
    navigator.clipboard.writeText(key)
    toast.success('API key copied to clipboard!')
  }

  const handleDelete = (id) => {
    if (!confirm('Are you sure you want to revoke this API key? This action cannot be undone.')) return
    setApiKeys(apiKeys.filter(k => k.id !== id))
    toast.success('API key revoked')
  }

  const toggleKeyVisibility = (id) => {
    setVisibleKeys(prev => ({ ...prev, [id]: !prev[id] }))
  }

  const maskKey = (key) => {
    return `${key.substring(0, 8)}${'•'.repeat(12)}`
  }

  return (
    <div className="space-y-6 animate-slideIn">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">API Keys</h1>
          <p className="text-slate-600 mt-1">Manage API keys for application integration</p>
        </div>
        <button
          onClick={() => setShowNewKeyModal(true)}
          className="btn-primary"
        >
          <Plus className="w-4 h-4 mr-2" />
          Generate New Key
        </button>
      </div>

      {/* Security Notice */}
      <div className="card bg-yellow-50 border border-yellow-200">
        <div className="flex items-start gap-4">
          <AlertCircle className="w-6 h-6 text-yellow-600 flex-shrink-0" />
          <div>
            <h3 className="font-bold text-yellow-900 mb-1">Security Best Practices</h3>
            <ul className="text-sm text-yellow-800 space-y-1">
              <li>• Never share your API keys publicly or commit them to version control</li>
              <li>• Use environment variables to store keys in your applications</li>
              <li>• Rotate keys regularly and revoke unused keys immediately</li>
              <li>• Monitor API usage for suspicious activity</li>
            </ul>
          </div>
        </div>
      </div>

      {/* API Keys List */}
      <div className="card">
        <h2 className="text-xl font-bold text-slate-900 mb-4">Your API Keys</h2>
        
        <div className="space-y-4">
          {apiKeys.map((apiKey) => (
            <div key={apiKey.id} className="border border-slate-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 bg-whatsapp/10 rounded-lg">
                      <Key className="w-5 h-5 text-whatsapp" />
                    </div>
                    <div>
                      <h3 className="font-bold text-slate-900">{apiKey.name}</h3>
                      <span className={`badge ${apiKey.status === 'active' ? 'badge-success' : 'badge-secondary'}`}>
                        {apiKey.status}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 mb-3">
                    <code className="flex-1 bg-slate-100 rounded px-3 py-2 font-mono text-sm text-slate-900">
                      {visibleKeys[apiKey.id] ? apiKey.key : maskKey(apiKey.key)}
                    </code>
                    <button
                      onClick={() => toggleKeyVisibility(apiKey.id)}
                      className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded"
                    >
                      {visibleKeys[apiKey.id] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                    <button
                      onClick={() => handleCopy(apiKey.key)}
                      className="p-2 text-slate-400 hover:text-whatsapp hover:bg-green-50 rounded"
                    >
                      <Copy className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-slate-600">Created</p>
                      <p className="font-semibold text-slate-900">{apiKey.created_at}</p>
                    </div>
                    <div>
                      <p className="text-slate-600">Last Used</p>
                      <p className="font-semibold text-slate-900">{apiKey.last_used}</p>
                    </div>
                    <div>
                      <p className="text-slate-600">Total Requests</p>
                      <p className="font-semibold text-slate-900">{apiKey.requests.toLocaleString()}</p>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => handleDelete(apiKey.id)}
                  className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Usage Examples */}
      <div className="card">
        <h2 className="text-xl font-bold text-slate-900 mb-4">Usage Examples</h2>
        
        <div className="space-y-6">
          {/* cURL Example */}
          <div>
            <h3 className="font-semibold text-slate-900 mb-2">cURL</h3>
            <pre className="bg-slate-900 text-green-400 rounded-lg p-4 overflow-x-auto text-sm">
{`curl -X POST http://localhost:8000/api/v1/messages/send \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "phone": "+1234567890",
    "message": "Hello from WhatsApp Agent!"
  }'`}
            </pre>
          </div>

          {/* JavaScript Example */}
          <div>
            <h3 className="font-semibold text-slate-900 mb-2">JavaScript / React</h3>
            <pre className="bg-slate-900 text-green-400 rounded-lg p-4 overflow-x-auto text-sm">
{`import axios from 'axios';

const sendMessage = async () => {
  const response = await axios.post(
    'http://localhost:8000/api/v1/messages/send',
    {
      phone: '+1234567890',
      message: 'Hello from WhatsApp Agent!'
    },
    {
      headers: {
        'Authorization': 'Bearer YOUR_API_KEY',
        'Content-Type': 'application/json'
      }
    }
  );
  console.log(response.data);
};`}
            </pre>
          </div>

          {/* Python Example */}
          <div>
            <h3 className="font-semibold text-slate-900 mb-2">Python</h3>
            <pre className="bg-slate-900 text-green-400 rounded-lg p-4 overflow-x-auto text-sm">
{`import requests

url = "http://localhost:8000/api/v1/messages/send"
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}
data = {
    "phone": "+1234567890",
    "message": "Hello from WhatsApp Agent!"
}

response = requests.post(url, headers=headers, json=data)
print(response.json())`}
            </pre>
          </div>
        </div>
      </div>

      {/* Generate New Key Modal */}
      {showNewKeyModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full mx-4">
            <div className="flex items-center justify-between p-6 border-b border-slate-200">
              <h2 className="text-xl font-bold text-slate-900">Generate New API Key</h2>
              <button
                onClick={() => {
                  setShowNewKeyModal(false)
                  setGeneratedKey(null)
                }}
                className="text-slate-400 hover:text-slate-600"
              >
                <Plus className="w-5 h-5 rotate-45" />
              </button>
            </div>

            <div className="p-6">
              {!generatedKey ? (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Key Name *
                    </label>
                    <input
                      type="text"
                      className="input w-full"
                      placeholder="e.g., Production Key, Testing Key"
                      value={newKeyName}
                      onChange={(e) => setNewKeyName(e.target.value)}
                    />
                  </div>

                  <button
                    onClick={handleGenerateKey}
                    disabled={!newKeyName}
                    className="btn-primary w-full"
                  >
                    <Key className="w-4 h-4 mr-2" />
                    Generate API Key
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                      <h3 className="font-semibold text-green-900">API Key Generated!</h3>
                    </div>
                    <p className="text-sm text-green-800 mb-3">
                      Save this key securely - you won't be able to see it again!
                    </p>
                    <div className="flex items-center gap-2">
                      <code className="flex-1 bg-white rounded px-3 py-2 font-mono text-sm text-slate-900 break-all">
                        {generatedKey}
                      </code>
                      <button
                        onClick={() => handleCopy(generatedKey)}
                        className="p-2 text-green-600 hover:text-green-800 hover:bg-green-100 rounded"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  <button
                    onClick={() => {
                      setShowNewKeyModal(false)
                      setGeneratedKey(null)
                    }}
                    className="btn-primary w-full"
                  >
                    Done
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
