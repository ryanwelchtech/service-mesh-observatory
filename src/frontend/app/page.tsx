'use client'

import React from 'react'
import Link from 'next/link'
import { Activity, Shield, Network, TrendingUp, AlertTriangle, Lock } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background-primary via-background-secondary to-background-primary">
      {/* Animated background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-accent-primary/20 rounded-full blur-3xl animate-pulse-slow"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent-secondary/20 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '1s' }}></div>
      </div>

      {/* Navigation */}
      <nav className="relative z-10 border-b border-border backdrop-blur-xl bg-background-secondary/50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Network className="w-8 h-8 text-accent-primary" />
            <h1 className="text-2xl font-bold text-text-primary">
              Service Mesh Observatory
            </h1>
          </div>
          <div className="flex items-center space-x-4">
            <Link
              href="/dashboard"
              className="px-6 py-2 bg-accent-primary hover:bg-accent-primary/80 text-white font-medium rounded-lg transition-all duration-200"
            >
              Launch Dashboard
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 pt-20 pb-16">
        <div className="text-center mb-16">
          <h2 className="text-5xl md:text-6xl font-bold mb-6">
            <span className="bg-gradient-to-r from-accent-primary via-accent-secondary to-accent-primary bg-clip-text text-transparent">
              Real-time Observability
            </span>
            <br />
            <span className="text-text-primary">for Service Mesh Deployments</span>
          </h2>
          <p className="text-xl text-text-secondary max-w-3xl mx-auto mb-8">
            Comprehensive monitoring, security analysis, and anomaly detection for Istio and Linkerd service meshes.
            Built for production environments.
          </p>
          <div className="flex items-center justify-center space-x-4">
            <Link
              href="/dashboard"
              className="px-8 py-3 bg-accent-primary hover:bg-accent-primary/80 text-white font-semibold rounded-lg transition-all duration-200 flex items-center space-x-2"
            >
              <Activity className="w-5 h-5" />
              <span>View Live Demo</span>
            </Link>
            <a
              href="https://github.com/ryanwelchtech/service-mesh-observatory"
              target="_blank"
              rel="noopener noreferrer"
              className="px-8 py-3 border border-border hover:border-border-hover bg-background-secondary/50 backdrop-blur-xl text-text-primary font-semibold rounded-lg transition-all duration-200"
            >
              View on GitHub
            </a>
          </div>
        </div>

        {/* Key Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
          {features.map((feature, index) => (
            <div
              key={index}
              className="group p-6 border border-border hover:border-border-hover bg-background-secondary/50 backdrop-blur-xl rounded-xl transition-all duration-300 hover:scale-105 animate-slide-up"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="w-12 h-12 bg-accent-primary/10 rounded-lg flex items-center justify-center mb-4 group-hover:bg-accent-primary/20 transition-colors">
                {feature.icon}
              </div>
              <h3 className="text-xl font-semibold text-text-primary mb-2">
                {feature.title}
              </h3>
              <p className="text-text-secondary leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>

        {/* Technical Highlights */}
        <div className="p-8 border border-border bg-background-secondary/50 backdrop-blur-xl rounded-xl">
          <h3 className="text-2xl font-bold text-text-primary mb-6 text-center">
            Production-Ready Architecture
          </h3>
          <div className="grid md:grid-cols-3 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-accent-success mb-2">99.9%</div>
              <div className="text-text-secondary">Platform Uptime</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-accent-primary mb-2">&lt;100ms</div>
              <div className="text-text-secondary">Query Latency</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-accent-warning mb-2">10K+</div>
              <div className="text-text-secondary">Metrics/Second</div>
            </div>
          </div>

          <div className="mt-8 flex flex-wrap gap-3 justify-center">
            {techStack.map((tech, index) => (
              <span
                key={index}
                className="px-4 py-2 bg-background-tertiary border border-border rounded-lg text-sm font-medium text-text-primary"
              >
                {tech}
              </span>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}

const features = [
  {
    title: 'Real-time Topology',
    description: 'Interactive service mesh visualization with live traffic flows, latency heat maps, and dependency tracking.',
    icon: <Network className="w-6 h-6 text-accent-primary" />
  },
  {
    title: 'mTLS Certificate Management',
    description: 'Automated monitoring of certificate expiration with 7/30/60/90-day alerts and renewal recommendations.',
    icon: <Lock className="w-6 h-6 text-accent-success" />
  },
  {
    title: 'Policy Testing Sandbox',
    description: 'Validate Istio AuthorizationPolicy configurations before production deployment with zero risk.',
    icon: <Shield className="w-6 h-6 text-accent-warning" />
  },
  {
    title: 'Anomaly Detection',
    description: 'ML-powered detection of data exfiltration, lateral movement, and unusual traffic patterns in real-time.',
    icon: <AlertTriangle className="w-6 h-6 text-accent-danger" />
  },
  {
    title: 'Distributed Tracing',
    description: 'Jaeger integration showing end-to-end request flows with bottleneck identification and latency analysis.',
    icon: <Activity className="w-6 h-6 text-accent-primary" />
  },
  {
    title: 'Multi-Cluster Support',
    description: 'Unified dashboard for monitoring service mesh deployments across multiple Kubernetes clusters.',
    icon: <TrendingUp className="w-6 h-6 text-accent-secondary" />
  }
]

const techStack = [
  'Kubernetes',
  'Istio',
  'FastAPI',
  'Next.js',
  'Prometheus',
  'Grafana',
  'Jaeger',
  'TimescaleDB',
  'Redis',
  'WebSocket',
  'Terraform',
  'GitHub Actions'
]
