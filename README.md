# legalcodex

LegalCodex is a LLM-based layer assistant that is specialized in searching through a large library of documents and answer with both an summary of the relevant information and the relevant references.

The user will interact with legalcodex through a conversational "chat" like interface.

## Architecture requirement: AI API agnostic

- All LegalCodex application logic must remain AI API agnostic.
- Application logic must not rely on provider-specific features from any single LLM API.
- All interaction with an LLM must go through the `Engine` abstract base class in `legalcodex/engine.py`.
- `legalcodex/engines/openai_engine.py` provides the current concrete implementation of `Engine`.
- This abstraction is required so another LLM API can be adopted later with minimal changes.

