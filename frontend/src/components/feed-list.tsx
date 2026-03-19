import { ChevronLeft, ChevronRight, Loader2 } from "lucide-react"
import { FeedCard } from "@/components/feed-card"
import { Button } from "@/components/ui/button"
import type { FeedResponse, FeedParams } from "@/types/api"

interface FeedListProps {
  data: FeedResponse | undefined
  isLoading: boolean
  error: Error | null
  params: FeedParams
  onChange: (params: FeedParams) => void
  onFeedback?: (id: number, action: "up" | "down") => void
  onToggleSave?: (id: number, save: boolean) => void
}

export function FeedList({ data, isLoading, error, params, onChange, onFeedback, onToggleSave }: FeedListProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-6 text-center">
        <p className="text-destructive font-medium">Failed to load feed</p>
        <p className="text-sm text-muted-foreground mt-1">{error.message}</p>
      </div>
    )
  }

  if (!data || data.data.length === 0) {
    return (
      <div className="rounded-lg border bg-muted/30 p-10 text-center">
        <p className="text-lg font-medium">No items found</p>
        <p className="text-sm text-muted-foreground mt-1">
          Try adjusting your filters or check back later.
        </p>
      </div>
    )
  }

  const { meta } = data

  return (
    <div className="space-y-4">
      {/* Items */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {data.data.map((item) => (
          <FeedCard key={item.id} item={item} onFeedback={onFeedback} onToggleSave={onToggleSave} />
        ))}
      </div>

      {/* Pagination */}
      {meta.total_pages > 1 && (
        <div className="flex items-center justify-between pt-2">
          <p className="text-sm text-muted-foreground">
            Page {meta.page} of {meta.total_pages} ({meta.total} items)
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={meta.page <= 1}
              onClick={() => onChange({ ...params, page: meta.page - 1 })}
            >
              <ChevronLeft className="h-4 w-4 mr-1" /> Prev
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={meta.page >= meta.total_pages}
              onClick={() => onChange({ ...params, page: meta.page + 1 })}
            >
              Next <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
