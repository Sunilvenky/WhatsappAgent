import { useState, useEffect } from 'react'
import axios from 'axios'
import {
  MessageSquare,
  Search,
  Send,
  Check,
  CheckCheck,
  Clock,
  Bot,
  Smile
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function Messages() {
  const [conversations, setConversations] = useState([])
  const [selectedConversation, setSelectedConversation] = useState(null)
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchConversations()
  }, [])

  useEffect(() => {
    if (selectedConversation) {
      fetchMessages(selectedConversation.id)
    }
  }, [selectedConversation])

  const fetchConversations = async () => {
    try {
      const response = await axios.get('/api/v1/conversations')
      setConversations(response.data)
    } catch (error) {
      console.error('Failed to fetch conversations:', error)
      // Mock data
      setConversations([
        {
          id: 1,
          contact_name: 'John Doe',
          contact_phone: '+1234567890',
          last_message: 'Thanks for the info!',
          last_message_time: '2 min ago',
          unread_count: 2,
          status: 'active',
          sentiment: 'positive'
        },
        {
          id: 2,
          contact_name: 'Jane Smith',
          contact_phone: '+1234567891',
          last_message: 'When can I get the product?',
          last_message_time: '15 min ago',
          unread_count: 0,
          status: 'active',
          sentiment: 'neutral'
        },
        {
          id: 3,
          contact_name: 'Bob Johnson',
          contact_phone: '+1234567892',
          last_message: 'I am interested in your services',
          last_message_time: '1 hour ago',
          unread_count: 1,
          status: 'active',
          sentiment: 'positive'
        },
      ])
      setSelectedConversation({
        id: 1,
        contact_name: 'John Doe',
        contact_phone: '+1234567890',
        last_message: 'Thanks for the info!',
        last_message_time: '2 min ago',
        unread_count: 2,
        status: 'active',
        sentiment: 'positive'
      })
    } finally {
      setLoading(false)
    }
  }

  const fetchMessages = async (conversationId) => {
    try {
      const response = await axios.get(`/api/v1/conversations/${conversationId}/messages`)
      setMessages(response.data)
    } catch (error) {
      console.error('Failed to fetch messages:', error)
      // Mock data
      setMessages([
        {
          id: 1,
          content: 'Hi! I saw your product and I am interested',
          direction: 'inbound',
          status: 'delivered',
          timestamp: '10:30 AM',
          sentiment: 'positive'
        },
        {
          id: 2,
          content: 'Hello! Thank you for reaching out. Which product are you interested in?',
          direction: 'outbound',
          status: 'read',
          timestamp: '10:32 AM'
        },
        {
          id: 3,
          content: 'The Premium package. Can you tell me more about it?',
          direction: 'inbound',
          status: 'delivered',
          timestamp: '10:35 AM',
          sentiment: 'neutral'
        },
        {
          id: 4,
          content: 'Of course! The Premium package includes...',
          direction: 'outbound',
          status: 'read',
          timestamp: '10:37 AM'
        },
        {
          id: 5,
          content: 'Thanks for the info!',
          direction: 'inbound',
          status: 'delivered',
          timestamp: '10:40 AM',
          sentiment: 'positive'
        },
      ])
    }
  }

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!newMessage.trim()) return

    try {
      await axios.post(`/api/v1/conversations/${selectedConversation.id}/messages`, {
        content: newMessage,
      })
      toast.success('Message sent')
      setNewMessage('')
      fetchMessages(selectedConversation.id)
    } catch (error) {
      toast.error('Failed to send message')
    }
  }

  const getSentimentColor = (sentiment) => {
    const colors = {
      positive: 'text-green-600',
      neutral: 'text-slate-600',
      negative: 'text-red-600',
    }
    return colors[sentiment] || 'text-slate-600'
  }

  return (
    <div className="h-[calc(100vh-8rem)] animate-slideIn">
      <div className="flex h-full gap-4">
        {/* Conversations List */}
        <div className="w-80 card flex flex-col">
          <div className="p-4 border-b border-slate-200">
            <h2 className="text-xl font-bold text-slate-900 mb-4">Messages</h2>
            <div className="relative">
              <Search className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search conversations..."
                className="input pl-10 w-full"
              />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto">
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-whatsapp"></div>
              </div>
            ) : (
              <div>
                {conversations.map((conv) => (
                  <button
                    key={conv.id}
                    onClick={() => setSelectedConversation(conv)}
                    className={`w-full text-left p-4 border-b border-slate-100 hover:bg-slate-50 transition-colors ${
                      selectedConversation?.id === conv.id ? 'bg-green-50 border-l-4 border-l-whatsapp' : ''
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="w-12 h-12 bg-gradient-to-br from-whatsapp to-green-600 rounded-full flex items-center justify-center text-white font-semibold flex-shrink-0">
                        {conv.contact_name.charAt(0)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1">
                          <h3 className="font-semibold text-slate-900 truncate">
                            {conv.contact_name}
                          </h3>
                          <span className="text-xs text-slate-500">{conv.last_message_time}</span>
                        </div>
                        <p className="text-sm text-slate-600 truncate">{conv.last_message}</p>
                        <div className="flex items-center gap-2 mt-1">
                          {conv.unread_count > 0 && (
                            <span className="badge-primary text-xs">{conv.unread_count} new</span>
                          )}
                          {conv.sentiment && (
                            <Bot className={`w-3 h-3 ${getSentimentColor(conv.sentiment)}`} />
                          )}
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 card flex flex-col">
          {selectedConversation ? (
            <>
              {/* Chat Header */}
              <div className="p-4 border-b border-slate-200 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-whatsapp to-green-600 rounded-full flex items-center justify-center text-white font-semibold">
                    {selectedConversation.contact_name.charAt(0)}
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-900">{selectedConversation.contact_name}</h3>
                    <p className="text-sm text-slate-600">{selectedConversation.contact_phone}</p>
                  </div>
                </div>
                {selectedConversation.sentiment && (
                  <div className={`flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100`}>
                    <Bot className={`w-4 h-4 ${getSentimentColor(selectedConversation.sentiment)}`} />
                    <span className="text-sm font-medium capitalize">{selectedConversation.sentiment}</span>
                  </div>
                )}
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.direction === 'outbound' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[70%] rounded-lg p-3 ${
                        message.direction === 'outbound'
                          ? 'bg-whatsapp text-white'
                          : 'bg-slate-100 text-slate-900'
                      }`}
                    >
                      <p className="text-sm">{message.content}</p>
                      <div className="flex items-center justify-end gap-1 mt-1">
                        <span className={`text-xs ${
                          message.direction === 'outbound' ? 'text-white/70' : 'text-slate-500'
                        }`}>
                          {message.timestamp}
                        </span>
                        {message.direction === 'outbound' && (
                          message.status === 'read' ? (
                            <CheckCheck className="w-4 h-4 text-white/70" />
                          ) : message.status === 'delivered' ? (
                            <CheckCheck className="w-4 h-4 text-white/70" />
                          ) : (
                            <Check className="w-4 h-4 text-white/70" />
                          )
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Message Input */}
              <form onSubmit={handleSendMessage} className="p-4 border-t border-slate-200">
                <div className="flex items-end gap-2">
                  <button
                    type="button"
                    className="p-3 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg"
                  >
                    <Smile className="w-5 h-5" />
                  </button>
                  <textarea
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Type a message..."
                    className="input flex-1 resize-none"
                    rows="2"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault()
                        handleSendMessage(e)
                      }
                    }}
                  />
                  <button
                    type="submit"
                    disabled={!newMessage.trim()}
                    className="btn-primary"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </div>
              </form>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-slate-400">
              <div className="text-center">
                <MessageSquare className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p>Select a conversation to start messaging</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
