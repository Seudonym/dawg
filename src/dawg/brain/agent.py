import logging
from typing import Literal, TypedDict
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam


logger = logging.getLogger(__name__)


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
        response = self.client.chat.completions.create(
            model="local-model", messages=self.messages
        )

        reply = response.choices[0].message.content or ""
        self.messages.append({"role": "assistant", "content": reply})

        return reply
