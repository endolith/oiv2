import asyncio, json
from .cli_utils import Text
from .oi import Interpreter
from .conversation import Message
from .structured import TaggedResponse
from .tools.tools import ToolRegistry
from .tools import screen, input, jupyter, files

async def main():
    interpreter = Interpreter()
    
    while True:
        if not interpreter.conversation.messages or interpreter.conversation.messages[-1].role != "tool":
            user_input = input(Text(text="You: ", color="blue"))
            interpreter.conversation.messages.append(Message(role="user", message=user_input))
        
        print(Text(text="Assistant: ", color="green"), end="")
        message = ""
        async for content in interpreter.respond(response_format=None):
            print(content, end="", flush=True)
            message += content
        print()
        
        response = TaggedResponse(message)
        interpreter.conversation.messages.append(Message(role="assistant", message=message))
        
        if response.tool_call and response.tool_call.tool.lower() != "none":
            tool_result = ToolRegistry.dispatch({"function": {"name": response.tool_call.tool, "arguments": json.dumps(response.tool_call.tool_args)}})
            print("\n" + Text(text="Tool: ", color="yellow"), tool_result.message if hasattr(tool_result, 'message') else str(tool_result))
            interpreter.conversation.messages.append(tool_result)

if __name__ == "__main__":
    import colorama; colorama.init(); asyncio.run(main())