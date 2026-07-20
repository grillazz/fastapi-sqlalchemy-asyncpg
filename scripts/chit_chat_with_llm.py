#!/usr/bin/env python3
"""Interactive Rich client for the FastAPI websocket chat endpoint.

The script keeps the original websocket wire format intact while making the
manual testing experience easier to discover and safer to operate.

Examples:
    python scripts/chit_chat_with_llm.py
    python scripts/chit_chat_with_llm.py --url ws://localhost:8080/v1/chat/ws
    python scripts/chit_chat_with_llm.py --debug --system-prompt "Be concise."

Interactive commands:
    /start           Start or restart a conversation.
    /history         Show the full message history.
    /end, /quit      Gracefully close the websocket.
    /help            Show the interactive help table.
    any other text   Send text as a user message.
"""

import argparse
import asyncio
import json
import logging
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal, Protocol, TypedDict, cast

import websockets
from rich import box
from rich.console import Console, Group
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text
from rich.traceback import install as install_rich_traceback
from websockets.exceptions import ConnectionClosed, InvalidURI, WebSocketException

DEFAULT_WS_URL = "ws://localhost:8080/v1/chat/ws"
DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."

EventType = Literal[
    "connected",
    "started",
    "assistant_chunk",
    "assistant_message",
    "history",
    "error",
]
ClientMessageType = Literal["start", "user_message", "history_request", "end"]


class WebSocketLike(Protocol):
    """Minimal websocket protocol used by this client."""

    async def send(self, message: str) -> None: ...

    async def recv(self) -> str | bytes: ...


class ChatMessage(TypedDict):
    """Role/content message shape returned by the websocket API."""

    role: Literal["system", "user", "assistant"]
    content: str


class ServerEvent(TypedDict, total=False):
    """Known server event fields.

    The websocket endpoint uses a discriminated JSON shape. ``total=False``
    keeps display code resilient to malformed or future server events.
    """

    type: EventType
    session_id: str
    index: int
    content: str
    message: ChatMessage
    messages: list[ChatMessage]


@dataclass(frozen=True, slots=True)
class ChatClientConfig:
    """Runtime settings parsed from the command line."""

    url: str = DEFAULT_WS_URL
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    connect_timeout: float = 10.0
    open_on_connect: bool = False
    debug: bool = False


@dataclass(slots=True)
class ChatClientState:
    """Mutable client state for the active websocket session."""

    session_id: str | None = None
    conversation_started: bool = False
    received_chunks: int = 0


