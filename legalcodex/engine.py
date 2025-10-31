"""
Represent an abstract AI API
"""
import logging
from typing import Optional, Literal, List, Dict
from abc import ABC, abstractmethod

from openai import OpenAI

from openai.types.chat.chat_completion import ChatCompletion, Choice
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionSystemMessageParam



from ._config import Config


_logger = logging.getLogger(__name__)

SYSTEM_PROMPT :str = "You are a sarcastic assistant. Please answer in a sarcastic tone, but with helpful answers."

Role    = Literal["system", "user", "assistant", "tool"]
Message = Dict[str, str]


class Engine(ABC):


    @abstractmethod
    def run(self, prompt:str)->str:
        """
        Run the engine with the given prompt and return the response.
        """
        pass


class OpenAIEngine(Engine):
    """
    An abstract AI engine interface.
    """

    #typing only
    _config:Config
    _client : Optional[OpenAI]

    def __init__(self, config :Optional[Config] )->None:
        """
        Initialize the Engine with the given configuration.
        """
        self._config = config if config is not None else Config()
        self._client = None

    @property
    def client(self)->OpenAI:
        """
        Get the OpenAI client, initializing it if necessary.
        """
        if self._client is None:
            self._client = OpenAI(api_key=self._config.api_key)
        return self._client



    def run(self, prompt:str)->str:
        """
        """
        _logger.debug("Running prompt: %s", prompt)
        messages = self.build_messages(prompt)

        response = self.client.chat.completions.create(
            model=self._config.model,
            messages=messages
        )

        completion :ChatCompletion= response
        for choice in completion.choices:
            _logger.debug("Choice: %s", choice)

        content = response.choices[0].message.content
        if content is None:
            raise ValueError("No content in response")
        return content

    def build_messages(self, prompt:str)->List[ChatCompletionMessageParam]:
        """
        Build a message dictionary for the chat completion.
        """
        return [  _message("system", SYSTEM_PROMPT),
                  _message("user",   prompt),
        ]


def _message(role:Role, content:str)->ChatCompletionMessageParam:
    """
    Create a message dictionary for the chat completion.
    """
    return {"role": role, "content": content} #type: ignore