'use client'

import { useContext, createContext } from 'react'
import type { User } from '@/types'

export interface AuthContextValue {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  refetch: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | null>(null)

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return ctx
}

// Role guards
export function useRequireAuth(redirectTo = '/auth/login') {
  const { user, isLoading } = useAuth()
  return { user, isLoading, isReady: !isLoading && !!user }
}

export function useIsExpert() {
  const { user } = useAuth()
  return user?.role === 'EXPERT'
}

export function useIsClient() {
  const { user } = useAuth()
  return user?.role === 'CLIENT'
}

export function useIsAdmin() {
  const { user } = useAuth()
  return user?.role === 'ADMIN'
}
