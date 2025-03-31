import os
import json
import asyncio
import colorama

from cli_utils import Text
from tools.tools import function_tool, ToolRegistry
from typing import List, Dict, Optional
from litellm import acompletion, completion
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    message: str
    summary: str = ""

    async def generate_summary(self) -> str:
        #print("Generating summary...")
        result = await acompletion(
            model="openai/local",
            base_url="http://localhost:1234/v1",
            api_key="dummy",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes messages. Summary must be a single sentence."},
                {"role": "user", "content": self.message},
            ],
            max_tokens=100,
        )
        return result.choices[0].message.content

    def model_post_init(self, __context) -> None:
        asyncio.create_task(self._update_summary())

    async def _update_summary(self):
        self.summary = await self.generate_summary()

class Conversation(BaseModel):
    messages: List[Message]
    max_recent: int

    def get_messages(self) -> List[Dict]:
        return [{
            "role": msg.role, 
            "content": msg.message if i < self.max_recent or msg.role.lower() == "system" else msg.summary}
            for i, msg in enumerate(self.messages[::-1])][::-1]

    def save(self, filename: str):
        with open(filename, "w") as f: json.dump([msg.model_dump() for msg in self.messages], f)

    def load(self, filename: str):
        with open(filename, "r") as f: self.messages = [Message(**msg) for msg in json.load(f)]

@function_tool
def unix_bash(command: str) -> Message:
    """Runs Bash commands on Unix-like systems."""
    import subprocess
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout or result.stderr or "Command executed successfully with no output"
    return Message(
        role="tool",
        message=f"{os.getcwd()}$ {command}\n{output}",
        summary="",
    )

@function_tool
def windows_cmd(command: str) -> Message:
    """Runs Windows CMD commands."""
    import subprocess
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout or result.stderr or "Command executed successfully with no output"
    return Message(
        role="tool",
        message=output,
        summary="",
    )

@function_tool
def get_operating_system() -> Message:
    """Returns the current operating system."""
    import platform
    return Message(
        role="tool",
        message=f"The OS is {platform.platform(terse=True)}",
        summary="",
    )

@function_tool
def user_input(prompt: Optional[str]) -> Message:
    if prompt:
        print(prompt)
    text = input(Text(text="You: ", color="blue"))
    return Message(role="user", message=text, summary="")

class Interpreter:
    def __init__(self, model: str = "openai/local"):
        self.model = model
        # Create a conversation with an initial system message.
        self.conversation = Conversation(messages=[Message(role="system",message=(
                        "You are a helpful tool calling assistant. Use tools to help the user. "
                        "If you need more information, run get_operating_system and wait for its output. "
                        "Do not run getter tools more than once per session."
                    ),summary="",)], max_recent=10)

    async def respond(self):
        # Await the completion call
        response = await acompletion(
            model=self.model,
            base_url="http://localhost:1234/v1",
            api_key="dummy",
            messages=self.conversation.get_messages(),
            max_tokens=1000,
            tools=ToolRegistry.get_all_tools(),
        )
        msg_resp = response.choices[0].message

        # Process any tool calls from the response
        if msg_resp.tool_calls:
            for tool_call in msg_resp.tool_calls:
                tool_result = ToolRegistry.dispatch(tool_call)
                if not isinstance(tool_result, Message):
                    tool_result = Message(role="tool", message="Tool call failed", summary="")
                self.conversation.messages.append(tool_result)
                print(Text(text="Tool: ", color="red"), tool_result.message)
        # Process assistant message content
        if msg_resp.content:
            assistant_msg = Message(
                role="assistant",
                message=msg_resp.content.rstrip("\n"),
                summary="",
            )
            self.conversation.messages.append(assistant_msg)
            print(Text(text="Assistant: ", color="green"), assistant_msg.message)
            self.conversation.messages.append(user_input(""))

    async def run(self):
        # Get initial user input in async context
        initial_text = input(Text(text="Enter a message: ", color="blue"))
        self.conversation.messages.append(
            Message(role="user", message=initial_text, summary="")
        )
        # Main loop – await asynchronous responses
        while True:
            await self.respond()

async def main():
    colorama.init()
    interpreter = Interpreter()
    await interpreter.run()

if __name__ == "__main__":
    asyncio.run(main())
