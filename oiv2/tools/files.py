import os, shutil, subprocess
from pathlib import Path
from .tools import function_tool
from ..conversation import Message

@function_tool
def ls(dir: str = ".", pattern: str = "*") -> Message:
    try:
        p = Path(dir).expanduser().resolve()
        items = [f"{'DIR' if i.is_dir() else 'FILE':<4} {i.name}" for i in p.iterdir() if pattern in i.name or pattern == "*"]
        return Message(role="tool", message=f"{p}:\n" + "\n".join(sorted(items)) if items else f"Empty: {p}")
    except Exception as e: return Message(role="tool", message=f"ls failed: {e}")

@function_tool
def cat(file: str, lines: int = 50) -> Message:
    try:
        p = Path(file).expanduser().resolve()
        with open(p, 'r', encoding='utf-8', errors='ignore') as f: content = f.readlines()
        text = ''.join(content[:lines]) + (f"\n...({len(content)} total)" if len(content) > lines else "")
        return Message(role="tool", message=f"{p}:\n```\n{text}\n```")
    except Exception as e: return Message(role="tool", message=f"cat failed: {e}")

@function_tool
def write(file: str, content: str, append: bool = False) -> Message:
    try:
        p = Path(file).expanduser().resolve(); p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, 'a' if append else 'w', encoding='utf-8') as f: f.write(content)
        return Message(role="tool", message=f"{'Appended' if append else 'Wrote'} {len(content)} chars to {p}")
    except Exception as e: return Message(role="tool", message=f"write failed: {e}")

@function_tool
def cp(src: str, dst: str) -> Message:
    try:
        s, d = Path(src).expanduser().resolve(), Path(dst).expanduser().resolve()
        if s.is_dir(): shutil.copytree(s, d, dirs_exist_ok=True)
        else: d.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(s, d)
        return Message(role="tool", message=f"Copied {s} -> {d}")
    except Exception as e: return Message(role="tool", message=f"cp failed: {e}")

@function_tool
def rm(path: str) -> Message:
    try:
        p = Path(path).expanduser().resolve()
        if input(f"Delete {p}? (y/n): ").lower() not in {'y', 'yes'}: return Message(role="tool", message="Cancelled")
        shutil.rmtree(p) if p.is_dir() else p.unlink()
        return Message(role="tool", message=f"Deleted {p}")
    except Exception as e: return Message(role="tool", message=f"rm failed: {e}")

@function_tool
def find(pattern: str, dir: str = ".", max: int = 20) -> Message:
    try:
        p = Path(dir).expanduser().resolve()
        matches = [str(i.relative_to(p)) for i in list(p.rglob(pattern))[:max]]
        return Message(role="tool", message=f"Found {len(matches)}:\n" + "\n".join(matches) if matches else f"No matches for {pattern}")
    except Exception as e: return Message(role="tool", message=f"find failed: {e}")

@function_tool
def pwd() -> Message:
    return Message(role="tool", message=str(Path.cwd()))

@function_tool
def cd(dir: str) -> Message:
    try: p = Path(dir).expanduser().resolve(); os.chdir(p); return Message(role="tool", message=f"cd {p}")
    except Exception as e: return Message(role="tool", message=f"cd failed: {e}")

@function_tool
def run(cmd: str, timeout: int = 30) -> Message:
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        out = r.stdout or r.stderr or "No output"
        return Message(role="tool", message=f"$ {cmd}\n{out}\nExit: {r.returncode}")
    except subprocess.TimeoutExpired: return Message(role="tool", message=f"Timeout: {cmd}")
    except Exception as e: return Message(role="tool", message=f"run failed: {e}")