// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const API_ENDPOINTS = {
  chat: `${API_BASE_URL}/chat`,
  chatStream: `${API_BASE_URL}/chat/stream`,
  plan: `${API_BASE_URL}/generate_learning_plan`,
  health: `${API_BASE_URL}/health`,
  
  // Learning Plans
  learningPlans: `${API_BASE_URL}/learning-plans`,
  learningPlansCheck: `${API_BASE_URL}/learning-plans/check`,
  
  // Teaching
  teachingStart: `${API_BASE_URL}/teaching/start`,
  teachingChat: `${API_BASE_URL}/teaching/chat`,
  teachingDiagram: `${API_BASE_URL}/teaching/generate-diagram`,
} as const

export { API_BASE_URL }
