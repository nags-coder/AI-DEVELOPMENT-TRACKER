/** TypeScript types matching the backend Pydantic schemas. */

export interface SourceBrief {
  id: number
  name: string
  category: string
}

export interface ContentItem {
  id: number
  title: string
  summary: string | null
  original_url: string
  author: string | null
  published_at: string | null
  content_type: string
  thumbnail_url: string | null
  topic_tags: string[]
  relevance_score: string
  engagement_score: number
  is_read: boolean
  is_saved: boolean
  feedback: string | null
  source: SourceBrief
}

export interface PaginationMeta {
  page: number
  per_page: number
  total: number
  total_pages: number
}

export interface PaginatedResponse<T> {
  data: T[]
  meta: PaginationMeta
}

export interface MustReadResponse {
  item: ContentItem | null
  message: string
}

export interface Source {
  id: number
  name: string
  category: string
  base_url: string
  source_type: string
  priority: number
  status: string
  user_rating: number | null
  quality_score: string
  added_at: string
  last_checked: string | null
  notes: string | null
}

export type FeedResponse = PaginatedResponse<ContentItem>

export interface FeedParams {
  page?: number
  per_page?: number
  source?: string
  content_type?: string
  time_range?: "today" | "7d" | "30d" | "all"
  search?: string
  sort_by?: "date" | "relevance"
}
