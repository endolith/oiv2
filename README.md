# oiv2

## Description
The `oiv2` project is designed to facilitate structured interactions with tools using Pydantic models for validation and serialization. It leverages dependencies such as `litellm`, `openai`, `openai-agents`, and `pydantic` to provide a robust framework for managing tool calls and reasoning responses.

## Features
- **Tool Call Management**: Define and manage tool calls using the `ToolCall` model.
- **Reasoning Responses**: Structure reasoning steps and optional tool calls using the `ReasonResponse` model.
- **Dependency Management**: Utilizes UV for dependency management, ensuring a consistent environment across different systems.

## Installation
To set up the project locally, follow these steps:
1. Clone the repository:
```bash
git clone <repository_url>
cd oiv2
```
2. Install dependencies using UV:
```bash
uv sync
```
3. Run using uv:
```bash
uv run cli.py
```

## Usage
```bash
uv install git+<repository_url>
```
This will execute the main functionality of the project. You can also explore other scripts and modules to understand how tool calls and reasoning responses are managed.
