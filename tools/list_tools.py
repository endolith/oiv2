from tools.tools import function_tool
from conversation import Message
from tools.tools import ToolRegistry


@function_tool
def list_tools() -> Message:
    """List all available tools"""
    return Message(
        role="tool",
        message=f"Available tools: \n{ToolRegistry.get_all_tools()}"
    )