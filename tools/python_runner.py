from tools.tools import function_tool
from conversation import Message

@function_tool
def python_runner(code: str) -> Message:
    __doc__ = "Runs python code."
    import subprocess
    result = exec(code)
    output = result.stdout or result.stderr or "Command executed successfully with no output"
    return Message(
        role="tool", 
        message=f"{code}\n\n{output}",
        summary=f'Assistant executed the python function with the following code:\n`{code}`'
    )