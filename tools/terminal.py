import os
import subprocess
import platform
from typing import Optional
from pydantic import BaseModel
from cli_utils import Text
from tools.tools import function_tool
from conversation import Message

@function_tool
def unix_bash(command: str) -> Message:
    """Runs Bash commands on Unix-like systems."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout or result.stderr or "Command executed successfully with no output"
    return Message(
        role="tool",
        message=f"{os.getcwd()}$ {command}\n{output}",
        summary="",
    )

@function_tool
def windows_cmd(command: str) -> Message:
    """Runs Windows CMD commands."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout or result.stderr or "Command executed successfully with no output"
    return Message(
        role="tool",
        message=output,
        summary="",
    )

@function_tool
def get_operating_system() -> Message:
    """Returns the current operating system."""
    return Message(
        role="tool",
        message=f"The OS is {platform.platform(terse=True)}",
        summary="",
    )

@function_tool
def user_input(prompt: Optional[str]) -> Message:
    if prompt:
        print(prompt)
    text = input(Text(text="You: ", color="blue"))
    return Message(role="user", message=text, summary="") 