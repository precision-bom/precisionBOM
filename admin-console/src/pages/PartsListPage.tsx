import { useEffect, useState } from 'react'
import { partsApi } from '@/lib/api-client'
import type { PartKnowledge } from '@/types/api'
import { Loader2, Ban, CheckCircle, Plus, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

export function PartsListPage() {
  const [parts, setParts] = useState<PartKnowledge[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [actionLoading, setActionLoading] = useState<string | null>(null)

  const fetchParts = async () => {
    try {
      const data = await partsApi.list()
      setParts(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load parts')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchParts()
  }, [])

  const handleBan = async (mpn: string) => {
    const reason = prompt('Enter ban reason:')
    if (!reason) return

    setActionLoading(mpn)
    try {
      await partsApi.ban(mpn, reason)
      fetchParts()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to ban part')
    } finally {
      setActionLoading(null)
    }
  }

  const handleUnban = async (mpn: string) => {
    setActionLoading(mpn)
    try {
      await partsApi.unban(mpn)
      fetchParts()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to unban part')
    } finally {
      setActionLoading(null)
    }
  }

  const handleAddAlternate = async (mpn: string) => {
    const alternateMpn = prompt('Enter alternate MPN:')
    if (!alternateMpn) return

    const reason = prompt('Enter reason (optional):') || ''

    setActionLoading(mpn)
    try {
      await partsApi.addAlternate(mpn, alternateMpn, reason)
      fetchParts()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to add alternate')
    } finally {
      setActionLoading(null)
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
      <h1 className="text-2xl font-semibold text-foreground mb-6">Parts Knowledge</h1>

      {parts.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          No parts in knowledge base
        </div>
      ) : (
        <div className="bg-card border border-border rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-muted/50">
              <tr>
                <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">MPN</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">Status</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">Times Used</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">Failures</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">Alternates</th>
                <th className="text-right px-4 py-3 text-sm font-medium text-muted-foreground">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {parts.map((part) => (
                <tr key={part.mpn} className="hover:bg-muted/30">
                  <td className="px-4 py-3 text-sm font-mono text-foreground">{part.mpn}</td>
                  <td className="px-4 py-3">
                    <div className="flex gap-1">
                      {part.banned && (
                        <span className="inline-flex px-2 py-0.5 text-xs font-medium rounded-full bg-red-100 text-red-800">
                          Banned
                        </span>
                      )}
                      {part.preferred && (
                        <span className="inline-flex px-2 py-0.5 text-xs font-medium rounded-full bg-green-100 text-green-800">
                          Preferred
                        </span>
                      )}
                      {!part.banned && !part.preferred && (
                        <span className="inline-flex px-2 py-0.5 text-xs font-medium rounded-full bg-gray-100 text-gray-800">
                          Active
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-foreground">{part.times_used}</td>
                  <td className="px-4 py-3 text-sm text-foreground">
                    <span className={cn(part.failure_count > 0 && 'text-destructive font-medium')}>
                      {part.failure_count}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-foreground">
                    {part.approved_alternates.length > 0 ? (
                      <span className="text-muted-foreground">
                        {part.approved_alternates.join(', ')}
                      </span>
                    ) : (
                      '-'
                    )}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-1">
                      {actionLoading === part.mpn ? (
                        <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
                      ) : (
                        <>
                          {part.banned ? (
                            <button
                              onClick={() => handleUnban(part.mpn)}
                              className="p-1.5 text-muted-foreground hover:text-green-600 hover:bg-green-50 rounded"
                              title="Unban"
                            >
                              <CheckCircle className="w-4 h-4" />
                            </button>
                          ) : (
                            <button
                              onClick={() => handleBan(part.mpn)}
                              className="p-1.5 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded"
                              title="Ban"
                            >
                              <Ban className="w-4 h-4" />
                            </button>
                          )}
                          <button
                            onClick={() => handleAddAlternate(part.mpn)}
                            className="p-1.5 text-muted-foreground hover:text-primary hover:bg-primary/10 rounded"
                            title="Add Alternate"
                          >
                            <Plus className="w-4 h-4" />
                          </button>
                        </>
                      )}
                    </div>
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
