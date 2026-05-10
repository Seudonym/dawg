import logging
from typing import Literal, TypedDict
import requests

logger = logging.getLogger(__name__)

Role = Literal["system", "user", "assistant", "tool"]


class ChatMessage(TypedDict):
    role: Role
    content: str


class ChatPayload(TypedDict):
    messages: list[ChatMessage]


class Choice(TypedDict):
    message: ChatMessage


class ChatCompletionResponse(TypedDict):
    choices: list[Choice]


class Agent:
    def __init__(self, system_prompt: str) -> None:
        self.session: requests.Session = requests.Session()
        self.messages: list[ChatMessage] = [
            ChatMessage(role="system", content=system_prompt)
        ]

    def _payload(self) -> ChatPayload:
        return {
            "messages": [
                {"role": m["role"], "content": m["content"]} for m in self.messages
            ]
        }

    def respond(self, message: str) -> str:
        self._add_message("user", message)

        response = self.session.post(
            url="http://localhost:8080/v1/chat/completions",
            json=self._payload(),
            timeout=60,
        )

        data: ChatCompletionResponse = response.json()
        reply = data["choices"][0]["message"]["content"]

        self._add_message("assistant", message)

        return reply

    def _add_message(self, role: Role, content: str) -> None:
        self.messages.append(ChatMessage(role=role, content=content))
