'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Zap, Menu, X, ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import { Avatar } from '@/components/ui/Avatar'

const NAV_LINKS = [
  { href: '/how-it-works', label: 'How It Works' },
  { href: '/explore',      label: 'Explore Experts' },
  { href: '/projects',     label: 'Projects' },
  { href: '/pricing',      label: 'Pricing' },
]

interface TopNavProps {
  user?: {
    name: string | null
    image: string | null
    role: string
  } | null
}

export function TopNav({ user }: TopNavProps) {
  const pathname = usePathname()
  const [scrolled, setScrolled]  = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 60)
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // Close mobile menu on route change
  useEffect(() => setMobileOpen(false), [pathname])

  return (
    <>
      <header
        className={cn(
          'fixed inset-x-0 top-0 z-fixed h-16 transition-all duration-300',
          scrolled
            ? 'border-b border-slate-200 bg-white/90 backdrop-blur-md shadow-xs'
            : 'bg-transparent'
        )}
      >
        <div className="container flex h-full items-center justify-between">
          {/* Logo */}
          <Link
            href="/"
            className="flex items-center gap-2 font-bold text-slate-900 hover:opacity-90 transition-opacity"
          >
            <Zap className="h-6 w-6 fill-primary-600 text-primary-600" aria-hidden="true" />
            <span className="text-lg tracking-tight">ExpertSpork</span>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden items-center gap-1 lg:flex" aria-label="Main navigation">
            {NAV_LINKS.map(link => (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  'rounded-lg px-3 py-2 text-sm font-medium transition-colors duration-200',
                  pathname === link.href
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                )}
              >
                {link.label}
              </Link>
            ))}
          </nav>

          {/* Auth area */}
          <div className="flex items-center gap-3">
            {user ? (
              <div className="flex items-center gap-3">
                <Link
                  href="/dashboard"
                  className="hidden items-center gap-2 text-sm font-medium text-slate-700 hover:text-primary-600 transition-colors lg:flex"
                >
                  <Avatar src={user.image} name={user.name} size="sm" />
                  <span>{user.name}</span>
                  <ChevronDown className="h-3.5 w-3.5" aria-hidden="true" />
                </Link>
              </div>
            ) : (
              <>
                <Link
                  href="/auth/login"
                  className="hidden text-sm font-medium text-slate-600 hover:text-primary-600 transition-colors lg:block"
                >
                  Sign In
                </Link>
                <Button asChild size="sm" className="hidden lg:inline-flex">
                  <Link href="/auth/register">Get Started Free</Link>
                </Button>
              </>
            )}

            {/* Mobile menu toggle */}
            <button
              type="button"
              className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 transition-colors lg:hidden"
              onClick={() => setMobileOpen(!mobileOpen)}
              aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
              aria-expanded={mobileOpen}
              aria-controls="mobile-menu"
            >
              {mobileOpen
                ? <X className="h-5 w-5" aria-hidden="true" />
                : <Menu className="h-5 w-5" aria-hidden="true" />
              }
            </button>
          </div>
        </div>
      </header>

      {/* Mobile menu overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-modal bg-slate-900/60 backdrop-blur-sm lg:hidden"
          onClick={() => setMobileOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Mobile menu panel */}
      <div
        id="mobile-menu"
        className={cn(
          'fixed inset-y-0 right-0 z-modal w-80 bg-white shadow-2xl transition-transform duration-300 ease-spring lg:hidden',
          mobileOpen ? 'translate-x-0' : 'translate-x-full'
        )}
        aria-hidden={!mobileOpen}
      >
        <div className="flex h-16 items-center justify-between border-b border-slate-100 px-4">
          <span className="font-semibold text-slate-900">Menu</span>
          <button
            type="button"
            className="rounded-lg p-2 text-slate-500 hover:bg-slate-100"
            onClick={() => setMobileOpen(false)}
            aria-label="Close menu"
          >
            <X className="h-5 w-5" aria-hidden="true" />
          </button>
        </div>

        <nav className="flex flex-col gap-1 p-4" aria-label="Mobile navigation">
          {NAV_LINKS.map(link => (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                'rounded-xl px-4 py-3 text-sm font-medium transition-colors',
                pathname === link.href
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-slate-700 hover:bg-slate-50'
              )}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="border-t border-slate-100 p-4 space-y-3">
          {user ? (
            <Button asChild variant="primary" className="w-full">
              <Link href="/dashboard">Go to Dashboard</Link>
            </Button>
          ) : (
            <>
              <Button asChild variant="secondary" className="w-full">
                <Link href="/auth/login">Sign In</Link>
              </Button>
              <Button asChild className="w-full">
                <Link href="/auth/register">Get Started Free</Link>
              </Button>
            </>
          )}
        </div>
      </div>
    </>
  )
}
