import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { ClerkProvider } from '@clerk/nextjs'
import '../styles/globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'VEDYA - AI-Powered Education Platform',
  description: 'Personalized learning experiences powered by advanced AI technology. Built by VAYU Innovations.',
  keywords: ['education', 'ai', 'learning', 'personalized', 'vayu innovations'],
  authors: [{ name: 'VAYU Innovations' }],
  openGraph: {
    title: 'VEDYA - AI-Powered Education Platform',
    description: 'Personalized learning experiences powered by advanced AI technology.',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'VEDYA - AI-Powered Education Platform',
    description: 'Personalized learning experiences powered by advanced AI technology.',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ClerkProvider>
      <html lang="en" className="scroll-smooth">
        <head>
          <link rel="icon" href="/favicon.ico" />
          <link
            rel="preconnect"
            href="https://fonts.googleapis.com"
          />
          <link
            rel="preconnect"
            href="https://fonts.gstatic.com"
            crossOrigin="anonymous"
          />
        </head>
        <body className={`${inter.className} antialiased`}>
          <div className="min-h-screen bg-gray-50">
            {children}
            
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
        </body>
      </html>
    </ClerkProvider>
  )
}
