import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/** Merge Tailwind classes safely */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/** Format currency */
export function formatCurrency(
  amount: number,
  currency = 'USD',
  options?: Intl.NumberFormatOptions
): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
    ...options,
  }).format(amount)
}

/** Format large numbers (1200 → 1.2K, 1200000 → 1.2M) */
export function formatCompact(n: number): string {
  return new Intl.NumberFormat('en-US', {
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(n)
}

/** Format date */
export function formatDate(
  date: Date | string,
  format: 'short' | 'long' | 'relative' = 'short'
): string {
  const d = typeof date === 'string' ? new Date(date) : date
  if (format === 'relative') return formatRelativeDate(d)
  if (format === 'long') {
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
  }
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function formatRelativeDate(date: Date): string {
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffSec = Math.floor(diffMs / 1000)
  const diffMin = Math.floor(diffSec / 60)
  const diffHr  = Math.floor(diffMin / 60)
  const diffDay = Math.floor(diffHr / 24)

  if (diffSec < 60)   return 'just now'
  if (diffMin < 60)   return `${diffMin}m ago`
  if (diffHr < 24)    return `${diffHr}h ago`
  if (diffDay < 7)    return `${diffDay}d ago`
  if (diffDay < 30)   return `${Math.floor(diffDay / 7)}w ago`
  if (diffDay < 365)  return `${Math.floor(diffDay / 30)}mo ago`
  return `${Math.floor(diffDay / 365)}y ago`
}

/** Calculate platform fee */
export function calculateFee(amount: number, isPro = false): {
  subtotal: number
  feeRate: number
  fee: number
  expertReceives: number
  clientPays: number
} {
  const feeRate = isPro ? 0.05 : 0.08
  const fee = amount * feeRate
  return {
    subtotal: amount,
    feeRate,
    fee,
    expertReceives: amount - fee,
    clientPays: amount,
  }
}

/** Generate expert slug from name */
export function generateSlug(name: string, suffix?: string): string {
  const base = name
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim()
  return suffix ? `${base}-${suffix}` : base
}

/** Get initials from name */
export function getInitials(name: string): string {
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

/** Generate category gradient color */
export function getCategoryGradient(category: string): string {
  const gradients: Record<string, string> = {
    Engineering:   'from-blue-500 to-indigo-600',
    Design:        'from-purple-500 to-pink-500',
    Strategy:      'from-emerald-500 to-teal-600',
    Marketing:     'from-orange-500 to-red-500',
    Data:          'from-cyan-500 to-blue-600',
    Content:       'from-amber-500 to-orange-500',
    default:       'from-slate-500 to-slate-700',
  }
  return gradients[category] ?? gradients.default
}

/** Truncate text */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength - 3) + '...'
}

/** Clamp number between min and max */
export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max)
}

/** Generate stars display */
export function formatRating(rating: number): string {
  return rating.toFixed(1)
}

/** Check if value is a valid email */
export function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

/** Debounce utility */
export function debounce<T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timer: NodeJS.Timeout
  return (...args: Parameters<T>) => {
    clearTimeout(timer)
    timer = setTimeout(() => fn(...args), delay)
  }
}

/** Parse query string filters */
export function parseFilters(searchParams: URLSearchParams) {
  return {
    query:        searchParams.get('q') ?? '',
    category:     searchParams.getAll('category'),
    skills:       searchParams.getAll('skills'),
    rateMin:      Number(searchParams.get('rate_min') ?? 0),
    rateMax:      Number(searchParams.get('rate_max') ?? 500),
    availability: searchParams.getAll('availability'),
    rating:       Number(searchParams.get('rating') ?? 0),
    sort:         searchParams.get('sort') ?? 'relevance',
    page:         Number(searchParams.get('page') ?? 1),
    pageSize:     Number(searchParams.get('pageSize') ?? 12),
  }
}
