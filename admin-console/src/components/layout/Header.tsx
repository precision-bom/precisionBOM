import { useAuth } from '@/context/AuthContext'
import { LogOut } from 'lucide-react'

export function Header() {
  const { logout } = useAuth()

  return (
    <header className="h-14 border-b border-border bg-card flex items-center justify-end px-6">
      <button
        onClick={logout}
        className="flex items-center gap-2 px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground rounded-md hover:bg-muted transition-colors"
      >
        <LogOut className="w-4 h-4" />
        Sign Out
      </button>
    </header>
  )
}
