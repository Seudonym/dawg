import logging
from dataclasses import dataclass
from typing import Literal
import requests

logger = logging.getLogger(__name__)

Role = Literal["system", "user", "assistant", "tool"]


@dataclass
class Message:
    role: Role
    content: str


class Agent:
    def __init__(self, system_prompt: str) -> None:
        self.messages: list[Message] = [Message(role="system", content=system_prompt)]

    def _payload(self) -> dict[str, list[dict[str, str]]]:
        return {
            "messages": [{"role": m.role, "content": m.content} for m in self.messages]
        }

    def respond(self, message: str) -> str:
        self._add_message("user", message)
        response = requests.post(
            url="http://localhost:8080/v1/chat/completions",
            json=self._payload(),
            timeout=60,
        )

        data = response.json()
        logger.info(data)

        reply = data["choices"][0]["message"]["content"]
        return reply

    def _add_message(self, role: Role, content: str) -> None:
        self.messages.append(Message(role=role, content=content))
