# oiv2 - Compact AI Computer Automation

AI assistant with computer automation tools designed for small local LLMs. Grid-based screen interaction, persistent Python environment, cross-platform compatibility.

## Features
- **Grid Screenshots**: A1, B2, C3 grid overlays for precise clicking
- **Persistent Python**: Jupyter-like environment with auto-package install  
- **Cross-Platform**: Wayland, X11, Windows, macOS support
- **XML Tags**: Simple response format for small LLMs
- **Compact Code**: Clean, minimal codebase

## Installation

You can install either **globally** (for quick use) or **locally** (for development).

### Global Install
```bash
uv tool install git+https://github.com/Notnaton/oiv2.git
```
This makes commands (`interpreter`, `oiv2-setup`, `oiv2-test`) available globally in `~/.local/bin`.

### Local Development Install
```bash
git clone <repo> && cd oiv2
uv sync
```
This creates a `.venv` folder inside the project.

Activate it before running commands:

**macOS/Linux**
```bash
source .venv/bin/activate
```

**Windows (PowerShell)**
```powershell
.venv\Scripts\Activate.ps1
```

Then you can run:
```bash
oiv2-setup
oiv2-test
interpreter
```

To reinstall after making code changes:
```bash
uv pip install -e .
```

### Environment Variables
For API keys or other env vars, create a `.env` file in the project root:
```
OPENAI_API_KEY=sk-xxxx
```
`python-dotenv` will automatically load it.

## Quick Start
```bash
# Check system and get setup commands if needed
oiv2-setup

# Test installation  
oiv2-test

# Launch the assistant
interpreter
```

## System Tools (Linux only)
**Wayland**: `sudo apt install grim dotool`  
**X11**: `sudo apt install scrot xdotool`  
**Windows/macOS**: No additional setup needed

## Tools
- `screenshot()` - Grid overlay screenshot
- `click_grid("A1")` - Click grid position
- `type_text("hello")` - Type text
- `press_key("enter")` - Press keys
- `python_exec("x=42")` - Run Python (persistent)
- `ls()`, `cat()`, `write()` - File operations
- `run("command")` - Shell commands

## Example
```
User: Take a screenshot and click the browser icon
AI: <thinking>Need to see screen first, then locate browser</thinking>
    <message>I'll take a screenshot to see what's available</message>
    <tool_name>screenshot</tool_name>
    <tool_args>{}</tool_args>
    
    # After seeing grid: Browser appears to be at B2
    <tool_name>click_grid</tool_name>
    <tool_args>{"label": "B2"}</tool_args>
```

## Grid System
- 4x4 default grid (A1-D4)
- Click using simple coordinates instead of "blue button top-left"
- Perfect for small LLMs that can't do complex visual reasoning
- Zoom into grid cells for detailed interaction

## Local LLM Setup
Works with any OpenAI-compatible server:
- **Ollama**: `ollama serve` (update base_url to localhost:11434)
- **LM Studio**: Usually localhost:1234 (default)
- **Text Generation WebUI**: With OpenAI extension

Best models: Code Llama 7B+, Mistral 7B+, Qwen2.5 7B+

## Commands
After installation, these commands are available globally:
- `interpreter` - Main assistant interface
- `oiv2-setup` - Check system requirements  
- `oiv2-test` - Verify installation
- `oiv2` - Alternative name for main interface

## Development
Add tools by creating files in `tools/` with `@function_tool` decorator. Tools auto-register on import.

**License**: MIT
