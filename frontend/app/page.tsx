'use client'

import { useState, useEffect } from 'react'
import { useUser, SignInButton } from '@clerk/nextjs'
import ChatInterface from '../components/ChatInterface'
import Navbar from '../components/Navbar'
import Hero from '../components/Hero'
import Features from '../components/Features'
import Footer from '../components/Footer'

export default function HomePage() {
  const [showChat, setShowChat] = useState(false)
  const [isLoaded, setIsLoaded] = useState(false)
  const { isSignedIn, isLoaded: userLoaded, user } = useUser()

  useEffect(() => {
    setIsLoaded(true)
  }, [])

  const handleStartLearning = () => {
    setShowChat(true)
  }

  if (!isLoaded || !userLoaded) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="spinner mx-auto mb-4"></div>
          <p className="text-vedya-purple font-medium">Loading VEDYA...</p>
        </div>
      </div>
    )
  }

  // Show sign-in screen if user is not authenticated
  if (!isSignedIn) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-vedya-purple/10 via-white to-vedya-pink/10">
        <div className="container mx-auto px-4 h-screen flex items-center justify-center">
          <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
            <div className="w-20 h-20 bg-gradient-to-br from-vedya-purple to-vedya-pink rounded-2xl flex items-center justify-center mx-auto mb-6">
              <span className="text-white font-bold text-3xl">V</span>
            </div>
            
            <h1 className="text-3xl font-bold gradient-text mb-2">Welcome to VEDYA</h1>
            <p className="text-gray-600 mb-6">
              AI-Powered Education Platform
            </p>
            <p className="text-sm text-gray-500 mb-8">
              Sign in to access your personalized learning experience powered by advanced AI technology.
            </p>
            
            <SignInButton mode="modal">
              <button className="btn-primary w-full mb-4">
                Sign In to Start Learning
              </button>
            </SignInButton>
            
            <p className="text-xs text-gray-400">
              By signing in, you agree to our Terms of Service and Privacy Policy
            </p>
          </div>
        </div>
        
        {/* VAYU Innovations Fixed Badge */}
        <div className="fixed bottom-4 right-4 z-50">
          <div className="bg-white/90 backdrop-blur-sm border border-gray-200 rounded-full px-4 py-2 shadow-lg">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-vedya-purple rounded-full animate-pulse"></div>
              <span className="text-sm font-medium text-gray-700">
                Powered by{' '}
                <span className="gradient-text font-bold">
                  VAYU Innovations
                </span>
              </span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Show main app for authenticated users
  return (
    <div className="min-h-screen">
      <Navbar onStartLearning={handleStartLearning} />
      <Hero onStartLearning={handleStartLearning} />
      <Features />
      <Footer />
      
      <ChatInterface isOpen={showChat} onClose={() => setShowChat(false)} />
      
      {/* Floating Chat Button */}
      {!showChat && (
        <button
          onClick={handleStartLearning}
          className="fixed bottom-20 right-4 z-30 bg-gradient-to-r from-vedya-purple to-vedya-pink text-white p-4 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-110 glow-animation"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </button>
      )}
    </div>
  )
}
