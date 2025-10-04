from __future__ import annotations
from typing import Dict, Any
import httpx
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from ..config import settings

# ------------------ Existing Recommendation Tools ------------------ #

class SetWeightsInput(BaseModel):
    weights: Dict[str, float] = Field(description="Feature weights, e.g. {'freshness':0.4,'similarity':0.3,'novelty':0.3}")

class BoostCreatorInput(BaseModel):
    creator_id: str = Field(description="Creator/user ID to boost")
    factor: float = Field(ge=0.0, le=10.0, description="Boost factor, 0 disables, 1 no change, >1 boosts")

class DemoteCreatorInput(BaseModel):
    creator_id: str = Field(description="Creator/user ID to demote")
    factor: float = Field(ge=0.0, le=10.0, description="Demotion factor, 0 disables, 1 no change, >1 demotes")

class BlockTagInput(BaseModel):
    tag: str = Field(description="Content tag/category to block")

class UnblockTagInput(BaseModel):
    tag: str = Field(description="Content tag/category to unblock")

def _post(path: str, payload: Dict[str, Any]) -> Any:
    base = settings.rec_engine_url.rstrip("/")
    headers = {}
    if settings.rec_api_key:
        headers["Authorization"] = f"Bearer {settings.rec_api_key}"
    with httpx.Client(timeout=15) as client:
        r = client.post(f"{base}{path}", json=payload, headers=headers)
        r.raise_for_status()
        return r.json()

def set_recommendation_weights(weights: Dict[str, float]) -> Any:
    return _post("/api/control/set_weights", {"weights": weights})

def boost_creator(creator_id: str, factor: float) -> Any:
    return _post("/api/control/boost_creator", {"creator_id": creator_id, "factor": factor})

def demote_creator(creator_id: str, factor: float) -> Any:
    return _post("/api/control/demote_creator", {"creator_id": creator_id, "factor": factor})

def block_tag(tag: str) -> Any:
    return _post("/api/control/block_tag", {"tag": tag})

def unblock_tag(tag: str) -> Any:
    return _post("/api/control/unblock_tag", {"tag": tag})

# ------------------ External API Tools ------------------ #

# Example 1: News API
class NewsInput(BaseModel):
    query: str = Field(description="Search term for news articles")
    page_size: int = Field(default=5, description="Number of articles to return")

def fetch_news(query: str, page_size: int = 5) -> Any:
    url = "https://newsapi.org/v2/everything"
    params = {"q": query, "pageSize": page_size, "apiKey": settings.newsapi_key}
    with httpx.Client(timeout=10) as client:
        r = client.get(url, params=params)
        r.raise_for_status()
        return r.json()

news_tool = StructuredTool(
    name="fetch_news",
    description="Fetch latest news articles from NewsAPI",
    func=fetch_news,
    args_schema=NewsInput,
)

# Example 2: OpenWeather API
class WeatherInput(BaseModel):
    city: str = Field(description="City to get weather for")

def get_weather(city: str) -> Any:
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": settings.openweather_key, "units": "metric"}
    with httpx.Client(timeout=10) as client:
        r = client.get(url, params=params)
        r.raise_for_status()
        return r.json()

weather_tool = StructuredTool(
    name="get_weather",
    description="Get current weather for a city from OpenWeather API",
    func=get_weather,
    args_schema=WeatherInput,
)

# Example 3: Pinterest Search (Free tier using unofficial API)
class PinterestInput(BaseModel):
    query: str = Field(description="Search term for Pinterest pins")
    limit: int = Field(default=5, description="Number of pins to return")

def search_pinterest(query: str, limit: int = 5) -> Any:
    url = "https://api.pinterest.com/v5/search/pins"
    headers = {"Authorization": f"Bearer {settings.pinterest_key}"}
    params = {"query": query, "page_size": limit}
    with httpx.Client(timeout=10) as client:
        r = client.get(url, params=params, headers=headers)
        r.raise_for_status()
        return r.json()

pinterest_tool = StructuredTool(
    name="search_pinterest",
    description="Search Pinterest pins",
    func=search_pinterest,
    args_schema=PinterestInput,
)



