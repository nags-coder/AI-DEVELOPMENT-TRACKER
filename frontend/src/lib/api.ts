const API_BASE = "/api/v1"

export async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE}${path}`
  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  })

  if (!res.ok) {
    const errorBody = await res.text()
    throw new Error(`API error ${res.status}: ${errorBody}`)
  }

  return res.json() as Promise<T>
}
