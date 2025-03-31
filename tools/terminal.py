import os
import subprocess
import platform
from typing import Optional
from pydantic import BaseModel
from cli_utils import Text
from tools.tools import function_tool
from conversation import Message

@function_tool
def shell(command: str) -> Message:
    __doc__ = "Runs shell commands. Make sure you only run commands suitable for the user's native shell environment."
    import subprocess
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return Message(
        role="user", 
        message=result.stdout or result.stderr or "Command executed successfully with no output", 
        summary=f'Assistant executed the shell function with the command `{command}`'
    )

@function_tool
def user_input(prompt: Optional[str]) -> Message:
    if prompt:
        print(prompt)
    text = input(Text(text="You: ", color="blue"))
    return Message(role="user", message=text, summary="") 

@function_tool
def read_file(file_path: str, line_start: int, line_end: int) -> Message:
    __doc__ = "Reads a range of lines from a file."
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()[line_start:line_end + 1]
            file_content = {f"Line: {i}": f"{line}" for i, line in enumerate(lines, start=line_start)}
            return Message(
                role="user",
                message=str(file_content),
                summary=f"Read lines {line_start}-{line_end} from {file_path}"
            )
    except Exception as e:
        return Message(role="user", message=str(e), summary=f"Error reading {file_path}")
    
@function_tool
def edit_line(file_path: str, line: int, content: str) -> Message:
    __doc__ = "Edits a range of lines in a file. Make sure you only edit files suitable for the user's native shell environment."
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
            lines[line] = content
            with open(file_path, "w") as file:
                file.writelines(lines)
    except Exception as e:
        return Message(role="user", message=str(e), summary=f"Error editing {file_path}")