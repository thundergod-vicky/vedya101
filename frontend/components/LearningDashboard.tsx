'use client'

import { useState, useEffect } from 'react'
import { useUser } from '@clerk/nextjs'
import { API_ENDPOINTS } from '../lib/api-config'

interface KanbanTask {
  id: string
  title: string
  description: string
  status: 'todo' | 'in_progress' | 'completed'
  module: string
  priority: 'low' | 'medium' | 'high'
  estimatedTime: string
}

interface LearningModule {
  id: string
  title: string
  description: string
  duration: string
  status: 'not_started' | 'in_progress' | 'completed'
  progress: number
  tasks: KanbanTask[]
}

interface LearningPlan {
  id: string
  title: string
  subject: string
  description: string
  totalDuration: string
  difficulty: string
  learningStyle: string
  modules: LearningModule[]
  overallProgress: number
  createdAt: string
}

export default function LearningDashboard() {
  const { user } = useUser()
  const [learningPlans, setLearningPlans] = useState<LearningPlan[]>([])
  const [selectedPlan, setSelectedPlan] = useState<LearningPlan | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchLearningPlans()
  }, [])

  const fetchLearningPlans = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.learningPlans, {
        headers: {
          'Authorization': `Bearer ${user?.id}`
        }
      })
      const data = await response.json()
      if (data.success) {
        setLearningPlans(data.plans)
        if (data.plans.length > 0) {
          setSelectedPlan(data.plans[0])
        }
      }
    } catch (error) {
      console.error('Error fetching learning plans:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800 border-green-200'
      case 'in_progress': return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'todo': return 'bg-gray-100 text-gray-800 border-gray-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const startTeaching = (planId: string) => {
    // Navigate to teaching interface
    window.open(`/teaching?plan=${planId}`, '_blank', 'width=1200,height=800')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 pt-16 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  if (learningPlans.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 pt-16 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">No Learning Plans Yet</h2>
          <p className="text-gray-600 mb-6">Start a conversation with our AI to create your first learning plan!</p>
          <a 
            href="/"
            className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Start Learning
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 pt-16">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8 flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Learning Dashboard</h1>
            <p className="text-gray-600">Track your progress and manage your learning journey</p>
          </div>
          <a 
            href="/"
            className="inline-flex items-center bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition-colors"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Start Learning Something New
          </a>
        </div>

        {/* Course Selection Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {learningPlans.map((plan) => (
                <button
                  key={plan.id}
                  onClick={() => setSelectedPlan(plan)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    selectedPlan?.id === plan.id
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {plan.title}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {selectedPlan && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Plan Overview */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">{selectedPlan.title}</h2>
                <p className="text-gray-600 mb-4">{selectedPlan.description}</p>
                
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Subject:</span>
                    <span className="text-sm font-medium">{selectedPlan.subject}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Difficulty:</span>
                    <span className="text-sm font-medium">{selectedPlan.difficulty}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Duration:</span>
                    <span className="text-sm font-medium">{selectedPlan.totalDuration}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Learning Style:</span>
                    <span className="text-sm font-medium">{selectedPlan.learningStyle}</span>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mt-6">
                  <div className="flex justify-between text-sm text-gray-600 mb-2">
                    <span>Overall Progress</span>
                    <span>{selectedPlan.overallProgress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${selectedPlan.overallProgress}%` }}
                    ></div>
                  </div>
                </div>

                {/* Start Teaching Button */}
                <button
                  onClick={() => startTeaching(selectedPlan.id)}
                  className="w-full mt-6 bg-indigo-600 text-white py-3 px-4 rounded-lg hover:bg-indigo-700 transition-colors font-medium flex items-center justify-center space-x-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  <span>Start Learning with AI Instructor</span>
                </button>
              </div>

              {/* Modules List */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Learning Modules</h3>
                <div className="space-y-3">
                  {selectedPlan.modules.map((module, index) => (
                    <div key={module.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-gray-900">
                          Module {index + 1}: {module.title}
                        </h4>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(module.status)}`}>
                          {module.status.replace('_', ' ')}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{module.description}</p>
                      <div className="flex justify-between text-xs text-gray-500">
                        <span>{module.duration}</span>
                        <span>{module.progress}% complete</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-1 mt-2">
                        <div 
                          className="bg-indigo-600 h-1 rounded-full"
                          style={{ width: `${module.progress}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Kanban Board */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-6">Learning Progress Board</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* To Do Column */}
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-4 flex items-center">
                      <div className="w-3 h-3 bg-gray-400 rounded-full mr-2"></div>
                      To Do
                    </h4>
                    <div className="space-y-3">
                      {selectedPlan.modules.flatMap(module => 
                        module.tasks.filter(task => task.status === 'todo')
                      ).map(task => (
                        <div key={task.id} className="bg-white rounded-lg p-3 shadow-sm border">
                          <h5 className="font-medium text-sm text-gray-900 mb-1">{task.title}</h5>
                          <p className="text-xs text-gray-600 mb-2">{task.description}</p>
                          <div className="flex justify-between items-center">
                            <span className={`px-2 py-1 rounded-full text-xs ${getPriorityColor(task.priority)}`}>
                              {task.priority}
                            </span>
                            <span className="text-xs text-gray-500">{task.estimatedTime}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* In Progress Column */}
                  <div className="bg-blue-50 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-4 flex items-center">
                      <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
                      In Progress
                    </h4>
                    <div className="space-y-3">
                      {selectedPlan.modules.flatMap(module => 
                        module.tasks.filter(task => task.status === 'in_progress')
                      ).map(task => (
                        <div key={task.id} className="bg-white rounded-lg p-3 shadow-sm border">
                          <h5 className="font-medium text-sm text-gray-900 mb-1">{task.title}</h5>
                          <p className="text-xs text-gray-600 mb-2">{task.description}</p>
                          <div className="flex justify-between items-center">
                            <span className={`px-2 py-1 rounded-full text-xs ${getPriorityColor(task.priority)}`}>
                              {task.priority}
                            </span>
                            <span className="text-xs text-gray-500">{task.estimatedTime}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Completed Column */}
                  <div className="bg-green-50 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-4 flex items-center">
                      <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                      Completed
                    </h4>
                    <div className="space-y-3">
                      {selectedPlan.modules.flatMap(module => 
                        module.tasks.filter(task => task.status === 'completed')
                      ).map(task => (
                        <div key={task.id} className="bg-white rounded-lg p-3 shadow-sm border">
                          <h5 className="font-medium text-sm text-gray-900 mb-1">{task.title}</h5>
                          <p className="text-xs text-gray-600 mb-2">{task.description}</p>
                          <div className="flex justify-between items-center">
                            <span className={`px-2 py-1 rounded-full text-xs ${getPriorityColor(task.priority)}`}>
                              {task.priority}
                            </span>
                            <span className="text-xs text-gray-500">{task.estimatedTime}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
