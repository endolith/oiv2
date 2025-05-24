from pydantic import BaseModel, Field
from typing import Optional
from conversation import Message
import re, json

class ToolCall(BaseModel):
    tool: str = Field(..., description="The tool to use")
    tool_args: dict = Field(..., description="The arguments to pass to the tool")
    def to_message(self) -> Message: return Message(role="tool", message=f"{self.tool} {self.tool_args}")

class TaggedResponse:
    def __init__(self, raw: str):
        self.raw, self.reasoning, self.message, self.tool_call = raw, self._tag("thinking") or self._tag("reasoning") or "", self._tag("message") or raw, self._tool()
    
    def _tag(self, tag: str) -> Optional[str]:
        m = re.search(f"<{tag}>(.*?)</{tag}>", self.raw, re.DOTALL)
        return m.group(1).strip() if m else None
    
    def _tool(self) -> Optional[ToolCall]:
        name, args = self._tag("tool_name"), self._tag("tool_args")
        if not name: return None
        try: return ToolCall(tool=name, tool_args=json.loads(args) if args else {})
        except: return None
    
    def to_message(self) -> Message: return Message(role="assistant", message=self.message)