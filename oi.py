import os
import json
import asyncio
import colorama
import platform
from typing import List, Dict, Optional
from litellm import acompletion
from cli_utils import Text
from tools.tools import function_tool, ToolRegistry
from conversation import Message, Conversation
from tools.terminal import user_input

class Interpreter:
    def __init__(self, model: str = "openai/local"):
        self.model = model
        self.conversation = Conversation(messages=[Message(role="system",message=(
            f"""You are a helpful tool calling assistant. Use tools to help the user. 
            Users Operating System is: {platform.platform(terse=True)}"""
            ),summary="",)], max_recent=10)

    async def respond(self):
        response = await acompletion(
            model=self.model,
            base_url="http://localhost:1234/v1",
            api_key="dummy",
            messages=self.conversation.get_messages(),
            max_tokens=1000,
            tools=ToolRegistry.get_all_tools(),
        )
        msg_resp = response.choices[0].message

        if msg_resp.tool_calls:
            for tool_call in msg_resp.tool_calls:
                tool_result = ToolRegistry.dispatch(tool_call)
                tool_result.tool_call_id = tool_call.id
                tool_result.name = tool_call.function.name
                if not isinstance(tool_result, Message):
                    tool_result = Message(role="tool", message="Tool call failed", summary="", tool_call_id=tool_call.id, name=tool_call.function.name)
                self.conversation.messages.append(tool_result)
                print(Text(text="Tool: ", color="red"), tool_result.message)
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
        initial_text = input(Text(text="Enter a message: ", color="blue"))
        self.conversation.messages.append(
            Message(role="user", message=initial_text, summary="")
        )

        while True:
            await self.respond()

async def main():
    colorama.init()
    interpreter = Interpreter()
    await interpreter.run()

if __name__ == "__main__":
    asyncio.run(main())