class ChatCli:
    """UX-focused websocket chat client."""

    def __init__(self, config: ChatClientConfig, console: Console) -> None:
        self.config = config
        self.console = console
        self.state = ChatClientState()

    async def run(self) -> int:
        """Connect to the websocket and start the interactive command loop."""
        self._show_welcome()

        try:
            with self._progress(f"Connecting to [bold]{self.config.url}[/bold]..."):
                websocket = await asyncio.wait_for(
                    websockets.connect(self.config.url),
                    timeout=self.config.connect_timeout,
                )

            async with websocket:
                connected_event = await self.receive_event(websocket)
                self.display_event(connected_event)

                if self.config.open_on_connect:
                    await self.start_conversation(websocket, self.config.system_prompt)

                await self.interactive_loop(websocket)
                return 0
        except TimeoutError:
            self.print_error(
                "Connection timed out.",
                f"No websocket accepted the connection within {self.config.connect_timeout:g} seconds. "
                "Check that the FastAPI server is running and reachable.",
            )
        except ConnectionRefusedError:
            self.print_error(
                "Connection refused.",
                "Start the API server first, then try again. Expected default: http://localhost:8080",
            )
        except InvalidURI as exc:
            self.print_error(
                "Invalid websocket URL.",
                f"{exc}. Use a URL such as ws://localhost:8080/v1/chat/ws.",
            )
        except ConnectionClosed as exc:
            close_code = exc.rcvd.code if exc.rcvd else exc.sent.code if exc.sent else "unknown"
            close_reason = exc.rcvd.reason if exc.rcvd else exc.sent.reason if exc.sent else "none"
            self.print_warning(
                f"The websocket closed unexpectedly (code={close_code}, reason={close_reason or 'none'})."
            )
        except KeyboardInterrupt:
            self.print_warning("Interrupted by user.")
        except WebSocketException as exc:
            self.print_error(
                "Websocket error.",
                f"{exc}. Verify the endpoint path and server logs for details.",
            )

        return 1

    async def interactive_loop(self, websocket: WebSocketLike) -> None:
        """Read commands from the terminal until the user exits."""
        self.print_info("Type [bold cyan]/help[/bold cyan] to see available commands.")

        while True:
            user_input = (await self.get_user_input("[bold green]You[/bold green] › ")).strip()

            if not user_input:
                continue

            command = user_input.casefold()
            match command:
                case "/help":
                    self.show_command_help()
                case "/start":
                    system_prompt = await self.get_user_input(
                        "[bold yellow]System prompt[/bold yellow] (Enter for default) › "
                    )
                    await self.start_conversation(websocket, system_prompt or self.config.system_prompt)
                case "/history":
                    await self.request_history(websocket)
                case "/end" | "/quit" | "/exit":
                    await self.end_conversation(websocket)
                    break
                case _:
                    await self.send_user_message(websocket, user_input)

    async def start_conversation(self, websocket: WebSocketLike, system_prompt: str) -> None:
        """Start or restart the server-side conversation history."""
        await self.send_message(websocket, {"type": "start", "system_prompt": system_prompt})
        with self._progress("Waiting for conversation acknowledgement..."):
            event = await self.receive_event(websocket)
        self.display_event(event)
        self.console.print()

    async def request_history(self, websocket: WebSocketLike) -> None:
        """Ask the server for complete message history."""
        await self.send_message(websocket, {"type": "history_request"})
        with self._progress("Loading message history..."):
            event = await self.receive_event(websocket)
        self.display_event(event)
        self.console.print()

    async def end_conversation(self, websocket: WebSocketLike) -> None:
        """Gracefully close the server-side conversation."""
        await self.send_message(websocket, {"type": "end"})
        self.print_warning("Conversation ended. Closing connection...")

    async def send_user_message(self, websocket: WebSocketLike, content: str) -> None:
        """Send one user message and stream the assistant response."""
        await self.send_message(websocket, {"type": "user_message", "content": content})
        self.console.print("[bold cyan]Assistant[/bold cyan] › ", end="")

        self.state.received_chunks = 0
        while True:
            event = await self.receive_event(websocket)
            event_type = event.get("type")
            self.display_event(event)

            if event_type == "assistant_message":
                break
            if event_type == "error":
                self.console.print()
                break
            if event_type != "assistant_chunk":
                self.print_warning(
                    f"Expected assistant_chunk or assistant_message, received {event_type!r}."
                )
                break

        self.console.print()

    async def send_message(
        self,
        websocket: WebSocketLike,
        message: Mapping[str, Any],
    ) -> None:
        """Serialize and send one client event."""
        await websocket.send(json.dumps(message))
        logging.getLogger(__name__).debug("Sent websocket event: %s", message)

    async def receive_event(self, websocket: WebSocketLike) -> ServerEvent:
        """Receive and decode one JSON server event."""
        raw_event = await websocket.recv()
        if isinstance(raw_event, bytes):
            raw_event = raw_event.decode()

        try:
            decoded = json.loads(raw_event)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Server returned invalid JSON: {raw_event!r}") from exc

        if not isinstance(decoded, dict):
            raise RuntimeError(f"Server returned a non-object event: {decoded!r}")

        logging.getLogger(__name__).debug("Received websocket event: %s", decoded)
        return cast(ServerEvent, cast(object, decoded))

    def display_event(self, event: ServerEvent) -> None:
        """Render one server event with semantic styling."""
        match event.get("type"):
            case "connected":
                self.state.session_id = event.get("session_id")
                self.print_success(f"Connected. Session ID: [bold]{self.state.session_id}[/bold]")
            case "started":
                self.state.conversation_started = True
                self.print_success(f"Conversation started. Session ID: [bold]{event.get('session_id')}[/bold]")
            case "assistant_chunk":
                self.state.received_chunks += 1
                self.console.print(event.get("content", ""), end="", soft_wrap=True)
            case "assistant_message":
                self.console.print()
                message = event.get("message", {})
                content = message.get("content", "") if isinstance(message, dict) else ""
                self.print_success(
                    f"Message complete ({self.state.received_chunks} chunk(s), {len(content)} character(s))."
                )
            case "history":
                self.render_history(event.get("messages", []))
            case "error":
                self.print_error("Server returned an error.", str(event.get("message", "Unknown error")))
            case unknown:
                self.console.print(
                    Panel.fit(
                        json.dumps(event, indent=2, default=str),
                        title=f"Unknown event: {unknown!r}",
                        border_style="yellow",
                    )
                )

    def render_history(self, messages: list[ChatMessage] | object) -> None:
        """Render conversation history as a Rich table."""
        if not isinstance(messages, list):
            self.print_warning("History response did not include a valid messages list.")
            return

        table = Table(
            title=f"Message History ({len(messages)} message(s))",
            box=box.ROUNDED,
            header_style="bold magenta",
            show_lines=True,
        )
        table.add_column("#", justify="right", style="dim", width=4)
        table.add_column("Role", style="cyan", width=12)
        table.add_column("Content", style="green", overflow="fold")

        for index, message in enumerate(messages, start=1):
            role = str(message.get("role", "unknown")) if isinstance(message, dict) else "unknown"
            content = str(message.get("content", "")) if isinstance(message, dict) else repr(message)
            table.add_row(str(index), role, content)

        self.console.print(table)

    async def get_user_input(self, prompt: str) -> str:
        """Read terminal input without blocking the event loop."""
        return await asyncio.to_thread(self.console.input, prompt)

    def show_command_help(self) -> None:
        """Display interactive command help."""
        table = Table(title="Interactive Commands", box=box.SIMPLE_HEAVY)
        table.add_column("Command", style="bold cyan", no_wrap=True)
        table.add_column("Action", style="white")
        table.add_row("/start", "Start or restart a conversation; clears server-side history.")
        table.add_row("/history", "Request and display the full role/content message history.")
        table.add_row("/end, /quit, /exit", "Gracefully close the websocket connection.")
        table.add_row("/help", "Show this help table.")
        table.add_row("any text", "Send text as a user message and stream the reply.")
        self.console.print(table)

    def _show_welcome(self) -> None:
        command_summary = Table.grid(padding=(0, 2))
        command_summary.add_column(style="bold cyan", no_wrap=True)
        command_summary.add_column(style="white")
        command_summary.add_row("Endpoint", self.config.url)
        command_summary.add_row("Default prompt", self.config.system_prompt)
        command_summary.add_row("Start mode", "auto" if self.config.open_on_connect else "manual (/start)")

        self.console.print(
            Panel(
                Group(
                    Text("FastAPI WebSocket Chat Tester", style="bold cyan"),
                    Text("Stream replies, inspect history, and validate the chat websocket UX."),
                    command_summary,
                ),
                border_style="cyan",
                padding=(1, 2),
            )
        )

    def _progress(self, message: str) -> Progress:
        """Create a compact indeterminate Rich progress spinner."""
        progress = Progress(
            SpinnerColumn(style="cyan"),
            TextColumn(message),
            TimeElapsedColumn(),
            console=self.console,
            transient=True,
        )
        progress.add_task("operation", total=None)
        return progress

    def print_info(self, message: str) -> None:
        self.console.print(f"[bold blue]ℹ[/bold blue] {message}")

    def print_success(self, message: str) -> None:
        self.console.print(f"[bold green]✓[/bold green] {message}")

    def print_warning(self, message: str) -> None:
        self.console.print(f"[bold yellow]⚠[/bold yellow] {message}")

    def print_error(self, title: str, detail: str) -> None:
        self.console.print(
            Panel(
                detail,
                title=f"[bold red]✗ {title}[/bold red]",
                border_style="red",
                expand=False,
            )
        )


