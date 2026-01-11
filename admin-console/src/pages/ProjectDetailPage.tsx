import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router'
import { projectsApi } from '@/lib/api-client'
import type { ProjectResponse } from '@/types/api'
import { Loader2, ArrowLeft, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

const statusColors: Record<string, string> = {
  created: 'bg-gray-100 text-gray-800',
  enriching: 'bg-blue-100 text-blue-800',
  decisioning: 'bg-yellow-100 text-yellow-800',
  ordering: 'bg-purple-100 text-purple-800',
  complete: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  pending_enrichment: 'bg-gray-100 text-gray-700',
  enriched: 'bg-blue-100 text-blue-700',
  pending_engineering: 'bg-yellow-100 text-yellow-700',
  pending_sourcing: 'bg-orange-100 text-orange-700',
  pending_finance: 'bg-purple-100 text-purple-700',
  pending_final_decision: 'bg-indigo-100 text-indigo-700',
  pending_purchase: 'bg-cyan-100 text-cyan-700',
  ordered: 'bg-green-100 text-green-700',
}

export function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [project, setProject] = useState<ProjectResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState<'items' | 'trace'>('items')

  useEffect(() => {
    async function fetchProject() {
      if (!id) return
      try {
        const data = await projectsApi.get(id)
        setProject(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load project')
      } finally {
        setIsLoading(false)
      }
    }
    fetchProject()
  }, [id])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error || !project) {
    return (
      <div className="flex items-center gap-2 p-4 bg-destructive/10 border border-destructive/20 rounded-md text-destructive">
        <AlertCircle className="w-5 h-5" />
        {error || 'Project not found'}
      </div>
    )
  }

  return (
    <div>
      <Link
        to="/projects"
        className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground mb-4"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Projects
      </Link>

      <div className="bg-card border border-border rounded-lg p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-foreground">
              {project.context.project_name || 'Unnamed Project'}
            </h1>
            <p className="text-sm text-muted-foreground font-mono mt-1">{project.project_id}</p>
          </div>
          <span className={cn(
            'inline-flex px-3 py-1 text-sm font-medium rounded-full',
            statusColors[project.status] || 'bg-gray-100 text-gray-800'
          )}>
            {project.status}
          </span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div>
            <p className="text-xs text-muted-foreground">Owner</p>
            <p className="text-sm text-foreground">{project.context.owner || '-'}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Product Type</p>
            <p className="text-sm text-foreground">{project.context.product_type}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Quantity</p>
            <p className="text-sm text-foreground">{project.context.quantity}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Line Items</p>
            <p className="text-sm text-foreground">{project.line_items.length}</p>
          </div>
        </div>
      </div>

      <div className="border-b border-border mb-4">
        <div className="flex gap-4">
          <button
            onClick={() => setActiveTab('items')}
            className={cn(
              'px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors',
              activeTab === 'items'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            )}
          >
            Line Items ({project.line_items.length})
          </button>
          <button
            onClick={() => setActiveTab('trace')}
            className={cn(
              'px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors',
              activeTab === 'trace'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            )}
          >
            Execution Trace ({project.trace.length})
          </button>
        </div>
      </div>

      {activeTab === 'items' && (
        <div className="bg-card border border-border rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-muted/50">
              <tr>
                <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">MPN</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">Manufacturer</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">Qty</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">Status</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">Selected</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {project.line_items.map((item, idx) => (
                <tr key={idx} className="hover:bg-muted/30">
                  <td className="px-4 py-3 text-sm font-mono text-foreground">{item.mpn || '-'}</td>
                  <td className="px-4 py-3 text-sm text-foreground">{item.manufacturer || '-'}</td>
                  <td className="px-4 py-3 text-sm text-foreground">{item.quantity}</td>
                  <td className="px-4 py-3">
                    <span className={cn(
                      'inline-flex px-2 py-0.5 text-xs font-medium rounded-full',
                      statusColors[item.status] || 'bg-gray-100 text-gray-800'
                    )}>
                      {item.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-foreground">
                    {item.selected_supplier ? `${item.selected_mpn} @ ${item.selected_supplier}` : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'trace' && (
        <div className="space-y-3">
          {project.trace.map((step, idx) => (
            <div key={idx} className="bg-card border border-border rounded-lg p-4">
              <div className="flex items-center gap-3 mb-2">
                <span className="text-xs font-mono text-muted-foreground">
                  {new Date(step.timestamp).toLocaleTimeString()}
                </span>
                <span className="px-2 py-0.5 text-xs font-medium bg-primary/10 text-primary rounded">
                  {step.step}
                </span>
                {step.agent && (
                  <span className="px-2 py-0.5 text-xs font-medium bg-muted text-muted-foreground rounded">
                    {step.agent}
                  </span>
                )}
              </div>
              <p className="text-sm text-foreground">{step.message}</p>
              {step.reasoning && (
                <p className="text-sm text-muted-foreground mt-2 italic">{step.reasoning}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
