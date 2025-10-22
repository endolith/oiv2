import json
from typing import Dict, List
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    message: str

class Conversation(BaseModel):
    messages: List[Message]

    def get_messages(self) -> List[Dict]:
        """Convert messages to OpenAI format, filtering out tool messages."""
        # Filter out tool messages to avoid OpenAI API issues
        # Tool results will be included in the next assistant message instead
        filtered_messages = [msg for msg in self.messages if msg.role != "tool"]

        return [{
            "role": msg.role,
            "content": msg.message
        } for msg in filtered_messages]

    def save(self, filename: str):
        with open(filename, "w") as f: json.dump([msg.model_dump() for msg in self.messages], f)

    def load(self, filename: str):
        with open(filename, "r") as f: self.messages = [Message(**msg) for msg in json.load(f)]