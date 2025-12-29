'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { Activity, Shield, Network, AlertTriangle, TrendingUp, Server, Map } from 'lucide-react'

export default function DashboardPage() {
  const [metrics, setMetrics] = useState({
    requestRate: 0,
    errorRate: 0,
    p95Latency: 0,
    activeConnections: 0
  })

  // Simulate real-time metrics updates
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics({
        requestRate: Math.random() * 1000 + 500,
        errorRate: Math.random() * 5,
        p95Latency: Math.random() * 100 + 50,
        activeConnections: Math.floor(Math.random() * 100 + 50)
      })
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-background-primary via-background-secondary to-background-primary">
      {/* Header */}
      <header className="border-b border-border backdrop-blur-xl bg-background-secondary/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Network className="w-8 h-8 text-accent-primary" />
            <h1 className="text-2xl font-bold text-text-primary">
              Service Mesh Observatory
            </h1>
          </div>
          <div className="flex items-center space-x-4">
            <Link
              href="/topology"
              className="flex items-center space-x-2 px-4 py-2 bg-accent-primary/10 hover:bg-accent-primary/20 text-accent-primary font-medium rounded-lg transition-colors"
            >
              <Map className="w-4 h-4" />
              <span>View Topology</span>
            </Link>
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 bg-accent-success rounded-full animate-pulse"></span>
              <span className="text-sm text-text-secondary">Live</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Metrics Overview */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Request Rate"
            value={`${metrics.requestRate.toFixed(0)} req/s`}
            icon={<Activity className="w-6 h-6" />}
            trend="+12.5%"
            trendUp={true}
          />
          <MetricCard
            title="Error Rate"
            value={`${metrics.errorRate.toFixed(2)}%`}
            icon={<AlertTriangle className="w-6 h-6" />}
            trend="-3.2%"
            trendUp={false}
          />
          <MetricCard
            title="P95 Latency"
            value={`${metrics.p95Latency.toFixed(0)}ms`}
            icon={<TrendingUp className="w-6 h-6" />}
            trend="+5.1%"
            trendUp={true}
          />
          <MetricCard
            title="Active Connections"
            value={metrics.activeConnections.toString()}
            icon={<Server className="w-6 h-6" />}
            trend="+8.3%"
            trendUp={true}
          />
        </div>

        {/* Service Topology & Alerts */}
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Service Topology */}
          <div className="lg:col-span-2 p-6 glass rounded-xl">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-text-primary">Service Topology</h2>
              <Link
                href="/topology"
                className="px-4 py-2 bg-accent-primary hover:bg-accent-primary/80 text-white font-medium rounded-lg transition-colors"
              >
                Open Full View
              </Link>
            </div>
            <Link href="/topology" className="block h-96 border border-border rounded-lg bg-background-tertiary/30 hover:border-accent-primary/50 transition-colors cursor-pointer overflow-hidden relative group">
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <Network className="w-16 h-16 text-accent-primary/50 mx-auto mb-4 group-hover:text-accent-primary transition-colors" />
                  <p className="text-text-secondary group-hover:text-text-primary transition-colors">Click to view interactive topology</p>
                  <p className="text-sm text-text-muted mt-2">12 services | 16 connections | Live metrics</p>
                </div>
              </div>
              {/* Mini topology preview */}
              <div className="absolute inset-0 opacity-20 group-hover:opacity-30 transition-opacity">
                <svg className="w-full h-full" viewBox="0 0 400 300">
                  <circle cx="200" cy="30" r="8" fill="#3b82f6" />
                  <circle cx="200" cy="80" r="8" fill="#10b981" />
                  <circle cx="200" cy="130" r="8" fill="#10b981" />
                  <circle cx="100" cy="180" r="8" fill="#10b981" />
                  <circle cx="200" cy="180" r="8" fill="#10b981" />
                  <circle cx="300" cy="180" r="8" fill="#f59e0b" />
                  <circle cx="150" cy="230" r="8" fill="#ef4444" />
                  <circle cx="250" cy="230" r="8" fill="#10b981" />
                  <circle cx="100" cy="270" r="8" fill="#8b5cf6" />
                  <circle cx="200" cy="270" r="8" fill="#8b5cf6" />
                  <circle cx="300" cy="270" r="8" fill="#10b981" />
                  <line x1="200" y1="30" x2="200" y2="80" stroke="#3b82f6" strokeWidth="2" />
                  <line x1="200" y1="80" x2="200" y2="130" stroke="#3b82f6" strokeWidth="2" />
                  <line x1="200" y1="130" x2="100" y2="180" stroke="#10b981" strokeWidth="1" />
                  <line x1="200" y1="130" x2="200" y2="180" stroke="#10b981" strokeWidth="1" />
                  <line x1="200" y1="130" x2="300" y2="180" stroke="#f59e0b" strokeWidth="2" />
                  <line x1="300" y1="180" x2="150" y2="230" stroke="#ef4444" strokeWidth="2" />
                  <line x1="100" y1="180" x2="100" y2="270" stroke="#8b5cf6" strokeWidth="1" />
                  <line x1="200" y1="180" x2="200" y2="270" stroke="#8b5cf6" strokeWidth="1" />
                  <line x1="300" y1="180" x2="300" y2="270" stroke="#10b981" strokeWidth="1" />
                </svg>
              </div>
            </Link>
          </div>

          {/* Recent Alerts */}
          <div className="p-6 glass rounded-xl">
            <h2 className="text-xl font-bold text-text-primary mb-6">Recent Alerts</h2>
            <div className="space-y-4">
              {alerts.map((alert, index) => (
                <div
                  key={index}
                  className="p-4 bg-background-tertiary/50 border border-border rounded-lg hover:border-border-hover transition-colors"
                >
                  <div className="flex items-start space-x-3">
                    <div className={`w-2 h-2 mt-2 rounded-full ${getSeverityColor(alert.severity)}`}></div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-semibold text-text-primary">{alert.title}</span>
                        <span className="text-xs text-text-muted">{alert.time}</span>
                      </div>
                      <p className="text-xs text-text-secondary">{alert.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Certificate Health & Policies */}
        <div className="grid lg:grid-cols-2 gap-6 mt-6">
          <div className="p-6 glass rounded-xl">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-text-primary flex items-center space-x-2">
                <Shield className="w-6 h-6 text-accent-success" />
                <span>mTLS Certificate Health</span>
              </h2>
              <span className="text-2xl font-bold text-accent-success">92/100</span>
            </div>
            <div className="space-y-4">
              <CertificateStatus label="Expiring in 7 days" count={0} color="text-accent-danger" />
              <CertificateStatus label="Expiring in 30 days" count={2} color="text-accent-warning" />
              <CertificateStatus label="Expiring in 60 days" count={5} color="text-accent-primary" />
              <CertificateStatus label="Healthy" count={38} color="text-accent-success" />
            </div>
          </div>

          <div className="p-6 glass rounded-xl">
            <h2 className="text-xl font-bold text-text-primary mb-6">Authorization Policies</h2>
            <div className="space-y-3">
              <PolicyItem name="frontend-allow" namespace="default" status="active" />
              <PolicyItem name="backend-deny-external" namespace="default" status="active" />
              <PolicyItem name="database-strict" namespace="production" status="active" />
              <PolicyItem name="test-permissive" namespace="development" status="warning" />
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

function MetricCard({ title, value, icon, trend, trendUp }: any) {
  return (
    <div className="p-6 glass rounded-xl hover:scale-105 transition-transform">
      <div className="flex items-center justify-between mb-4">
        <div className="p-2 bg-accent-primary/10 rounded-lg">
          {icon}
        </div>
        <span className={`text-sm font-medium ${trendUp ? 'text-accent-success' : 'text-accent-danger'}`}>
          {trend}
        </span>
      </div>
      <div className="text-3xl font-bold text-text-primary mb-1">{value}</div>
      <div className="text-sm text-text-secondary">{title}</div>
    </div>
  )
}

function CertificateStatus({ label, count, color }: any) {
  return (
    <div className="flex items-center justify-between p-3 bg-background-tertiary/30 rounded-lg">
      <span className="text-sm text-text-secondary">{label}</span>
      <span className={`text-lg font-bold ${color}`}>{count}</span>
    </div>
  )
}

function PolicyItem({ name, namespace, status }: any) {
  return (
    <div className="p-3 bg-background-tertiary/30 border border-border rounded-lg hover:border-border-hover transition-colors">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm font-medium text-text-primary">{name}</div>
          <div className="text-xs text-text-muted">{namespace}</div>
        </div>
        <span className={`text-xs px-2 py-1 rounded ${
          status === 'active' ? 'bg-accent-success/20 text-accent-success' : 'bg-accent-warning/20 text-accent-warning'
        }`}>
          {status}
        </span>
      </div>
    </div>
  )
}

function getSeverityColor(severity: string) {
  switch (severity) {
    case 'critical': return 'bg-accent-danger'
    case 'high': return 'bg-accent-warning'
    case 'medium': return 'bg-accent-primary'
    default: return 'bg-accent-success'
  }
}

const alerts = [
  {
    title: 'Certificate Expiring Soon',
    description: 'backend-service cert expires in 15 days',
    time: '5m ago',
    severity: 'high'
  },
  {
    title: 'Anomaly Detected',
    description: 'Unusual traffic pattern from frontend',
    time: '12m ago',
    severity: 'medium'
  },
  {
    title: 'Policy Violation',
    description: 'Unauthorized access attempt blocked',
    time: '1h ago',
    severity: 'critical'
  }
]
