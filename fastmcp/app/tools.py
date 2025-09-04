import inspect
from functools import wraps
from typing import Callable, List, Dict, Any, Optional

# A simple in-memory registry for our tools
_tools = {}

def tool(name: Optional[str] = None) -> Callable:
    """
    A decorator to register a function as a tool that the AI agent can call.
    
    This decorator allows for an optional 'name' argument to avoid collisions
    when multiple tools have the same function name.
    """
    def decorator(func: Callable) -> Callable:
        # Use the provided name or default to the function's name
        tool_name = name or func.__name__
        if tool_name in _tools:
            print(f"Warning: Overwriting tool '{tool_name}'")

        description = inspect.getdoc(func)
        if not description:
            print(f"Warning: Tool '{tool_name}' has no docstring.")
            description = "No description available."

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Store the function and its description in the registry
        _tools[tool_name] = {
            "function": wrapper,
            "description": description,
            "signature": inspect.signature(func)
        }
        
        return wrapper
    return decorator

def get_tools() -> Dict[str, Any]:
    """Returns the registry of all decorated tools."""
    return _tools

def get_tool_descriptions() -> List[Dict[str, str]]:
    """Returns a list of tool names and their descriptions."""
    return [
        {"name": name, "description": data["description"], "signature": str(data["signature"])}
        for name, data in _tools.items()
    ]