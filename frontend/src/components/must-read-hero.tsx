import { Sparkles } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { formatDate } from "@/lib/utils"
import type { ContentItem } from "@/types/api"

interface MustReadHeroProps {
  item: ContentItem | null
  message: string
}

export function MustReadHero({ item, message }: MustReadHeroProps) {
  if (!item) {
    return (
      <Card className="border-primary/20 bg-primary/5">
        <CardContent className="p-6 text-center text-muted-foreground">
          {message}
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border-primary/20 bg-gradient-to-r from-primary/5 to-primary/10">
      <CardHeader>
        <div className="flex items-center gap-2 mb-1">
          <Sparkles className="h-5 w-5 text-primary" />
          <span className="text-sm font-medium text-primary">Today's Must-Read</span>
        </div>
        <CardTitle className="text-xl">
          <a
            href={item.original_url}
            target="_blank"
            rel="noopener noreferrer"
            className="hover:underline"
          >
            {item.title}
          </a>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {item.summary && (
          <p className="text-sm text-muted-foreground mb-3">{item.summary}</p>
        )}
        <div className="flex items-center gap-2 flex-wrap">
          <Badge variant="secondary">{item.content_type}</Badge>
          <span className="text-xs text-muted-foreground">{item.source.name}</span>
          {item.author && (
            <span className="text-xs text-muted-foreground">by {item.author}</span>
          )}
          <span className="text-xs text-muted-foreground">
            {formatDate(item.published_at)}
          </span>
          <span className="text-xs font-mono text-primary ml-auto">
            Score: {(parseFloat(item.relevance_score) * 100).toFixed(0)}%
          </span>
        </div>
      </CardContent>
    </Card>
  )
}
