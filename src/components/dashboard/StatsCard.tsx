import React from 'react'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { cn } from '@/lib/utils'

interface StatsCardProps {
  label: string
  value: string
  delta?: number
  deltaLabel?: string
  icon?: React.ReactNode
  iconBg?: string
  className?: string
}

export function StatsCard({
  label,
  value,
  delta,
  deltaLabel = 'this month',
  icon,
  iconBg = 'bg-primary-100',
  className,
}: StatsCardProps) {
  const isPositive = delta !== undefined && delta > 0
  const isNegative = delta !== undefined && delta < 0
  const isNeutral  = delta !== undefined && delta === 0

  return (
    <div
      className={cn(
        'rounded-xl border border-slate-200 bg-white p-5 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md',
        className
      )}
    >
      <div className="mb-4 flex items-start justify-between">
        {icon && (
          <div className={cn('flex h-10 w-10 items-center justify-center rounded-lg', iconBg)}>
            {icon}
          </div>
        )}
      </div>

      <div className="mb-1 text-sm font-medium uppercase tracking-wide text-slate-500">
        {label}
      </div>

      <div className="mb-2 text-2xl font-extrabold tabular-nums text-slate-900">
        {value}
      </div>

      {delta !== undefined && (
        <div
          className={cn(
            'inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold',
            isPositive && 'bg-green-50 text-green-700',
            isNegative && 'bg-red-50 text-red-700',
            isNeutral  && 'bg-slate-100 text-slate-600'
          )}
        >
          {isPositive && <TrendingUp className="h-3 w-3" aria-hidden="true" />}
          {isNegative && <TrendingDown className="h-3 w-3" aria-hidden="true" />}
          {isNeutral  && <Minus className="h-3 w-3" aria-hidden="true" />}
          <span>
            {isPositive ? '+' : ''}{delta.toFixed(1)}% {deltaLabel}
          </span>
        </div>
      )}
    </div>
  )
}
