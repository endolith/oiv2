from pydantic import BaseModel, Field
from typing import Literal, Optional, Union, Dict, List
from conversation import Message

class ToolCall(BaseModel):
    tool: str = Field(..., description="The tool to use")
    tool_args: dict = Field(..., description="The arguments to pass to the tool")

    def to_message(self) -> Message: return Message(role="tool", message=f"{self.tool} {self.tool_args}")

class ReasonResponse(BaseModel):
    reasoning: str | Dict[str, str] = Field(..., description="Use this to reason about the task. Use step by step reasoning. use markdown for formatting.")
    message: str = Field(..., description="A message to the user. Use markdown for formatting.")
    tool_call: Optional[ToolCall] = Field(None, description="Call a tool if you need to, else return None. Not running a toll will prompt the user to input.")

    def to_message(self) -> Message: return Message(role="assistant", message=self.message)
