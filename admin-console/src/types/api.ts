// Project types
export interface ProjectSummary {
  project_id: string
  project_name: string | null
  status: string
  line_item_count: number
  created_at: string
  updated_at: string
}

export interface ProjectContext {
  project_id: string
  project_name: string
  owner: string
  product_type: string
  quantity: number
  deadline: string | null
  budget_total: number
}

export interface BOMLineItem {
  reference_designators: string[]
  quantity: number
  mpn: string
  manufacturer: string
  description: string
  package: string
  value: string
  status: string
  selected_mpn: string | null
  selected_supplier: string | null
}

export interface FlowTraceStep {
  step: string
  agent: string | null
  message: string
  reasoning: string | null
  references: string[]
  timestamp: string
}

export interface ProjectResponse {
  project_id: string
  context: ProjectContext
  line_items: BOMLineItem[]
  status: string
  created_at: string
  updated_at: string
  trace: FlowTraceStep[]
}

// Part types
export interface PartKnowledge {
  mpn: string
  notes: string[]
  approved_alternates: string[]
  banned: boolean
  ban_reason: string
  preferred: boolean
  times_used: number
  failure_count: number
}

// Supplier types
export interface SupplierKnowledge {
  supplier_id: string
  name: string
  supplier_type: 'authorized' | 'broker' | 'direct'
  trust_level: 'high' | 'medium' | 'low' | 'blocked'
  on_time_rate: number
  quality_rate: number
  order_count_ytd: number
  notes: string[]
}

export interface CreateSupplierRequest {
  supplier_id: string
  name: string
  supplier_type?: string
  trust_level?: string
}

// API Key types
export interface ApiKey {
  key_id: string
  client_id: string
  name: string
  scopes: string[]
  created_at: string
  last_used: string | null
  is_active: boolean
}

export interface ApiKeyCreateResponse {
  key: ApiKey
  raw_key: string
}

// Client types
export interface Client {
  client_id: string
  name: string
  slug: string
  is_active: boolean
  created_at: string
}
