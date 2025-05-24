import os
from typing import Optional
from ..cli_utils import Text
from .tools import function_tool
from ..conversation import Message

@function_tool
def shell(command: str) -> Message:
    """Runs shell commands. Make sure you only run commands suitable for the user's native shell environment."""
    import subprocess
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout or result.stderr or "Command executed successfully with no output"
    except Exception:
        output = "Command failed to execute"
    finally:
        return Message(
            role="tool", 
            message=f"{command}\n{output}"
        )