import os
import json
import asyncio
import subprocess
import colorama
import platform
from typing import List, Dict, Optional
from litellm import acompletion
from cli_utils import Text
from tools.tools import function_tool, ToolRegistry
from conversation import Message, Conversation
from tools.terminal import user_input
from structured import ReasonResponse, ToolResponse, CompletedResponse

class Interpreter:
    def __init__(self, model: str = "openai/local"):
        self.model = model
        self.conversation = Conversation(messages=[Message(role="system",message=(
            f"""You are a helpful tool calling assistant that can run code. Use code field to run python, bash, shell.
            Users Operating System is: {platform.platform(terse=True)}. Available tools: {ToolRegistry.get_all_tools()}"""
            ),summary="",)], max_recent=10)

    async def respond(self, response_format):
        response = await acompletion(
            model=self.model,
            base_url="http://localhost:1234/v1",
            api_key="dummy",
            messages=self.conversation.get_messages(),
            max_tokens=1000,
            response_format=response_format,
        )
        msg_resp = response.choices[0].message
        print(Text(text="Debug - Raw response: ", color="yellow"), msg_resp.content)
        return response_format(**json.loads(msg_resp.content))

    async def run(self):
        initial_text = input(Text(text="Enter a message: ", color="blue"))
        self.conversation.messages.append(
            Message(role="user", message=initial_text, summary=initial_text)
        )

        while True:
            response = await self.respond()
            print(response)

async def main():
    colorama.init()
    interpreter = Interpreter()
    await interpreter.run()

if __name__ == "__main__":
    asyncio.run(main())
