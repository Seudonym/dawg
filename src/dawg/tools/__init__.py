from typing import Any, Callable
from openai.types.chat import ChatCompletionToolParam

from dawg.tools.shell import list_files
from dawg.tools.files import find_files, read_file, write_file
from dawg.tools.media import (
    media_play,
    media_pause,
    media_play_pause,
    media_next,
    media_previous,
    media_stop,
)
from dawg.tools.clipboard import clipboard_read, clipboard_write
from dawg.tools.browser import open_url
from dawg.tools.notifications import notify

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
    },
    {
        "type": "function",
        "function": {
            "name": "find_files",
            "description": "Find files by regex pattern",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "The directory to look in",
                    },
                    "keyword": {
                        "type": "string",
                        "description": "Regex to use to search with",
                    },
                },
                "required": ["directory", "keyword"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute path to the file",
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file (creates directories as needed)",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute path to the file",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write",
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "media_play",
            "description": "Resume playback of current media",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "media_pause",
            "description": "Pause current media playback",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "media_play_pause",
            "description": "Toggle between play and pause",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "media_next",
            "description": "Skip to the next track",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "media_previous",
            "description": "Go back to the previous track",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "media_stop",
            "description": "Stop media playback",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "clipboard_read",
            "description": "Read text from the system clipboard",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "clipboard_write",
            "description": "Write text to the system clipboard",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to copy to clipboard",
                    },
                },
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_url",
            "description": "Open a URL in the default browser",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to open",
                    },
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "notify",
            "description": "Send a desktop notification",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Notification title",
                    },
                    "message": {
                        "type": "string",
                        "description": "Notification body text",
                    },
                    "type": {
                        "type": "string",
                        "description": "error or success status",
                    },
                },
                "required": ["title", "message"],
            },
        },
    },
]

TOOL_REGISTRY: dict[str, Callable[..., Any]] = {
    "list_files": list_files,
    "find_files": find_files,
    "read_file": read_file,
    "write_file": write_file,
    "media_play": media_play,
    "media_pause": media_pause,
    "media_play_pause": media_play_pause,
    "media_next": media_next,
    "media_previous": media_previous,
    "media_stop": media_stop,
    "clipboard_read": clipboard_read,
    "clipboard_write": clipboard_write,
    "open_url": open_url,
    "notify": notify,
}

__all__ = ["TOOLS", "TOOL_REGISTRY"]
