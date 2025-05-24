from tools.tools import function_tool
from conversation import Message

@function_tool
def print_tool(message: str) -> Message:
    """Prints a message to the terminal. Formats escape characters"""
    print(message)
    return Message(
        role="tool",
        message=f"Printed: {message}"
    )