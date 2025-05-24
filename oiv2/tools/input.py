import subprocess, shutil, time, os
from .tools import function_tool
from ..conversation import Message

try: from .screen import screen
except: screen = None

class Input:
    def __init__(self):
        self.sys = 'wayland' if os.environ.get('WAYLAND_DISPLAY') else 'x11' if os.environ.get('DISPLAY') else 'windows' if os.name == 'nt' else 'unknown'
        
    def click(self, x, y, btn="left", n=1):
        if self.sys == 'wayland':
            if shutil.which('dotool'): [subprocess.run(['dotool', 'mousemove', str(x), str(y)]) or subprocess.run(['dotool', 'click', btn]) for _ in range(n)]
            elif shutil.which('ydotool'): subprocess.run(['ydotool', 'mousemove', str(x), str(y)]) or [subprocess.run(['ydotool', 'click', {'left':'0xC0','right':'0xC1','middle':'0xC2'}[btn]]) for _ in range(n)]
        elif self.sys == 'x11' and shutil.which('xdotool'): subprocess.run(['xdotool', 'mousemove', str(x), str(y)]) or [subprocess.run(['xdotool', 'click', {'left':'1','right':'3','middle':'2'}[btn]]) for _ in range(n)]
        elif self.sys == 'windows': import pyautogui; pyautogui.click(x, y, clicks=n, button=btn)
    
    def type(self, text, delay=0.05):
        if self.sys == 'wayland':
            if shutil.which('dotool'): subprocess.run(['dotool', 'type', text])
            elif shutil.which('wtype'): subprocess.run(['wtype', text])
            elif shutil.which('ydotool'): subprocess.run(['ydotool', 'type', text])
        elif self.sys == 'x11' and shutil.which('xdotool'): subprocess.run(['xdotool', 'type', text])
        elif self.sys == 'windows': import pyautogui; pyautogui.typewrite(text, interval=delay)
    
    def key(self, k, n=1):
        keys = {'enter':'Return','space':'space','tab':'Tab','esc':'Escape','backspace':'BackSpace','delete':'Delete','up':'Up','down':'Down','left':'Left','right':'Right','ctrl':'Control_L','alt':'Alt_L','shift':'Shift_L'}
        k = keys.get(k.lower(), k)
        if self.sys == 'wayland':
            if shutil.which('dotool'): [subprocess.run(['dotool', 'key', k]) for _ in range(n)]
            elif shutil.which('ydotool'): [subprocess.run(['ydotool', 'key', k]) for _ in range(n)]
        elif self.sys == 'x11' and shutil.which('xdotool'): [subprocess.run(['xdotool', 'key', k]) for _ in range(n)]
        elif self.sys == 'windows': import pyautogui; [pyautogui.press(k) for _ in range(n)]
    
    def combo(self, keys):
        ks = keys.split('+')
        if self.sys == 'wayland' and shutil.which('dotool'): subprocess.run(['dotool', 'key'] + ks)
        elif self.sys == 'x11' and shutil.which('xdotool'): subprocess.run(['xdotool', 'key'] + ks)
        elif self.sys == 'windows': import pyautogui; pyautogui.hotkey(*ks)

inp = Input()

@function_tool
def click_grid(label: str, button: str = "left", clicks: int = 1) -> Message:
    if not screen: return Message(role="tool", message="No screen available")
    try: x, y = screen.coord(label); inp.click(int(x), int(y), button, clicks); return Message(role="tool", message=f"Clicked {label} at ({x},{y})")
    except Exception as e: return Message(role="tool", message=f"Click failed: {e}")

@function_tool
def click_xy(x: int, y: int, button: str = "left", clicks: int = 1) -> Message:
    try: inp.click(x, y, button, clicks); return Message(role="tool", message=f"Clicked ({x},{y})")
    except Exception as e: return Message(role="tool", message=f"Click failed: {e}")

@function_tool
def type_text(text: str) -> Message:
    try: inp.type(text); return Message(role="tool", message=f"Typed: {text}")
    except Exception as e: return Message(role="tool", message=f"Type failed: {e}")

@function_tool
def press_key(key: str, times: int = 1) -> Message:
    try: inp.key(key, times); return Message(role="tool", message=f"Pressed {key} x{times}")
    except Exception as e: return Message(role="tool", message=f"Key failed: {e}")

@function_tool
def key_combo(keys: str) -> Message:
    try: inp.combo(keys); return Message(role="tool", message=f"Combo: {keys}")
    except Exception as e: return Message(role="tool", message=f"Combo failed: {e}")

@function_tool
def scroll(direction: str = "down", amount: int = 3) -> Message:
    try: inp.key("Page_Down" if direction == "down" else "Page_Up", amount); return Message(role="tool", message=f"Scrolled {direction} x{amount}")
    except Exception as e: return Message(role="tool", message=f"Scroll failed: {e}")

@function_tool
def wait(seconds: float) -> Message:
    time.sleep(seconds); return Message(role="tool", message=f"Waited {seconds}s")