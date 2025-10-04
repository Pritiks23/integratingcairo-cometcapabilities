from __future__ import annotations
from typing import Optional, List
from deepagents import create_deep_agent
from langchain_core.runnables import Runnable

# --- Load API keys from .env ---
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env in the project root

NEWS_API_KEY = os.getenv("NEWS_TOOL_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_TOOL_API_KEY")
PINTEREST_API_KEY = os.getenv("PINTEREST_TOOL_API_KEY")
CALENDLY_API_KEY = os.getenv("CALENDLY_TOOL_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_TOOL_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_TOOL_API_KEY")
CRYPTO_API_KEY = os.getenv("CRYPTO_TOOL_API_KEY")
JOKE_API_KEY = os.getenv("JOKE_TOOL_API_KEY")
DICTIONARY_API_KEY = os.getenv("DICTIONARY_TOOL_API_KEY")
QUOTE_API_KEY = os.getenv("QUOTE_TOOL_API_KEY")

# Now import your tools
from .llm import get_mc1_model
from .memory import CairoMemoryTools
from .tools.search import internet_search
from .tools.recommendation import (
    set_weights_tool,
    boost_creator_tool,
    demote_creator_tool,
    block_tag_tool,
    unblock_tag_tool,
)
# Universal integration tools
from .tools.stripe import stripe_tool
from .tools.gmail import gmail_tool
from .tools.email import email_tool
from .tools.calendar import calendar_tool
from .tools.webapp import webapp_tool
from .tools.googlemaps import google_maps_tool
from .tools.news import news_tool

from .tools.weather import weather_tool
from .tools.pinterest import pinterest_tool
from .tools.calendly import calendly_tool
from .tools.pixabay import pixabay_tool
from .tools.tmdb import tmdb_tool
from .tools.crypto import crypto_tool
from .tools.joke import joke_tool
from .tools.dictionary import dictionary_tool
from .tools.quote import quote_tool

from .policy import guard_tools

CAIRO_SYSTEM_INSTRUCTIONS = """
... (your instructions remain the same) ...
"""

def build_cairo_agent(builtin_tools: Optional[List[str]] = None) -> Runnable:
    mem_tools = CairoMemoryTools()
    tools = [
        internet_search,
        mem_tools.add_tool,
        mem_tools.search_tool,
        mem_tools.get_all_tool,
        set_weights_tool,
        boost_creator_tool,
        demote_creator_tool,
        block_tag_tool,
        unblock_tag_tool,
        # Integration
        news_tool,
        weather_tool,
        pinterest_tool,
        calendly_tool,
        pixabay_tool,
        tmdb_tool,
        crypto_tool,
        joke_tool,
        dictionary_tool,
        quote_tool,
    ]
    tools = guard_tools(tools)  # Enforce policy: block like/comment actions
    model = get_mc1_model(temperature=0.2, max_tokens=2048)
    agent = create_deep_agent(
        tools=tools,
        instructions=CAIRO_SYSTEM_INSTRUCTIONS,
        model=model,
        builtin_tools=builtin_tools,
    )
    return agent


