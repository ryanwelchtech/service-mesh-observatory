'use client'

import React, { useState, useCallback, useEffect } from 'react'
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
  Position,
} from 'react-flow-renderer'
import { Network, ArrowLeft, Activity, Shield, AlertTriangle, Zap, Database, Globe, Server, Lock } from 'lucide-react'
import Link from 'next/link'

// Custom node component for services
const ServiceNode = ({ data }: { data: any }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-accent-success'
      case 'warning': return 'bg-accent-warning'
      case 'critical': return 'bg-accent-danger'
      default: return 'bg-accent-primary'
    }
  }

  const getIcon = (type: string) => {
    switch (type) {
      case 'gateway': return <Globe className="w-5 h-5" />
      case 'frontend': return <Activity className="w-5 h-5" />
      case 'backend': return <Server className="w-5 h-5" />
      case 'database': return <Database className="w-5 h-5" />
      case 'cache': return <Zap className="w-5 h-5" />
      case 'auth': return <Lock className="w-5 h-5" />
      default: return <Server className="w-5 h-5" />
    }
  }

  return (
    <div className={`px-4 py-3 rounded-xl border-2 ${
      data.selected ? 'border-accent-primary shadow-lg shadow-accent-primary/20' : 'border-border'
    } bg-background-secondary/90 backdrop-blur-sm min-w-[140px] transition-all hover:border-accent-primary/50`}>
      <div className="flex items-center space-x-3">
        <div className={`p-2 rounded-lg ${data.status === 'healthy' ? 'bg-accent-success/10 text-accent-success' : data.status === 'warning' ? 'bg-accent-warning/10 text-accent-warning' : 'bg-accent-danger/10 text-accent-danger'}`}>
          {getIcon(data.type)}
        </div>
        <div className="flex-1">
          <div className="text-sm font-semibold text-text-primary">{data.label}</div>
          <div className="text-xs text-text-muted">{data.namespace}</div>
        </div>
        <div className={`w-2 h-2 rounded-full ${getStatusColor(data.status)} animate-pulse`}></div>
      </div>
      {data.metrics && (
        <div className="mt-3 pt-3 border-t border-border grid grid-cols-2 gap-2 text-xs">
          <div>
            <span className="text-text-muted">RPS:</span>
            <span className="text-text-primary ml-1">{data.metrics.rps}</span>
          </div>
          <div>
            <span className="text-text-muted">Latency:</span>
            <span className="text-text-primary ml-1">{data.metrics.latency}ms</span>
          </div>
          <div>
            <span className="text-text-muted">Errors:</span>
            <span className={`ml-1 ${data.metrics.errorRate > 1 ? 'text-accent-danger' : 'text-accent-success'}`}>{data.metrics.errorRate}%</span>
          </div>
          <div>
            <span className="text-text-muted">mTLS:</span>
            <span className={`ml-1 ${data.metrics.mtls ? 'text-accent-success' : 'text-accent-danger'}`}>{data.metrics.mtls ? 'On' : 'Off'}</span>
          </div>
        </div>
      )}
    </div>
  )
}

const nodeTypes = {
  service: ServiceNode,
}

