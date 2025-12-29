'use client'

import React, { useState, useEffect } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card'

interface DataPoint {
  time: string
  value: number
}

interface MetricsChartProps {
  title: string
  data: DataPoint[]
  color?: string
  unit?: string
  height?: number
}

export function MetricsChart({
  title,
  data,
  color = '#3b82f6',
  unit = '',
  height = 300,
}: MetricsChartProps) {
  return (
    <Card variant="glass">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={height}>
          <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis
              dataKey="time"
              stroke="#9ca3af"
              fontSize={12}
              tickLine={false}
            />
            <YAxis
              stroke="#9ca3af"
              fontSize={12}
              tickLine={false}
              tickFormatter={(value) => `${value}${unit}`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1f2937',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '8px',
                color: '#f9fafb',
              }}
              labelStyle={{ color: '#9ca3af' }}
              formatter={(value: number) => [`${value.toFixed(2)}${unit}`, title]}
            />
            <Line
              type="monotone"
              dataKey="value"
              stroke={color}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: color }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

interface MultiLineChartProps {
  title: string
  data: Array<Record<string, number | string>>
  lines: Array<{ key: string; color: string; name: string }>
  height?: number
}

export function MultiLineChart({ title, data, lines, height = 300 }: MultiLineChartProps) {
  return (
    <Card variant="glass">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={height}>
          <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis
              dataKey="time"
              stroke="#9ca3af"
              fontSize={12}
              tickLine={false}
            />
            <YAxis stroke="#9ca3af" fontSize={12} tickLine={false} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1f2937',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '8px',
                color: '#f9fafb',
              }}
              labelStyle={{ color: '#9ca3af' }}
            />
            <Legend
              wrapperStyle={{ color: '#9ca3af' }}
              iconType="line"
            />
            {lines.map((line) => (
              <Line
                key={line.key}
                type="monotone"
                dataKey={line.key}
                stroke={line.color}
                strokeWidth={2}
                dot={false}
                name={line.name}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

// Real-time metrics chart with auto-updating data
export function RealTimeMetricsChart() {
  const [data, setData] = useState<Array<{ time: string; p50: number; p95: number; p99: number }>>([])

  useEffect(() => {
    // Generate initial data
    const initialData = Array.from({ length: 20 }, (_, i) => ({
      time: new Date(Date.now() - (19 - i) * 3000).toLocaleTimeString(),
      p50: Math.random() * 50 + 30,
      p95: Math.random() * 100 + 80,
      p99: Math.random() * 150 + 120,
    }))
    setData(initialData)

    // Simulate real-time updates
    const interval = setInterval(() => {
      setData((prev) => {
        const newPoint = {
          time: new Date().toLocaleTimeString(),
          p50: Math.random() * 50 + 30,
          p95: Math.random() * 100 + 80,
          p99: Math.random() * 150 + 120,
        }
        return [...prev.slice(1), newPoint]
      })
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  return (
    <MultiLineChart
      title="Latency Percentiles (ms)"
      data={data}
      lines={[
        { key: 'p50', color: '#10b981', name: 'P50' },
        { key: 'p95', color: '#f59e0b', name: 'P95' },
        { key: 'p99', color: '#ef4444', name: 'P99' },
      ]}
    />
  )
}
