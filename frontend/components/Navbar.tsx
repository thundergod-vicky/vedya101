'use client'

import { useState, useEffect } from 'react'
import { UserButton, useUser } from '@clerk/nextjs'
import { useRouter } from 'next/navigation'
import { API_ENDPOINTS } from '../lib/api-config'

interface NavbarProps {
  onStartLearning?: () => void
  onBackToHome?: () => void
  showBackButton?: boolean
}

export default function Navbar({ onStartLearning, onBackToHome, showBackButton }: NavbarProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [hasLearningPlans, setHasLearningPlans] = useState(false)
  const { isSignedIn, user } = useUser()
  const router = useRouter()

  useEffect(() => {
    // Check if user has learning plans
    if (isSignedIn) {
      checkLearningPlans()
    }
  }, [isSignedIn])

  const checkLearningPlans = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.learningPlansCheck, {
        headers: {
          'Authorization': `Bearer ${user?.id}`
        }
      })
      const data = await response.json()
      setHasLearningPlans(data.hasPlans)
    } catch (error) {
      console.error('Error checking learning plans:', error)
    }
  }

  const navigateToDashboard = () => {
    router.push('/dashboard')
    setIsMenuOpen(false)
  }

  const navigateToHome = () => {
    router.push('/')
    setIsMenuOpen(false)
  }

  const handleBackToHome = () => {
    if (onBackToHome) {
      onBackToHome()
    } else {
      navigateToHome()
    }
  }

  return (
    <nav className="bg-white/90 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Brand */}
          <div className="flex items-center space-x-4">
            {showBackButton && (
              <button
                onClick={handleBackToHome}
                className="p-2 rounded-lg text-gray-600 hover:text-vedya-purple hover:bg-gray-100 transition-colors"
                aria-label="Back to home"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
            )}
            
            <button
              onClick={navigateToHome}
              className="flex items-center space-x-3 hover:opacity-80 transition-opacity"
            >
              <div className="w-10 h-10 bg-gradient-to-br from-vedya-purple to-vedya-pink rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-lg">V</span>
              </div>
              <div>
                <h1 className="text-xl font-bold gradient-text">VEDYA</h1>
                <p className="text-xs text-gray-500">AI-Powered Education</p>
              </div>
            </button>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-6">
            <button
              onClick={navigateToHome}
              className="text-gray-700 hover:text-vedya-purple font-medium transition-colors duration-200"
            >
              Home
            </button>
            
            {isSignedIn && hasLearningPlans && (
              <button
                onClick={navigateToDashboard}
                className="text-indigo-600 hover:text-indigo-700 font-medium transition-colors duration-200 flex items-center space-x-1"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <span>Dashboard</span>
              </button>
            )}
            
            {isSignedIn ? (
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-600">
                  Welcome, {user?.firstName || 'User'}!
                </span>
                <UserButton 
                  appearance={{
                    elements: {
                      avatarBox: "w-10 h-10"
                    }
                  }}
                />
              </div>
            ) : (
              !showBackButton && onStartLearning && (
                <button
                  onClick={onStartLearning}
                  className="btn-primary"
                >
                  Start Learning
                </button>
              )
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="p-2 rounded-lg text-gray-600 hover:text-vedya-purple hover:bg-gray-100 transition-colors"
              aria-label="Toggle menu"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {isMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-200">
            <div className="flex flex-col space-y-3">
              <button
                onClick={navigateToHome}
                className="block px-3 py-2 text-gray-700 hover:text-vedya-purple hover:bg-gray-50 rounded-lg font-medium transition-colors duration-200 text-left"
              >
                Home
              </button>
              
              {isSignedIn && hasLearningPlans && (
                <button
                  onClick={navigateToDashboard}
                  className="flex items-center space-x-2 px-3 py-2 text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 rounded-lg font-medium transition-colors duration-200"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <span>Dashboard</span>
                </button>
              )}
              
              {isSignedIn ? (
                <div className="px-3 py-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">
                      Welcome, {user?.firstName || 'User'}!
                    </span>
                    <UserButton 
                      appearance={{
                        elements: {
                          avatarBox: "w-8 h-8"
                        }
                      }}
                    />
                  </div>
                </div>
              ) : (
                !showBackButton && onStartLearning && (
                  <button
                    onClick={() => {
                      onStartLearning()
                      setIsMenuOpen(false)
                    }}
                    className="btn-primary w-full mt-4"
                  >
                    Start Learning
                  </button>
                )
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}

function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <a
      href={href}
      className="text-gray-700 hover:text-vedya-purple font-medium transition-colors duration-200"
    >
      {children}
    </a>
  )
}

function MobileNavLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <a
      href={href}
      className="block px-3 py-2 text-gray-700 hover:text-vedya-purple hover:bg-gray-50 rounded-lg font-medium transition-colors duration-200"
    >
      {children}
    </a>
  )
}
