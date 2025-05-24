import os, subprocess, shutil
from .tools import function_tool
from ..conversation import Message

try: import PIL.Image, PIL.ImageDraw, PIL.ImageFont
except: PIL = None

class Screen:
    def __init__(self):
        self.sys = 'wayland' if os.environ.get('WAYLAND_DISPLAY') else 'x11' if os.environ.get('DISPLAY') else 'windows' if os.name == 'nt' else 'macos' if 'darwin' in os.uname().sysname.lower() else 'unknown'
        self.region = (0, 0, 1920, 1080)
        self.grid = (4, 4)
        
    def shot(self, path="screenshot.png", region=None):
        r = region or self.region
        if self.sys == 'wayland':
            if shutil.which('grim'): subprocess.run(['grim', path] if not region else ['grim', '-g', f'{r[0]},{r[1]} {r[2]}x{r[3]}', path], check=True)
            else: subprocess.run(['gnome-screenshot', '-f', path], check=True)
        elif self.sys == 'x11':
            if shutil.which('scrot'): subprocess.run(['scrot', path] if not region else ['scrot', '-a', f'{r[0]},{r[1]},{r[2]},{r[3]}', path], check=True)
            else: subprocess.run(['import', '-window', 'root', path], check=True)
        elif self.sys == 'windows':
            import pyautogui; pyautogui.screenshot(region=r).save(path)
        
    def grid_overlay(self, path):
        if not PIL: return
        with PIL.Image.open(path) as img:
            d = PIL.ImageDraw.Draw(img)
            w, h = img.size
            gw, gh = w // self.grid[0], h // self.grid[1]
            for i in range(1, self.grid[0]): d.line([(i*gw, 0), (i*gw, h)], fill="red", width=2)
            for i in range(1, self.grid[1]): d.line([(0, i*gh), (w, i*gh)], fill="red", width=2)
            labels = [f"{'ABCDEFGH'[i//self.grid[0]]}{i%self.grid[0]+1}" for i in range(self.grid[0]*self.grid[1])]
            for i, l in enumerate(labels):
                x, y = (i%self.grid[0])*gw+10, (i//self.grid[0])*gh+10
                d.rectangle((x, y, x+30, y+20), fill="white", outline="red")
                d.text((x+2, y+2), l, fill="red")
            img.save(path)
    
    def coord(self, label): # A1 -> (x,y)
        row, col = ord(label[0])-ord('A'), int(label[1:])-1
        return (self.region[0] + col*self.region[2]//self.grid[0] + self.region[2]//(2*self.grid[0]), 
                self.region[1] + row*self.region[3]//self.grid[1] + self.region[3]//(2*self.grid[1]))
    
    def zoom(self, label): # Zoom to grid cell
        row, col = ord(label[0])-ord('A'), int(label[1:])-1
        cw, ch = self.region[2]//self.grid[0], self.region[3]//self.grid[1]
        self.region = (self.region[0]+col*cw, self.region[1]+row*ch, cw, ch)

screen = Screen()

@function_tool
def screenshot(save_path: str = "screenshot.png") -> Message:
    try:
        screen.shot(save_path)
        screen.grid_overlay(save_path)
        labels = [f"{'ABCDEFGH'[i//screen.grid[0]]}{i%screen.grid[0]+1}" for i in range(screen.grid[0]*screen.grid[1])]
        return Message(role="tool", message=f"Screenshot: {save_path} | System: {screen.sys} | Grid: {', '.join(labels)}")
    except Exception as e: return Message(role="tool", message=f"Screenshot failed: {e}")

@function_tool
def zoom_grid(label: str) -> Message:
    screen.zoom(label); return Message(role="tool", message=f"Zoomed to {label}")

@function_tool
def reset_zoom() -> Message:
    screen.region = (0, 0, 1920, 1080); return Message(role="tool", message="Reset zoom")

@function_tool
def set_grid(rows: int = 4, cols: int = 4) -> Message:
    screen.grid = (cols, rows); return Message(role="tool", message=f"Grid: {rows}x{cols}")

@function_tool
def check_system() -> Message:
    tools = {'wayland': [shutil.which('grim'), shutil.which('dotool')], 'x11': [shutil.which('scrot'), shutil.which('xdotool')], 'windows': ['pyautogui']}
    return Message(role="tool", message=f"System: {screen.sys} | Tools: {tools.get(screen.sys, [])}")