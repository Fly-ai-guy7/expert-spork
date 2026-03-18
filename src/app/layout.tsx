import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import '@/styles/globals.css'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

export const metadata: Metadata = {
  metadataBase: new URL('https://expertspork.com'),
  title: {
    default: 'ExpertSpork — AI-Powered Freelancer Marketplace',
    template: '%s | ExpertSpork',
  },
  description:
    'ExpertSpork connects world-class freelance talent with ambitious companies. AI matching, escrow payments, and zero-hassle contracts. Join 12,000+ vetted experts.',
  keywords: [
    'freelancer marketplace',
    'hire freelancers',
    'top talent',
    'AI matching',
    'escrow payments',
    'remote work',
    'expert network',
  ],
  authors: [{ name: 'ExpertSpork' }],
  creator: 'ExpertSpork',
  publisher: 'ExpertSpork Ltd.',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://expertspork.com',
    siteName: 'ExpertSpork',
    title: 'ExpertSpork — AI-Powered Freelancer Marketplace',
    description:
      'Connect with the top 3% of freelance talent. AI matching, escrow protection, contract management.',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'ExpertSpork — Work with the Best',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    site: '@expertspork',
    creator: '@expertspork',
    title: 'ExpertSpork — AI-Powered Freelancer Marketplace',
    description: 'Connect with the top 3% of freelance talent.',
    images: ['/og-image.png'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  icons: {
    icon: [
      { url: '/favicon.ico' },
      { url: '/icon-16.png', sizes: '16x16', type: 'image/png' },
      { url: '/icon-32.png', sizes: '32x32', type: 'image/png' },
    ],
    apple: [{ url: '/apple-touch-icon.png', sizes: '180x180' }],
  },
  manifest: '/site.webmanifest',
  alternates: {
    canonical: 'https://expertspork.com',
  },
}

export const viewport: Viewport = {
  themeColor: '#2563EB',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.variable} suppressHydrationWarning>
      <body className="min-h-screen bg-white antialiased">
        {/* Skip to main content link (accessibility) */}
        <a href="#main-content" className="skip-link">
          Skip to main content
        </a>

        {/* Main content */}
        <main id="main-content">
          {children}
        </main>
      </body>
    </html>
  )
}
