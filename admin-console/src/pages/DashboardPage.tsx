import { useEffect, useState } from 'react'
import { Link } from 'react-router'
import { projectsApi, partsApi, suppliersApi } from '@/lib/api-client'
import { FolderKanban, Cpu, Building2, Loader2 } from 'lucide-react'

interface Stats {
  projects: number
  parts: number
  suppliers: number
}

export function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function fetchStats() {
      try {
        const [projects, parts, suppliers] = await Promise.all([
          projectsApi.list(),
          partsApi.list(),
          suppliersApi.list(),
        ])
        setStats({
          projects: projects.length,
          parts: parts.length,
          suppliers: suppliers.length,
        })
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load stats')
      } finally {
        setIsLoading(false)
      }
    }
    fetchStats()
  }, [])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-md text-destructive">
        {error}
      </div>
    )
  }

  const cards = [
    { label: 'Projects', value: stats?.projects ?? 0, icon: FolderKanban, href: '/projects', color: 'text-blue-600' },
    { label: 'Parts', value: stats?.parts ?? 0, icon: Cpu, href: '/parts', color: 'text-green-600' },
    { label: 'Suppliers', value: stats?.suppliers ?? 0, icon: Building2, href: '/suppliers', color: 'text-purple-600' },
  ]

  return (
    <div>
      <h1 className="text-2xl font-semibold text-foreground mb-6">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {cards.map((card) => (
          <Link
            key={card.label}
            to={card.href}
            className="bg-card border border-border rounded-lg p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">{card.label}</p>
                <p className="text-3xl font-semibold text-foreground mt-1">{card.value}</p>
              </div>
              <card.icon className={`w-10 h-10 ${card.color}`} />
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
