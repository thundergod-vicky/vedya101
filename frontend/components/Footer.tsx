export default function Footer() {
  const currentYear = new Date().getFullYear()

  const footerLinks = {
    product: [
      { name: 'Features', href: '#features' },
      { name: 'AI Agents', href: '#' },
      { name: 'Learning Paths', href: '#' },
      { name: 'Assessments', href: '#' },
      { name: 'Progress Tracking', href: '#' }
    ],
    company: [
      { name: 'About Us', href: '#' },
      { name: 'Careers', href: '#' },
      { name: 'Blog', href: '#' },
      { name: 'Press', href: '#' },
      { name: 'Contact', href: '#' }
    ],
    resources: [
      { name: 'Documentation', href: '#' },
      { name: 'API Reference', href: '#' },
      { name: 'Community', href: '#' },
      { name: 'Help Center', href: '#' },
      { name: 'Tutorials', href: '#' }
    ],
    legal: [
      { name: 'Privacy Policy', href: '#' },
      { name: 'Terms of Service', href: '#' },
      { name: 'Cookie Policy', href: '#' },
      { name: 'Security', href: '#' },
      { name: 'Compliance', href: '#' }
    ]
  }

  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Main Footer Content */}
        <div className="py-16">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8">
            {/* Brand Section */}
            <div className="lg:col-span-2">
              <div className="mb-6">
                <h3 className="text-3xl font-bold gradient-text-white">VEDYA</h3>
                <p className="text-gray-400 mt-2">
                  Powered by AI. Designed for learners.
                </p>
              </div>
              <p className="text-gray-300 leading-relaxed mb-6">
                Experience the future of education with our AI-powered platform. 
                Personalized learning paths, intelligent assessments, and real-time 
                progress tracking make learning more effective and engaging.
              </p>
              
              {/* Newsletter Signup */}
              <div className="mb-6">
                <h4 className="text-lg font-semibold mb-3">Stay Updated</h4>
                <div className="flex">
                  <input
                    type="email"
                    placeholder="Enter your email"
                    className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-vedya-purple focus:border-transparent text-white placeholder-gray-400"
                  />
                  <button className="bg-gradient-to-r from-vedya-purple to-vedya-pink px-6 py-2 rounded-r-lg hover:from-vedya-purple/90 hover:to-vedya-pink/90 transition-all duration-300 font-medium">
                    Subscribe
                  </button>
                </div>
              </div>

              {/* Social Links */}
              <div className="flex space-x-4">
                <SocialLink href="#" icon="🐦" label="Twitter" />
                <SocialLink href="#" icon="📘" label="Facebook" />
                <SocialLink href="#" icon="💼" label="LinkedIn" />
                <SocialLink href="#" icon="📸" label="Instagram" />
                <SocialLink href="#" icon="🎥" label="YouTube" />
              </div>
            </div>

            {/* Product Links */}
            <div>
              <h4 className="text-lg font-semibold mb-4 text-vedya-yellow">Product</h4>
              <ul className="space-y-3">
                {footerLinks.product.map((link) => (
                  <li key={link.name}>
                    <a
                      href={link.href}
                      className="text-gray-400 hover:text-white transition-colors duration-200"
                    >
                      {link.name}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Company Links */}
            <div>
              <h4 className="text-lg font-semibold mb-4 text-vedya-pink">Company</h4>
              <ul className="space-y-3">
                {footerLinks.company.map((link) => (
                  <li key={link.name}>
                    <a
                      href={link.href}
                      className="text-gray-400 hover:text-white transition-colors duration-200"
                    >
                      {link.name}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Resources Links */}
            <div>
              <h4 className="text-lg font-semibold mb-4 text-vedya-orange">Resources</h4>
              <ul className="space-y-3">
                {footerLinks.resources.map((link) => (
                  <li key={link.name}>
                    <a
                      href={link.href}
                      className="text-gray-400 hover:text-white transition-colors duration-200"
                    >
                      {link.name}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Features Highlight */}
          <div className="mt-16 pt-8 border-t border-gray-800">
            <h4 className="text-xl font-semibold mb-6 text-center">Why Choose VEDYA?</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <FeatureHighlight
                icon={
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                }
                title="AI-Powered Learning"
                description="Adaptive algorithms that personalize your educational journey"
              />
              <FeatureHighlight
                icon={
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                }
                title="Real-time Analytics"
                description="Track your progress with detailed insights and recommendations"
              />
              <FeatureHighlight
                icon={
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                }
                title="Goal-Oriented"
                description="Structured learning paths designed to achieve your objectives"
              />
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="py-6 border-t border-gray-800">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex flex-col md:flex-row items-center space-y-2 md:space-y-0 md:space-x-6">
              <p className="text-gray-400 text-sm">
                © {currentYear} VEDYA. All rights reserved.
              </p>
              <div className="flex space-x-6">
                {footerLinks.legal.map((link) => (
                  <a
                    key={link.name}
                    href={link.href}
                    className="text-gray-400 hover:text-white text-sm transition-colors duration-200"
                  >
                    {link.name}
                  </a>
                ))}
              </div>
            </div>
            <div className="mt-4 md:mt-0">
              <p className="text-gray-400 text-sm">
                Made with ❤️ for learners worldwide
              </p>
            </div>
          </div>
        </div>

        {/* VAYU Innovations Badge - Fixed positioning */}
        <div className="fixed bottom-4 right-4 z-40">
          <div className="bg-gradient-to-r from-vedya-purple to-vedya-pink p-3 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 group cursor-pointer">
            <div className="flex items-center space-x-2 text-white">
              <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                <span className="text-sm font-bold">V</span>
              </div>
              <div className="hidden group-hover:block transition-all duration-300">
                <p className="text-xs font-medium">Powered by</p>
                <p className="text-sm font-bold">VAYU Innovations</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}

interface SocialLinkProps {
  href: string
  icon: string
  label: string
}

function SocialLink({ href, icon, label }: SocialLinkProps) {
  return (
    <a
      href={href}
      className="w-10 h-10 bg-gray-800 hover:bg-gradient-to-r hover:from-vedya-purple hover:to-vedya-pink rounded-full flex items-center justify-center transition-all duration-300 transform hover:scale-110"
      aria-label={label}
    >
      <span className="text-lg">{icon}</span>
    </a>
  )
}

interface FeatureHighlightProps {
  icon: React.ReactNode
  title: string
  description: string
}

function FeatureHighlight({ icon, title, description }: FeatureHighlightProps) {
  return (
    <div className="text-center">
      <div className="text-vedya-purple mb-3 flex justify-center">{icon}</div>
      <h5 className="text-lg font-semibold text-white mb-2">{title}</h5>
      <p className="text-gray-400 text-sm">{description}</p>
    </div>
  )
}
