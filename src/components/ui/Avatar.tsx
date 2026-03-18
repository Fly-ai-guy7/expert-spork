import * as React from 'react'
import * as AvatarPrimitive from '@radix-ui/react-avatar'
import { cn, getInitials } from '@/lib/utils'

const sizeMap = {
  xs:  'h-6 w-6 text-[10px]',
  sm:  'h-8 w-8 text-xs',
  md:  'h-10 w-10 text-sm',
  lg:  'h-14 w-14 text-lg',
  xl:  'h-20 w-20 text-2xl',
  '2xl': 'h-28 w-28 text-4xl',
}

export interface AvatarProps {
  src?: string | null
  name?: string | null
  size?: keyof typeof sizeMap
  className?: string
  ring?: boolean
}

function Avatar({ src, name, size = 'md', className, ring }: AvatarProps) {
  return (
    <AvatarPrimitive.Root
      className={cn(
        'relative flex shrink-0 overflow-hidden rounded-full',
        sizeMap[size],
        ring && 'ring-2 ring-white ring-offset-0 shadow-sm',
        className
      )}
    >
      {src && (
        <AvatarPrimitive.Image
          src={src}
          alt={name ?? 'User avatar'}
          className="h-full w-full object-cover"
        />
      )}
      <AvatarPrimitive.Fallback
        className="flex h-full w-full items-center justify-center rounded-full bg-primary-100 text-primary-700 font-semibold"
        delayMs={src ? 300 : 0}
      >
        {name ? getInitials(name) : '?'}
      </AvatarPrimitive.Fallback>
    </AvatarPrimitive.Root>
  )
}

export { Avatar }
