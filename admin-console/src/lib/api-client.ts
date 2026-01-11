import type {
  ProjectSummary,
  ProjectResponse,
  FlowTraceStep,
  PartKnowledge,
  SupplierKnowledge,
  CreateSupplierRequest,
  ApiKey,
  ApiKeyCreateResponse,
  Client,
} from '@/types/api'

const API_BASE = '/api/proxy'

class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

interface RequestOptions {
  method?: string
  body?: unknown
  params?: Record<string, string>
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, params } = options

  let url = `${API_BASE}${endpoint}`
  if (params) {
    url += '?' + new URLSearchParams(params).toString()
  }

  const res = await fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
    credentials: 'include',
  })

  // Don't redirect on 401 - let the component handle the error
  // The auth context handles session expiry separately

  const data = await res.json()

  if (!res.ok) {
    throw new ApiError(res.status, data.detail || data.error || 'Request failed')
  }

  return data
}

// Projects API
export const projectsApi = {
  list: (limit = 100) =>
    request<ProjectSummary[]>('/projects', { params: { limit: String(limit) } }),
  get: (id: string) =>
    request<ProjectResponse>(`/projects/${id}`),
  delete: (id: string) =>
    request<{ deleted: string }>(`/projects/${id}`, { method: 'DELETE' }),
  getTrace: (id: string) =>
    request<FlowTraceStep[]>(`/projects/${id}/trace`),
}

// Parts API
export const partsApi = {
  list: (limit = 100) =>
    request<PartKnowledge[]>('/knowledge/parts', { params: { limit: String(limit) } }),
  get: (mpn: string) =>
    request<PartKnowledge>(`/knowledge/parts/${encodeURIComponent(mpn)}`),
  ban: (mpn: string, reason: string, user = 'admin-console') =>
    request(`/knowledge/parts/${encodeURIComponent(mpn)}/ban`, {
      method: 'POST',
      body: { reason, user },
    }),
  unban: (mpn: string, user = 'admin-console') =>
    request(`/knowledge/parts/${encodeURIComponent(mpn)}/unban`, {
      method: 'POST',
      body: { user },
    }),
  addAlternate: (mpn: string, alternateMpn: string, reason = '') =>
    request(`/knowledge/parts/${encodeURIComponent(mpn)}/alternates`, {
      method: 'POST',
      body: { alternate_mpn: alternateMpn, reason },
    }),
  getAlternates: (mpn: string) =>
    request<string[]>(`/knowledge/parts/${encodeURIComponent(mpn)}/alternates`),
}

// Suppliers API
export const suppliersApi = {
  list: (limit = 100) =>
    request<SupplierKnowledge[]>('/knowledge/suppliers', { params: { limit: String(limit) } }),
  get: (id: string) =>
    request<SupplierKnowledge>(`/knowledge/suppliers/${id}`),
  create: (data: CreateSupplierRequest) =>
    request('/knowledge/suppliers', { method: 'POST', body: data }),
  setTrust: (id: string, trustLevel: string, reason = '') =>
    request(`/knowledge/suppliers/${id}/trust`, {
      method: 'POST',
      body: { trust_level: trustLevel, reason },
    }),
}

// API Keys API
export const apiKeysApi = {
  list: () =>
    request<ApiKey[]>('/api-keys'),
  create: (clientId: string, name: string, scopes: string[] = ['all']) =>
    request<ApiKeyCreateResponse>('/api-keys', {
      method: 'POST',
      body: { client_id: clientId, name, scopes },
    }),
  revoke: (keyId: string) =>
    request(`/api-keys/${keyId}/revoke`, { method: 'POST' }),
}

// Clients API
export const clientsApi = {
  list: () =>
    request<Client[]>('/clients'),
  create: (name: string, slug: string) =>
    request<Client>('/clients', { method: 'POST', body: { name, slug } }),
}
