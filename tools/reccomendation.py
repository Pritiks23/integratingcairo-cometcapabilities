from __future__ import annotations
from typing import Dict, Any, List
import httpx
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from ..config import settings

# --- Input models ---
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

# Tools input
class StripeInput(BaseModel):
    amount: float
    currency: str = "usd"
    customer_id: str

class GmailInput(BaseModel):
    recipient: str
    subject: str
    body: str

class EmailInput(BaseModel):
    recipient: str
    subject: str
    body: str

class CalendarInput(BaseModel):
    event_name: str
    start_time: str
    end_time: str
    attendees: List[str] = []

class WebAppInput(BaseModel):
    url: str
    action: str

class GoogleMapsInput(BaseModel):
    location: str

class NewsInput(BaseModel):
    query: str
    max_results: int = 5

# --- Internal rec engine helper ---
def _post(path: str, payload: Dict[str, Any]) -> Any:
    base = settings.rec_engine_url.rstrip("/")
    headers = {}
    if settings.rec_api_key:
        headers["Authorization"] = f"Bearer {settings.rec_api_key}"
    with httpx.Client(timeout=15) as client:
        r = client.post(f"{base}{path}", json=payload, headers=headers)
        r.raise_for_status()
        return r.json()

# --- MCP (multi-tool control platform) helper ---
def _post_mcp(tool: str, payload: Dict[str, Any]) -> Any:
    mcp_url = getattr(settings, "mcp_url", None)
    if not mcp_url:
        raise RuntimeError("Set settings.mcp_url to your MCP platform URL.")
    with httpx.Client(timeout=20) as client:
        r = client.post(f"{mcp_url}/{tool}", json=payload)
        r.raise_for_status()
        return r.json()

# --- Recommendation functions ---
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

# --- External tools via MCP ---
def stripe_tool(amount: float, currency: str, customer_id: str) -> Any:
    return _post_mcp("stripe", {"amount": amount, "currency": currency, "customer_id": customer_id})

def gmail_tool(recipient: str, subject: str, body: str) -> Any:
    return _post_mcp("gmail", {"recipient": recipient, "subject": subject, "body": body})

def email_tool(recipient: str, subject: str, body: str) -> Any:
    return _post_mcp("email", {"recipient": recipient, "subject": subject, "body": body})

def calendar_tool(event_name: str, start_time: str, end_time: str, attendees: List[str]) -> Any:
    return _post_mcp("calendar", {"event_name": event_name, "start_time": start_time, "end_time": end_time, "attendees": attendees})

def webapp_tool(url: str, action: str) -> Any:
    return _post_mcp("webapp", {"url": url, "action": action})

def google_maps_tool(location: str) -> Any:
    return _post_mcp("google_maps", {"location": location})

def news_tool(query: str, max_results: int = 5) -> Any:
    return _post_mcp("news", {"query": query, "max_results": max_results})

# --- StructuredTools ---
set_weights_tool = StructuredTool("set_recommendation_weights", "Control rec engine weights", set_recommendation_weights, SetWeightsInput)
boost_creator_tool = StructuredTool("boost_creator", "Boost creator content", boost_creator, BoostCreatorInput)
demote_creator_tool = StructuredTool("demote_creator", "Demote creator content", demote_creator, DemoteCreatorInput)
block_tag_tool = StructuredTool("block_tag", "Block content tag", block_tag, BlockTagInput)
unblock_tag_tool = StructuredTool("unblock_tag", "Unblock content tag", unblock_tag, UnblockTagInput)
stripe_tool_struct = StructuredTool("stripe_tool", "Stripe payment (via MCP)", stripe_tool, StripeInput)
gmail_tool_struct = StructuredTool("gmail_tool", "Send Gmail (via MCP)", gmail_tool, GmailInput)
email_tool_struct = StructuredTool("email_tool", "Send email (via MCP)", email_tool, EmailInput)
calendar_tool_struct = StructuredTool("calendar_tool", "Manage calendar events (via MCP)", calendar_tool, CalendarInput)
webapp_tool_struct = StructuredTool("webapp_tool", "Interact with web apps (via MCP)", webapp_tool, WebAppInput)
google_maps_tool_struct = StructuredTool("google_maps_tool", "Query Google Maps (via MCP)", google_maps_tool, GoogleMapsInput)
news_tool_struct = StructuredTool("news_tool", "Search news (via MCP)", news_tool, NewsInput)
