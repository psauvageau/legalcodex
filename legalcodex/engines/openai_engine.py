"""
Represent an abstract AI API
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Final, Optional

from openai import OpenAI, RateLimitError

from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat import ChatCompletionMessageParam

from ..engine import Engine
from ..context import Context
from ..message import Message
from ..exceptions import LCException, QuotaExceeded


_logger = logging.getLogger(__name__)






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


    def run_messages(self, context: Context) -> str:
        try:
            messages: list[ChatCompletionMessageParam] = [
                _message(message) for message in context
                ]

            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
            )

            completion: ChatCompletion = response
            for choice in completion.choices:
                _logger.debug("Choice: %s", choice)

            content = response.choices[0].message.content
            if content is None:
                raise LCException("Model returned an empty response")

            return content
        except RateLimitError:
            _logger.exception("API quota exceeded")
            raise QuotaExceeded(self.NAME) from None
        except LCException:
            raise
        except Exception as e:
            _logger.exception("OpenAI request failed")
            raise LCException("The AI request failed. Please try again.") from e





def _message(message:Message)->ChatCompletionMessageParam:
    """
    Create a message dictionary for the chat completion.
    """
    return {"role":     message.role,
            "content":  message.content} #type: ignore