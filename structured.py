from pydantic import BaseModel, Field
from typing import Literal, Optional, Union, Dict, List
from conversation import Message

class ToolResponse(BaseModel):
    tool: str = Field(..., description="The tool to use")
    tool_args: dict = Field(..., description="The arguments to pass to the tool")

    def to_message(self) -> Message: return Message(role="tool", message=f"{self.tool} {self.tool_args}")

class ReasonResponse(BaseModel):
    reasoning: str | Dict[str, str] = Field(..., description="Use this to reason about the task. Use step by step reasoning. use markdown for formatting.")
    tool_response: Optional[ToolResponse] = Field(None, description="Call a tool if you need to. Not running a toll will prompt the user to input.")

    def to_message(self) -> Message: 
        if isinstance(self.reasoning, dict):
            message = "\n".join(f"{k}: {v}" for k, v in self.reasoning.items())
        else:
            message = str(self.reasoning)
        return Message(role="assistant", message=message)
