"""
Command-line based chat client that connects to a running LegalCodex HTTP API server.
Used for testing and debugging only.
"""
from __future__ import annotations

import argparse
import json
import logging
import urllib.request
import urllib.error
import http.cookiejar
from typing import Any, Final

from .cli_cmd import CliCmd
from ..exceptions import LCException

_logger = logging.getLogger(__name__)


DEFAULT_BASE_URL: Final[str] = "http://127.0.0.1:8000/api/v1"
DEFAULT_USERNAME: Final[str] = "test"
DEFAULT_PASSWORD: Final[str] = "hello"


class CommandChatRemote(CliCmd):
    title: str = "chat-remote"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--url", default=DEFAULT_BASE_URL, help="HTTP API base URL (prefix with /api/v1)")
        parser.add_argument("--username", default=DEFAULT_USERNAME, help="Username for API login")
        parser.add_argument("--password", default=DEFAULT_PASSWORD, help="Password for API login")
        parser.add_argument("--engine", default=None, help="Engine name for new sessions")
        parser.add_argument("--model", default=None, help="Model name for new sessions")
        parser.add_argument("--max-turns", type=int, default=None, help="Max messages when creating a new session")
        parser.add_argument("--session-id", default=None, help="Open a specific session id instead of creating/reusing the first available")

    def register(self, subparsers: Any) -> None:
        parser = subparsers.add_parser(self.title, help=f"{self.title} Help")
        self.add_arguments(parser)
        parser.set_defaults(command=self)

    def run(self, args: argparse.Namespace) -> None:
        client = _RemoteChatClient(args.url)
        client.login(args.username, args.password)

        session_id: str

        if args.session_id:
            client.open_session(args.session_id)
            session_id = args.session_id
        else:
            session_id = client.new_session(args.max_turns,
                                            args.engine,
                                            args.model)

        processor = _RemoteChatCommandProcessor(client, session_id)

        _write("Starting remote chat session. Type 'help' for commands.")
        try:
            while True:
                try:
                    print("=============================")
                    prompt = input("You> ").strip()
                    if not prompt:
                        _write("Please enter a message or type 'help'.")
                        continue
                    print()

                    processor.execute(prompt)

                    response_text = client.send_message(session_id, prompt)
                    _print_response(response_text)

                except CommandExecutedException:
                    continue
                except LCException as exc:
                    _write(f"Error: {exc}")
                except (KeyboardInterrupt, ExitException):
                    _write("Exiting chat session.")
                    break
        finally:
            client.close_session(session_id)
            client.close()


class _RemoteChatClient:
    _base_url: str

    def __init__(self, base_url: str):
        self._base_url = base_url.rstrip("/")
        self._cookies = http.cookiejar.CookieJar()
        self._opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self._cookies))

    def close(self) -> None:
        # Nothing to close for urllib but left for symmetry/extensibility.
        self._opener = None  # type: ignore[assignment]

    def login(self, username: str, password: str) -> None:
        _logger.info("Logging in as %s", username)
        self._post_json("/auth/login", {"username": username, "password": password}, expect_body=False)


    def open_session(self, session_id: str) -> None:
        _logger.info("Opening session %s", session_id)
        self._post_json("/chat/sessions", {"session_id": session_id}, expect_body=False)

    def close_session(self, session_id: str) -> None:
        _logger.info("Closing session %s", session_id)
        self._post_json(f"/chat/sessions/{session_id}/close", payload=None, expect_body=False)

    def new_session(self, max_messages: int | None, engine: str | None, model: str | None) -> str:
        payload = {
            "max_messages": max_messages,
            "engine": engine,
            "model": model,
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        _logger.info("Creating new session with %s", payload)
        response = self._post_json("/chat/sessions", payload)
        return response["session_id"] # type: ignore[no-any-return]



    def list_sessions(self) -> list[dict[str, Any]]:
        data =  self._get_json("/chat/sessions")
        assert isinstance(data, list), "Expected list of sessions"
        return data

    def get_context(self, session_id: str) -> dict[str, Any]:
        data = self._get_json(f"/chat/sessions/{session_id}/context")
        assert isinstance(data, dict), "Expected session context as a dict"
        return data

    def reset_context(self, session_id: str) -> None:
        self._post_json(f"/chat/sessions/{session_id}/reset", payload=None, expect_body=False)

    def send_message(self, session_id: str, message: str) -> str:
        data = self._post_json(
            f"/chat/sessions/{session_id}/messages",
            {"message": message},
        )
        return data.get("response", "") # type: ignore[no-any-return]

    def _get_json(self, path: str) -> Any:
        req = urllib.request.Request(self._build_url(path))
        return self._request(req)

    def _post_json(self, path: str, payload: Any | None, expect_body: bool = True) -> Any:
        data_bytes = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(self._build_url(path), data=data_bytes, method="POST")
        req.add_header("Content-Type", "application/json")
        return self._request(req, expect_body)

    def _request(self, req: urllib.request.Request, expect_body: bool = True) -> Any:
        try:
            with self._opener.open(req, timeout=30) as resp:
                status_code = resp.getcode()
                raw = resp.read()
        except urllib.error.HTTPError as err:
            detail = err.read().decode("utf-8", errors="ignore")
            raise LCException(f"HTTP {err.code}: {detail or err.reason}") from None
        except urllib.error.URLError as err:  # includes connection errors
            raise LCException(f"HTTP request failed: {err.reason}") from None

        if status_code >= 400:
            raise LCException(f"HTTP {status_code}: unexpected response")

        if not expect_body:
            return {}

        if not raw:
            return {}

        try:
            return json.loads(raw)
        except json.JSONDecodeError as err:
            raise LCException(f"Invalid JSON response: {err}") from None

    def _build_url(self, path: str) -> str:
        suffix = path if path.startswith("/") else f"/{path}"
        return f"{self._base_url}{suffix}"


class _RemoteChatCommandProcessor:
    _session_id: str

    def __init__(self, client: _RemoteChatClient, session_id: str) -> None:
        self._client = client
        self._session_id = session_id

        def exit_cmd() -> None:
            raise ExitException()

        def help_cmd() -> None:
            cmds = ", ".join(self._commands.keys())
            _write(f"Commands: {cmds}")

        def history_cmd() -> None:
            context = self._client.get_context(self._session_id)
            history = context.get("context", {}).get("history", [])
            for msg in history:
                role = msg.get("role", "?")
                content = msg.get("content", "")
                _write(f"{role}: {content}")
            print()

        def reset_cmd() -> None:
            self._client.reset_context(self._session_id)
            _write("Chat context reset.")

        self._commands = {
            "exit": exit_cmd,
            "quit": exit_cmd,
            "help": help_cmd,
            "history": history_cmd,
            "reset": reset_cmd,
        }

    def execute(self, prompt: str) -> None:
        command = prompt.lower()
        if command in self._commands:
            self._commands[command]()
            raise CommandExecutedException()


class CommandExecutedException(LCException):
    pass


class ExitException(Exception):
    pass


def _write(msg: str) -> None:
    _logger.info(msg)
    print(msg)
    print()


def _print_response(content: str) -> None:
    print("AI > ", end="", flush=True)
    print(content)
    _logger.info("Response: %s", content)

