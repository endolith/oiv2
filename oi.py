import asyncio
import json
import os
import platform
import subprocess
from typing import Dict, List, Optional

import colorama
from litellm import acompletion

from cli_utils import Text
from conversation import Conversation, Message
from structured import ReasonResponse, ToolResponse
from tools.terminal import user_input
from tools.tools import ToolRegistry

class Interpreter:
    def __init__(self, model: str = "openai/local"):
        self.model = model
        self.conversation = Conversation(messages=[Message(role="system",message=(
            f"""You are a helpful tool calling assistant that can run code. 
            Step by step reasoning is required.
            Always as step 1 gather information.
            No placeholders are allowed.
            Users Operating System is: {platform.platform(terse=True)}. 
            Available tools: {ToolRegistry.get_all_tools()}"""
            ),summary="",)], max_recent=10)

    async def respond(self, response_format):
        response = await acompletion(
            model=self.model,
            base_url="http://localhost:1234/v1",
            api_key="dummy",
            messages=self.conversation.get_messages(),
            max_tokens=1000,
            response_format=response_format,
            temperature=0.0,
        )
        msg_resp = response.choices[0].message
        #print(Text(text="Debug - Raw response: ", color="yellow"), msg_resp.content)
        return response_format(**json.loads(msg_resp.content))

    async def run(self):
        initial_text = input(Text(text="You: ", color="blue"))
        self.conversation.messages.append(Message(role="user", message=initial_text))

        while True:            
            response = await self.respond(ReasonResponse)
            print(Text(text="Assistant: ", color="green"), response.reasoning)
            self.conversation.messages.append(response.to_message())
            if response.tool_response:
                tool_result = ToolRegistry.dispatch({
                    "function": {
                        "name": response.tool_response.tool,
                        "arguments": json.dumps(response.tool_response.tool_args)
                    }
                })
                print(Text(text="Tool result: ", color="yellow"), tool_result)
                self.conversation.messages.append(tool_result)
            else:
                initial_text = input(Text(text="You: ", color="blue"))
                self.conversation.messages.append(Message(role="user", message=initial_text))

async def main():
    colorama.init()
    interpreter = Interpreter()
    await interpreter.run()

if __name__ == "__main__":
    asyncio.run(main())
