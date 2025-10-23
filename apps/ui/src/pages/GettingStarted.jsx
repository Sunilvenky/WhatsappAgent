import { useState } from 'react'
import { Check, Smartphone, Key, Send, Puzzle, ArrowRight, Copy, ExternalLink } from 'lucide-react'
import toast from 'react-hot-toast'

export default function GettingStarted() {
  const [currentStep, setCurrentStep] = useState(1)
  const [apiKey, setApiKey] = useState('wa_1234567890abcdefghij')

  const steps = [
    {
      id: 1,
      title: 'Connect WhatsApp',
      icon: Smartphone,
      description: 'Scan QR code to connect your WhatsApp Business account',
      completed: false,
    },
    {
      id: 2,
      title: 'Generate API Key',
      icon: Key,
      description: 'Create your first API key for integration',
      completed: false,
    },
    {
      id: 3,
      title: 'Send Test Message',
      icon: Send,
      description: 'Send your first WhatsApp message via API',
      completed: false,
    },
    {
      id: 4,
      title: 'Integrate with Your App',
      icon: Puzzle,
      description: 'Connect to React, WordPress, or any platform',
      completed: false,
    },
  ]

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    toast.success('Copied to clipboard!')
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-slideIn">
      {/* Header */}
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-whatsapp to-green-600 rounded-2xl mb-4">
          <Smartphone className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-3xl font-bold text-slate-900 mb-2">Getting Started</h1>
        <p className="text-slate-600">Follow these steps to set up your WhatsApp marketing automation</p>
      </div>

      {/* Progress Steps */}
      <div className="flex items-center justify-between mb-12">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-center">
            <div className="flex flex-col items-center">
              <div
                className={`w-12 h-12 rounded-full flex items-center justify-center border-2 transition-all ${
                  currentStep >= step.id
                    ? 'bg-whatsapp border-whatsapp text-white'
                    : 'bg-white border-slate-300 text-slate-400'
                }`}
              >
                {step.completed ? (
                  <Check className="w-6 h-6" />
                ) : (
                  <step.icon className="w-6 h-6" />
                )}
              </div>
              <p className="text-sm font-medium text-slate-700 mt-2">{step.title}</p>
            </div>
            {index < steps.length - 1 && (
              <div
                className={`w-24 h-1 mx-4 transition-all ${
                  currentStep > step.id ? 'bg-whatsapp' : 'bg-slate-200'
                }`}
              />
            )}
          </div>
        ))}
      </div>

      {/* Step Content */}
      <div className="card">
        {currentStep === 1 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-slate-900 mb-2">Connect Your WhatsApp</h2>
              <p className="text-slate-600">
                Scan the QR code below with your WhatsApp mobile app to connect your account
              </p>
            </div>

            <div className="flex items-center justify-center p-8 bg-slate-50 rounded-xl">
              <div className="w-64 h-64 bg-white border-4 border-slate-200 rounded-xl flex items-center justify-center">
                <p className="text-slate-400 text-center px-8">
                  QR Code will appear here<br />
                  <span className="text-sm">(Scan with WhatsApp mobile app)</span>
                </p>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-2">📱 How to scan:</h3>
              <ol className="text-sm text-blue-800 space-y-1 ml-4 list-decimal">
                <li>Open WhatsApp on your phone</li>
                <li>Tap Menu (⋮) or Settings</li>
                <li>Tap "Linked Devices"</li>
                <li>Tap "Link a Device"</li>
                <li>Point your phone at this screen to scan the code</li>
              </ol>
            </div>

            <button
              onClick={() => setCurrentStep(2)}
              className="btn-primary w-full"
            >
              Continue to API Key <ArrowRight className="w-4 h-4 ml-2" />
            </button>
          </div>
        )}

        {currentStep === 2 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-slate-900 mb-2">Generate API Key</h2>
              <p className="text-slate-600">
                Create your API key to authenticate requests from your applications
              </p>
            </div>

            <div className="bg-slate-50 rounded-xl p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  API Key Name
                </label>
                <input
                  type="text"
                  className="input w-full"
                  placeholder="My First API Key"
                  defaultValue="Production API Key"
                />
              </div>

              <button className="btn-primary">
                <Key className="w-4 h-4 mr-2" />
                Generate API Key
              </button>
            </div>

            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h3 className="font-semibold text-green-900 mb-2">✅ Your API Key</h3>
              <div className="flex items-center gap-2 bg-white rounded p-3 font-mono text-sm">
                <code className="flex-1">{apiKey}</code>
                <button
                  onClick={() => copyToClipboard(apiKey)}
                  className="text-slate-400 hover:text-slate-600"
                >
                  <Copy className="w-4 h-4" />
                </button>
              </div>
              <p className="text-sm text-green-800 mt-2">
                ⚠️ Save this key securely - you won't be able to see it again!
              </p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setCurrentStep(1)}
                className="btn-secondary"
              >
                Back
              </button>
              <button
                onClick={() => setCurrentStep(3)}
                className="btn-primary flex-1"
              >
                Continue to Send Message <ArrowRight className="w-4 h-4 ml-2" />
              </button>
            </div>
          </div>
        )}

        {currentStep === 3 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-slate-900 mb-2">Send Test Message</h2>
              <p className="text-slate-600">
                Try sending your first WhatsApp message using our API
              </p>
            </div>

            <div className="bg-slate-50 rounded-xl p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Recipient Phone Number
                </label>
                <input
                  type="tel"
                  className="input w-full"
                  placeholder="+1234567890"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Message
                </label>
                <textarea
                  className="input w-full"
                  rows="4"
                  placeholder="Hello! This is a test message from WhatsApp Agent 🚀"
                  defaultValue="Hello! This is a test message from WhatsApp Agent 🚀"
                />
              </div>

              <button className="btn-primary">
                <Send className="w-4 h-4 mr-2" />
                Send Test Message
              </button>
            </div>

            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <h3 className="font-semibold text-purple-900 mb-2">📝 API Example (cURL)</h3>
              <pre className="bg-white rounded p-3 text-xs overflow-x-auto">
{`curl -X POST http://localhost:8000/api/v1/messages/send \\
  -H "Authorization: Bearer ${apiKey}" \\
  -H "Content-Type: application/json" \\
  -d '{
    "phone": "+1234567890",
    "message": "Hello from API!"
  }'`}
              </pre>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setCurrentStep(2)}
                className="btn-secondary"
              >
                Back
              </button>
              <button
                onClick={() => setCurrentStep(4)}
                className="btn-primary flex-1"
              >
                Continue to Integration <ArrowRight className="w-4 h-4 ml-2" />
              </button>
            </div>
          </div>
        )}

        {currentStep === 4 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-slate-900 mb-2">Integrate with Your App</h2>
              <p className="text-slate-600">
                Choose your platform and follow the integration guide
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <IntegrationCard
                title="React / Next.js"
                description="JavaScript client library"
                icon="⚛️"
                to="/integrations?platform=react"
              />
              <IntegrationCard
                title="WordPress"
                description="Plugin installation"
                icon="🔌"
                to="/integrations?platform=wordpress"
              />
              <IntegrationCard
                title="HTML / JavaScript"
                description="Vanilla JS integration"
                icon="🌐"
                to="/integrations?platform=html"
              />
              <IntegrationCard
                title="Zapier / Make"
                description="No-code automation"
                icon="⚡"
                to="/integrations?platform=zapier"
              />
            </div>

            <div className="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-lg p-6 text-center">
              <h3 className="text-xl font-bold text-slate-900 mb-2">🎉 You're All Set!</h3>
              <p className="text-slate-600 mb-4">
                Your WhatsApp Agent is ready to start sending messages and automating conversations
              </p>
              <div className="flex gap-3 justify-center">
                <a href="/dashboard" className="btn-primary">
                  Go to Dashboard
                </a>
                <a href="/campaigns" className="btn-secondary">
                  Create First Campaign
                </a>
              </div>
            </div>

            <button
              onClick={() => setCurrentStep(3)}
              className="btn-secondary w-full"
            >
              Back
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

function IntegrationCard({ title, description, icon, to }) {
  return (
    <a
      href={to}
      className="card hover:shadow-lg transition-all group"
    >
      <div className="flex items-start gap-4">
        <div className="text-4xl">{icon}</div>
        <div className="flex-1">
          <h3 className="font-bold text-slate-900 mb-1 group-hover:text-whatsapp transition-colors">
            {title}
          </h3>
          <p className="text-sm text-slate-600">{description}</p>
        </div>
        <ExternalLink className="w-5 h-5 text-slate-400 group-hover:text-whatsapp transition-colors" />
      </div>
    </a>
  )
}
