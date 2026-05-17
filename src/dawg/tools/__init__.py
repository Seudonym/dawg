from typing import Any, Callable
from openai.types.chat import ChatCompletionToolParam

from dawg.tools.shell import list_files


TOOLS: list[ChatCompletionToolParam] = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories at a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "The directory to look in",
                    },
                },
                "required": ["directory"],
            },
        },
    }
]

TOOL_REGISTRY: dict[str, Callable[..., Any]] = {"list_files": list_files}

__all__ = ["TOOLS", "TOOL_REGISTRY"]
