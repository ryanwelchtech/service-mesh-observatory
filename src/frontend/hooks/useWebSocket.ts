'use client'

import { useState, useEffect, useCallback, useRef } from 'react'

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws'

interface WebSocketMessage {
  type: 'metrics_update' | 'topology_update' | 'alert' | 'cert_expiry_warning' | 'ack'
  timestamp: string
  data?: Record<string, unknown>
  severity?: string
}

interface UseWebSocketOptions {
  onMessage?: (message: WebSocketMessage) => void
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: (error: Event) => void
  reconnectAttempts?: number
  reconnectInterval?: number
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const {
    onMessage,
    onConnect,
    onDisconnect,
    onError,
    reconnectAttempts = 5,
    reconnectInterval = 3000,
  } = options

  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const [connectionAttempts, setConnectionAttempts] = useState(0)

  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return
    }

    try {
      const ws = new WebSocket(WS_URL)

      ws.onopen = () => {
        setIsConnected(true)
        setConnectionAttempts(0)
        onConnect?.()
      }

      ws.onclose = () => {
        setIsConnected(false)
        onDisconnect?.()

        // Attempt reconnection
        if (connectionAttempts < reconnectAttempts) {
          reconnectTimeoutRef.current = setTimeout(() => {
            setConnectionAttempts((prev) => prev + 1)
            connect()
          }, reconnectInterval)
        }
      }

      ws.onerror = (error) => {
        onError?.(error)
      }

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          setLastMessage(message)
          onMessage?.(message)
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e)
        }
      }

      wsRef.current = ws
    } catch (error) {
      console.error('WebSocket connection error:', error)
    }
  }, [connectionAttempts, reconnectAttempts, reconnectInterval, onConnect, onDisconnect, onError, onMessage])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    setIsConnected(false)
  }, [])

  const sendMessage = useCallback((message: Record<string, unknown>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    }
  }, [])

  useEffect(() => {
    connect()

    return () => {
      disconnect()
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return {
    isConnected,
    lastMessage,
    sendMessage,
    connect,
    disconnect,
    connectionAttempts,
  }
}

// Hook for subscribing to specific message types
export function useWebSocketMetrics() {
  const [metrics, setMetrics] = useState<{
    request_rate: number
    error_rate: number
    p50_latency: number
    p95_latency: number
    p99_latency: number
    active_connections: number
  } | null>(null)

  const handleMessage = useCallback((message: WebSocketMessage) => {
    if (message.type === 'metrics_update' && message.data) {
      setMetrics(message.data as typeof metrics)
    }
  }, [])

  const { isConnected, connectionAttempts } = useWebSocket({
    onMessage: handleMessage,
  })

  return {
    metrics,
    isConnected,
    connectionAttempts,
  }
}

// Hook for receiving alerts
export function useWebSocketAlerts() {
  const [alerts, setAlerts] = useState<WebSocketMessage[]>([])

  const handleMessage = useCallback((message: WebSocketMessage) => {
    if (message.type === 'alert' || message.type === 'cert_expiry_warning') {
      setAlerts((prev) => [message, ...prev].slice(0, 50)) // Keep last 50 alerts
    }
  }, [])

  const { isConnected } = useWebSocket({
    onMessage: handleMessage,
  })

  const clearAlerts = useCallback(() => {
    setAlerts([])
  }, [])

  return {
    alerts,
    isConnected,
    clearAlerts,
  }
}
