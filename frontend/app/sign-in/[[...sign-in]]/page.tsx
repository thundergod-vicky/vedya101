import { SignIn } from '@clerk/nextjs'

export default function SignInPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-vedya-purple/10 via-white to-vedya-pink/10 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-vedya-purple to-vedya-pink rounded-2xl flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-bold text-2xl">V</span>
          </div>
          <h1 className="text-2xl font-bold gradient-text mb-2">Welcome Back to VEDYA</h1>
          <p className="text-gray-600">Sign in to continue your learning journey</p>
        </div>
        
        <SignIn 
          appearance={{
            elements: {
              formButtonPrimary: "bg-gradient-to-r from-vedya-purple to-vedya-pink hover:from-vedya-purple/90 hover:to-vedya-pink/90",
              card: "shadow-xl border-0",
              headerTitle: "hidden",
              headerSubtitle: "hidden"
            }
          }}
        />
        
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
    </div>
  )
}