def parse_args(argv: list[str] | None = None) -> ChatClientConfig:
    """Parse CLI options into a typed configuration object."""
    parser = argparse.ArgumentParser(
        description="Interactive Rich client for the FastAPI websocket chat endpoint.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_WS_URL,
        help="Websocket endpoint to connect to.",
    )
    parser.add_argument(
        "--system-prompt",
        default=DEFAULT_SYSTEM_PROMPT,
        help="Default system prompt used by /start or --start.",
    )
    parser.add_argument(
        "--connect-timeout",
        type=float,
        default=10.0,
        help="Seconds to wait while opening the websocket connection.",
    )
    parser.add_argument(
        "--start",
        action="store_true",
        dest="open_on_connect",
        help="Automatically send a start event after connecting.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable Rich-formatted debug logging and local tracebacks.",
    )

    namespace = parser.parse_args(argv)
    return ChatClientConfig(
        url=namespace.url,
        system_prompt=namespace.system_prompt,
        connect_timeout=namespace.connect_timeout,
        open_on_connect=namespace.open_on_connect,
        debug=namespace.debug,
    )


def configure_logging(debug: bool) -> None:
    """Install Rich tracebacks and configure optional debug logging."""
    install_rich_traceback(show_locals=debug, suppress=[websockets])
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.WARNING,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, show_path=debug)],
    )


async def async_main(argv: list[str] | None = None) -> int:
    """Async application entry point."""
    config = parse_args(argv)
    configure_logging(config.debug)
    console = Console()
    return await ChatCli(config=config, console=console).run()


def main() -> None:
    """Synchronous script entry point."""
    raise SystemExit(asyncio.run(async_main()))


if __name__ == "__main__":
    main()

