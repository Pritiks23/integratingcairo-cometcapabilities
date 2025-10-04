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

## NewsAPI
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

## OpenWeatherAPI
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

## Pinterest API
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

## Calendly API
class CalendlyInput(BaseModel):
    user_email: str = Field(description="Email of the Calendly user to fetch events for")

def get_calendly_events(user_email: str) -> Any:
    url = f"https://api.calendly.com/scheduled_events"
    headers = {"Authorization": f"Bearer {settings.calendly_key}"}
    params = {"user": user_email, "count": 5}
    with httpx.Client(timeout=10) as client:
        r = client.get(url, headers=headers, params=params)
        r.raise_for_status()
        return r.json()

calendly_tool = StructuredTool(
    name="get_calendly_events",
    description="Fetch upcoming Calendly events for a user",
    func=get_calendly_events,
    args_schema=CalendlyInput,
)

## Pixabay API
class PixabayInput(BaseModel):
    query: str = Field(description="Search term for images")
    per_page: int = Field(default=5, description="Number of images to return")

def search_pixabay(query: str, per_page: int = 5) -> Any:
    url = "https://pixabay.com/api/"
    params = {"q": query, "key": settings.pixabay_key, "per_page": per_page}
    with httpx.Client(timeout=10) as client:
        r = client.get(url, params=params)
        r.raise_for_status()
        return r.json()

pixabay_tool = StructuredTool(
    name="search_pixabay",
    description="Search for images on Pixabay",
    func=search_pixabay,
    args_schema=PixabayInput,
)

## TMDB API (Movies)
class TMDBInput(BaseModel):
    query: str = Field(description="Search term for movies")
    limit: int = Field(default=5, description="Number of results")

def search_tmdb(query: str, limit: int = 5) -> Any:
    url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": settings.tmdb_key, "query": query, "page": 1}
    with httpx.Client(timeout=10) as client:
        r = client.get(url, params=params)
        r.raise_for_status()
        return r.json().get("results", [])[:limit]

tmdb_tool = StructuredTool(
    name="search_tmdb",
    description="Search movies on TMDB",
    func=search_tmdb,
    args_schema=TMDBInput,
)

## CoinGecko API
class CryptoInput(BaseModel):
    coin: str = Field(description="Cryptocurrency name/id")

def get_crypto_price(coin: str) -> Any:
    url = f"https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": coin, "vs_currencies": "usd"}
    with httpx.Client(timeout=10) as client:
        r = client.get(url, params=params)
        r.raise_for_status()
        return r.json()

crypto_tool = StructuredTool(
    name="get_crypto_price",
    description="Get current price of a cryptocurrency from CoinGecko",
    func=get_crypto_price,
    args_schema=CryptoInput,
)

## JokeAPI
class JokeInput(BaseModel):
    category: str = Field(default="Any", description="Category of jokes")

def get_joke(category: str = "Any") -> Any:
    url = f"https://v2.jokeapi.dev/joke/{category}"
    with httpx.Client(timeout=10) as client:
        r = client.get(url)
        r.raise_for_status()
        return r.json()

joke_tool = StructuredTool(
    name="get_joke",
    description="Get a random joke from JokeAPI",
    func=get_joke,
    args_schema=JokeInput,
)

## Dictionary API
class WordInput(BaseModel):
    word: str = Field(description="Word to look up")

def define_word(word: str) -> Any:
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    with httpx.Client(timeout=10) as client:
        r = client.get(url)
        r.raise_for_status()
        return r.json()

dictionary_tool = StructuredTool(
    name="define_word",
    description="Get word definitions from Dictionary API",
    func=define_word,
    args_schema=WordInput,
)

## Quotes API
class QuoteInput(BaseModel):
    category: str = Field(default="", description="Category of quotes (optional)")

def get_quote(category: str = "") -> Any:
    url = "https://api.quotable.io/random"
    params = {"tags": category} if category else {}
    with httpx.Client(timeout=10) as client:
        r = client.get(url, params=params)
        r.raise_for_status()
        return r.json()

quote_tool = StructuredTool(
    name="get_quote",
    description="Fetch a random quote",
    func=get_quote,
    args_schema=QuoteInput,
)



