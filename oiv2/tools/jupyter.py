import io, sys, contextlib, subprocess, importlib.util
from .tools import function_tool
from ..conversation import Message

class Jupyter:
    def __init__(self): self.g, self.l, self.pkgs = {"__name__": "__main__"}, {}, set()
    
    def install(self, pkgs):
        new = [p for p in pkgs if p not in self.pkgs]
        if new: subprocess.check_call([sys.executable, "-m", "pip", "install"] + new); self.pkgs.update(new)
    
    def run(self, code):
        out, err = io.StringIO(), io.StringIO()
        try:
            imports = [l.split()[1].split('.')[0] for l in code.split('\n') if l.strip().startswith(('import ', 'from '))]
            missing = [p for p in imports if not importlib.util.find_spec(p)]
            if missing: self.install(missing)
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err): exec(code, self.g, self.l)
            self.g.update(self.l)
            return out.getvalue() or err.getvalue() or "OK", "success"
        except Exception as e: return f"Error: {e}", "error"

j = Jupyter()

@function_tool
def python_exec(code: str) -> Message:
    print(f"\n{code}\nRun? (y/n): ", end="")
    if input().lower() not in {'y', 'yes'}: return Message(role="tool", message="Cancelled")
    result, status = j.run(code)
    return Message(role="tool", message=f"```python\n{code}\n```\n{result}")

@function_tool
def python_vars() -> Message:
    vars_info = [f"{k}: {type(v).__name__} = {str(v)[:50]}" for k, v in j.g.items() if not k.startswith('_')]
    return Message(role="tool", message="\n".join(vars_info) or "No variables")

@function_tool
def python_reset() -> Message:
    global j; j = Jupyter(); return Message(role="tool", message="Session reset")