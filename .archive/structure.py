from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict
from enum import Enum

class ResponseType(str, Enum):
    TEXT = "text"
    CODE = "code"

class ResponseContent(BaseModel):
    type: ResponseType = Field(..., description="Type of response: text or code")
    content: str = Field(..., description="The actual response content")

class ThinkingStep(BaseModel):
    step: str = Field(..., description="A single step in the reasoning process")
    explanation: str = Field(..., description="Detailed explanation of this thinking step")

class Context(BaseModel):
    key: str = Field(..., description="Key identifier for the context")
    value: str = Field(..., description="Value or content of the context")
    description: str = Field(..., description="Description of what this context represents")

class SubPlan(BaseModel):
    id: str = Field(..., description="Unique identifier for the sub-plan")
    title: str = Field(..., description="Title or brief description of the sub-plan")
    description: str = Field(..., description="Detailed description of what this sub-plan aims to achieve")
    context_keys: List[str] = Field(default_factory=list, description="List of context keys required for this sub-plan")
    dependencies: List[str] = Field(default_factory=list, description="List of sub-plan IDs that must be completed before this one")
    estimated_time: str = Field(..., description="Estimated time to complete this sub-plan")
    priority: int = Field(default=1, description="Priority level (1 being highest)")

class Plan(BaseModel):
    id: str = Field(..., description="Unique identifier for the plan")
    title: str = Field(..., description="Title or brief description of the plan")
    description: str = Field(..., description="Detailed description of the overall plan")
    contexts: Dict[str, Context] = Field(default_factory=dict, description="Dictionary of contexts required for the plan")
    sub_plans: List[SubPlan] = Field(..., description="List of sub-plans to be executed")
    total_estimated_time: str = Field(..., description="Total estimated time for the entire plan")

class Response(BaseModel):
    quick_response: str = Field(..., description="Quick response for TTS with approximate time")
    thinking_steps: List[ThinkingStep] = Field(..., description="List of reasoning and analysis steps")
    final_response: List[ResponseContent] = Field(..., description="List of responses, each with its type and content")