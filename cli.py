import asyncio
from cli_utils import Text, Spinner
from oi import Interpreter
from conversation import Message
from structured import ReasonResponse
from tools.tools import ToolRegistry, function_tool
import tools.terminal
import json

async def main():
    interpreter = Interpreter()
    print(ToolRegistry.get_all_tools())
    
    while True:
        # Get user input only if last message wasn't a tool call
        if not interpreter.conversation.messages or interpreter.conversation.messages[-1].role != "tool":
            user_input = input(Text(text="You: ", color="blue"))
            interpreter.conversation.messages.append(Message(role="user", message=user_input))
        
        # Process response
        print(Text(text="Assistant: ", color="green"), end="")
        message = ""
        async for content in interpreter.respond(ReasonResponse):
            print(content, end="", flush=True)
            message += content
        print()
        
        response = ReasonResponse(**json.loads(message))
        if response:
            interpreter.conversation.messages.append(Message(role="assistant", message=message))
            if response.tool_call:
                tool_result = ToolRegistry.dispatch({
                    "function": {
                        "name": response.tool_call.tool,
                        "arguments": json.dumps(response.tool_call.tool_args)
                    }
                })
                print("\n" + Text(text="Tool result: ", color="yellow"), tool_result)
                interpreter.conversation.messages.append(tool_result)

if __name__ == "__main__":
    asyncio.run(main()) 