import logging
from typing import Optional, Final
from dataclasses import dataclass

from ..engine import Engine
from ..message import Message

_logger = logging.getLogger(__name__)

SUMMARIZE_PROMPT : Final[str] = \
""" You summarize chat history. Keep all important facts, decisions, constraints,
    names, dates, and unresolved questions. Be concise.
    If the conversation is about a specific topic, include that in the summary.
    If the conversation is about a specific case, include the case name and jurisdiction in the summary
"""


def summarize_overflow( engine:Engine,
                        existing_summary: Optional[str],
                        overflow: list[Message]) -> str:
    """
    Summarize the overflow messages into a single Message that can be prepended to the context.
    If summarization fails, returns an empty string to indicate that the overflow should be kept as-is.
    """
    _logger.debug("Summarizing overflow of %d messages", len(overflow))
    _logger.debug("Existing summary: %s", bool(existing_summary))

    messages = [ Message("system",SUMMARIZE_PROMPT)]

    if existing_summary:
        messages.append(Message("user", f"Existing summary:\n{existing_summary}"))

    summary_input = collate_messages(overflow)
    messages.append(
        Message("user",
                "Merge and compress the following older conversation turns into a short summary:\n"\
                f"{summary_input.content}")
    )
    summary_text :str = engine.run_messages(messages).strip()

    if not summary_text:
        _logger.warning("Received empty overflow summary")

    return summary_text




def collate_messages(overflow: list[Message]) -> Message:
    """
    Build a compact summary Message from overflow messages.
    """
    summary_lines: list[str] = []
    for message in overflow:
        summary_lines.append(f"{message.role}: {message.content}")

    summary = "\n".join(summary_lines)
    return Message(role="system", content=f"Conversation summary:\n{summary}")







