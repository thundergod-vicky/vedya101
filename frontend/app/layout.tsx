import type { Metadata } from 'next'
import { Inter, Poppins } from 'next/font/google'
import { ClerkProvider } from '@clerk/nextjs'
import '../styles/globals.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import LenisProvider from '../components/LenisProvider'

const inter = Inter({ subsets: ['latin'] })
const poppins = Poppins({ 
  subsets: ['latin'],
  weight: ['600', '700', '800', '900'],
  variable: '--font-poppins',
  display: 'swap',
})

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
      <html lang="en">
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
        <body className={`${inter.className} ${poppins.variable} antialiased`}>
          <LenisProvider>
            <div className="min-h-screen">
              {children}

              {/* VAYU Innovations Fixed Badge */}
              <div className="fixed bottom-4 right-4 z-50">
                <div className="group bg-white/90 backdrop-blur-sm border border-gray-200 rounded-full px-4 py-2 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
                  <div className="flex items-center space-x-2">
                    <i className="bi bi-lightning-charge-fill text-vedya-purple text-sm animate-pulse"></i>
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
          </LenisProvider>
        </body>
      </html>
    </ClerkProvider>
  )
}
