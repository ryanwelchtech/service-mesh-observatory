/**
 * API Client for Service Mesh Observatory
 * Handles all REST API communication with the backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface ApiError {
  detail: string
  status: number
}

class ApiClient {
  private baseUrl: string
  private token: string | null = null

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('access_token')
    }
  }

  setToken(token: string) {
    this.token = token
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token)
    }
  }

  clearToken() {
    this.token = null
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    }

    if (this.token) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${this.token}`
    }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        detail: 'An error occurred',
        status: response.status,
      }))
      throw new Error(error.detail)
    }

    return response.json()
  }

  // Auth endpoints
  async login(email: string, password: string) {
    const response = await this.request<{
      access_token: string
      refresh_token: string
      token_type: string
      expires_in: number
    }>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
    this.setToken(response.access_token)
    if (typeof window !== 'undefined') {
      localStorage.setItem('refresh_token', response.refresh_token)
    }
    return response
  }

  async register(email: string, password: string, name: string) {
    return this.request<{ id: string; email: string; name: string; role: string }>(
      '/api/v1/auth/register',
      {
        method: 'POST',
        body: JSON.stringify({ email, password, name }),
      }
    )
  }

  async logout() {
    await this.request('/api/v1/auth/logout', { method: 'POST' })
    this.clearToken()
  }

  async getCurrentUser() {
    return this.request<{ id: string; email: string; name: string; role: string }>(
      '/api/v1/auth/me'
    )
  }

  // Topology endpoints
  async getTopology() {
    return this.request<{
      timestamp: string
      nodes: Array<{
        id: string
        name: string
        namespace: string
        type: string
      }>
      edges: Array<{
        source: string
        target: string
        request_rate: number
      }>
      summary: {
        total_services: number
        total_connections: number
      }
    }>('/api/v1/topology/')
  }

  async getServices() {
    return this.request<Array<{
      name: string
      namespace: string
      type: string
      cluster_ip: string
    }>>('/api/v1/topology/services')
  }

  // Metrics endpoints
  async getMetricsOverview() {
    return this.request<{
      timestamp: string
      request_rate: number
      error_rate: number
      p50_latency_ms: number
      p95_latency_ms: number
      p99_latency_ms: number
      active_connections: number
    }>('/api/v1/metrics/overview')
  }

  async getServiceMetrics(serviceName: string, namespace: string = 'default') {
    return this.request<{
      service: string
      namespace: string
      duration: string
      timestamp: string
      metrics: Record<string, number>
    }>(`/api/v1/metrics/service/${serviceName}?namespace=${namespace}`)
  }

  // Certificate endpoints
  async getCertificates() {
    return this.request<{
      timestamp: string
      total_certificates: number
      certificates: Array<{
        service: string
        namespace: string
        expires_at: string
        days_until_expiry: number
        status: string
      }>
    }>('/api/v1/certificates/')
  }

  async getCertificateHealth() {
    return this.request<{
      health_score: number
      expiring_within_7_days: number
      expiring_within_30_days: number
      total_certificates: number
      status: string
    }>('/api/v1/certificates/health')
  }

  // Anomaly endpoints
  async getAnomalies(limit: number = 50, severity?: string) {
    const params = new URLSearchParams({ limit: limit.toString() })
    if (severity) params.append('severity', severity)
    return this.request<{
      timestamp: string
      count: number
      anomalies: Array<{
        id: string
        type: string
        severity: string
        score: number
        service: string
        namespace: string
        title: string
        description: string
        created_at: string
        is_acknowledged: boolean
      }>
    }>(`/api/v1/anomalies/?${params}`)
  }

  async acknowledgeAnomaly(anomalyId: string, notes?: string) {
    return this.request<{ anomaly_id: string; acknowledged: boolean }>(
      `/api/v1/anomalies/${anomalyId}/acknowledge`,
      {
        method: 'POST',
        body: JSON.stringify({ notes }),
      }
    )
  }

  async getAnomalyStatistics(duration: string = '7d') {
    return this.request<{
      duration: string
      total: number
      by_severity: Record<string, number>
      by_type: Record<string, number>
      acknowledged: number
      unacknowledged: number
    }>(`/api/v1/anomalies/statistics?duration=${duration}`)
  }

  // Policy endpoints
  async getPolicies(namespace?: string) {
    const params = namespace ? `?namespace=${namespace}` : ''
    return this.request<Array<{
      name: string
      namespace: string
      action: string
      rules: number
    }>>(`/api/v1/policies/${params}`)
  }

  async validatePolicy(policyYaml: string) {
    return this.request<{
      valid: boolean
      errors: string[]
      warnings: string[]
      suggestions: string[]
    }>('/api/v1/policies/validate', {
      method: 'POST',
      body: JSON.stringify({ policy_yaml: policyYaml }),
    })
  }

  async getComplianceStatus() {
    return this.request<{
      total_services: number
      services_with_policies: number
      compliance_percentage: number
      non_compliant_services: Array<{ name: string; namespace: string }>
    }>('/api/v1/policies/compliance/status')
  }

  // Health check
  async healthCheck() {
    return this.request<{ status: string; service: string }>('/health')
  }
}

export const api = new ApiClient(API_BASE_URL)
export type { ApiError }
