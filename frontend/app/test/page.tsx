import React from 'react'

export default function TestPage() {
  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">CSS Test Page</h1>
        
        {/* Test Tailwind Basic Classes */}
        <div className="bg-white p-6 rounded-lg shadow-lg mb-8">
          <h2 className="text-2xl font-semibold mb-4">Basic Tailwind Classes</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-red-500 text-white p-4 rounded">Red Background</div>
            <div className="bg-blue-500 text-white p-4 rounded">Blue Background</div>
            <div className="bg-green-500 text-white p-4 rounded">Green Background</div>
          </div>
        </div>

        {/* Test Custom VEDYA Colors */}
        <div className="bg-white p-6 rounded-lg shadow-lg mb-8">
          <h2 className="text-2xl font-semibold mb-4">VEDYA Custom Colors</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-vedya-purple text-white p-4 rounded">Vedya Purple</div>
            <div className="bg-vedya-pink text-white p-4 rounded">Vedya Pink</div>
            <div className="bg-vedya-orange text-white p-4 rounded">Vedya Orange</div>
          </div>
          <div className="mt-4 space-y-2">
            <p className="text-vedya-purple">Text in Vedya Purple</p>
            <p className="text-vedya-pink">Text in Vedya Pink</p>
            <p className="text-vedya-orange">Text in Vedya Orange</p>
          </div>
        </div>

        {/* Test Custom Components */}
        <div className="bg-white p-6 rounded-lg shadow-lg mb-8">
          <h2 className="text-2xl font-semibold mb-4">Custom Component Classes</h2>
          <div className="space-y-4">
            <button className="btn-primary">Primary Button</button>
            <button className="btn-secondary">Secondary Button</button>
            <div className="card">
              <h3 className="text-lg font-semibold gradient-text">Gradient Text in Card</h3>
              <p>This is a test card with gradient text.</p>
            </div>
            <div className="spinner"></div>
          </div>
        </div>

        {/* Test Animations */}
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-2xl font-semibold mb-4">Custom Animations</h2>
          <div className="space-y-4">
            <div className="animate-fade-in bg-vedya-purple text-white p-4 rounded">Fade In Animation</div>
            <div className="animate-pulse-slow bg-vedya-pink text-white p-4 rounded">Pulse Slow Animation</div>
            <div className="animate-float bg-vedya-orange text-white p-4 rounded">Float Animation</div>
          </div>
        </div>
      </div>
    </div>
  )
}