// Initial nodes representing a microservices architecture
const initialNodes: Node[] = [
  {
    id: 'ingress',
    type: 'service',
    position: { x: 400, y: 0 },
    data: {
      label: 'Istio Ingress',
      type: 'gateway',
      namespace: 'istio-system',
      status: 'healthy',
      metrics: { rps: 1250, latency: 12, errorRate: 0.1, mtls: true }
    },
  },
  {
    id: 'frontend',
    type: 'service',
    position: { x: 400, y: 120 },
    data: {
      label: 'Frontend',
      type: 'frontend',
      namespace: 'production',
      status: 'healthy',
      metrics: { rps: 1180, latency: 45, errorRate: 0.2, mtls: true }
    },
  },
  {
    id: 'api-gateway',
    type: 'service',
    position: { x: 400, y: 240 },
    data: {
      label: 'API Gateway',
      type: 'backend',
      namespace: 'production',
      status: 'healthy',
      metrics: { rps: 2340, latency: 28, errorRate: 0.3, mtls: true }
    },
  },
  {
    id: 'auth-service',
    type: 'service',
    position: { x: 100, y: 360 },
    data: {
      label: 'Auth Service',
      type: 'auth',
      namespace: 'production',
      status: 'healthy',
      metrics: { rps: 890, latency: 35, errorRate: 0.1, mtls: true }
    },
  },
  {
    id: 'user-service',
    type: 'service',
    position: { x: 300, y: 360 },
    data: {
      label: 'User Service',
      type: 'backend',
      namespace: 'production',
      status: 'healthy',
      metrics: { rps: 720, latency: 52, errorRate: 0.4, mtls: true }
    },
  },
  {
    id: 'order-service',
    type: 'service',
    position: { x: 500, y: 360 },
    data: {
      label: 'Order Service',
      type: 'backend',
      namespace: 'production',
      status: 'warning',
      metrics: { rps: 450, latency: 125, errorRate: 2.1, mtls: true }
    },
  },
  {
    id: 'payment-service',
    type: 'service',
    position: { x: 700, y: 360 },
    data: {
      label: 'Payment Service',
      type: 'backend',
      namespace: 'production',
      status: 'healthy',
      metrics: { rps: 380, latency: 85, errorRate: 0.2, mtls: true }
    },
  },
  {
    id: 'notification-service',
    type: 'service',
    position: { x: 200, y: 500 },
    data: {
      label: 'Notification',
      type: 'backend',
      namespace: 'production',
      status: 'healthy',
      metrics: { rps: 290, latency: 42, errorRate: 0.1, mtls: true }
    },
  },
  {
    id: 'inventory-service',
    type: 'service',
    position: { x: 500, y: 500 },
    data: {
      label: 'Inventory',
      type: 'backend',
      namespace: 'production',
      status: 'critical',
      metrics: { rps: 180, latency: 450, errorRate: 8.5, mtls: true }
    },
  },
  {
    id: 'postgres-users',
    type: 'service',
    position: { x: 100, y: 620 },
    data: {
      label: 'PostgreSQL',
      type: 'database',
      namespace: 'database',
      status: 'healthy',
      metrics: { rps: 1200, latency: 8, errorRate: 0.0, mtls: true }
    },
  },
  {
    id: 'postgres-orders',
    type: 'service',
    position: { x: 400, y: 620 },
    data: {
      label: 'TimescaleDB',
      type: 'database',
      namespace: 'database',
      status: 'healthy',
      metrics: { rps: 850, latency: 12, errorRate: 0.1, mtls: true }
    },
  },
  {
    id: 'redis-cache',
    type: 'service',
    position: { x: 700, y: 620 },
    data: {
      label: 'Redis Cache',
      type: 'cache',
      namespace: 'cache',
      status: 'healthy',
      metrics: { rps: 5400, latency: 2, errorRate: 0.0, mtls: true }
    },
  },
]

