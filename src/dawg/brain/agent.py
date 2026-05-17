import json
import logging
from typing import Callable
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCall,
    ChatCompletionToolParam,
)


logger = logging.getLogger(__name__)


def greet(name: str) -> str:
    return json.dumps(
        {
            "greeting": "Hello there! " + name,
        },
    )


TOOLS: list[ChatCompletionToolParam] = [
    {
        "type": "function",
        "function": {
            "name": "greet",
            "description": "Greet the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the user",
                    },
                },
                "required": ["name"],
            },
        },
    }
]

TOOL_REGISTRY: dict[str, Callable[..., str]] = {"greet": greet}


class Agent:
    def __init__(self, system_prompt: str) -> None:
        self.client: OpenAI = OpenAI(
            base_url="http://localhost:8080/v1", api_key="unused"
        )
        self.messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": system_prompt}
        ]

    def respond(self, message: str) -> str:
        self.messages.append({"role": "user", "content": message})

        while True:
            response = self.client.chat.completions.create(
                model="local-model", messages=self.messages, tools=TOOLS
            )
            choice = response.choices[0]
            assistant_message: ChatCompletionAssistantMessageParam = {
                "role": "assistant",
                "content": choice.message.content,
            }

            if choice.message.tool_calls:
                assistant_message["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in choice.message.tool_calls
                    if isinstance(tc, ChatCompletionMessageToolCall)
                ]

            self.messages.append(assistant_message)

            if choice.finish_reason != "tool_calls" or not choice.message.tool_calls:
                return choice.message.content or ""

            for tc in choice.message.tool_calls:
                if not isinstance(tc, ChatCompletionMessageToolCall):
                    continue
                args = json.loads(tc.function.arguments)
                logger.info("Calling tool %s with args %s", tc.function.name, args)

                result = TOOL_REGISTRY[tc.function.name](**args)

                self.messages.append(
                    {"role": "tool", "tool_call_id": tc.id, "content": result}
                )
