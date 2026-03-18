'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { Eye, EyeOff, Github, Chrome } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { cn } from '@/lib/utils'

type Role = 'CLIENT' | 'EXPERT'

export function RegisterForm() {
  const [role, setRole]           = useState<Role>('CLIENT')
  const [showPassword, setShow]   = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [password, setPassword]   = useState('')

  // Password strength (0-4)
  const strength = getPasswordStrength(password)
  const strengthLabels = ['', 'Weak', 'Fair', 'Strong', 'Excellent']
  const strengthColors = ['', 'bg-red-400', 'bg-amber-400', 'bg-blue-400', 'bg-green-500']

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setIsLoading(true)
    // TODO: connect to API
    await new Promise(r => setTimeout(r, 1500))
    setIsLoading(false)
  }

  return (
    <div>
      {/* Role toggle */}
      <div className="mb-6 flex rounded-xl border border-slate-200 bg-slate-50 p-1" role="group" aria-label="Account type">
        {(['CLIENT', 'EXPERT'] as Role[]).map(r => (
          <button
            key={r}
            type="button"
            onClick={() => setRole(r)}
            className={cn(
              'flex-1 rounded-lg py-2.5 text-sm font-medium transition-all duration-200',
              role === r
                ? 'bg-white text-primary-700 shadow-xs'
                : 'text-slate-500 hover:text-slate-700'
            )}
            aria-pressed={role === r}
          >
            {r === 'CLIENT' ? 'Hire Experts' : 'Work as Expert'}
          </button>
        ))}
      </div>

      {/* OAuth */}
      <div className="mb-5 grid grid-cols-2 gap-3">
        <Button
          type="button"
          variant="secondary"
          leftIcon={<Chrome className="h-4 w-4 text-red-500" />}
          className="justify-center"
        >
          Google
        </Button>
        <Button
          type="button"
          variant="secondary"
          leftIcon={<Github className="h-4 w-4" />}
          className="justify-center"
        >
          GitHub
        </Button>
      </div>

      {/* Divider */}
      <div className="mb-5 flex items-center gap-3">
        <div className="flex-1 border-t border-slate-200" />
        <span className="text-xs text-slate-400">or continue with email</span>
        <div className="flex-1 border-t border-slate-200" />
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        <Input
          label="Full name"
          type="text"
          name="name"
          placeholder="Sarah Chen"
          required
          autoComplete="name"
        />

        <Input
          label="Work email"
          type="email"
          name="email"
          placeholder="sarah@company.com"
          required
          autoComplete="email"
        />

        {role === 'EXPERT' && (
          <Input
            label="Professional headline"
            type="text"
            name="headline"
            placeholder="Senior React Developer & UI Architect"
            hint="This is the first thing clients see on your profile."
            required
          />
        )}

        {/* Password with strength meter */}
        <div>
          <Input
            label="Password"
            type={showPassword ? 'text' : 'password'}
            name="password"
            placeholder="Create a strong password"
            required
            autoComplete="new-password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            rightIcon={
              <button
                type="button"
                onClick={() => setShow(!showPassword)}
                className="text-slate-400 hover:text-slate-600"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword
                  ? <EyeOff className="h-4 w-4" />
                  : <Eye className="h-4 w-4" />
                }
              </button>
            }
          />
          {/* Strength indicator */}
          {password.length > 0 && (
            <div className="mt-2">
              <div className="flex gap-1 mb-1" role="presentation">
                {[1, 2, 3, 4].map(level => (
                  <div
                    key={level}
                    className={cn(
                      'h-1 flex-1 rounded-full transition-all duration-300',
                      strength >= level ? strengthColors[strength] : 'bg-slate-200'
                    )}
                    aria-hidden="true"
                  />
                ))}
              </div>
              {strength > 0 && (
                <p className={cn('text-xs font-medium', {
                  'text-red-500':   strength === 1,
                  'text-amber-500': strength === 2,
                  'text-blue-500':  strength === 3,
                  'text-green-600': strength === 4,
                })}>
                  {strengthLabels[strength]}
                </p>
              )}
            </div>
          )}
        </div>

        {/* Terms */}
        <div className="flex items-start gap-3">
          <input
            id="terms"
            type="checkbox"
            required
            className="mt-0.5 h-4 w-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
          />
          <label htmlFor="terms" className="text-xs leading-relaxed text-slate-500">
            By signing up you agree to our{' '}
            <Link href="/terms" className="text-primary-600 hover:underline">Terms of Service</Link>
            {' '}and{' '}
            <Link href="/privacy" className="text-primary-600 hover:underline">Privacy Policy</Link>.
          </label>
        </div>

        <Button
          type="submit"
          className="w-full"
          size="lg"
          isLoading={isLoading}
        >
          {isLoading ? 'Creating Account...' : 'Create Account'}
        </Button>
      </form>

      {/* Sign in link */}
      <p className="mt-6 text-center text-sm text-slate-500">
        Already have an account?{' '}
        <Link href="/auth/login" className="font-semibold text-primary-600 hover:underline">
          Sign in →
        </Link>
      </p>
    </div>
  )
}

function getPasswordStrength(password: string): number {
  if (!password) return 0
  let score = 0
  if (password.length >= 8)   score++
  if (password.length >= 12)  score++
  if (/[A-Z]/.test(password) && /[a-z]/.test(password)) score++
  if (/\d/.test(password) && /[^a-zA-Z\d]/.test(password)) score++
  return Math.min(score, 4)
}
