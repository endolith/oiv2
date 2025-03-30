import sys, time, threading

class Spinner:
    def __enter__(self): self.start(); return self
    def __exit__(self, *_): self.stop()
    def __init__(self, msg="", frames=['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏'], delay=0.1, color=None):
        self.msg, self.frames, self.delay = msg, frames, delay
        self.running, self._done = False, threading.Event()
        self._colors = {'black':30, 'red':31, 'green':32, 'yellow':33, 'blue':34, 'magenta':35, 'cyan':36, 'white':37,
                        'bright_black':90, 'bright_red':91, 'bright_green':92, 'bright_yellow':93, 
                        'bright_blue':94, 'bright_magenta':95, 'bright_cyan':96, 'bright_white':97}
        self._color = f"\033[{self._colors.get(color, 0)}m" if color else ""
        self._reset = "\033[0m" if color else ""
    def start(self):
        if self.running: return
        self.running, i = True, 0
        self._done.clear(); sys.stdout.write('\033[?25l')
        def spin():
            nonlocal i
            while self.running:
                sys.stdout.write(f"\r{self._color}{self.frames[i%len(self.frames)]}{self._reset} {self.msg}")
                sys.stdout.flush(); time.sleep(self.delay); i += 1
            sys.stdout.write(f"\r{' '*(len(self.msg)+2)}\r\033[?25h"); sys.stdout.flush()
            self._done.set()
        threading.Thread(target=spin, daemon=True).start()
    def stop(self): 
        if not self.running: return
        self.running = False; self._done.wait(timeout=0.5)

class Text:
    _colors = {'black':30, 'red':31, 'green':32, 'yellow':33, 'blue':34, 'magenta':35, 'cyan':36, 'white':37,
               'bright_black':90, 'bright_red':91, 'bright_green':92, 'bright_yellow':93, 
               'bright_blue':94, 'bright_magenta':95, 'bright_cyan':96, 'bright_white':97}
    _bg = {'black':40, 'red':41, 'green':42, 'yellow':43, 'blue':44, 'magenta':45, 'cyan':46, 'white':47,
           'bright_black':100, 'bright_red':101, 'bright_green':102, 'bright_yellow':103, 
           'bright_blue':104, 'bright_magenta':105, 'bright_cyan':106, 'bright_white':107}
    _styles = {'bold':1, 'dim':2, 'italic':3, 'underline':4, 'blink':5, 'reverse':7, 'strike':9}
    for color in _colors: locals()[color] = classmethod(lambda cls, text, c=color: cls(text, color=c))
    for style in _styles: locals()[style] = classmethod(lambda cls, text, s=style, color=None: cls(text, color=color, style=s))
    del color, style
    def __init__(self, text="", color=None, bg=None, style=None):
        self.text = text
        self.fmt = []
        if color in self._colors: self.fmt.append(str(self._colors[color]))
        if bg in self._bg: self.fmt.append(str(self._bg[bg]))
        if style in self._styles: self.fmt.append(str(self._styles[style]))
    
    def __str__(self): return f"\033[{';'.join(self.fmt)}m{self.text}\033[0m" if self.fmt else self.text
    def __repr__(self): return self.__str__()
    def __add__(self, other): return str(self) + str(other)
    def __radd__(self, other): return str(other) + str(self)
    def __len__(self): return len(self.text)