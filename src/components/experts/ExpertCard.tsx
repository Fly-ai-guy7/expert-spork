'use client'

import React from 'react'
import Link from 'next/link'
import { MapPin, Star, Clock, Zap } from 'lucide-react'
import { cn, formatCurrency, getCategoryGradient } from '@/lib/utils'
import { Avatar } from '@/components/ui/Avatar'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import type { ExpertProfile } from '@/types'

interface ExpertCardProps {
  expert: ExpertProfile
  aiMatchScore?: number
  className?: string
}

export function ExpertCard({ expert, aiMatchScore, className }: ExpertCardProps) {
  const primarySkills = expert.skills
    .filter(s => s.isPrimary)
    .slice(0, 3)
    .map(s => s.skill)

  const extraSkillCount = expert.skills.length - primarySkills.length
  const topCategory = expert.skills[0]?.skill?.category ?? 'default'
  const gradientClass = getCategoryGradient(topCategory)

  const availabilityConfig = {
    FULL_TIME:   { label: 'Available',      variant: 'success' as const, dot: true },
    PART_TIME:   { label: 'Part-time',      variant: 'warning' as const, dot: true },
    UNAVAILABLE: { label: 'Unavailable',    variant: 'neutral' as const, dot: false },
  }
  const avail = availabilityConfig[expert.availability]

  return (
    <article
      className={cn(
        'group relative flex flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white',
        'transition-all duration-200 hover:-translate-y-0.5 hover:border-primary-300 hover:shadow-lg',
        className
      )}
    >
      {/* Cover gradient strip */}
      <div className={cn('h-20 bg-gradient-to-br', gradientClass)} aria-hidden="true" />

      {/* AI Match badge (absolute) */}
      {aiMatchScore && aiMatchScore >= 80 && (
        <div className="absolute right-3 top-3">
          <Badge variant="ai" size="md">
            <Zap className="h-3 w-3" aria-hidden="true" />
            {aiMatchScore}% match
          </Badge>
        </div>
      )}

      {/* Availability badge (absolute) */}
      <div className="absolute left-3 top-3">
        <Badge variant={avail.variant} dot={avail.dot} size="sm">
          {avail.label}
        </Badge>
      </div>

      {/* Content */}
      <div className="flex flex-1 flex-col p-4">
        {/* Avatar (overlapping cover) */}
        <div className="-mt-10 mb-3">
          <Avatar
            src={expert.user.image}
            name={expert.displayName}
            size="lg"
            ring
            className="shadow-md"
          />
        </div>

        {/* Name + verified */}
        <div className="mb-1 flex items-center gap-1.5">
          <Link
            href={`/explore/${expert.slug}`}
            className="font-semibold text-slate-900 hover:text-primary-600 transition-colors line-clamp-1"
          >
            {expert.displayName}
          </Link>
          {expert.isVerified && (
            <svg
              className="h-4 w-4 shrink-0 text-primary-500"
              viewBox="0 0 20 20"
              fill="currentColor"
              aria-label="Verified expert"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z"
                clipRule="evenodd"
              />
            </svg>
          )}
        </div>

        {/* Headline */}
        <p className="mb-3 text-sm text-slate-500 line-clamp-2 leading-snug">
          {expert.headline}
        </p>

        {/* Skills */}
        <div className="mb-3 flex flex-wrap gap-1.5" aria-label="Skills">
          {primarySkills.map(skill => (
            <span
              key={skill.id}
              className="rounded-full bg-primary-50 px-2.5 py-0.5 text-[11px] font-medium text-primary-700"
            >
              {skill.name}
            </span>
          ))}
          {extraSkillCount > 0 && (
            <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-[11px] font-medium text-slate-500">
              +{extraSkillCount} more
            </span>
          )}
        </div>

        {/* Meta row */}
        <div className="mb-4 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-500">
          {expert.averageRating !== undefined && (
            <span className="flex items-center gap-0.5 font-medium text-amber-600">
              <Star className="h-3.5 w-3.5 fill-current" aria-hidden="true" />
              {expert.averageRating.toFixed(1)}
              {expert._count?.reviews ? (
                <span className="font-normal text-slate-400">({expert._count.reviews})</span>
              ) : null}
            </span>
          )}
          {expert.location && (
            <span className="flex items-center gap-1">
              <MapPin className="h-3 w-3" aria-hidden="true" />
              {expert.location}
            </span>
          )}
          {expert.responseTime > 0 && (
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" aria-hidden="true" />
              ~{expert.responseTime < 60
                ? `${expert.responseTime}m`
                : `${Math.round(expert.responseTime / 60)}h`}
            </span>
          )}
        </div>

        {/* Footer */}
        <div className="mt-auto flex items-center justify-between border-t border-slate-100 pt-4">
          <p className="font-bold text-slate-900">
            {formatCurrency(expert.hourlyRate)}
            <span className="text-xs font-normal text-slate-400">/hr</span>
          </p>

          <Button
            asChild
            variant="primary"
            size="sm"
            className="opacity-0 transition-opacity duration-200 group-hover:opacity-100"
          >
            <Link href={`/explore/${expert.slug}`}>
              Hire Now
            </Link>
          </Button>
        </div>
      </div>
    </article>
  )
}
