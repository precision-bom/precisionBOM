import { useEffect, useState } from 'react'
import { suppliersApi } from '@/lib/api-client'
import type { SupplierKnowledge } from '@/types/api'
import { Loader2, Plus, AlertCircle, Shield } from 'lucide-react'
import { cn } from '@/lib/utils'

const trustColors: Record<string, string> = {
  high: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  low: 'bg-orange-100 text-orange-800',
  blocked: 'bg-red-100 text-red-800',
}

const typeColors: Record<string, string> = {
  authorized: 'bg-blue-100 text-blue-800',
  broker: 'bg-purple-100 text-purple-800',
  direct: 'bg-gray-100 text-gray-800',
}

export function SuppliersListPage() {
  const [suppliers, setSuppliers] = useState<SupplierKnowledge[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [showCreateForm, setShowCreateForm] = useState(false)

  const fetchSuppliers = async () => {
    try {
      const data = await suppliersApi.list()
      setSuppliers(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load suppliers')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchSuppliers()
  }, [])

  const handleSetTrust = async (id: string, currentTrust: string) => {
    const levels = ['high', 'medium', 'low', 'blocked'].filter(l => l !== currentTrust)
    const newLevel = prompt(`Set trust level (${levels.join('/')}):`)
    if (!newLevel || !levels.includes(newLevel)) return

    const reason = prompt('Enter reason (optional):') || ''

    setActionLoading(id)
    try {
      await suppliersApi.setTrust(id, newLevel, reason)
      fetchSuppliers()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to update trust level')
    } finally {
      setActionLoading(null)
    }
  }

  const handleCreate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const form = e.currentTarget
    const formData = new FormData(form)

    try {
      await suppliersApi.create({
        supplier_id: formData.get('supplier_id') as string,
        name: formData.get('name') as string,
        supplier_type: formData.get('supplier_type') as string,
        trust_level: formData.get('trust_level') as string,
      })
      setShowCreateForm(false)
      fetchSuppliers()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to create supplier')
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center gap-2 p-4 bg-destructive/10 border border-destructive/20 rounded-md text-destructive">
        <AlertCircle className="w-5 h-5" />
        {error}
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold text-foreground">Suppliers</h1>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="flex items-center gap-2 px-3 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium hover:bg-primary/90"
        >
          <Plus className="w-4 h-4" />
          Add Supplier
        </button>
      </div>

      {showCreateForm && (
        <form onSubmit={handleCreate} className="bg-card border border-border rounded-lg p-4 mb-6">
          <h2 className="text-lg font-medium mb-4">Create Supplier</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Supplier ID</label>
              <input
                name="supplier_id"
                required
                placeholder="e.g., digikey"
                className="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Name</label>
              <input
                name="name"
                required
                placeholder="e.g., DigiKey"
                className="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Type</label>
              <select name="supplier_type" className="w-full px-3 py-2 border border-input rounded-md bg-background text-sm">
                <option value="authorized">Authorized</option>
                <option value="broker">Broker</option>
                <option value="direct">Direct</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Trust Level</label>
              <select name="trust_level" className="w-full px-3 py-2 border border-input rounded-md bg-background text-sm">
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="low">Low</option>
              </select>
            </div>
          </div>
          <div className="flex gap-2 mt-4">
            <button type="submit" className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium hover:bg-primary/90">
              Create
            </button>
            <button type="button" onClick={() => setShowCreateForm(false)} className="px-4 py-2 bg-muted text-foreground rounded-md text-sm font-medium hover:bg-muted/80">
              Cancel
            </button>
          </div>
        </form>
      )}

      {suppliers.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          No suppliers in knowledge base
        </div>
      ) : (
        <div className="bg-card border border-border rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-muted/50">
              <tr>
                <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">Supplier</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">Type</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">Trust</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">On-Time</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">Quality</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">Orders YTD</th>
                <th className="text-right px-4 py-3 text-sm font-medium text-muted-foreground">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {suppliers.map((supplier) => (
                <tr key={supplier.supplier_id} className="hover:bg-muted/30">
                  <td className="px-4 py-3">
                    <div>
                      <p className="text-sm font-medium text-foreground">{supplier.name}</p>
                      <p className="text-xs text-muted-foreground font-mono">{supplier.supplier_id}</p>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className={cn(
                      'inline-flex px-2 py-0.5 text-xs font-medium rounded-full',
                      typeColors[supplier.supplier_type] || 'bg-gray-100 text-gray-800'
                    )}>
                      {supplier.supplier_type}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={cn(
                      'inline-flex px-2 py-0.5 text-xs font-medium rounded-full',
                      trustColors[supplier.trust_level] || 'bg-gray-100 text-gray-800'
                    )}>
                      {supplier.trust_level}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-foreground">
                    {(supplier.on_time_rate * 100).toFixed(0)}%
                  </td>
                  <td className="px-4 py-3 text-sm text-foreground">
                    {(supplier.quality_rate * 100).toFixed(0)}%
                  </td>
                  <td className="px-4 py-3 text-sm text-foreground">{supplier.order_count_ytd}</td>
                  <td className="px-4 py-3 text-right">
                    {actionLoading === supplier.supplier_id ? (
                      <Loader2 className="w-4 h-4 animate-spin text-muted-foreground inline" />
                    ) : (
                      <button
                        onClick={() => handleSetTrust(supplier.supplier_id, supplier.trust_level)}
                        className="p-1.5 text-muted-foreground hover:text-primary hover:bg-primary/10 rounded"
                        title="Change Trust Level"
                      >
                        <Shield className="w-4 h-4" />
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
