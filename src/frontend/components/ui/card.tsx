'use client'

import React from 'react'
import { clsx } from 'clsx'

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'glass' | 'bordered'
  hover?: boolean
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

export function Card({
  children,
  variant = 'default',
  hover = false,
  padding = 'md',
  className,
  ...props
}: CardProps) {
  const baseStyles = 'rounded-xl transition-all duration-300'

  const variants = {
    default: 'bg-background-secondary border border-border',
    glass: 'bg-background-secondary/50 backdrop-blur-xl border border-border',
    bordered: 'bg-transparent border-2 border-border'
  }

  const paddings = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8'
  }

  const hoverStyles = hover ? 'hover:border-border-hover hover:scale-[1.02] cursor-pointer' : ''

  return (
    <div
      className={clsx(baseStyles, variants[variant], paddings[padding], hoverStyles, className)}
      {...props}
    >
      {children}
    </div>
  )
}

interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {}

export function CardHeader({ children, className, ...props }: CardHeaderProps) {
  return (
    <div className={clsx('mb-4', className)} {...props}>
      {children}
    </div>
  )
}

interface CardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {}

export function CardTitle({ children, className, ...props }: CardTitleProps) {
  return (
    <h3 className={clsx('text-xl font-bold text-text-primary', className)} {...props}>
      {children}
    </h3>
  )
}

interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {}

export function CardContent({ children, className, ...props }: CardContentProps) {
  return (
    <div className={clsx('text-text-secondary', className)} {...props}>
      {children}
    </div>
  )
}

interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {}

export function CardFooter({ children, className, ...props }: CardFooterProps) {
  return (
    <div className={clsx('mt-4 pt-4 border-t border-border', className)} {...props}>
      {children}
    </div>
  )
}
