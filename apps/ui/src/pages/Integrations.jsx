import { useState } from 'react'
import { Puzzle, Code, ExternalLink, Copy, CheckCircle } from 'lucide-react'
import toast from 'react-hot-toast'

export default function Integrations() {
  const [selectedPlatform, setSelectedPlatform] = useState('react')

  const platforms = [
    {
      id: 'react',
      name: 'React / Next.js',
      icon: '⚛️',
      description: 'JavaScript client library for React and Next.js applications'
    },
    {
      id: 'wordpress',
      name: 'WordPress',
      icon: '🔌',
      description: 'Plugin integration for WordPress sites'
    },
    {
      id: 'html',
      name: 'HTML / JavaScript',
      icon: '🌐',
      description: 'Vanilla JS integration for any website'
    },
    {
      id: 'shopify',
      name: 'Shopify',
      icon: '🛍️',
      description: 'E-commerce integration for Shopify stores'
    },
    {
      id: 'zapier',
      name: 'Zapier / Make',
      icon: '⚡',
      description: 'No-code automation with 5000+ apps'
    },
    {
      id: 'python',
      name: 'Python',
      icon: '🐍',
      description: 'Python SDK for backend integration'
    },
  ]

  const integrationGuides = {
    react: {
      steps: [
        'Install the axios package: npm install axios',
        'Create an API client configuration file',
        'Set up authentication with your API key',
        'Make API calls from your React components',
        'Handle responses and errors'
      ],
      code: `// src/api/whatsapp.js
import axios from 'axios';

const whatsappClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  }
});

export const sendMessage = async (phone, message) => {
  const response = await whatsappClient.post('/messages/send', {
    phone,
    message
  });
  return response.data;
};

export const getContacts = async () => {
  const response = await whatsappClient.get('/contacts');
  return response.data;
};

// Usage in component
import { sendMessage } from './api/whatsapp';

function SendMessageButton() {
  const handleSend = async () => {
    try {
      const result = await sendMessage('+1234567890', 'Hello!');
      console.log('Message sent:', result);
    } catch (error) {
      console.error('Failed to send:', error);
    }
  };

  return <button onClick={handleSend}>Send Message</button>;
}`
    },
    wordpress: {
      steps: [
        'Download the WhatsApp Agent WordPress plugin',
        'Upload and activate the plugin in WordPress admin',
        'Go to Settings → WhatsApp Agent',
        'Enter your API key and API URL',
        'Configure shortcodes for forms and widgets',
        'Test the integration'
      ],
      code: `<!-- WordPress Shortcode -->
[whatsapp_agent_form]

<!-- PHP Integration -->
<?php
function send_whatsapp_message($phone, $message) {
    $api_key = get_option('whatsapp_agent_api_key');
    $api_url = get_option('whatsapp_agent_api_url');
    
    $response = wp_remote_post($api_url . '/messages/send', array(
        'headers' => array(
            'Authorization' => 'Bearer ' . $api_key,
            'Content-Type' => 'application/json'
        ),
        'body' => json_encode(array(
            'phone' => $phone,
            'message' => $message
        ))
    ));
    
    if (is_wp_error($response)) {
        return false;
    }
    
    return json_decode(wp_remote_retrieve_body($response));
}

// Hook into WooCommerce order completion
add_action('woocommerce_order_status_completed', function($order_id) {
    $order = wc_get_order($order_id);
    $phone = $order->get_billing_phone();
    $message = "Thank you for your order! Order #" . $order_id;
    send_whatsapp_message($phone, $message);
});
?>`
    },
    html: {
      steps: [
        'Include the fetch API or axios CDN',
        'Create a form for user input',
        'Add JavaScript to handle form submission',
        'Make API calls to WhatsApp Agent',
        'Display success/error messages'
      ],
      code: `<!DOCTYPE html>
<html>
<head>
    <title>WhatsApp Integration</title>
</head>
<body>
    <form id="whatsappForm">
        <input type="tel" id="phone" placeholder="+1234567890" required>
        <textarea id="message" placeholder="Your message" required></textarea>
        <button type="submit">Send WhatsApp Message</button>
    </form>
    <div id="result"></div>

    <script>
        const API_KEY = 'YOUR_API_KEY';
        const API_URL = 'http://localhost:8000/api/v1';

        document.getElementById('whatsappForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            const phone = document.getElementById('phone').value;
            const message = document.getElementById('message').value;

            try {
                const response = await fetch(\`\${API_URL}/messages/send\`, {
                    method: 'POST',
                    headers: {
                        'Authorization': \`Bearer \${API_KEY}\`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ phone, message })
                });

                const data = await response.json();
                document.getElementById('result').innerHTML = 
                    '<p style="color: green;">Message sent successfully!</p>';
            } catch (error) {
                document.getElementById('result').innerHTML = 
                    '<p style="color: red;">Failed to send message</p>';
            }
        });
    </script>
</body>
</html>`
    },
    shopify: {
      steps: [
        'Install WhatsApp Agent app from Shopify App Store',
        'Connect your WhatsApp Agent account',
        'Configure automated messages for orders',
        'Set up abandoned cart recovery',
        'Customize message templates',
        'Enable order notifications'
      ],
      code: `// Shopify Liquid Template
{% comment %} Add to cart page {% endcomment %}
<script>
  // Send WhatsApp notification when order is placed
  window.addEventListener('checkout:completed', function(event) {
    fetch('http://localhost:8000/api/v1/messages/send', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer YOUR_API_KEY',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        phone: '{{ customer.phone }}',
        message: 'Thank you for your order! Order #{{ order.name }} is confirmed.'
      })
    });
  });
</script>

// Abandoned Cart Recovery
{% if cart.item_count > 0 %}
<script>
  setTimeout(function() {
    if (window.location.pathname === '/cart') {
      fetch('http://localhost:8000/api/v1/messages/send', {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer YOUR_API_KEY',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          phone: '{{ customer.phone }}',
          message: 'You have items in your cart! Complete your purchase now: {{ shop.url }}/cart'
        })
      });
    }
  }, 300000); // 5 minutes
</script>
{% endif %}`
    },
    zapier: {
      steps: [
        'Create a new Zap in Zapier',
        'Choose your trigger app (Gmail, Google Sheets, etc.)',
        'Select "Webhooks by Zapier" as action',
        'Configure POST request to WhatsApp Agent API',
        'Add your API key in headers',
        'Map data fields from trigger to message',
        'Test and activate your Zap'
      ],
      code: `// Zapier Webhook Configuration

URL: http://localhost:8000/api/v1/messages/send

Method: POST

Headers:
{
  "Authorization": "Bearer YOUR_API_KEY",
  "Content-Type": "application/json"
}

Body:
{
  "phone": "{{trigger_phone}}",
  "message": "{{trigger_message}}"
}

// Example: Google Sheets → WhatsApp
// Trigger: New row in Google Sheets
// Action: Send WhatsApp message
// Map fields: 
//   - Column A (Phone) → phone
//   - Column B (Message) → message

// Example: Gmail → WhatsApp
// Trigger: New email in Gmail
// Action: Send WhatsApp notification
// Message: "New email from {{from_email}}: {{subject}}"`
    },
    python: {
      steps: [
        'Install the requests library: pip install requests',
        'Create a WhatsApp client class',
        'Implement authentication and API methods',
        'Use the client in your application',
        'Handle errors and rate limiting'
      ],
      code: `# whatsapp_client.py
import requests
from typing import Optional, Dict, Any

class WhatsAppAgent:
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def send_message(self, phone: str, message: str) -> Dict[str, Any]:
        """Send a WhatsApp message"""
        response = self.session.post(
            f"{self.base_url}/messages/send",
            json={"phone": phone, "message": message}
        )
        response.raise_for_status()
        return response.json()
    
    def get_contacts(self) -> list:
        """Get all contacts"""
        response = self.session.get(f"{self.base_url}/contacts")
        response.raise_for_status()
        return response.json()
    
    def create_campaign(self, name: str, message: str, contacts: list) -> Dict[str, Any]:
        """Create a new campaign"""
        response = self.session.post(
            f"{self.base_url}/campaigns",
            json={"name": name, "message": message, "contacts": contacts}
        )
        response.raise_for_status()
        return response.json()

# Usage
if __name__ == "__main__":
    client = WhatsAppAgent(api_key="YOUR_API_KEY")
    
    # Send message
    result = client.send_message("+1234567890", "Hello from Python!")
    print(f"Message sent: {result}")
    
    # Get contacts
    contacts = client.get_contacts()
    print(f"Total contacts: {len(contacts)}")`
    }
  }

  const copyCode = (code) => {
    navigator.clipboard.writeText(code)
    toast.success('Code copied to clipboard!')
  }

  const currentGuide = integrationGuides[selectedPlatform]

  return (
    <div className="space-y-6 animate-slideIn">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Integrations</h1>
        <p className="text-slate-600 mt-1">Connect WhatsApp Agent to your favorite platforms</p>
      </div>

      {/* Platform Selection */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {platforms.map((platform) => (
          <button
            key={platform.id}
            onClick={() => setSelectedPlatform(platform.id)}
            className={`card text-left hover:shadow-lg transition-all ${
              selectedPlatform === platform.id
                ? 'border-2 border-whatsapp bg-green-50'
                : 'border border-slate-200'
            }`}
          >
            <div className="flex items-start gap-3">
              <div className="text-4xl">{platform.icon}</div>
              <div className="flex-1">
                <h3 className="font-bold text-slate-900 mb-1">{platform.name}</h3>
                <p className="text-sm text-slate-600">{platform.description}</p>
              </div>
              {selectedPlatform === platform.id && (
                <CheckCircle className="w-5 h-5 text-whatsapp flex-shrink-0" />
              )}
            </div>
          </button>
        ))}
      </div>

      {/* Integration Guide */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-slate-900">
            Integration Guide: {platforms.find(p => p.id === selectedPlatform)?.name}
          </h2>
          <Puzzle className="w-6 h-6 text-slate-400" />
        </div>

        {/* Steps */}
        <div className="mb-6">
          <h3 className="font-semibold text-slate-900 mb-3">Setup Steps</h3>
          <ol className="space-y-2">
            {currentGuide.steps.map((step, index) => (
              <li key={index} className="flex items-start gap-3">
                <span className="flex-shrink-0 w-6 h-6 bg-whatsapp text-white rounded-full flex items-center justify-center text-sm font-semibold">
                  {index + 1}
                </span>
                <span className="text-slate-700 pt-0.5">{step}</span>
              </li>
            ))}
          </ol>
        </div>

        {/* Code Example */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-slate-900 flex items-center gap-2">
              <Code className="w-5 h-5" />
              Code Example
            </h3>
            <button
              onClick={() => copyCode(currentGuide.code)}
              className="btn-secondary flex items-center gap-2"
            >
              <Copy className="w-4 h-4" />
              Copy Code
            </button>
          </div>
          <pre className="bg-slate-900 text-green-400 rounded-lg p-4 overflow-x-auto text-sm max-h-[500px]">
            {currentGuide.code}
          </pre>
        </div>
      </div>

      {/* Documentation Link */}
      <div className="card bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-slate-900 mb-1">Full API Documentation</h3>
            <p className="text-slate-700">Explore all available endpoints and examples</p>
          </div>
          <a
            href="/docs"
            target="_blank"
            className="btn-primary flex items-center gap-2"
          >
            View Docs
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>

      {/* Support */}
      <div className="card">
        <h3 className="text-lg font-bold text-slate-900 mb-4">Need Help?</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <a href="https://github.com" className="p-4 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors">
            <h4 className="font-semibold text-slate-900 mb-1">GitHub</h4>
            <p className="text-sm text-slate-600">View source code and examples</p>
          </a>
          <a href="https://discord.com" className="p-4 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors">
            <h4 className="font-semibold text-slate-900 mb-1">Discord</h4>
            <p className="text-sm text-slate-600">Join our community</p>
          </a>
          <a href="mailto:support@example.com" className="p-4 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors">
            <h4 className="font-semibold text-slate-900 mb-1">Email Support</h4>
            <p className="text-sm text-slate-600">Get help from our team</p>
          </a>
        </div>
      </div>
    </div>
  )
}
