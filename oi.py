from tools.tools import function_tool, ToolRegistry
from typing import List, Dict
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
            for i, msg in enumerate(self.messages)
        ]
    
@function_tool
def bash(command: str) -> Message:
    import subprocess
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return Message(
        role="user", 
        message=result.stdout or result.stderr or "Command executed successfully with no output", 
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
                result = ToolRegistry.dispatch(tool_call)
                self.messages.messages.append(result)
        if response.choices[0].message.content:
            self.messages.messages.append(
                Message(
                    role="assistant", 
                    message=response.choices[0].message.content, 
                    summary=""
                ))
        
def main():
    interpreter = Interpreter()
    interpreter.messages.messages = [
        Message(role="system", message="You are a helpful assistant.", summary="")
    ]
    while True:
        user_input = input("Enter a message: ")
        if user_input == "exit":
            break
        interpreter.messages.messages.append(
            Message(role="user", message=user_input, summary="")
        )
        interpreter.respond()
        print(interpreter.messages.messages[-1].message)

if __name__ == "__main__":
    main()