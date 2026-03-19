import { useState } from "react"
import { Header } from "@/components/header"
import { MustReadHero } from "@/components/must-read-hero"
import { FeedFilters } from "@/components/feed-filters"
import { FeedList } from "@/components/feed-list"
import { useFeed, useMustRead, useSources } from "@/hooks/use-feed"
import type { FeedParams } from "@/types/api"

function App() {
  const [params, setParams] = useState<FeedParams>({
    page: 1,
    per_page: 12,
    sort_by: "date",
  })

  const feed = useFeed(params)
  const mustRead = useMustRead()
  const sources = useSources()

  const sourceNames = (sources.data ?? []).map((s) => s.name)

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />

      <main className="container mx-auto px-4 py-6 space-y-6 max-w-6xl">
        {/* Must-Read Hero */}
        <MustReadHero
          item={mustRead.data?.item ?? null}
          message={
            mustRead.isLoading
              ? "Finding today's must-read..."
              : mustRead.data?.message ?? "Check back later for your must-read."
          }
        />

        {/* Filters */}
        <FeedFilters
          params={params}
          onChange={setParams}
          sourceNames={sourceNames}
        />

        {/* Feed */}
        <FeedList
          data={feed.data}
          isLoading={feed.isLoading}
          error={feed.error}
          params={params}
          onChange={setParams}
        />
      </main>

      <footer className="border-t py-6 text-center text-sm text-muted-foreground">
        AI Pulse - Your personalized AI news feed
      </footer>
    </div>
  )
}

export default App
