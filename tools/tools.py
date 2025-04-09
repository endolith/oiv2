from typing import Dict, Any, Callable, Type
from pydantic import BaseModel
import inspect
import json
from typing import get_type_hints

class Tool(BaseModel):
    type: str = "function"
    function: Dict[str, Any]
    func: Callable

    def __call__(self, *args, **kwargs): return self.func(*args, **kwargs)

class ToolRegistry:
    _tools: Dict[str, Tool] = {}
    _TYPE_MAP: Dict[Type, str] = {
        str: "string", int: "integer", float: "number", 
        bool: "boolean", list: "array", dict: "object"
    }

    @classmethod
    def register(cls, func: Callable) -> Tool:
        params = {n: p for n, p in inspect.signature(func).parameters.items() 
                 if n not in ('self', 'cls')}
        hints = get_type_hints(func)
        
        tool = Tool(
            function={
                "name": func.__name__,
                "description": func.__doc__ or f"Function {func.__name__}",
                "parameters": {
                    "type": "object",
                    "properties": {
                        n: {
                            "type": cls._TYPE_MAP.get(hints.get(n, str), "string"),
                            "description": f"{n} parameter"
                        } for n in params
                    },
                    "required": [n for n, p in params.items() 
                               if p.default == inspect.Parameter.empty]
                }
            },
            func=func
        )
        cls._tools[func.__name__] = tool
        return tool

    @classmethod
    def get_all_tools(cls) -> Dict[str, Dict[str, str]]: 
        return {
            name: {
                param: "input"  # Simplified to just show it needs input
                for param in tool.function['parameters']['properties']
            }
            for name, tool in cls._tools.items()
        }

    @classmethod
    def dispatch(cls, call: Dict[str, Any]) -> Any:
        try:
            tool_name = call["function"]["name"]
            args = json.loads(call["function"]["arguments"]) if isinstance(call["function"]["arguments"], str) else call["function"]["arguments"]
            return cls._tools.get(tool_name, lambda **_: f"Tool {tool_name} not found")(**args)
        except Exception as e:
            return f"Error executing tool {tool_name}: {str(e)}"

function_tool = ToolRegistry.register