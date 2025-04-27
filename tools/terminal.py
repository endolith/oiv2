from tools.tools import function_tool, ToolRegistry
from conversation import Message

@function_tool
def shell(command: str) -> Message:
    __doc__ = "Runs shell commands. Make sure you only run commands suitable for the user's native shell environment."
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
    
@function_tool
def print_tool(message: str) -> Message:
    __doc__ = "Prints a message to the terminal"
    print(message)
    return Message(
        role="tool",
        message=f"Printed: {message}"
    )
    
@function_tool
def list_tools() -> Message:
    __doc__ = "List all available tools"
    return Message(
        role="tool",
        message=f"Available tools: \n{ToolRegistry.get_all_tools()}"
    )