"""
Represent an abstract AI API
"""
from __future__ import annotations
import os
import logging
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Final, Optional, Iterator, cast, Generator

from openai import OpenAI, RateLimitError

from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat import ChatCompletionMessageParam

from ...exceptions import LCException, QuotaExceeded
from ..._misc import log_timer
from ..._environ import LC_API_KEY

from ..engine import Engine
from ..context import Context
from ..message import Message
from ..stream import Stream

_logger = logging.getLogger(__name__)

class OpenAIEngine(Engine):
    """
    An abstract AI engine interface.
    """
    NAME : Final[str]  = "openai"

    #typing only
    _client         : Optional[OpenAI] = None
    _token_counter  : Optional[TokenCounter] = None

    @property
    def client(self)->OpenAI:
        """
        Get the OpenAI client, initializing it if necessary.
        """
        if self._client is None:
            api_key:str = _get_api_key()
            self._client = OpenAI(api_key=api_key)
        return self._client


    def run_messages_stream(self, context: Context) -> Stream:
        with _handle_exceptions():
            messages = _context_to_messages(context)

            with log_timer("OpenAI streaming response"):
                stream = cast(
                    Iterator[object],
                    self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        stream=True,
                    ),
                )
            #self.token_counter.add_tokens(stream) # type: ignore
            return _OpenAIStream(stream, self.token_counter)

    @property
    def token_counter(self)->TokenCounter:
        if self._token_counter is None:
            self._token_counter = TokenCounter()
        return self._token_counter

def _context_to_messages(context:Context)->list[ChatCompletionMessageParam]:
    """
    Convert a Context to a list of ChatCompletionMessageParam.
    """
    return [
        _message(message) for message in context
    ]

def _message(message:Message)->ChatCompletionMessageParam:
    """
    Create a message dictionary for the chat completion.
    """
    return {"role":     message.role,
            "content":  message.content} #type: ignore





class _OpenAIStream(Stream):
    def __init__(self, stream: Iterator[object], token_counter: TokenCounter)->None:
        self._stream = stream
        self._token_counter = token_counter

    def __iter__(self)->Iterator[str]:
        with _handle_exceptions():
            for chunk in self._stream:
                choices = getattr(chunk, "choices", None)
                if not choices:
                    continue

                delta = getattr(choices[0], "delta", None)
                if delta is None:
                    continue

                content = getattr(delta, "content", None)
                if content:
                    yield content
        self._token_counter.add_tokens(self._stream) # type: ignore

class TokenCounter:
    def __init__(self) -> None:
        self.total = TokenCount()

    def add_tokens(self, response:ChatCompletion) -> None:
        count = _token_count(response)
        self.total += count
        count.log_usage(logging.DEBUG)

    def log_usage(self, log_level:int) -> None:
        self.total.log_usage(log_level)




@dataclass
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

@contextmanager
def _handle_exceptions()->Generator[None, None, None]:
    try:
        yield
    except RateLimitError:
        _logger.exception("API quota exceeded")
        raise QuotaExceeded() from None
    except LCException:
        raise
    except Exception as e:
        _logger.exception("OpenAI request failed")
        raise LCException("The AI request failed. Please try again.") from e



def _get_api_key()-> str:
    key = os.environ.get(LC_API_KEY)
    if not key:
        raise LCException(f"API key not found. Please set the {LC_API_KEY} environment variable.")
    return key

