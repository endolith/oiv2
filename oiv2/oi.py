import platform, locale, os
from litellm import acompletion
from .conversation import Conversation, Message
from .tools.tools import ToolRegistry

def get_system_message():
    return f"""You are a helpful tool calling assistant.

Use XML tags to structure responses:
<think>Your reasoning about what to do next</think>
<tool_name>tool_name</tool_name>
<tool_args>{{"arg": "value"}}</tool_args>
<message>Your response to the user if needed</message>

Flow:
- Think about what you need to do
- Use tools when you need information
- Provide messages to help the user
- Continue the conversation naturally

You decide what to do based on the situation:
- Need info? Use tools
- Got results? Explain them
- Bad results? Try again differently
- User unclear? Ask for clarification
- Ready to answer? Provide final response

OS: {platform.platform(terse=True)} | Locale: {locale.getlocale()[0]} | Current folder: {os.getcwd()}
Tools: {ToolRegistry.get_all_tools()}"""

class Interpreter:
    def __init__(self, model: str = None):
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()

        # Determine model and configuration
        self.model = model or os.getenv("OIV2_MODEL", "gpt-3.5-turbo")
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OIV2_BASE_URL")

        # If no API key is set, default to local model
        if not self.api_key:
            self.model = "openai/local"
            self.base_url = "http://localhost:1234/v1"
            self.api_key = "dummy"
            print("⚠️  No OPENAI_API_KEY found. Using local model (localhost:1234)")
            print("   Set OPENAI_API_KEY in .env file to use OpenAI API")

        self.conversation = Conversation(messages=[Message(role="system", message=get_system_message())])

    async def respond(self, response_format=None):
        # Prepare completion parameters
        completion_params = {
            "model": self.model,
            "messages": self.conversation.get_messages(),
            "max_tokens": 1000,
            "temperature": 0.0,
            "stream": True
        }

        # Add API key and base URL if using OpenAI
        if self.api_key != "dummy":
            completion_params["api_key"] = self.api_key
        if self.base_url:
            completion_params["base_url"] = self.base_url

        response = await acompletion(**completion_params)
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content