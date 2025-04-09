import asyncio
from typing import Dict, List, Optional, Literal
from pydantic import BaseModel
from litellm import acompletion

class Message(BaseModel):
    role: str
    message: str
    summary: str = ""

class Conversation(BaseModel):
    messages: List[Message]
    max_recent: int

    def get_messages(self) -> List[Dict]:
        return [{
            "role": msg.role, 
            "message": msg.message if i < self.max_recent or msg.role.lower() == "system" else msg.summary,}
            for i, msg in enumerate(self.messages[::-1])][::-1]

    def save(self, filename: str):
        import json
        with open(filename, "w") as f: json.dump([msg.model_dump() for msg in self.messages], f)

    def load(self, filename: str):
        import json
        with open(filename, "r") as f: self.messages = [Message(**msg) for msg in json.load(f)] 