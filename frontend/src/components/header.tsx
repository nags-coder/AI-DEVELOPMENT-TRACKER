import { Moon, Sun, Zap, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useTheme } from "@/hooks/use-theme"

interface HeaderProps {
  onRefresh?: () => void
  isRefreshing?: boolean
}

export function Header({ onRefresh, isRefreshing }: HeaderProps) {
  const { theme, toggleTheme } = useTheme()

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center justify-between mx-auto px-4">
        <div className="flex items-center gap-2">
          <Zap className="h-6 w-6 text-primary" />
          <h1 className="text-xl font-bold tracking-tight">AI Pulse</h1>
        </div>
        <div className="flex items-center gap-1">
          {onRefresh && (
            <Button variant="ghost" size="icon" onClick={onRefresh} disabled={isRefreshing}>
              <RefreshCw className={`h-5 w-5 ${isRefreshing ? "animate-spin" : ""}`} />
            </Button>
          )}
          <Button variant="ghost" size="icon" onClick={toggleTheme}>
            {theme === "dark" ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </Button>
        </div>
      </div>
    </header>
  )
}
