'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import { useUser } from '@clerk/nextjs'
import { Group, Panel, Separator } from 'react-resizable-panels'
import { API_ENDPOINTS } from '../lib/api-config'
import Sketchboard from './Sketchboard'

const CHAT_WIDTH_DEFAULT_PX = 380
const CHAT_WIDTH_MIN_PX = 280
const CHAT_WIDTH_MAX_PX = 600
const CHAT_COLLAPSED_WIDTH_PX = 52

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
  // Layout: chat collapsible; playground + sketchboard always visible on right
  const [chatCollapsed, setChatCollapsed] = useState(false)
  const [playgroundLanguage, setPlaygroundLanguage] = useState<'python' | 'java' | 'c' | 'cpp' | 'javascript'>('python')
  const [playgroundCode, setPlaygroundCode] = useState('# Try the code from the lesson here!\n# Example:\nprint("Hello from the playground!")\nprint(2 + 2)')
  const [playgroundOutput, setPlaygroundOutput] = useState<{ stdout: string; stderr: string; exitCode: number } | null>(null)
  const [playgroundRunning, setPlaygroundRunning] = useState(false)
  // Voice: input (mic) and output (TTS)
  const [isListening, setIsListening] = useState(false)
  const [speechInputSupported, setSpeechInputSupported] = useState(false)
  const [ttsSupported, setTtsSupported] = useState(false)
  const [voiceReplyEnabled, setVoiceReplyEnabled] = useState(false)
  const recognitionRef = useRef<{ stop: () => void } | null>(null)
  // Chat width in pixels when expanded; guarantees visible width and drag resize
  const [chatWidthPx, setChatWidthPx] = useState(CHAT_WIDTH_DEFAULT_PX)
  const containerRef = useRef<HTMLDivElement>(null)
  const isDraggingRef = useRef(false)

  const PLAYGROUND_DEFAULTS: Record<string, string> = {
    python: '# Try the code from the lesson here!\n# Example:\nprint("Hello from the playground!")\nprint(2 + 2)',
    java: 'public class Main {\n  public static void main(String[] args) {\n    System.out.println("Hello from Java!");\n  }\n}',
    c: '#include <stdio.h>\nint main() {\n  printf("Hello from C!\\n");\n  return 0;\n}',
    cpp: '#include <iostream>\nint main() {\n  std::cout << "Hello from C++!" << std::endl;\n  return 0;\n}',
    javascript: 'console.log("Hello from JavaScript!");\nconsole.log(2 + 2);',
  }
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const messagesScrollRef = useRef<HTMLDivElement>(null)
  const playgroundCodeRef = useRef<HTMLTextAreaElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const handleMessagesWheel = (e: React.WheelEvent<HTMLDivElement>) => {
    const el = messagesScrollRef.current
    if (!el) return
    const { scrollHeight, clientHeight, scrollTop } = el
    const canScrollUp = scrollTop > 0
    const canScrollDown = scrollTop < scrollHeight - clientHeight - 1
    const scrollingDown = e.deltaY > 0
    const scrollingUp = e.deltaY < 0
    if ((scrollingDown && canScrollDown) || (scrollingUp && canScrollUp)) {
      e.preventDefault()
      e.stopPropagation()
      el.scrollTop += e.deltaY
    }
  }

  const handlePlaygroundCodeWheel = (e: React.WheelEvent<HTMLTextAreaElement>) => {
    const el = playgroundCodeRef.current
    if (!el) return
    const { scrollHeight, clientHeight, scrollTop } = el
    const canScrollUp = scrollTop > 0
    const canScrollDown = scrollTop < scrollHeight - clientHeight - 1
    const scrollingDown = e.deltaY > 0
    const scrollingUp = e.deltaY < 0
    if ((scrollingDown && canScrollDown) || (scrollingUp && canScrollUp)) {
      e.preventDefault()
      e.stopPropagation()
      el.scrollTop += e.deltaY
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (typeof window === 'undefined') return
    const SR = (window as unknown as { SpeechRecognition?: unknown; webkitSpeechRecognition?: unknown }).SpeechRecognition ?? (window as unknown as { webkitSpeechRecognition?: unknown }).webkitSpeechRecognition
    if (SR) setSpeechInputSupported(true)
    if ('speechSynthesis' in window && typeof SpeechSynthesisUtterance !== 'undefined') setTtsSupported(true)
  }, [])

  useEffect(() => {
    // Initialize teaching session when component mounts
    initializeTeachingSession()
  }, [planId, moduleId])

  // Drag-to-resize chat width (horizontal, in pixels)
  const handleResizeStart = useCallback((e: React.MouseEvent) => {
    e.preventDefault()
    isDraggingRef.current = true
    const startX = e.clientX
    const startWidth = chatWidthPx

    const onMove = (moveEvent: MouseEvent) => {
      const deltaX = moveEvent.clientX - startX
      let next = startWidth + deltaX
      next = Math.max(CHAT_WIDTH_MIN_PX, Math.min(CHAT_WIDTH_MAX_PX, next))
      setChatWidthPx(next)
    }
    const onUp = () => {
      isDraggingRef.current = false
      document.removeEventListener('mousemove', onMove)
      document.removeEventListener('mouseup', onUp)
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
    document.addEventListener('mousemove', onMove)
    document.addEventListener('mouseup', onUp)
  }, [chatWidthPx])

  const speakText = useCallback((text: string) => {
    if (!voiceReplyEnabled || !text.trim()) return
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) return
    window.speechSynthesis.cancel()
    const u = new SpeechSynthesisUtterance(text.slice(0, 3000))
    u.lang = 'en-US'
    u.rate = 1
    window.speechSynthesis.speak(u)
  }, [voiceReplyEnabled])

  const startVoiceInput = useCallback(() => {
    if (typeof window === 'undefined') return
    const Win = window as unknown as { SpeechRecognition?: new () => { start: () => void; stop: () => void; lang: string; interimResults: boolean; maxAlternatives: number; onresult: (e: { results: { [i: number]: { [j: number]: { transcript: string } } } }) => void; onerror: () => void; onend: () => void }; webkitSpeechRecognition?: new () => { start: () => void; stop: () => void; lang: string; interimResults: boolean; maxAlternatives: number; onresult: (e: { results: { [i: number]: { [j: number]: { transcript: string } } } }) => void; onerror: () => void; onend: () => void } }
    const SR = Win.SpeechRecognition ?? Win.webkitSpeechRecognition
    if (!SR || isListening) return
    const recognition = new SR()
    recognition.lang = 'en-US'
    recognition.interimResults = false
    recognition.maxAlternatives = 1
    recognition.onresult = (e: { results: { [i: number]: { [j: number]: { transcript: string } } } }) => {
      const t = e.results?.[0]?.[0]?.transcript?.trim()
      if (t) sendMessage(t)
    }
    recognition.onerror = () => { setIsListening(false); recognitionRef.current = null }
    recognition.onend = () => { setIsListening(false); recognitionRef.current = null }
    recognitionRef.current = recognition
    setIsListening(true)
    recognition.start()
  }, [isListening])

  const stopVoiceInput = useCallback(() => {
    recognitionRef.current?.stop()
    recognitionRef.current = null
    setIsListening(false)
  }, [])

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
        
        // Accept both http(s) URLs and inline data URLs (e.g. data:image/svg+xml;base64,...)
        const validUrl = typeof data.diagram_url === 'string' && (
          data.diagram_url.startsWith('http') || data.diagram_url.startsWith('data:image/')
        );
        if (!validUrl) {
          console.error("❌ Invalid diagram URL format:", data.diagram_url?.slice?.(0, 80));
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

  const sendMessage = async (raw: string) => {
    const currentInput = raw.trim()
    if (!currentInput) return

    const userMessage: TeachingMessage = {
      id: Date.now().toString(),
      content: currentInput,
      sender: 'user',
      timestamp: new Date(),
      type: 'text'
    }
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      const response = await fetch(API_ENDPOINTS.teachingChat, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: currentInput,
          plan_id: planId,
          module_id: moduleId,
          current_concept: currentConcept,
          stream: false
        }),
      })
      const data = await response.json()

      if (!response.ok) throw new Error(data.detail || data.error || `Request failed (${response.status})`)
      if (!data.success) throw new Error(data.error || data.detail || 'Failed to get response from teaching assistant')

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
      speakText(teacherResponse.content)

      if (data.current_concept) setCurrentConcept(data.current_concept)
      if (data.should_generate_visual) {
        const conceptToVisualize = data.visual_concept || data.current_concept || currentConcept
        const visualType = data.visual_type || 'concept_illustration'
        setTimeout(() => generateSupervisedVisual(conceptToVisualize, visualType), 800)
      }
      if (data.diagram_url) {
        const visualMessage: TeachingMessage = {
          id: (Date.now() + 2).toString(),
          content: `Here's a visual to help illustrate ${data.current_concept || currentConcept}:`,
          sender: 'teacher',
          timestamp: new Date(),
          type: 'image',
          imageUrl: data.diagram_url
        }
        setTimeout(() => setMessages(prev => [...prev, visualMessage]), 500)
      }
    } catch (error) {
      console.error('❌ Error sending message:', error)
      const fallbackResponse: TeachingMessage = {
        id: (Date.now() + 1).toString(),
        content: "I'm having a bit of trouble right now, but let's continue. Can you tell me more about what you'd like to understand?",
        sender: 'teacher',
        timestamp: new Date(),
        type: 'text'
      }
      setMessages(prev => [...prev, fallbackResponse])
      speakText(fallbackResponse.content)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSendMessage = () => {
    if (!inputValue.trim()) return
    const t = inputValue.trim()
    setInputValue('')
    sendMessage(t)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const runPlaygroundCode = async () => {
    setPlaygroundRunning(true)
    setPlaygroundOutput(null)
    try {
      const res = await fetch(API_ENDPOINTS.executeCode, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: playgroundLanguage, code: playgroundCode }),
      })
      const data = await res.json()
      setPlaygroundOutput({
        stdout: data.stdout ?? '',
        stderr: data.stderr ?? '',
        exitCode: data.exit_code ?? -1,
      })
    } catch (e) {
      setPlaygroundOutput({ stdout: '', stderr: String(e), exitCode: -1 })
    } finally {
      setPlaygroundRunning(false)
    }
  }

  const handlePlaygroundLanguageChange = (lang: 'python' | 'java' | 'c' | 'cpp' | 'javascript') => {
    setPlaygroundLanguage(lang)
    setPlaygroundCode(PLAYGROUND_DEFAULTS[lang] ?? PLAYGROUND_DEFAULTS.python)
    setPlaygroundOutput(null)
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
                  <div className="p-8 bg-gradient-to-br from-indigo-50 to-purple-50 text-center rounded-lg border border-indigo-100">
                    <div className="w-16 h-16 mx-auto mb-3 rounded-xl bg-indigo-100 flex items-center justify-center">
                      <svg className="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <p className="text-sm font-medium text-indigo-900">Visual placeholder</p>
                    <p className="text-xs text-indigo-600 mt-1">Diagram for this concept will appear when the visual service is available.</p>
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
                    onError={() => {
                      console.warn("🖼️ Image failed to load (showing placeholder):", message.imageUrl?.slice(0, 60));
                      setImageError(true);
                    }}
                  />
                )}
                <div className="p-2 text-xs text-center text-gray-500">
                  Visual aid for: {message.content.replace("Here's a visual to help illustrate ", "").replace(":", "").trim()}
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
    <div ref={containerRef} className="h-full min-h-0 w-full flex bg-white/80 border border-gray-200/80 rounded-t-xl overflow-hidden shadow-sm">
      {/* Left: Chat — pixel width so it always starts visible (380px), resizable 280–600px */}
      <div
        className="flex flex-col bg-gray-50/90 border-r border-gray-200 min-h-0 overflow-hidden flex-shrink-0"
        style={{
          width: chatCollapsed ? CHAT_COLLAPSED_WIDTH_PX : chatWidthPx,
          minWidth: chatCollapsed ? CHAT_COLLAPSED_WIDTH_PX : CHAT_WIDTH_MIN_PX,
          maxWidth: chatCollapsed ? CHAT_COLLAPSED_WIDTH_PX : CHAT_WIDTH_MAX_PX,
        }}
      >
        {/* Chat header: collapse toggle + title when expanded */}
        <div className="flex items-center gap-2 px-3 py-2 border-b border-gray-200 bg-white/80 flex-shrink-0">
          <button
            type="button"
            onClick={() => setChatCollapsed(!chatCollapsed)}
            className="p-2 rounded-lg text-gray-600 hover:bg-gray-100 hover:text-indigo-600 transition-colors"
            title={chatCollapsed ? 'Expand chat' : 'Collapse chat'}
          >
            {chatCollapsed ? (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            )}
          </button>
          {!chatCollapsed && (
            <>
              <span className="text-sm font-medium text-gray-700 truncate flex-1">
                {planData?.subject ? planData.subject : 'Chat'}
              </span>
              {ttsSupported && (
                <button
                  type="button"
                  onClick={() => setVoiceReplyEnabled((v) => !v)}
                  className={`px-2 py-1 text-xs rounded-lg border transition-colors flex-shrink-0 ${
                    voiceReplyEnabled ? 'border-indigo-500 bg-indigo-50 text-indigo-700' : 'border-gray-300 text-gray-600 hover:bg-gray-100'
                  }`}
                  title={voiceReplyEnabled ? 'AI voice on' : 'AI voice off'}
                >
                  Voice
                </button>
              )}
            </>
          )}
        </div>

        {!chatCollapsed && (
          <>
            <div
              ref={messagesScrollRef}
              onWheel={handleMessagesWheel}
              className="p-4 space-y-4 flex-1 min-h-0 overflow-y-auto overflow-x-hidden overscroll-contain"
              style={{ WebkitOverflowScrolling: 'touch' }}
            >
              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}
              {isLoading && (
                <div className="flex justify-start mb-4">
                  <div className="flex items-start space-x-3 max-w-3xl">
                    <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center text-white flex-shrink-0">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                    </div>
                    <div className="bg-white border rounded-2xl px-4 py-3 shadow-sm">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
            <div className="bg-white border-t p-3 flex-shrink-0">
              <div className="flex items-end gap-2">
                <textarea
                  ref={inputRef}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={handleKeyPress}
                  placeholder="Ask or type a message..."
                  className="flex-1 min-w-0 px-3 py-2 border border-gray-200 rounded-lg resize-none text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  rows={2}
                  disabled={isLoading}
                />
                {speechInputSupported && (
                  <button
                    type="button"
                    onClick={isListening ? stopVoiceInput : startVoiceInput}
                    className={`p-2.5 rounded-lg border text-sm transition-colors flex-shrink-0 ${
                      isListening ? 'border-red-500 text-red-600 bg-red-50' : 'border-gray-300 text-gray-600 hover:bg-gray-100'
                    }`}
                    aria-label={isListening ? 'Stop listening' : 'Voice input'}
                    title={isListening ? 'Stop' : 'Speak to type & send'}
                  >
                    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                      <path d="M12 3a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V6a3 3 0 0 0-3-3z" />
                      <path d="M19 10a7 7 0 0 1-14 0" />
                      <path d="M12 17v4" />
                      <path d="M8 21h8" />
                    </svg>
                  </button>
                )}
                <button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isLoading}
                  className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex-shrink-0"
                >
                  Send
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Resize handle: only when chat is expanded */}
      {!chatCollapsed && (
        <div
          role="separator"
          aria-orientation="vertical"
          onMouseDown={handleResizeStart}
          className="w-3 flex-shrink-0 bg-gray-300 hover:bg-indigo-300 active:bg-indigo-400 rounded transition-colors cursor-col-resize flex items-center justify-center"
          title="Drag to resize chat"
        />
      )}

      {/* Right: Code Playground (top) + Sketchboard (bottom) — resizable */}
      <div className="flex-1 min-w-0 min-h-0 flex flex-col">
        <Group orientation="vertical" className="h-full flex-1 min-h-0">
            <Panel defaultSize={50} minSize={25} className="min-h-0 flex flex-col">
              <div className="flex flex-col flex-1 min-h-0 p-3 pt-0">
                <div className="flex flex-col flex-1 min-h-0 bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="flex items-center justify-between px-3 py-2 border-b border-gray-200 bg-gray-50/80 flex-shrink-0 flex-wrap gap-2">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-sm font-medium text-gray-800">Code Playground</span>
              <select
                value={playgroundLanguage}
                onChange={(e) => handlePlaygroundLanguageChange(e.target.value as 'python' | 'java' | 'c' | 'cpp' | 'javascript')}
                className="text-xs font-medium rounded border border-gray-200 bg-white px-2 py-1.5 text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="python">Python</option>
                <option value="java">Java</option>
                <option value="c">C</option>
                <option value="cpp">C++</option>
                <option value="javascript">JavaScript</option>
              </select>
            </div>
          </div>
          <div className="flex flex-col flex-1 min-h-0 overflow-hidden">
            <div className="relative flex-1 min-h-[120px]">
              <textarea
                ref={playgroundCodeRef}
                onWheel={handlePlaygroundCodeWheel}
                value={playgroundCode}
                onChange={(e) => setPlaygroundCode(e.target.value)}
                className="absolute inset-0 w-full h-full p-3 font-mono text-sm border-0 border-b border-gray-200 focus:outline-none focus:ring-0 resize-none bg-gray-50/50 overflow-y-auto"
                placeholder="# Write or paste code from the lesson..."
                spellCheck={false}
              />
            </div>
            <div className="flex items-center gap-2 px-3 py-2 border-t border-gray-200 bg-gray-50 flex-shrink-0">
              <button
                onClick={runPlaygroundCode}
                disabled={playgroundRunning}
                className="px-3 py-1.5 bg-emerald-600 text-white text-sm font-medium rounded-lg hover:bg-emerald-700 disabled:opacity-60 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {playgroundRunning ? (
                  <>
                    <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Running...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Run
                  </>
                )}
              </button>
              <button
                onClick={() => { setPlaygroundCode(''); setPlaygroundOutput(null); }}
                className="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-200 rounded-lg transition-colors"
              >
                Clear
              </button>
            </div>
            <div className="min-h-[80px] max-h-[140px] overflow-auto border-t border-gray-200 bg-gray-900 text-gray-100 font-mono text-xs p-3">
              {playgroundOutput === null && !playgroundRunning && (
                <div className="text-gray-500">Output appears here after you run the code.</div>
              )}
              {playgroundOutput !== null && (
                <div className="space-y-1">
                  {playgroundOutput.stdout && (
                    <pre className="whitespace-pre-wrap break-words text-emerald-200">{playgroundOutput.stdout}</pre>
                  )}
                  {playgroundOutput.stderr && (
                    <pre className="whitespace-pre-wrap break-words text-red-300">{playgroundOutput.stderr}</pre>
                  )}
                  {playgroundOutput.exitCode !== 0 && !playgroundOutput.stdout && !playgroundOutput.stderr && (
                    <span className="text-amber-300">Exit code {playgroundOutput.exitCode}</span>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
              </div>
            </Panel>

            <Separator className="h-2 shrink-0 bg-gray-200 hover:bg-indigo-200 rounded transition-colors cursor-row-resize" />

            <Panel defaultSize={50} minSize={20} className="min-h-0 flex flex-col">
              <div className="flex flex-col flex-1 min-h-0 p-3">
                <Sketchboard />
              </div>
            </Panel>
          </Group>
      </div>
    </div>
  )
}