// Edges representing traffic flow between services
const initialEdges: Edge[] = [
  { id: 'e1', source: 'ingress', target: 'frontend', animated: true, style: { stroke: '#3b82f6', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#3b82f6' } },
  { id: 'e2', source: 'frontend', target: 'api-gateway', animated: true, style: { stroke: '#3b82f6', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#3b82f6' } },
  { id: 'e3', source: 'api-gateway', target: 'auth-service', animated: true, style: { stroke: '#10b981', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#10b981' } },
  { id: 'e4', source: 'api-gateway', target: 'user-service', animated: true, style: { stroke: '#10b981', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#10b981' } },
  { id: 'e5', source: 'api-gateway', target: 'order-service', animated: true, style: { stroke: '#f59e0b', strokeWidth: 3 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#f59e0b' } },
  { id: 'e6', source: 'api-gateway', target: 'payment-service', animated: true, style: { stroke: '#10b981', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#10b981' } },
  { id: 'e7', source: 'order-service', target: 'inventory-service', animated: true, style: { stroke: '#ef4444', strokeWidth: 3 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#ef4444' } },
  { id: 'e8', source: 'order-service', target: 'payment-service', animated: true, style: { stroke: '#10b981', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#10b981' } },
  { id: 'e9', source: 'user-service', target: 'notification-service', animated: true, style: { stroke: '#10b981', strokeWidth: 1 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#10b981' } },
  { id: 'e10', source: 'order-service', target: 'notification-service', animated: true, style: { stroke: '#10b981', strokeWidth: 1 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#10b981' } },
  { id: 'e11', source: 'auth-service', target: 'postgres-users', animated: true, style: { stroke: '#8b5cf6', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#8b5cf6' } },
  { id: 'e12', source: 'user-service', target: 'postgres-users', animated: true, style: { stroke: '#8b5cf6', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#8b5cf6' } },
  { id: 'e13', source: 'order-service', target: 'postgres-orders', animated: true, style: { stroke: '#8b5cf6', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#8b5cf6' } },
  { id: 'e14', source: 'inventory-service', target: 'postgres-orders', animated: true, style: { stroke: '#8b5cf6', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#8b5cf6' } },
  { id: 'e15', source: 'api-gateway', target: 'redis-cache', animated: true, style: { stroke: '#10b981', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#10b981' } },
  { id: 'e16', source: 'user-service', target: 'redis-cache', animated: true, style: { stroke: '#10b981', strokeWidth: 1 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#10b981' } },
]

export default function TopologyPage() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)

  // Simulate live metrics updates
  useEffect(() => {
    const interval = setInterval(() => {
      setNodes((nds) =>
        nds.map((node) => ({
          ...node,
          data: {
            ...node.data,
            metrics: {
              ...node.data.metrics,
              rps: Math.max(0, node.data.metrics.rps + (Math.random() - 0.5) * 50),
              latency: Math.max(1, node.data.metrics.latency + (Math.random() - 0.5) * 10),
            },
          },
        }))
      )
    }, 2000)

    return () => clearInterval(interval)
  }, [setNodes])

  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node)
  }, [])

  const totalRequests = nodes.reduce((sum, n) => sum + (n.data.metrics?.rps || 0), 0)
  const healthyServices = nodes.filter(n => n.data.status === 'healthy').length
  const warningServices = nodes.filter(n => n.data.status === 'warning').length
  const criticalServices = nodes.filter(n => n.data.status === 'critical').length

  return (
    <div className="min-h-screen bg-gradient-to-br from-background-primary via-background-secondary to-background-primary">
      {/* Header */}
      <header className="border-b border-border backdrop-blur-xl bg-background-secondary/50 sticky top-0 z-50">
        <div className="max-w-full mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/dashboard" className="p-2 hover:bg-background-tertiary rounded-lg transition-colors">
              <ArrowLeft className="w-5 h-5 text-text-secondary" />
            </Link>
            <div className="flex items-center space-x-3">
              <Network className="w-8 h-8 text-accent-primary" />
              <div>
                <h1 className="text-xl font-bold text-text-primary">Service Mesh Topology</h1>
                <p className="text-xs text-text-muted">Real-time service mesh visualization</p>
              </div>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-accent-primary" />
              <span className="text-sm text-text-secondary">Total RPS:</span>
              <span className="text-sm font-bold text-text-primary">{Math.round(totalRequests).toLocaleString()}</span>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-1">
                <span className="w-2 h-2 bg-accent-success rounded-full"></span>
                <span className="text-sm text-text-secondary">{healthyServices} Healthy</span>
              </div>
              <div className="flex items-center space-x-1">
                <span className="w-2 h-2 bg-accent-warning rounded-full"></span>
                <span className="text-sm text-text-secondary">{warningServices} Warning</span>
              </div>
              <div className="flex items-center space-x-1">
                <span className="w-2 h-2 bg-accent-danger rounded-full"></span>
                <span className="text-sm text-text-secondary">{criticalServices} Critical</span>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 bg-accent-success rounded-full animate-pulse"></span>
              <span className="text-sm text-text-secondary">Live</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-73px)]">
        {/* Topology Graph */}
        <div className="flex-1">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            nodeTypes={nodeTypes}
            fitView
            attributionPosition="bottom-left"
            style={{ background: '#0a0e1a' }}
          >
            <Background color="#1f2937" gap={20} />
            <Controls
              style={{
                background: '#111827',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '8px'
              }}
            />
            <MiniMap
              nodeColor={(node) => {
                switch (node.data.status) {
                  case 'healthy': return '#10b981'
                  case 'warning': return '#f59e0b'
                  case 'critical': return '#ef4444'
                  default: return '#3b82f6'
                }
              }}
              style={{
                background: '#111827',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '8px'
              }}
            />
          </ReactFlow>
        </div>

        {/* Side Panel - Service Details */}
        <div className="w-80 border-l border-border bg-background-secondary/50 backdrop-blur-xl p-6 overflow-y-auto">
          <h2 className="text-lg font-bold text-text-primary mb-4">Service Details</h2>

          {selectedNode ? (
            <div className="space-y-4">
              <div className="p-4 bg-background-tertiary/50 rounded-xl border border-border">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-lg font-semibold text-text-primary">{selectedNode.data.label}</span>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    selectedNode.data.status === 'healthy' ? 'bg-accent-success/20 text-accent-success' :
                    selectedNode.data.status === 'warning' ? 'bg-accent-warning/20 text-accent-warning' :
                    'bg-accent-danger/20 text-accent-danger'
                  }`}>
                    {selectedNode.data.status}
                  </span>
                </div>
                <div className="text-sm text-text-muted mb-4">Namespace: {selectedNode.data.namespace}</div>

                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-text-secondary">Request Rate</span>
                    <span className="text-sm font-medium text-text-primary">{Math.round(selectedNode.data.metrics?.rps || 0)} req/s</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-text-secondary">P95 Latency</span>
                    <span className="text-sm font-medium text-text-primary">{Math.round(selectedNode.data.metrics?.latency || 0)}ms</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-text-secondary">Error Rate</span>
                    <span className={`text-sm font-medium ${(selectedNode.data.metrics?.errorRate || 0) > 1 ? 'text-accent-danger' : 'text-accent-success'}`}>
                      {selectedNode.data.metrics?.errorRate?.toFixed(1) || 0}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-text-secondary">mTLS Enabled</span>
                    <span className={`text-sm font-medium ${selectedNode.data.metrics?.mtls ? 'text-accent-success' : 'text-accent-danger'}`}>
                      {selectedNode.data.metrics?.mtls ? 'Yes' : 'No'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="p-4 bg-background-tertiary/50 rounded-xl border border-border">
                <h3 className="text-sm font-semibold text-text-primary mb-3">Security Status</h3>
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <Shield className="w-4 h-4 text-accent-success" />
                    <span className="text-sm text-text-secondary">AuthorizationPolicy: Active</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Lock className="w-4 h-4 text-accent-success" />
                    <span className="text-sm text-text-secondary">PeerAuthentication: STRICT</span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <Network className="w-12 h-12 text-text-muted mx-auto mb-3" />
              <p className="text-sm text-text-secondary">Click on a service node to view details</p>
            </div>
          )}

          {/* Legend */}
          <div className="mt-6 p-4 bg-background-tertiary/50 rounded-xl border border-border">
            <h3 className="text-sm font-semibold text-text-primary mb-3">Legend</h3>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-1 bg-accent-success rounded"></div>
                <span className="text-xs text-text-secondary">Healthy Connection</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-8 h-1 bg-accent-warning rounded"></div>
                <span className="text-xs text-text-secondary">High Latency</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-8 h-1 bg-accent-danger rounded"></div>
                <span className="text-xs text-text-secondary">High Error Rate</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-8 h-1 bg-accent-primary rounded"></div>
                <span className="text-xs text-text-secondary">Primary Traffic Flow</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-8 h-1 bg-[#8b5cf6] rounded"></div>
                <span className="text-xs text-text-secondary">Database Connection</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
