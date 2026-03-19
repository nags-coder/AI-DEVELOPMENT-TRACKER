import { ExternalLink, ThumbsDown, ThumbsUp, Bookmark, BookmarkCheck } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { formatDate } from "@/lib/utils"
import type { ContentItem } from "@/types/api"

interface FeedCardProps {
  item: ContentItem
  onFeedback?: (id: number, action: "up" | "down") => void
  onToggleSave?: (id: number, save: boolean) => void
}

const TYPE_COLORS: Record<string, string> = {
  paper: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  repo: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  model: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
  space: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  dataset: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
}

export function FeedCard({ item, onFeedback, onToggleSave }: FeedCardProps) {
  return (
    <Card className="transition-shadow hover:shadow-md">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <Badge
                variant="secondary"
                className={TYPE_COLORS[item.content_type] ?? ""}
              >
                {item.content_type}
              </Badge>
              <span className="text-xs text-muted-foreground">
                {item.source.name}
              </span>
              <span className="text-xs text-muted-foreground">
                {formatDate(item.published_at)}
              </span>
            </div>
            <CardTitle className="text-base leading-snug">
              <a
                href={item.original_url}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:underline"
              >
                {item.title}
              </a>
            </CardTitle>
          </div>
          <div className="text-xs font-mono text-muted-foreground shrink-0">
            {(parseFloat(item.relevance_score) * 100).toFixed(0)}%
          </div>
        </div>
      </CardHeader>

      {item.summary && (
        <CardContent className="pb-3">
          <p className="text-sm text-muted-foreground line-clamp-2">
            {item.summary}
          </p>
        </CardContent>
      )}

      <CardFooter className="gap-1 flex-wrap">
        {item.author && (
          <span className="text-xs text-muted-foreground mr-2">
            by {item.author}
          </span>
        )}

        {item.topic_tags.slice(0, 3).map((tag) => (
          <Badge key={tag} variant="outline" className="text-xs">
            {tag}
          </Badge>
        ))}

        <div className="ml-auto flex items-center gap-1">
          {item.engagement_score > 0 && (
            <span className="text-xs text-muted-foreground mr-2">
              ⭐ {item.engagement_score.toLocaleString()}
            </span>
          )}

          <Button
            variant="ghost"
            size="icon"
            className={item.feedback === "up" ? "text-green-600" : ""}
            onClick={() => onFeedback?.(item.id, "up")}
          >
            <ThumbsUp className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className={item.feedback === "down" ? "text-red-600" : ""}
            onClick={() => onFeedback?.(item.id, "down")}
          >
            <ThumbsDown className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => onToggleSave?.(item.id, !item.is_saved)}
          >
            {item.is_saved ? (
              <BookmarkCheck className="h-4 w-4 text-primary" />
            ) : (
              <Bookmark className="h-4 w-4" />
            )}
          </Button>
          <a
            href={item.original_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center h-9 w-9 rounded-md hover:bg-accent hover:text-accent-foreground"
          >
            <ExternalLink className="h-4 w-4" />
          </a>
        </div>
      </CardFooter>
    </Card>
  )
}
