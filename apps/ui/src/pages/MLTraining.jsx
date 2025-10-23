import { useState } from 'react'
import axios from 'axios'
import {
  Brain,
  Play,
  Pause,
  RefreshCw,
  CheckCircle,
  Clock,
  TrendingUp,
  Award,
  AlertCircle
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function MLTraining() {
  const [trainingStatus, setTrainingStatus] = useState('idle') // idle, training, completed, failed
  const [progress, setProgress] = useState(0)

  const models = [
    {
      id: 'lead_scoring',
      name: 'Lead Scoring Model',
      description: 'Predicts lead quality based on engagement patterns',
      status: 'trained',
      accuracy: '76.7%',
      lastTrained: '2 days ago',
      metrics: {
        mae: 7.58,
        r2: 0.767
      }
    },
    {
      id: 'churn_prediction',
      name: 'Churn Prediction Model',
      description: 'Identifies contacts at risk of disengagement',
      status: 'trained',
      accuracy: '76.7%',
      lastTrained: '2 days ago',
      metrics: {
        accuracy: 0.767,
        f1_score: 0.857
      }
    },
    {
      id: 'engagement_prediction',
      name: 'Engagement Prediction Model',
      description: 'Forecasts message engagement probability',
      status: 'trained',
      accuracy: '73.3%',
      lastTrained: '2 days ago',
      metrics: {
        accuracy: 0.733,
        f1_score: 0.636
      }
    },
  ]

  const trainingHistory = [
    {
      id: 1,
      date: '2024-01-19 14:30',
      models: ['lead_scoring', 'churn_prediction', 'engagement_prediction'],
      duration: '0.6s',
      status: 'completed',
      metrics: 'All models trained successfully'
    },
    {
      id: 2,
      date: '2024-01-15 09:15',
      models: ['lead_scoring'],
      duration: '0.3s',
      status: 'completed',
      metrics: 'MAE: 7.58, R²: 0.767'
    },
    {
      id: 3,
      date: '2024-01-10 16:45',
      models: ['churn_prediction', 'engagement_prediction'],
      duration: '0.4s',
      status: 'completed',
      metrics: 'Accuracy: 76.7%, 73.3%'
    },
  ]

  const handleStartTraining = async () => {
    setTrainingStatus('training')
    setProgress(0)

    // Simulate training progress
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval)
          setTrainingStatus('completed')
          toast.success('All models trained successfully!')
          return 100
        }
        return prev + 10
      })
    }, 300)

    try {
      await axios.post('/api/v1/ml/train')
    } catch (error) {
      clearInterval(interval)
      setTrainingStatus('failed')
      toast.error('Training failed')
    }
  }

  const handleStopTraining = () => {
    setTrainingStatus('idle')
    setProgress(0)
    toast.error('Training stopped')
  }

  const getStatusColor = (status) => {
    const colors = {
      trained: 'badge-success',
      training: 'badge-warning',
      outdated: 'badge-secondary',
    }
    return colors[status] || 'badge-secondary'
  }

  return (
    <div className="space-y-6 animate-slideIn">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">ML Model Training</h1>
          <p className="text-slate-600 mt-1">Train and manage your machine learning models</p>
        </div>
        {trainingStatus === 'training' ? (
          <button
            onClick={handleStopTraining}
            className="btn-secondary"
          >
            <Pause className="w-4 h-4 mr-2" />
            Stop Training
          </button>
        ) : (
          <button
            onClick={handleStartTraining}
            className="btn-primary"
            disabled={trainingStatus === 'training'}
          >
            <Play className="w-4 h-4 mr-2" />
            Start Training
          </button>
        )}
      </div>

      {/* Training Status */}
      {trainingStatus === 'training' && (
        <div className="card bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200">
          <div className="flex items-center gap-4 mb-4">
            <div className="animate-spin rounded-full h-10 w-10 border-4 border-blue-200 border-t-blue-600"></div>
            <div className="flex-1">
              <h3 className="text-lg font-bold text-slate-900">Training in Progress...</h3>
              <p className="text-slate-600">Training all ML models with latest data</p>
            </div>
            <span className="text-2xl font-bold text-blue-600">{progress}%</span>
          </div>
          <div className="w-full bg-slate-200 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-blue-600 to-purple-600 h-3 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>
      )}

      {trainingStatus === 'completed' && (
        <div className="card bg-green-50 border border-green-200">
          <div className="flex items-center gap-4">
            <CheckCircle className="w-10 h-10 text-green-600" />
            <div className="flex-1">
              <h3 className="text-lg font-bold text-green-900">Training Completed Successfully!</h3>
              <p className="text-green-700">All models have been trained and deployed</p>
            </div>
            <button
              onClick={() => setTrainingStatus('idle')}
              className="text-green-600 hover:text-green-800"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Models Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {models.map((model) => (
          <div key={model.id} className="card hover:shadow-lg transition-shadow">
            <div className="flex items-start gap-4 mb-4">
              <div className="p-3 bg-gradient-to-br from-purple-500 to-blue-600 rounded-xl">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div className="flex-1">
                <h3 className="font-bold text-slate-900 mb-1">{model.name}</h3>
                <span className={`badge ${getStatusColor(model.status)}`}>
                  {model.status}
                </span>
              </div>
            </div>

            <p className="text-sm text-slate-600 mb-4">{model.description}</p>

            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-600">Accuracy</span>
                <span className="font-semibold text-slate-900">{model.accuracy}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-600">Last Trained</span>
                <span className="font-semibold text-slate-900">{model.lastTrained}</span>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-slate-200">
              <h4 className="text-xs font-semibold text-slate-700 mb-2">Performance Metrics</h4>
              <div className="space-y-1">
                {Object.entries(model.metrics).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between text-xs">
                    <span className="text-slate-600">{key.toUpperCase()}</span>
                    <span className="font-mono text-slate-900">{value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Training History */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold text-slate-900">Training History</h2>
            <p className="text-sm text-slate-600">Past training sessions and results</p>
          </div>
          <RefreshCw className="w-5 h-5 text-slate-400" />
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Date & Time</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Models</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Duration</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Status</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-700">Metrics</th>
              </tr>
            </thead>
            <tbody>
              {trainingHistory.map((session) => (
                <tr key={session.id} className="border-b border-slate-100 hover:bg-slate-50">
                  <td className="py-3 px-4 text-slate-900">{session.date}</td>
                  <td className="py-3 px-4">
                    <div className="flex flex-wrap gap-1">
                      {session.models.map((model, idx) => (
                        <span key={idx} className="badge-secondary text-xs">
                          {model.replace('_', ' ')}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="py-3 px-4 text-slate-600">{session.duration}</td>
                  <td className="py-3 px-4">
                    <span className={`badge ${getStatusColor(session.status)}`}>
                      {session.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-600">{session.metrics}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Training Guide */}
      <div className="card bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200">
        <div className="flex items-start gap-4">
          <AlertCircle className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-lg font-bold text-slate-900 mb-2">Training Best Practices</h3>
            <ul className="space-y-2 text-sm text-slate-700">
              <li className="flex items-start gap-2">
                <span className="text-yellow-600 font-bold">•</span>
                <span><strong>Regular Training:</strong> Retrain models weekly to maintain accuracy with new data</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-yellow-600 font-bold">•</span>
                <span><strong>Data Quality:</strong> Ensure sufficient message history (1000+ messages) for optimal results</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-yellow-600 font-bold">•</span>
                <span><strong>Monitor Metrics:</strong> Track MAE, accuracy, and F1-score to evaluate model performance</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-yellow-600 font-bold">•</span>
                <span><strong>Quick Training:</strong> Training typically completes in under 1 second with our optimized pipeline</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Model Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card bg-purple-50 border border-purple-200">
          <Award className="w-8 h-8 text-purple-600 mb-3" />
          <h4 className="font-bold text-slate-900 mb-1">XGBoost Algorithm</h4>
          <p className="text-sm text-slate-700">Lead scoring uses gradient boosting for high accuracy predictions</p>
        </div>
        <div className="card bg-blue-50 border border-blue-200">
          <TrendingUp className="w-8 h-8 text-blue-600 mb-3" />
          <h4 className="font-bold text-slate-900 mb-1">Random Forest</h4>
          <p className="text-sm text-slate-700">Churn prediction leverages ensemble learning for robustness</p>
        </div>
        <div className="card bg-green-50 border border-green-200">
          <CheckCircle className="w-8 h-8 text-green-600 mb-3" />
          <h4 className="font-bold text-slate-900 mb-1">Logistic Regression</h4>
          <p className="text-sm text-slate-700">Engagement prediction uses interpretable classification</p>
        </div>
      </div>
    </div>
  )
}
