'use client'

import { useState, useRef, useEffect } from 'react'
import { useUser } from '@clerk/nextjs'
import { API_ENDPOINTS } from '../lib/api-config'

interface TeachingMessage {
  id: string
  content: string
  sender: 'user' | 'teacher'
  timestamp: Date
  type?: 'text' | 'image' | 'graph' | 'explanation'
  imageUrl?: string
  graphData?: any
}

interface TeachingInterfaceProps {
  planId: string
  moduleId?: string
}

export default function TeachingInterface({ planId, moduleId }: TeachingInterfaceProps) {
  const { user } = useUser()
  const [messages, setMessages] = useState<TeachingMessage[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentConcept, setCurrentConcept] = useState('')
  const [showExplanationPanel, setShowExplanationPanel] = useState(false)
  const [explanationText, setExplanationText] = useState('')
  const [planData, setPlanData] = useState<any>(null)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Initialize teaching session when component mounts
    initializeTeachingSession()
  }, [planId, moduleId])

  const initializeTeachingSession = async () => {
    try {
      // Start teaching session with contextual introduction
      const response = await fetch(API_ENDPOINTS.teachingStart, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plan_id: planId,
          module_id: moduleId
        }),
      })

      const data = await response.json()
      setPlanData(data.plan_data)
      
      // Add intelligent welcome message from the TeachingAssistant
      const welcomeMessage: TeachingMessage = {
        id: '1',
        content: data.initial_message || `Welcome to your learning session! I'm your AI instructor, ready to guide you through this subject step by step.`,
        sender: 'teacher',
        timestamp: new Date(),
        type: 'text'
      }
      
      setMessages([welcomeMessage])
      setCurrentConcept(data.current_concept || 'introduction')
      
      // Don't auto-generate visuals immediately - let the teaching flow naturally
      // Visuals will be generated when contextually appropriate during the conversation
      
    } catch (error) {
      console.error('Error initializing teaching session:', error)
      // Fallback welcome message
      const fallbackMessage: TeachingMessage = {
        id: '1',
        content: `Welcome to your learning session! I'm your AI instructor, and I'm here to guide you through this topic step by step. I'll help you understand each concept thoroughly and provide visual aids when they'll be most helpful for your learning.`,
        sender: 'teacher',
        timestamp: new Date(),
        type: 'text'
      }
      setMessages([fallbackMessage])
    }
  }

  const generateSupervisedVisual = async (concept: string, visualType: string = 'concept_illustration') => {
    if (!concept) return
    
    try {
      console.log('🎨 Generating supervised visual for concept:', concept)
      
      const response = await fetch(API_ENDPOINTS.teachingDiagram, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          concept: concept,
          visual_type: visualType,
          subject: planData?.subject || 'Artificial Intelligence',
          supervised: true // Ensures supervision by ImageGenerationAssistant
        }),
      })

      const data = await response.json()
      console.log("Visual generation response:", data) // Log full response for debugging
      
      if (data.success && data.diagram_url) {
        console.log("🎨 Generated diagram URL:", data.diagram_url)
        
        // Validate the URL
        if (!data.diagram_url.startsWith('http')) {
          console.error("❌ Invalid diagram URL format:", data.diagram_url);
          throw new Error("Invalid URL format received from server");
        }
        
        // Create visual message
        const visualMessage: TeachingMessage = {
          id: Date.now().toString(),
          content: `Here's a visual to help illustrate ${concept}:`,
          sender: 'teacher',
          timestamp: new Date(),
          type: 'image',
          imageUrl: data.diagram_url
        }
        
        // Pre-validate the image URL by trying to load it
        const imgTest = new Image();
        imgTest.onload = () => {
          console.log("✅ Image pre-validation successful:", data.diagram_url);
          setMessages(prev => [...prev, visualMessage]);
        };
        imgTest.onerror = () => {
          console.error("❌ Image pre-validation failed:", data.diagram_url);
          // Still add the message, but our component will handle the error state
          setMessages(prev => [...prev, visualMessage]);
        };
        imgTest.src = data.diagram_url;
        
        // Log supervision status
        if (data.supervised) {
          console.log('✅ Visual approved by supervision system')
        }
      } else {
        console.error("❌ Failed to generate visual:", data.error || "Unknown error")
        
        // Add an error message
        const errorMessage: TeachingMessage = {
          id: Date.now().toString(),
          content: "I tried to generate a visual for this concept, but encountered an issue. Let's continue with the explanation.",
          sender: 'teacher',
          timestamp: new Date(),
          type: 'text'
        }
        
        setMessages(prev => [...prev, errorMessage])
      }
      
    } catch (error) {
      console.error('❌ Error generating supervised visual:', error)
      
      // Add a fallback message when visual generation fails
      const fallbackMessage: TeachingMessage = {
        id: Date.now().toString(),
        content: "I wanted to show you a visual for this concept, but I encountered a technical issue. Let's continue with our discussion.",
        sender: 'teacher',
        timestamp: new Date(),
        type: 'text'
      }
      
      setMessages(prev => [...prev, fallbackMessage])
    }
  }

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const userMessage: TeachingMessage = {
      id: Date.now().toString(),
      content: inputValue.trim(),
      sender: 'user',
      timestamp: new Date(),
      type: 'text'
    }

    setMessages(prev => [...prev, userMessage])
    const currentInput = inputValue.trim()
    setInputValue('')
    setIsLoading(true)

    try {
      // Call teaching API endpoint
      console.log("📤 Sending teaching chat request:", currentInput);
      const response = await fetch(API_ENDPOINTS.teachingChat, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: currentInput,
          plan_id: planId,
          module_id: moduleId,
          current_concept: currentConcept,
          stream: false // Use non-streaming for now to ensure we get full metadata
        }),
      })

      const data = await response.json()
      console.log("📥 Teacher response data:", data) // Log the full response for debugging
      
      if (!data.success) {
        throw new Error(data.error || "Failed to get response from teaching assistant");
      }
      
      const teacherResponse: TeachingMessage = {
        id: (Date.now() + 1).toString(),
        content: data.response,
        sender: 'teacher',
        timestamp: new Date(),
        type: data.type || 'text',
        imageUrl: data.image_url,
        graphData: data.graph_data
      }
      
      setMessages(prev => [...prev, teacherResponse])
      
      if (data.current_concept) {
        setCurrentConcept(data.current_concept)
      }
      
      // Handle visual generation if the teacher agent suggests it
      if (data.should_generate_visual) {
        console.log("🖼️ Visual generation triggered from response data");
        const conceptToVisualize = data.visual_concept || data.current_concept || currentConcept;
        const visualType = data.visual_type || 'concept_illustration';
        
        console.log(`🖼️ Will generate visual for "${conceptToVisualize}" of type "${visualType}"`);
        
        // Add slight delay before generating visual to ensure UI updates first
        setTimeout(() => {
          generateSupervisedVisual(conceptToVisualize, visualType);
        }, 800);
      }
      
      // If the response directly includes a diagram_url, add it as a separate message
      if (data.diagram_url) {
        console.log("🖼️ Direct diagram URL found in response:", data.diagram_url);
        
        const visualMessage: TeachingMessage = {
          id: (Date.now() + 2).toString(),
          content: `Here's a visual to help illustrate ${data.current_concept || currentConcept}:`,
          sender: 'teacher',
          timestamp: new Date(),
          type: 'image',
          imageUrl: data.diagram_url
        }
        
        // Add slight delay before adding the visual message
        setTimeout(() => {
          setMessages(prev => [...prev, visualMessage]);
        }, 500);
      }
      
    } catch (error) {
      console.error('❌ Error sending message:', error)
      
      // Fallback teacher response
      const fallbackResponse: TeachingMessage = {
        id: (Date.now() + 1).toString(),
        content: "I'm having a bit of trouble right now, but let's continue. Can you tell me more about what you'd like to understand?",
        sender: 'teacher',
        timestamp: new Date(),
        type: 'text'
      }
      setMessages(prev => [...prev, fallbackResponse])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const generateVisualExplanation = async (topic: string) => {
    setIsLoading(true)
    try {
      const response = await fetch('/api/teaching/generate-visual', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic,
          plan_id: planId,
          type: 'diagram'
        }),
      })

      const data = await response.json()
      
      const visualMessage: TeachingMessage = {
        id: Date.now().toString(),
        content: `Here's a visual explanation of ${topic}:`,
        sender: 'teacher',
        timestamp: new Date(),
        type: 'image',
        imageUrl: data.image_url
      }
      
      setMessages(prev => [...prev, visualMessage])
    } catch (error) {
      console.error('Error generating visual:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const requestExplanation = () => {
    if (!explanationText.trim()) return
    
    const explanationMessage: TeachingMessage = {
      id: Date.now().toString(),
      content: `Can you explain: ${explanationText}`,
      sender: 'user',
      timestamp: new Date(),
      type: 'explanation'
    }
    
    setMessages(prev => [...prev, explanationMessage])
    setExplanationText('')
    setShowExplanationPanel(false)
    
    // Trigger explanation response
    handleTeachingRequest(explanationText)
  }

  const handleTeachingRequest = async (topic: string) => {
    setIsLoading(true)
    try {
      const response = await fetch('/api/teaching/explain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic,
          plan_id: planId,
          include_visual: true
        }),
      })

      const data = await response.json()
      
      const explanationResponse: TeachingMessage = {
        id: Date.now().toString(),
        content: data.explanation,
        sender: 'teacher',
        timestamp: new Date(),
        type: 'text'
      }
      
      setMessages(prev => [...prev, explanationResponse])
      
      // Add visual if available
      if (data.visual_url) {
        const visualMessage: TeachingMessage = {
          id: (Date.now() + 1).toString(),
          content: `Here's a visual representation to help you understand:`,
          sender: 'teacher',
          timestamp: new Date(),
          type: 'image',
          imageUrl: data.visual_url
        }
        setMessages(prev => [...prev, visualMessage])
      }
    } catch (error) {
      console.error('Error with teaching request:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const MessageBubble = ({ message }: { message: TeachingMessage }) => {
    const [imageLoaded, setImageLoaded] = useState(false);
    const [imageError, setImageError] = useState(false);

    useEffect(() => {
      // Reset image states when a new message comes in
      if (message.type === 'image' && message.imageUrl) {
        setImageLoaded(false);
        setImageError(false);
        // Pre-load the image
        const img = new Image();
        img.src = message.imageUrl;
        img.onload = () => setImageLoaded(true);
        img.onerror = () => setImageError(true);
      }
    }, [message]);

    return (
      <div className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} mb-4`}>
        <div className={`flex items-start space-x-3 max-w-3xl ${message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
          {/* Avatar */}
          <div className="flex-shrink-0">
            {message.sender === 'user' ? (
              user?.imageUrl ? (
                <img src={user.imageUrl} alt="You" className="w-8 h-8 rounded-full" />
              ) : (
                <div className="w-8 h-8 bg-indigo-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
                  {user?.firstName?.[0] || 'U'}
                </div>
              )
            ) : (
              <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center text-white">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
            )}
          </div>

          {/* Message Content */}
          <div className={`rounded-2xl px-4 py-3 ${
            message.sender === 'user' 
              ? 'bg-indigo-500 text-white' 
              : 'bg-white border shadow-sm'
          }`}>
            <div className="whitespace-pre-wrap">{message.content}</div>
            
            {/* Visual Content */}
            {message.type === 'image' && message.imageUrl && (
              <div className="mt-3 overflow-hidden rounded-lg border border-gray-200">
                {imageError ? (
                  <div className="p-4 bg-red-50 text-red-500 text-center rounded-lg">
                    <svg className="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    <p>Image failed to load</p>
                    <p className="text-xs mt-1">{message.imageUrl}</p>
                  </div>
                ) : !imageLoaded ? (
                  <div className="p-8 bg-gray-50 text-center rounded-lg">
                    <div className="flex justify-center items-center space-x-2">
                      <div className="w-3 h-3 bg-indigo-500 rounded-full animate-bounce"></div>
                      <div className="w-3 h-3 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      <div className="w-3 h-3 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                    </div>
                    <p className="text-sm text-gray-500 mt-2">Loading visual...</p>
                  </div>
                ) : (
                  <img 
                    src={message.imageUrl} 
                    alt="Visual explanation" 
                    className="rounded-lg max-w-full h-auto w-full object-contain"
                    onError={(e) => {
                      console.error("🖼️ Image failed to load:", message.imageUrl);
                      setImageError(true);
                    }}
                  />
                )}
                <div className="p-2 text-xs text-center text-gray-500">
                  Visual aid for: {message.content.replace("Here's a visual to help illustrate ", "").replace(":", "")}
                </div>
              </div>
            )}
            
            {/* Graph Content */}
            {message.type === 'graph' && message.graphData && (
              <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-600">Interactive Graph</div>
                {/* Graph component would go here */}
              </div>
            )}
            
            <div className={`text-xs mt-2 ${
              message.sender === 'user' ? 'text-indigo-100' : 'text-gray-400'
            }`}>
              {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b shadow-sm p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center text-white">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div>
              <h1 className="font-semibold text-gray-900">AI Instructor</h1>
              <p className="text-sm text-gray-500">
                {planData?.subject ? `Teaching: ${planData.subject}` : 'Interactive Learning Session'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowExplanationPanel(!showExplanationPanel)}
              className="px-3 py-1 text-sm bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors flex items-center space-x-1"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>Request Explanation</span>
            </button>
            <button
              onClick={() => generateSupervisedVisual(currentConcept || 'current topic')}
              className="px-3 py-1 text-sm bg-green-50 text-green-600 rounded-lg hover:bg-green-100 transition-colors flex items-center space-x-1"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span>Generate Visual</span>
            </button>
          </div>
        </div>
      </div>

      {/* Explanation Panel */}
      {showExplanationPanel && (
        <div className="bg-yellow-50 border-b p-4">
          <div className="flex items-center space-x-3">
            <div className="flex-1">
              <input
                type="text"
                value={explanationText}
                onChange={(e) => setExplanationText(e.target.value)}
                placeholder="What would you like me to explain? (e.g., 'neural networks', 'how transformers work')"
                className="w-full px-3 py-2 border border-yellow-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500"
                onKeyPress={(e) => e.key === 'Enter' && requestExplanation()}
              />
            </div>
            <button
              onClick={requestExplanation}
              className="px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 transition-colors"
            >
              Explain
            </button>
            <button
              onClick={() => setShowExplanationPanel(false)}
              className="px-3 py-2 text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        
        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="flex items-start space-x-3 max-w-3xl">
              <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center text-white">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div className="bg-white border rounded-2xl px-4 py-3 shadow-sm">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white border-t p-4">
        <div className="flex items-end space-x-3">
          <div className="flex-1">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask questions, request explanations, or let me know when you're ready to continue..."
              className="w-full px-4 py-3 border border-gray-200 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              rows={3}
              disabled={isLoading}
            />
          </div>
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading}
            className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </div>
        
        <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
          <span>Press Enter to send, Shift+Enter for new line</span>
          <span>AI Teacher • Interactive Learning Mode</span>
        </div>
      </div>
    </div>
  )
}
