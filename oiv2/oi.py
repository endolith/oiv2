import platform, locale
from litellm import acompletion
from conversation import Conversation, Message
from tools.tools import ToolRegistry

class Interpreter:
    def __init__(self, model: str = "openai/local"):
        self.model = model
        self.conversation = Conversation(messages=[Message(role="system",message=(
            f"""You are a helpful tool calling assistant.

Use XML tags to structure responses:
<thinking>Step-by-step reasoning here</thinking>
<message>Response to user</message>

If using a tool:
<tool_name>tool_name</tool_name>
<tool_args>{{"arg": "value"}}</tool_args>

Rules: Always include thinking and message tags. Only add tool tags if needed.
OS: {platform.platform(terse=True)} | Locale: {locale.getlocale()[0]}
Tools: {ToolRegistry.get_all_tools()}"""))], max_recent=10)

    async def respond(self, response_format=None):
        response = await acompletion(model=self.model, base_url="http://localhost:1234/v1", api_key="dummy", 
                                    messages=self.conversation.get_messages(), max_tokens=1000, temperature=0.0, stream=True)
        async for chunk in response:
            if chunk.choices[0].delta.content: yield chunk.choices[0].delta.content