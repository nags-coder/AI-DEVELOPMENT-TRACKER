import { useQuery } from "@tanstack/react-query"
import { apiFetch } from "@/lib/api"
import type { ContentItem, FeedParams, FeedResponse, MustReadResponse, Source } from "@/types/api"

export function useFeed(params: FeedParams = {}) {
  const searchParams = new URLSearchParams()
  if (params.page) searchParams.set("page", String(params.page))
  if (params.per_page) searchParams.set("per_page", String(params.per_page))
  if (params.source) searchParams.set("source", params.source)
  if (params.content_type) searchParams.set("content_type", params.content_type)
  if (params.time_range) searchParams.set("time_range", params.time_range)
  if (params.search) searchParams.set("search", params.search)
  if (params.sort_by) searchParams.set("sort_by", params.sort_by)

  const qs = searchParams.toString()
  const path = qs ? `/feed?${qs}` : "/feed"

  return useQuery<FeedResponse>({
    queryKey: ["feed", params],
    queryFn: () => apiFetch<FeedResponse>(path),
  })
}

export function useMustRead() {
  return useQuery<MustReadResponse>({
    queryKey: ["must-read"],
    queryFn: () => apiFetch<MustReadResponse>("/feed/must-read"),
  })
}

export function useSources() {
  return useQuery<Source[]>({
    queryKey: ["sources"],
    queryFn: () => apiFetch<Source[]>("/sources"),
  })
}

export async function submitFeedback(contentId: number, action: "up" | "down"): Promise<ContentItem> {
  return apiFetch<ContentItem>(`/content/${contentId}/feedback`, {
    method: "POST",
    body: JSON.stringify({ action }),
  })
}

export async function toggleSave(contentId: number, save: boolean): Promise<ContentItem> {
  return apiFetch<ContentItem>(`/content/${contentId}/save`, {
    method: save ? "POST" : "DELETE",
  })
}
