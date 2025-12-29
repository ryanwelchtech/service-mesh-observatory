'use client'

import React from 'react'
import { clsx } from 'clsx'

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info'
  size?: 'sm' | 'md'
  dot?: boolean
  pulse?: boolean
}

export function Badge({
  children,
  variant = 'default',
  size = 'md',
  dot = false,
  pulse = false,
  className,
  ...props
}: BadgeProps) {
  const variants = {
    default: 'bg-background-tertiary text-text-primary',
    success: 'bg-accent-success/20 text-accent-success',
    warning: 'bg-accent-warning/20 text-accent-warning',
    danger: 'bg-accent-danger/20 text-accent-danger',
    info: 'bg-accent-primary/20 text-accent-primary'
  }

  const dotColors = {
    default: 'bg-text-muted',
    success: 'bg-accent-success',
    warning: 'bg-accent-warning',
    danger: 'bg-accent-danger',
    info: 'bg-accent-primary'
  }

  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm'
  }

  return (
    <span
      className={clsx(
        'inline-flex items-center font-medium rounded-full',
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {dot && (
        <span
          className={clsx(
            'w-1.5 h-1.5 rounded-full mr-1.5',
            dotColors[variant],
            pulse && 'animate-pulse'
          )}
        />
      )}
      {children}
    </span>
  )
}

interface StatusBadgeProps {
  status: 'healthy' | 'warning' | 'critical' | 'unknown'
  label?: string
}

export function StatusBadge({ status, label }: StatusBadgeProps) {
  const statusConfig = {
    healthy: { variant: 'success' as const, text: 'Healthy' },
    warning: { variant: 'warning' as const, text: 'Warning' },
    critical: { variant: 'danger' as const, text: 'Critical' },
    unknown: { variant: 'default' as const, text: 'Unknown' }
  }

  const config = statusConfig[status]

  return (
    <Badge variant={config.variant} dot pulse={status === 'critical'}>
      {label || config.text}
    </Badge>
  )
}
