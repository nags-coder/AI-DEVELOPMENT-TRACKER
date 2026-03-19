import { Search, SlidersHorizontal } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import type { FeedParams } from "@/types/api"

interface FeedFiltersProps {
  params: FeedParams
  onChange: (params: FeedParams) => void
  sourceNames?: string[]
}

const TIME_RANGES = [
  { label: "Today", value: "today" as const },
  { label: "7 days", value: "7d" as const },
  { label: "30 days", value: "30d" as const },
  { label: "All", value: "all" as const },
]

const CONTENT_TYPES = ["paper", "repo", "model", "space"]

const SORT_OPTIONS = [
  { label: "Latest", value: "date" as const },
  { label: "Relevance", value: "relevance" as const },
]

export function FeedFilters({ params, onChange, sourceNames = [] }: FeedFiltersProps) {
  return (
    <div className="space-y-3">
      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search papers, repos, models..."
          className="pl-9"
          value={params.search ?? ""}
          onChange={(e) => onChange({ ...params, search: e.target.value || undefined, page: 1 })}
        />
      </div>

      {/* Filter bar */}
      <div className="flex flex-wrap items-center gap-2">
        <SlidersHorizontal className="h-4 w-4 text-muted-foreground" />

        {/* Time range */}
        <div className="flex gap-1">
          {TIME_RANGES.map((t) => (
            <Button
              key={t.value}
              variant={params.time_range === t.value ? "default" : "outline"}
              size="sm"
              onClick={() =>
                onChange({
                  ...params,
                  time_range: params.time_range === t.value ? undefined : t.value,
                  page: 1,
                })
              }
            >
              {t.label}
            </Button>
          ))}
        </div>

        <span className="text-muted-foreground">|</span>

        {/* Content types */}
        <div className="flex gap-1">
          {CONTENT_TYPES.map((ct) => (
            <Badge
              key={ct}
              variant={params.content_type === ct ? "default" : "outline"}
              className="cursor-pointer"
              onClick={() =>
                onChange({
                  ...params,
                  content_type: params.content_type === ct ? undefined : ct,
                  page: 1,
                })
              }
            >
              {ct}
            </Badge>
          ))}
        </div>

        <span className="text-muted-foreground">|</span>

        {/* Sources */}
        <div className="flex gap-1">
          {sourceNames.map((name) => (
            <Badge
              key={name}
              variant={params.source?.toLowerCase() === name.toLowerCase() ? "default" : "outline"}
              className="cursor-pointer"
              onClick={() =>
                onChange({
                  ...params,
                  source: params.source?.toLowerCase() === name.toLowerCase() ? undefined : name,
                  page: 1,
                })
              }
            >
              {name}
            </Badge>
          ))}
        </div>

        <span className="text-muted-foreground">|</span>

        {/* Sort */}
        <div className="flex gap-1">
          {SORT_OPTIONS.map((s) => (
            <Button
              key={s.value}
              variant={params.sort_by === s.value ? "default" : "ghost"}
              size="sm"
              onClick={() => onChange({ ...params, sort_by: s.value })}
            >
              {s.label}
            </Button>
          ))}
        </div>
      </div>
    </div>
  )
}
