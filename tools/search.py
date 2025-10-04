import os
import httpx
from ..config import settings

def internet_search(
    query: str,
    max_results: int = 5,
    categories: str = "general",
    language: str | None = None,
    site_list: list[str] = None,
    filters: dict = None,
) -> list[dict]:
    """
    Perform an internet search using a SearxNG-compatible backend.
    Optionally restrict to specific sites or apply result filters.
    """
    base = os.getenv("SEARXNG_URL", settings.searxng_url).rstrip("/")
    params = {"q": query, "format": "json", "categories": categories, "count": max_results}
    if language:
        params["language"] = language
    if site_list:
        params["q"] = query + " " + " OR ".join(f"site:{s}" for s in site_list)
    if filters:
        params.update(filters)
    try:
        with httpx.Client(timeout=15) as client:
            r = client.get(f"{base}/search", params=params)
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        return [{"error": str(e), "query": query, "endpoint": base}]
    results = []
    for item in data.get("results", [])[:max_results]:
        results.append({
            "title": item.get("title"),
            "url": item.get("url"),
            "snippet": item.get("content"),
            "source": item.get("source"),
            "score": item.get("score"),
        })
    return results
