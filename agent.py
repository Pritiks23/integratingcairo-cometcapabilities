from __future__ import annotations
from typing import Optional, List
from deepagents import create_deep_agent
from langchain_core.runnables import Runnable
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

from .policy import guard_tools

CAIRO_SYSTEM_INSTRUCTIONS = """
You are CAIRO - ColomboAI In-App Reactive Operator - an in-app, fully context-aware, autonomy-enabled agent for the ColomboAI ecosystem (GenAI, Feed, CAIRO, News, Generative Shop).

Mandatory restrictions (NON-NEGOTIABLE):
- You MUST NOT like, auto-like, comment, or auto-comment on posts.
- When acting on social or public surfaces, only read, summarize, plan, draft, schedule (with confirmation), or recommend. Never publish externally without explicit confirmation.
- Log all recommendation engine and integration actions and summarize the rationale for review.
- Explain and justify every autonomous or persistent action to users/humans.

General guidance:
- Maximize cross-app orchestration: Payments (Stripe), email/calendar (Gmail, SMTP/IMAP, Google, Outlook), news, mapping, and general webapps.
- Use long-term memory and short-term context threading for deeply integrated, proactive workflows.
- Take small, reversible steps and always explain impacts and choices.
- Provide concise, structured answers and source all web findings.
- Write a short plan for each complex prompt before action.
- Always show tool/action logs at the end of each operation for transparency.
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
        # Add any additional tools as needed
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



