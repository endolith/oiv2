from pydantic import BaseModel, Field
from typing import Literal, Optional, Union, Dict

class ToolResponse(BaseModel):
    type: Literal["tool"] = Field("tool", description="The type of the response")
    tool: str = Field(..., description="The tool to use")
    tool_args: dict = Field(..., description="The arguments to pass to the tool")

class CompletedResponse(BaseModel):
    type: Literal["completed"] = Field("completed", description="The type of the response")
    final_result: str = Field(..., description="The final result of the operation")

class ReasonResponse(BaseModel):
    type: Literal["reason"] = Field("reason", description="The type of the response")
    reasoning: Dict[str, str] = Field(..., description="The reasoning behind the response")
    next_response_type: Optional[Literal["tool", "reason", "completed"]] = Field(None, description="The type of the next response")
