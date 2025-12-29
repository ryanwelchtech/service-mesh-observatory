'use client'

import React from 'react'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { Card } from '../ui/card'
import { clsx } from 'clsx'

interface MetricsCardProps {
  title: string
  value: string | number
  unit?: string
  icon?: React.ReactNode
  trend?: {
    value: number
    isPositive?: boolean
  }
  status?: 'normal' | 'warning' | 'critical'
  onClick?: () => void
}

export function MetricsCard({
  title,
  value,
  unit,
  icon,
  trend,
  status = 'normal',
  onClick,
}: MetricsCardProps) {
  const statusColors = {
    normal: 'text-accent-success',
    warning: 'text-accent-warning',
    critical: 'text-accent-danger',
  }

  const TrendIcon = trend
    ? trend.value > 0
      ? TrendingUp
      : trend.value < 0
      ? TrendingDown
      : Minus
    : null

  return (
    <Card
      variant="glass"
      hover={!!onClick}
      className={clsx(onClick && 'cursor-pointer')}
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-4">
        {icon && (
          <div className="p-2 bg-accent-primary/10 rounded-lg text-accent-primary">
            {icon}
          </div>
        )}
        {trend && TrendIcon && (
          <div
            className={clsx(
              'flex items-center gap-1 text-sm font-medium',
              trend.isPositive ? 'text-accent-success' : 'text-accent-danger'
            )}
          >
            <TrendIcon className="w-4 h-4" />
            <span>{Math.abs(trend.value).toFixed(1)}%</span>
          </div>
        )}
      </div>

      <div className={clsx('text-3xl font-bold mb-1', statusColors[status])}>
        {typeof value === 'number' ? value.toLocaleString() : value}
        {unit && <span className="text-lg text-text-muted ml-1">{unit}</span>}
      </div>

      <div className="text-sm text-text-secondary">{title}</div>
    </Card>
  )
}

interface MetricsGridProps {
  metrics: {
    requestRate: number
    errorRate: number
    p95Latency: number
    activeConnections: number
  }
}

export function MetricsGrid({ metrics }: MetricsGridProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <MetricsCard
        title="Request Rate"
        value={metrics.requestRate.toFixed(0)}
        unit="req/s"
        trend={{ value: 12.5, isPositive: true }}
        status="normal"
      />
      <MetricsCard
        title="Error Rate"
        value={metrics.errorRate.toFixed(2)}
        unit="%"
        trend={{ value: -3.2, isPositive: true }}
        status={metrics.errorRate > 5 ? 'critical' : metrics.errorRate > 2 ? 'warning' : 'normal'}
      />
      <MetricsCard
        title="P95 Latency"
        value={metrics.p95Latency.toFixed(0)}
        unit="ms"
        trend={{ value: 5.1, isPositive: false }}
        status={metrics.p95Latency > 500 ? 'critical' : metrics.p95Latency > 200 ? 'warning' : 'normal'}
      />
      <MetricsCard
        title="Active Connections"
        value={metrics.activeConnections}
        trend={{ value: 8.3, isPositive: true }}
        status="normal"
      />
    </div>
  )
}
