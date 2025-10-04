from __future__ import annotations
from typing import Dict, Any
import httpx
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from ..config import settings

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

set_weights_tool = StructuredTool(
    name="set_recommendation_weights",
    description="Control the recommendation engine feature weights",
    func=set_recommendation_weights,
    args_schema=SetWeightsInput,
)
boost_creator_tool = StructuredTool(
    name="boost_creator",
    description="Temporarily boost a creator's content in recommendations",
    func=boost_creator,
    args_schema=BoostCreatorInput,
)
demote_creator_tool = StructuredTool(
    name="demote_creator",
    description="Temporarily demote a creator's content in recommendations",
    func=demote_creator,
    args_schema=DemoteCreatorInput,
)
block_tag_tool = StructuredTool(
    name="block_tag",
    description="Block a content tag/category from recommendations",
    func=block_tag,
    args_schema=BlockTagInput,
)
unblock_tag_tool = StructuredTool(
    name="unblock_tag",
    description="Unblock a content tag/category in recommendations",
    func=unblock_tag,
    args_schema=UnblockTagInput,
)
