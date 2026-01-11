import { useEffect, useState } from 'react'
import { Link } from 'react-router'
import { projectsApi } from '@/lib/api-client'
import type { ProjectSummary } from '@/types/api'
import { Loader2, Trash2, Eye, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

const statusColors: Record<string, string> = {
  created: 'bg-gray-100 text-gray-800',
  enriching: 'bg-blue-100 text-blue-800',
  decisioning: 'bg-yellow-100 text-yellow-800',
  ordering: 'bg-purple-100 text-purple-800',
  complete: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
}

export function ProjectsListPage() {
  const [projects, setProjects] = useState<ProjectSummary[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [deleting, setDeleting] = useState<string | null>(null)

  const fetchProjects = async () => {
    try {
      const data = await projectsApi.list()
      setProjects(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load projects')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchProjects()
  }, [])

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this project?')) return

    setDeleting(id)
    try {
      await projectsApi.delete(id)
      setProjects(projects.filter((p) => p.project_id !== id))
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete project')
    } finally {
      setDeleting(null)
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
      <h1 className="text-2xl font-semibold text-foreground mb-6">Projects</h1>

      {projects.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          No projects found
        </div>
      ) : (
        <div className="bg-card border border-border rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-muted/50">
              <tr>
                <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">Project ID</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">Name</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">Status</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">Items</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">Created</th>
                <th className="text-right px-4 py-3 text-sm font-medium text-muted-foreground">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {projects.map((project) => (
                <tr key={project.project_id} className="hover:bg-muted/30">
                  <td className="px-4 py-3 text-sm font-mono text-foreground">
                    {project.project_id.slice(0, 8)}...
                  </td>
                  <td className="px-4 py-3 text-sm text-foreground">
                    {project.project_name || '-'}
                  </td>
                  <td className="px-4 py-3">
                    <span className={cn(
                      'inline-flex px-2 py-0.5 text-xs font-medium rounded-full',
                      statusColors[project.status] || 'bg-gray-100 text-gray-800'
                    )}>
                      {project.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-foreground">
                    {project.line_item_count}
                  </td>
                  <td className="px-4 py-3 text-sm text-muted-foreground">
                    {new Date(project.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Link
                        to={`/projects/${project.project_id}`}
                        className="p-1.5 text-muted-foreground hover:text-foreground hover:bg-muted rounded"
                      >
                        <Eye className="w-4 h-4" />
                      </Link>
                      <button
                        onClick={() => handleDelete(project.project_id)}
                        disabled={deleting === project.project_id}
                        className="p-1.5 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded disabled:opacity-50"
                      >
                        {deleting === project.project_id ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <Trash2 className="w-4 h-4" />
                        )}
                      </button>
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
