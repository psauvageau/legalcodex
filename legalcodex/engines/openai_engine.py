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
    _token_counter : Optional[TokenCounter] = None

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
                model=self.model,
                messages=messages,
            )
            self.token_counter.add_tokens(response)

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

    @property
    def token_counter(self)->TokenCounter:
        if self._token_counter is None:
            self._token_counter = TokenCounter()
        return self._token_counter

    def close(self)->None:
        """
        Clean up any resources used by the engine.
        Override this method if your engine needs to do any cleanup.
        """
        if self._token_counter is not None:
            _logger.info("Total token usage for this session:")
            self._token_counter.log_usage(logging.INFO)

def _message(message:Message)->ChatCompletionMessageParam:
    """
    Create a message dictionary for the chat completion.
    """
    return {"role":     message.role,
            "content":  message.content} #type: ignore

class TokenCounter:
    def __init__(self) -> None:
        self.total = TokenCount()

    def add_tokens(self, response:ChatCompletion) -> None:
        count = _token_count(response)
        self.total += count
        count.log_usage(logging.DEBUG)

    def log_usage(self, log_level:int) -> None:
        self.total.log_usage(log_level)




@dataclass()
class TokenCount:
    prompt_tokens:      int = 0
    completion_tokens:  int = 0
    total_tokens:       int = 0

    def __add__(self, other:TokenCount)->TokenCount:
        return TokenCount(
            prompt_tokens = self.prompt_tokens + other.prompt_tokens,
            completion_tokens = self.completion_tokens + other.completion_tokens,
            total_tokens = self.total_tokens + other.total_tokens
        )

    def log_usage(self, log_level:int) -> None:
        _logger.log(log_level,"Usage:")
        _logger.log(log_level,f"  Prompt:     {self.prompt_tokens}")
        _logger.log(log_level,f"  Completion: {self.completion_tokens}")
        _logger.log(log_level,f"  Total:      {self.total_tokens}")

def _token_count(response:ChatCompletion)->TokenCount:
    usage = getattr(response, "usage", None)
    if usage is None:
        return TokenCount()

    return TokenCount(
        prompt_tokens = usage.prompt_tokens or 0,
        completion_tokens = usage.completion_tokens or 0,
        total_tokens = usage.total_tokens or 0
    )

