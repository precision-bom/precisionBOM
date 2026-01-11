import { useEffect, useState } from 'react'
import { apiKeysApi, clientsApi } from '@/lib/api-client'
import type { ApiKey, Client } from '@/types/api'
import { Loader2, Plus, AlertCircle, Trash2, Copy, CheckCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

export function ApiKeysPage() {
  const [keys, setKeys] = useState<ApiKey[]>([])
  const [clients, setClients] = useState<Client[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newKey, setNewKey] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  const fetchData = async () => {
    try {
      const [keysData, clientsData] = await Promise.all([
        apiKeysApi.list().catch(() => []),
        clientsApi.list().catch(() => []),
      ])
      setKeys(keysData)
      setClients(clientsData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleRevoke = async (keyId: string) => {
    if (!confirm('Are you sure you want to revoke this API key?')) return

    setActionLoading(keyId)
    try {
      await apiKeysApi.revoke(keyId)
      fetchData()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to revoke key')
    } finally {
      setActionLoading(null)
    }
  }

  const handleCreate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const form = e.currentTarget
    const formData = new FormData(form)

    try {
      const result = await apiKeysApi.create(
        formData.get('client_id') as string,
        formData.get('name') as string,
        (formData.get('scopes') as string).split(',').map(s => s.trim())
      )
      setNewKey(result.raw_key)
      fetchData()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to create key')
    }
  }

  const copyToClipboard = () => {
    if (newKey) {
      navigator.clipboard.writeText(newKey)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
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
        <h1 className="text-2xl font-semibold text-foreground">API Keys</h1>
        <button
          onClick={() => { setShowCreateForm(!showCreateForm); setNewKey(null); }}
          className="flex items-center gap-2 px-3 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium hover:bg-primary/90"
        >
          <Plus className="w-4 h-4" />
          Create Key
        </button>
      </div>

      {newKey && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <span className="font-medium text-green-800">API Key Created</span>
          </div>
          <p className="text-sm text-green-700 mb-3">
            Copy this key now. It will not be shown again.
          </p>
          <div className="flex items-center gap-2">
            <code className="flex-1 p-2 bg-white border border-green-300 rounded text-sm font-mono">
              {newKey}
            </code>
            <button
              onClick={copyToClipboard}
              className="p-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              {copied ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            </button>
          </div>
        </div>
      )}

      {showCreateForm && !newKey && (
        <form onSubmit={handleCreate} className="bg-card border border-border rounded-lg p-4 mb-6">
          <h2 className="text-lg font-medium mb-4">Create API Key</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Client</label>
              <select name="client_id" required className="w-full px-3 py-2 border border-input rounded-md bg-background text-sm">
                <option value="">Select client...</option>
                {clients.map(client => (
                  <option key={client.client_id} value={client.client_id}>
                    {client.name} ({client.slug})
                  </option>
                ))}
              </select>
              {clients.length === 0 && (
                <p className="text-xs text-muted-foreground mt-1">
                  No clients found. Create one via CLI first.
                </p>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Name</label>
              <input
                name="name"
                required
                placeholder="e.g., admin-key"
                className="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
              />
            </div>
            <div className="col-span-2">
              <label className="block text-sm font-medium mb-1">Scopes</label>
              <input
                name="scopes"
                defaultValue="admin,all"
                placeholder="admin,all"
                className="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
              />
              <p className="text-xs text-muted-foreground mt-1">Comma-separated list of scopes</p>
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

      {keys.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          No API keys found. API key endpoints may not be available yet.
        </div>
      ) : (
        <div className="bg-card border border-border rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-muted/50">
              <tr>
                <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">Name</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">Key ID</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">Scopes</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">Status</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">Last Used</th>
                <th className="text-right px-4 py-3 text-sm font-medium text-muted-foreground">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {keys.map((key) => (
                <tr key={key.key_id} className="hover:bg-muted/30">
                  <td className="px-4 py-3 text-sm font-medium text-foreground">{key.name}</td>
                  <td className="px-4 py-3 text-sm font-mono text-muted-foreground">
                    {key.key_id.slice(0, 8)}...
                  </td>
                  <td className="px-4 py-3 text-sm text-foreground">
                    {key.scopes.join(', ')}
                  </td>
                  <td className="px-4 py-3">
                    <span className={cn(
                      'inline-flex px-2 py-0.5 text-xs font-medium rounded-full',
                      key.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    )}>
                      {key.is_active ? 'Active' : 'Revoked'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-muted-foreground">
                    {key.last_used ? new Date(key.last_used).toLocaleDateString() : 'Never'}
                  </td>
                  <td className="px-4 py-3 text-right">
                    {key.is_active && (
                      actionLoading === key.key_id ? (
                        <Loader2 className="w-4 h-4 animate-spin text-muted-foreground inline" />
                      ) : (
                        <button
                          onClick={() => handleRevoke(key.key_id)}
                          className="p-1.5 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded"
                          title="Revoke"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )
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
