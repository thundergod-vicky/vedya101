import { useState } from 'react'

const features = [
  {
    id: 'ai-personalization',
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
      </svg>
    ),
    title: 'AI-Powered Personalization',
    description: 'Our advanced AI algorithms analyze your learning patterns and preferences to create a completely personalized educational experience.',
    details: [
      'Adaptive learning paths based on your progress',
      'Smart content recommendations',
      'Personalized difficulty adjustments',
      'Learning style recognition and adaptation'
    ]
  },
  {
    id: 'interactive-content',
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h8m2-8V8a2 2 0 00-2-2H7a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2V8z" />
      </svg>
    ),
    title: 'Interactive Learning Content',
    description: 'Engage with dynamic, multimedia content that makes learning enjoyable and effective.',
    details: [
      'Interactive simulations and demos',
      'Gamified learning experiences',
      'Real-time coding environments',
      'Virtual labs and experiments'
    ]
  },
  {
    id: 'progress-tracking',
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
    title: 'Advanced Progress Tracking',
    description: 'Monitor your learning journey with comprehensive analytics and insights.',
    details: [
      'Real-time progress visualization',
      'Detailed performance analytics',
      'Achievement badges and milestones',
      'Learning streak tracking'
    ]
  },
  {
    id: 'multi-agent-system',
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
      </svg>
    ),
    title: 'Multi-Agent Learning System',
    description: 'Experience coordinated AI agents working together to optimize your learning experience.',
    details: [
      'Specialized agents for different subjects',
      'Coordinated learning plan creation',
      'Real-time assistance and guidance',
      'Continuous curriculum optimization'
    ]
  },
  {
    id: 'assessments',
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    title: 'Smart Assessments',
    description: 'Take adaptive quizzes and assessments that adjust to your knowledge level.',
    details: [
      'AI-generated quiz questions',
      'Adaptive difficulty scaling',
      'Instant feedback and explanations',
      'Comprehensive performance reports'
    ]
  },
  {
    id: 'collaboration',
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
    ),
    title: 'Collaborative Learning',
    description: 'Connect with peers and learn together in our interactive community environment.',
    details: [
      'Study groups and discussions',
      'Peer-to-peer learning',
      'Expert mentorship programs',
      'Community challenges and competitions'
    ]
  }
]

export default function Features() {
  const [activeFeature, setActiveFeature] = useState<string | null>(null)

  return (
    <section id="features" className="py-20 bg-gradient-to-b from-white to-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Powerful Features for 
            <span className="gradient-text block mt-2">Modern Learning</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Discover how our cutting-edge technology transforms the way you learn, 
            making education more personalized, engaging, and effective than ever before.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature) => (
            <FeatureCard
              key={feature.id}
              feature={feature}
              isActive={activeFeature === feature.id}
              onClick={() => setActiveFeature(activeFeature === feature.id ? null : feature.id)}
            />
          ))}
        </div>

        {/* Feature Showcase */}
        <div className="mt-20">
          <div className="bg-white rounded-3xl shadow-2xl overflow-hidden">
            <div className="grid grid-cols-1 lg:grid-cols-2">
              {/* Left side - Feature visualization */}
              <div className="bg-gradient-to-br from-vedya-purple/10 to-vedya-pink/10 p-8 lg:p-12 flex items-center justify-center">
                <div className="text-center">
                  <div className="w-32 h-32 mx-auto mb-6 bg-gradient-to-br from-vedya-purple to-vedya-pink rounded-full flex items-center justify-center text-white shadow-2xl">
                    <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">
                    Experience the Future of Learning
                  </h3>
                  <p className="text-gray-600">
                    Join thousands of learners who have transformed their education with VEDYA
                  </p>
                </div>
              </div>

              {/* Right side - Stats */}
              <div className="p-8 lg:p-12">
                <h3 className="text-2xl font-bold text-gray-900 mb-8">Learning Impact</h3>
                <div className="space-y-6">
                  <StatItem 
                    label="Learning Efficiency Increase"
                    value="85%"
                    color="text-vedya-purple"
                  />
                  <StatItem 
                    label="Student Engagement Rate"
                    value="94%"
                    color="text-vedya-pink"
                  />
                  <StatItem 
                    label="Knowledge Retention"
                    value="78%"
                    color="text-vedya-orange"
                  />
                  <StatItem 
                    label="Course Completion Rate"
                    value="92%"
                    color="text-vedya-yellow"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

interface FeatureCardProps {
  feature: typeof features[0]
  isActive: boolean
  onClick: () => void
}

function FeatureCard({ feature, isActive, onClick }: FeatureCardProps) {
  return (
    <div
      className={`
        bg-white rounded-2xl p-6 shadow-lg cursor-pointer transition-all duration-300
        hover:shadow-xl hover:transform hover:scale-105
        ${isActive ? 'ring-2 ring-vedya-purple shadow-xl scale-105' : ''}
      `}
      onClick={onClick}
    >
      <div className="text-vedya-purple mb-4 flex justify-center">{feature.icon}</div>
      <h3 className="text-xl font-semibold text-gray-900 mb-3">
        {feature.title}
      </h3>
      <p className="text-gray-600 mb-4 leading-relaxed">
        {feature.description}
      </p>
      
      {/* Expandable details */}
      <div className={`overflow-hidden transition-all duration-300 ${isActive ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'}`}>
        <div className="border-t border-gray-200 pt-4 mt-4">
          <ul className="space-y-2">
            {feature.details.map((detail, index) => (
              <li key={index} className="flex items-start text-sm text-gray-600">
                <span className="text-vedya-purple mr-2">•</span>
                {detail}
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="mt-4 text-vedya-purple font-medium text-sm">
        {isActive ? 'Click to collapse' : 'Click to learn more'}
      </div>
    </div>
  )
}

interface StatItemProps {
  label: string
  value: string
  color: string
}

function StatItem({ label, value, color }: StatItemProps) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-gray-600">{label}</span>
      <div className="flex items-center">
        <div className="w-24 h-2 bg-gray-200 rounded-full mr-3">
          <div 
            className={`h-full ${color.replace('text-', 'bg-')} rounded-full transition-all duration-1000`}
            style={{ width: value }}
          ></div>
        </div>
        <span className={`font-bold ${color}`}>{value}</span>
      </div>
    </div>
  )
}
