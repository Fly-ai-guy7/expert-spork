'use client'

import * as React from 'react'
import { Slot } from '@radix-ui/react-slot'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'
import { Loader2 } from 'lucide-react'

const buttonVariants = cva(
  // Base styles
  'inline-flex items-center justify-center gap-2 whitespace-nowrap font-semibold transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 active:translate-y-px select-none',
  {
    variants: {
      variant: {
        primary:
          'bg-primary-600 text-white border border-primary-600 hover:bg-primary-700 hover:border-primary-700 hover:shadow-md',
        secondary:
          'bg-slate-50 text-slate-800 border border-slate-200 hover:bg-slate-100 hover:border-slate-300',
        ghost:
          'bg-transparent text-primary-600 border border-transparent hover:bg-primary-50 hover:text-primary-700',
        danger:
          'bg-red-50 text-red-700 border border-red-200 hover:bg-red-100',
        outline:
          'bg-transparent text-primary-600 border border-primary-300 hover:bg-primary-50 hover:border-primary-400',
        'outline-white':
          'bg-transparent text-white border border-white/40 hover:bg-white/10 hover:border-white/60',
        link:
          'bg-transparent text-primary-600 underline-offset-4 hover:underline p-0 h-auto',
      },
      size: {
        xs:  'h-7  px-2.5 text-xs rounded-md',
        sm:  'h-8  px-3   text-sm rounded-md',
        md:  'h-10 px-4   text-sm rounded-lg',
        lg:  'h-11 px-5   text-base rounded-lg',
        xl:  'h-14 px-8   text-lg rounded-xl',
        icon:'h-10 w-10   rounded-lg',
        'icon-sm': 'h-8 w-8 rounded-md',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
  isLoading?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant,
      size,
      asChild = false,
      isLoading = false,
      leftIcon,
      rightIcon,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    const Comp = asChild ? Slot : 'button'

    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        disabled={disabled || isLoading}
        aria-disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
        ) : leftIcon ? (
          <span className="shrink-0" aria-hidden="true">{leftIcon}</span>
        ) : null}
        {children}
        {!isLoading && rightIcon && (
          <span className="shrink-0" aria-hidden="true">{rightIcon}</span>
        )}
      </Comp>
    )
  }
)
Button.displayName = 'Button'

export { Button, buttonVariants }
