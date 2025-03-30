import json
import colorama

from cli_utils import Text
from tools.tools import function_tool, ToolRegistry
from typing import List, Dict, Optional
from litellm import acompletion, completion
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    message: str
    summary: str

class Conversation(BaseModel):
    messages: List[Message]
    max_recent: int

    def get_messages(self) -> List[Dict]:
        return [{
            "role": msg.role, 
            "content": msg.message if i < self.max_recent or msg.role.lower() == "system" else msg.summary}
            for i, msg in enumerate(self.messages[::-1])
        ][::-1]

    def save(self, filename: str):
        with open(filename, "w") as f: json.dump([msg.model_dump() for msg in self.messages], f)

    def load(self, filename: str):
        with open(filename, "r") as f: self.messages = [Message(**msg) for msg in json.load(f)]
    
@function_tool
def bash(command: str) -> Message:
    import subprocess
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return Message(
        role="tool", 
        message=result.stdout or result.stderr or "Command executed successfully with no output", 
        summary=""
    )

@function_tool
def user_input(prompt: Optional[str]) -> Message:
    if prompt:
        print(prompt)
    text = input(Text(text="You: ", color="blue"))
    return Message(
        role="user",
        message=text,
        summary=""
    )

class Interpreter():
    def __init__(self, model: str = "openai/local"):
        self.model = model
        self.messages = Conversation(messages=[], max_recent=3)

    def respond(self, max_tokens: int = 1000):
        response = completion(
            model=self.model,
            base_url="http://localhost:1234/v1",
            api_key="dummy",
            messages=self.messages.get_messages(),
            max_tokens=max_tokens,
            tools=ToolRegistry.get_all_tools(),
        )
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                self.messages.messages.append(ToolRegistry.dispatch(tool_call))
                print(self.messages.messages[-1].message)
        if response.choices[0].message.content:
            self.messages.messages.append(
                Message(
                    role="assistant", 
                    message=response.choices[0].message.content, 
                    summary=""
                ))
            print(self.messages.messages[-1].message)
            self.messages.messages.append(user_input(""))
        
def main():
    interpreter = Interpreter()
    interpreter.messages.messages = [
        Message(role="system", message="You are a helpful assistant. Use tools to help the user.", summary="")
    ]
    user_input = input(Text(text="Enter a message: ", color="blue"))
    interpreter.messages.messages.append(
        Message(role="user", message=user_input, summary="")
    )
        
    while True:
        interpreter.respond()
        #print(interpreter.messages.messages[-1].message)

if __name__ == "__main__":
    colorama.init()
    main()