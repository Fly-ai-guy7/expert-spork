import React from 'react'
import Link from 'next/link'
import { Zap, Twitter, Linkedin, Github, Youtube } from 'lucide-react'

const FOOTER_LINKS = {
  'For Clients': [
    { label: 'How It Works',    href: '/how-it-works' },
    { label: 'Post a Project',  href: '/projects/post' },
    { label: 'Browse Experts',  href: '/explore' },
    { label: 'AI Matching',     href: '/how-it-works#ai' },
    { label: 'Pricing',         href: '/pricing' },
    { label: 'Enterprise',      href: '/enterprise' },
  ],
  'For Experts': [
    { label: 'Become an Expert',      href: '/auth/register?role=expert' },
    { label: 'How Experts Get Paid',  href: '/how-it-works#payments' },
    { label: 'Expert Success Stories',href: '/blog?category=success-stories' },
    { label: 'Expert Community',      href: '/community' },
    { label: 'Help Centre',           href: '/help' },
  ],
  'Company': [
    { label: 'About Us',        href: '/about' },
    { label: 'Blog',            href: '/blog' },
    { label: 'Careers',         href: '/careers', badge: "We're hiring" },
    { label: 'Press',           href: '/press' },
    { label: 'Partner Program', href: '/partners' },
  ],
  'Support': [
    { label: 'Help Centre',         href: '/help' },
    { label: 'Contact Us',          href: '/contact' },
    { label: 'Trust & Safety',      href: '/trust' },
    { label: 'Dispute Resolution',  href: '/disputes' },
    { label: 'API Docs',            href: '/docs/api' },
  ],
}

const SOCIAL_LINKS = [
  { icon: Twitter,  href: 'https://twitter.com/expertspork',  label: 'Twitter' },
  { icon: Linkedin, href: 'https://linkedin.com/company/expertspork', label: 'LinkedIn' },
  { icon: Github,   href: 'https://github.com/expertspork',  label: 'GitHub' },
  { icon: Youtube,  href: 'https://youtube.com/@expertspork',label: 'YouTube' },
]

export function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-slate-50" role="contentinfo">
      <div className="container py-16">
        <div className="grid gap-10 lg:grid-cols-5">
          {/* Brand column */}
          <div className="lg:col-span-1">
            <Link
              href="/"
              className="mb-4 flex items-center gap-2 font-bold text-slate-900 hover:opacity-80 transition-opacity"
            >
              <Zap className="h-5 w-5 fill-primary-600 text-primary-600" aria-hidden="true" />
              <span>ExpertSpork</span>
            </Link>
            <p className="mb-6 text-sm leading-relaxed text-slate-500">
              The AI-powered talent marketplace for builders and makers.
            </p>
            {/* Social icons */}
            <div className="flex gap-3">
              {SOCIAL_LINKS.map(({ icon: Icon, href, label }) => (
                <a
                  key={label}
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-500 transition-all duration-200 hover:border-primary-300 hover:text-primary-600 hover:shadow-xs"
                  aria-label={label}
                >
                  <Icon className="h-4 w-4" aria-hidden="true" />
                </a>
              ))}
            </div>
          </div>

          {/* Link columns */}
          {Object.entries(FOOTER_LINKS).map(([heading, links]) => (
            <div key={heading}>
              <h3 className="mb-4 text-xs font-semibold uppercase tracking-wider text-slate-900">
                {heading}
              </h3>
              <ul className="space-y-3">
                {links.map(link => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      className="flex items-center gap-2 text-sm text-slate-500 transition-colors duration-200 hover:text-primary-600"
                    >
                      {link.label}
                      {'badge' in link && link.badge && (
                        <span className="rounded-full bg-green-100 px-1.5 py-0.5 text-[10px] font-semibold text-green-700">
                          {link.badge}
                        </span>
                      )}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-slate-200 pt-8 sm:flex-row">
          <p className="text-xs text-slate-400">
            © {new Date().getFullYear()} ExpertSpork Ltd. All rights reserved.
          </p>
          <div className="flex flex-wrap items-center gap-4">
            {['Privacy Policy', 'Terms of Service', 'Cookie Policy', 'GDPR'].map(item => (
              <Link
                key={item}
                href={`/${item.toLowerCase().replace(/\s+/g, '-')}`}
                className="text-xs text-slate-400 transition-colors hover:text-primary-600"
              >
                {item}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </footer>
  )
}
