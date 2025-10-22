import asyncio, json, argparse
from .cli_utils import Text, Spinner
from .oi import Interpreter
from .conversation import Message
from .structured import TaggedResponse
from .tools.tools import ToolRegistry

# Save builtin input before tools import
builtin_input = input

def confirm_tool(tool_name, tool_args):
    """Simple y/n confirmation for tool execution."""
    print(f"Execute {tool_name}({tool_args})? (y/n): ", end="")
    return builtin_input().lower().startswith('y')

def execute_tool_with_confirmation(tool_call, unsafe=False):
    """Execute a tool with user confirmation."""
    if not unsafe and not confirm_tool(tool_call.tool, tool_call.tool_args):
        return None
        
    return ToolRegistry.dispatch({
        "function": {
            "name": tool_call.tool, 
            "arguments": json.dumps(tool_call.tool_args)
        }
    })

async def async_main(raw_mode=False, unsafe=False):
    # Import all tools to register them
    from .tools import screen, jupyter, files, input, list_tools, python_runner, terminal
    
    interpreter = Interpreter()
    
    try:
        while True:
            # Get user input if the last message wasn't from a tool
            if not interpreter.conversation.messages or interpreter.conversation.messages[-1].role != "tool":
                user_input = builtin_input(Text(text="You: ", color="blue"))
                interpreter.conversation.messages.append(Message(role="user", message=user_input))
            
            print(Text(text="Assistant: ", color="green"), end="")
            
            # Get agent response
            message = ""
            if raw_mode:
                # Raw mode: stream tokens directly as they come
                async for content in interpreter.respond(response_format=None):
                    print(content, end="", flush=True)
                    message += content
                print()  # New line after response
            else:
                # Normal mode: show spinner while collecting response
                with Spinner("Thinking...", color="yellow") as spinner:
                    async for content in interpreter.respond(response_format=None):
                        message += content
            
            response = TaggedResponse(message)
            interpreter.conversation.messages.append(Message(role="assistant", message=message))
            
            # Show message if present (only in normal mode, raw mode already showed everything)
            if not raw_mode and response.message and response.message.strip():
                print(response.message)
            
            # Execute tool(s) if present
            tools_executed = False
            
            # Handle multiple tool calls
            if hasattr(response, 'tool_calls') and response.tool_calls:
                for tool_call in response.tool_calls:
                    if tool_call.tool.lower() != "none":
                        tool_result = execute_tool_with_confirmation(tool_call, unsafe)
                        if tool_result:
                            tool_output = tool_result.message if hasattr(tool_result, 'message') else str(tool_result)
                            print(Text(text="🔧 ", color="cyan") + Text(text=f"{tool_call.tool}: ", color="cyan") + tool_output)
                            interpreter.conversation.messages.append(tool_result)
                            tools_executed = True
            
            # Handle single tool call
            elif response.tool_call and response.tool_call.tool.lower() != "none":
                tool_result = execute_tool_with_confirmation(response.tool_call, unsafe)
                if tool_result:
                    # Tool was executed
                    tool_output = tool_result.message if hasattr(tool_result, 'message') else str(tool_result)
                    print(Text(text="🔧 ", color="cyan") + Text(text=f"{response.tool_call.tool}: ", color="cyan") + tool_output)
                    interpreter.conversation.messages.append(tool_result)
                    tools_executed = True
                else:
                    # User declined or tool failed
                    decline_msg = Message(role="tool", message=f"Tool {response.tool_call.tool} was not executed")
                    interpreter.conversation.messages.append(decline_msg)
                    print(Text(text="❌ ", color="red") + f"Skipped {response.tool_call.tool}")
                    tools_executed = True  # Still continue the loop to let AI respond
            
            # Continue loop if tools were executed to let agent see results
            if tools_executed:
                continue
                
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        return

def main():
    parser = argparse.ArgumentParser(description="OIV2 AI Assistant")
    parser.add_argument("--raw", action="store_true", help="Show raw token stream instead of parsed output")
    parser.add_argument("--unsafe", action="store_true", help="Skip tool execution confirmations")
    args = parser.parse_args()
    
    import colorama
    colorama.init()
    asyncio.run(async_main(raw_mode=args.raw, unsafe=args.unsafe))

if __name__ == "__main__":
    main()