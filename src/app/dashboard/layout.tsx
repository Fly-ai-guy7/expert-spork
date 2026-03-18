import React from 'react'
import Link from 'next/link'
import { redirect } from 'next/navigation'
import {
  LayoutDashboard, FolderOpen, FileText, CreditCard,
  MessageSquare, BarChart3, User, Settings, Zap,
  ChevronLeft
} from 'lucide-react'
import { cn } from '@/lib/utils'

const NAV_ITEMS = [
  { href: '/dashboard/overview',  label: 'Overview',    icon: LayoutDashboard },
  { href: '/dashboard/projects',  label: 'Projects',    icon: FolderOpen },
  { href: '/dashboard/contracts', label: 'Contracts',   icon: FileText },
  { href: '/dashboard/payments',  label: 'Payments',    icon: CreditCard },
  { href: '/dashboard/messages',  label: 'Messages',    icon: MessageSquare },
  { href: '/dashboard/analytics', label: 'Analytics',   icon: BarChart3 },
]

const BOTTOM_ITEMS = [
  { href: '/dashboard/profile',  label: 'Profile',  icon: User },
  { href: '/dashboard/settings', label: 'Settings', icon: Settings },
]

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Sidebar */}
      <aside
        className="fixed inset-y-0 left-0 z-fixed flex w-60 flex-col border-r border-slate-800 bg-slate-900"
        aria-label="Dashboard navigation"
      >
        {/* Logo */}
        <div className="flex h-16 items-center border-b border-slate-800 px-5">
          <Link href="/" className="flex items-center gap-2 font-bold text-white hover:opacity-80">
            <Zap className="h-5 w-5 fill-primary-500 text-primary-500" aria-hidden="true" />
            <span>ExpertSpork</span>
          </Link>
        </div>

        {/* Primary nav */}
        <nav className="flex-1 overflow-y-auto p-3" aria-label="Primary">
          <ul className="space-y-0.5">
            {NAV_ITEMS.map(({ href, label, icon: Icon }) => (
              <li key={href}>
                <Link
                  href={href}
                  className={cn(
                    'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-150',
                    'text-slate-400 hover:bg-slate-800 hover:text-white'
                    // Active state would be added with usePathname in a client component
                  )}
                >
                  <Icon className="h-4.5 w-4.5 shrink-0" aria-hidden="true" />
                  {label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        {/* Pro upsell */}
        <div className="m-3 rounded-xl bg-slate-800 p-4">
          <p className="mb-1 text-xs font-semibold text-white">Upgrade to Pro</p>
          <p className="mb-3 text-xs text-slate-400">Save 37% on platform fees</p>
          <Link
            href="/pricing"
            className="block w-full rounded-lg bg-primary-600 px-3 py-2 text-center text-xs font-semibold text-white transition-colors hover:bg-primary-700"
          >
            Start 14-day trial
          </Link>
        </div>

        {/* Bottom nav */}
        <div className="border-t border-slate-800 p-3">
          <ul className="space-y-0.5">
            {BOTTOM_ITEMS.map(({ href, label, icon: Icon }) => (
              <li key={href}>
                <Link
                  href={href}
                  className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-400 transition-all duration-150 hover:bg-slate-800 hover:text-white"
                >
                  <Icon className="h-4.5 w-4.5 shrink-0" aria-hidden="true" />
                  {label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex min-h-screen flex-1 flex-col pl-60">
        {/* Top bar */}
        <header className="sticky top-0 z-sticky flex h-16 items-center border-b border-slate-200 bg-white px-6 shadow-xs">
          <div className="flex flex-1 items-center gap-4">
            <h1 className="text-sm font-semibold text-slate-600">Dashboard</h1>
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/"
              className="flex items-center gap-1.5 rounded-lg px-2 py-1.5 text-xs font-medium text-slate-500 hover:bg-slate-100 hover:text-slate-700 transition-colors"
            >
              <ChevronLeft className="h-3.5 w-3.5" aria-hidden="true" />
              Back to site
            </Link>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
