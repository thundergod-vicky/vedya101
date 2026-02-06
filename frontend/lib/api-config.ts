// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const API_ENDPOINTS = {
  chat: `${API_BASE_URL}/chat`,
  chatStream: `${API_BASE_URL}/chat/stream`,
  chatSessions: `${API_BASE_URL}/chat/sessions`,
  chatSessionsList: (clerkId: string) => `${API_BASE_URL}/chat/sessions?clerk_user_id=${encodeURIComponent(clerkId)}`,
  chatSessionDelete: (sessionId: string, clerkId: string) => `${API_BASE_URL}/chat/sessions/${encodeURIComponent(sessionId)}?clerk_user_id=${encodeURIComponent(clerkId)}`,
  chatMessages: `${API_BASE_URL}/chat/messages`,
  chatMessagesList: (sessionId: string) => `${API_BASE_URL}/chat/messages?session_id=${encodeURIComponent(sessionId)}`,
  plan: `${API_BASE_URL}/generate_learning_plan`,
  health: `${API_BASE_URL}/health`,
  
  // Learning Plans (pass clerk_user_id for DB-backed plans)
  learningPlans: `${API_BASE_URL}/learning-plans`,
  learningPlansForUser: (clerkId: string) => `${API_BASE_URL}/learning-plans?clerk_user_id=${encodeURIComponent(clerkId)}`,
  learningPlanById: (planId: string, clerkId: string) => `${API_BASE_URL}/learning-plans/${planId}?clerk_user_id=${encodeURIComponent(clerkId)}`,
  learningPlanDelete: (planId: string, clerkId: string) => `${API_BASE_URL}/learning-plans/${planId}?clerk_user_id=${encodeURIComponent(clerkId)}`,
  learningPlanProgress: (planId: string, clerkId: string) => `${API_BASE_URL}/learning-plans/${planId}/progress?clerk_user_id=${encodeURIComponent(clerkId)}`,
  learningPlanSaveFromSession: `${API_BASE_URL}/learning-plans/from-session`,
  learningPlansCheck: `${API_BASE_URL}/learning-plans/check`,
  
  // Teaching
  teachingStart: `${API_BASE_URL}/teaching/start`,
  teachingChat: `${API_BASE_URL}/teaching/chat`,
  teachingTts: `${API_BASE_URL}/teaching/tts`,
  teachingDiagram: `${API_BASE_URL}/teaching/generate-diagram`,
  executeCode: `${API_BASE_URL}/teaching/execute-code`,

  // User & Onboarding
  userRegister: `${API_BASE_URL}/users/register`,
  userByClerk: (clerkId: string) => `${API_BASE_URL}/users/clerk/${clerkId}`,
  onboardingStatus: (clerkId: string) => `${API_BASE_URL}/users/onboarding-status?clerk_user_id=${encodeURIComponent(clerkId)}`,
  onboardingData: (clerkId: string) => `${API_BASE_URL}/users/onboarding-data?clerk_user_id=${encodeURIComponent(clerkId)}`,
  onboardingSave: `${API_BASE_URL}/users/onboarding`,
  planReadyMessage: `${API_BASE_URL}/settings/plan-ready-message`,
} as const

export { API_BASE_URL }
