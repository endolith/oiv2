from tools.tools import function_tool
from conversation import Message
from typing import Optional
from cli_utils import Text

@function_tool
def user_input(prompt: Optional[str]) -> Message:
    """Prompts the user for input."""
    if prompt:
        print(prompt)
    text = input(Text(text="You: ", color="blue"))
    return Message(role="tool", message="User: " + text, summary="") 