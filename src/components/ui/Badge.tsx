import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center gap-1 rounded-full border text-xs font-semibold transition-colors',
  {
    variants: {
      variant: {
        success: 'bg-green-50 text-green-700 border-green-200',
        warning: 'bg-amber-50 text-amber-800 border-amber-200',
        error:   'bg-red-50 text-red-700 border-red-200',
        info:    'bg-blue-50 text-blue-700 border-blue-200',
        neutral: 'bg-slate-100 text-slate-600 border-slate-200',
        primary: 'bg-primary-50 text-primary-700 border-primary-200',
        ai:      'bg-gradient-to-r from-orange-50 to-amber-50 text-orange-600 border-orange-200',
        dark:    'bg-slate-800 text-slate-200 border-slate-700',
      },
      size: {
        sm: 'px-1.5 py-0.5 text-[10px]',
        md: 'px-2.5 py-0.5 text-xs',
        lg: 'px-3 py-1 text-sm',
      },
    },
    defaultVariants: {
      variant: 'neutral',
      size: 'md',
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {
  dot?: boolean
}

function Badge({ className, variant, size, dot, children, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant, size }), className)} {...props}>
      {dot && (
        <span
          className={cn('h-1.5 w-1.5 rounded-full', {
            'bg-green-500':  variant === 'success',
            'bg-amber-500':  variant === 'warning',
            'bg-red-500':    variant === 'error',
            'bg-blue-500':   variant === 'info',
            'bg-slate-400':  variant === 'neutral',
            'bg-primary-500':variant === 'primary',
          })}
          aria-hidden="true"
        />
      )}
      {children}
    </span>
  )
}

export { Badge, badgeVariants }
