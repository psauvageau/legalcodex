"""
Represent an abstract AI API
"""
import logging
from typing import Optional, Literal, List, Dict, Final
from abc import ABC, abstractmethod

from openai import OpenAI, RateLimitError

from openai.types.chat.chat_completion import ChatCompletion, Choice
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionSystemMessageParam

from .._config import Config
from ..engine import Engine
from ..exceptions import LCException, QuotaExceeded


_logger = logging.getLogger(__name__)

_SYSTEM_PROMPT :str = "You are a sarcastic assistant. Please answer in a sarcastic tone, but with helpful answers."

Role    = Literal["system", "user", "assistant", "tool"]
Message = Dict[str, str]

class OpenAIEngine(Engine):
    """
    An abstract AI engine interface.
    """
    NAME : Final[str]  = "openai"

    #typing only
    _client : Optional[OpenAI] = None

    @property
    def client(self)->OpenAI:
        """
        Get the OpenAI client, initializing it if necessary.
        """
        if self._client is None:
            api_key:str = self.config.api_keys[self.NAME]
            self._client = OpenAI(api_key=api_key)
        return self._client


    def run(self, prompt:str)->str:
        """
        """
        try:
            _logger.debug("Running prompt: %s", prompt)
            messages = self.build_messages(prompt)

            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages
            )

            completion :ChatCompletion= response
            for choice in completion.choices:
                _logger.debug("Choice: %s", choice)

            content = response.choices[0].message.content
            if content is None:
                raise ValueError("No content in response")
            return content
        except RateLimitError as e:
            _logger.error("API quota exceeded: %s", e)
            raise QuotaExceeded(self.NAME) from None

    def build_messages(self, prompt:str)->List[ChatCompletionMessageParam]:
        """
        Build a message dictionary for the chat completion.
        """
        return [  _message("system", _SYSTEM_PROMPT),
                  _message("user",   prompt),
        ]


def _message(role:Role, content:str)->ChatCompletionMessageParam:
    """
    Create a message dictionary for the chat completion.
    """
    return {"role": role, "content": content} #type: ignore