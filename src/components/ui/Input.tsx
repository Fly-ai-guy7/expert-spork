import * as React from 'react'
import { cn } from '@/lib/utils'

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string
  label?: string
  hint?: string
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
  wrapperClassName?: string
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, error, label, hint, leftIcon, rightIcon, wrapperClassName, id, ...props }, ref) => {
    const inputId = id ?? React.useId()

    return (
      <div className={cn('w-full', wrapperClassName)}>
        {label && (
          <label
            htmlFor={inputId}
            className="mb-1.5 block text-sm font-medium text-slate-700"
          >
            {label}
            {props.required && <span className="ml-0.5 text-red-500" aria-hidden="true">*</span>}
          </label>
        )}
        <div className="relative">
          {leftIcon && (
            <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
              {leftIcon}
            </div>
          )}
          <input
            id={inputId}
            type={type}
            className={cn(
              'flex h-10 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 transition-all duration-200',
              'focus-visible:outline-none focus-visible:border-primary-500 focus-visible:ring-3 focus-visible:ring-primary-500/30',
              'disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-400',
              leftIcon  && 'pl-10',
              rightIcon && 'pr-10',
              error     && 'border-red-400 focus-visible:border-red-400 focus-visible:ring-red-500/20',
              className
            )}
            ref={ref}
            aria-invalid={!!error}
            aria-describedby={error ? `${inputId}-error` : hint ? `${inputId}-hint` : undefined}
            {...props}
          />
          {rightIcon && (
            <div className="absolute inset-y-0 right-0 flex items-center pr-3 text-slate-400">
              {rightIcon}
            </div>
          )}
        </div>
        {hint && !error && (
          <p id={`${inputId}-hint`} className="mt-1.5 text-xs text-slate-500">
            {hint}
          </p>
        )}
        {error && (
          <p id={`${inputId}-error`} className="mt-1.5 text-xs text-red-600" role="alert">
            {error}
          </p>
        )}
      </div>
    )
  }
)
Input.displayName = 'Input'

export { Input }
