import platform
from litellm import acompletion

from conversation import Conversation, Message
from structured import ReasonResponse
from tools.tools import ToolRegistry
import locale

class Interpreter:
    def __init__(self, model: str = "openai/local"):
        self.model = model
        self.conversation = Conversation(messages=[Message(role="system",message=(
            f"""You are a helpful tool calling assistant that can run code. 
            Step by step reasoning is required.
            Step 1: Explore the environment and gather information, and then proceed to the next step.
            No placeholders are allowed.
            User's Operating System is: {platform.platform(terse=True)}.
            The native locale is: {locale.getlocale()[0]}. 
            Available tools you can use: {ToolRegistry.get_all_tools()}"""
            ))], max_recent=10)

    async def respond(self, response_format):
        response = await acompletion(
            model=self.model,
            base_url="http://localhost:1234/v1",
            api_key="dummy",
            messages=self.conversation.get_messages(),
            max_tokens=1000,
            response_format=response_format,
            temperature=0.0,
            stream=True
        )
        
        async for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                yield content
