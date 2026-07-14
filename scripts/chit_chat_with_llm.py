#!/usr/bin/env python
"""Manual testing script for the websocket chat endpoint.

This script allows you to interact with the chat websocket endpoint manually.
It connects to the endpoint and provides an interactive interface to:
- Start conversations
- Send messages
- View full history
- See streamed responses in real-time

Usage:
    python test_websocket_manual.py

Commands:
    /start           - Start a new conversation (optionally with a system prompt)
    /history         - Request the full message history
    /end             - End the conversation
    /help            - Show this help message
    (any other text) - Send as a user message
"""

import asyncio
import json
import sys
from typing import Any

import websockets
from rich import print as rprint
from rich.console import Console
from rich.table import Table

console = Console()

# Configuration
WS_URL = "ws://localhost:8080/v1/chat/ws"


async def send_message(websocket: websockets.WebSocketClientProtocol, message: dict[str, Any]) -> None:
    """Send a message to the websocket."""
    await websocket.send(json.dumps(message))


async def receive_and_display_event(websocket: websockets.WebSocketClientProtocol) -> dict[str, Any]:
    """Receive an event from websocket and display it."""
    data = await websocket.recv()
    event = json.loads(data)

    if event["type"] == "connected":
        rprint(f"[green]✓ Connected[/green] - Session ID: {event['session_id']}")
    elif event["type"] == "started":
        rprint(f"[green]✓ Conversation started[/green] - Session ID: {event['session_id']}")
    elif event["type"] == "assistant_chunk":
        # Print chunk without newline for streaming effect
        console.print(event["content"], end="", soft_wrap=True)
    elif event["type"] == "assistant_message":
        console.print()  # New line after chunks
        rprint(f"[blue]✓ Message complete[/blue]")
    elif event["type"] == "history":
        rprint("\n[cyan]Message History:[/cyan]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Role", style="cyan", width=12)
        table.add_column("Content", style="green")

        for msg in event["messages"]:
            role = msg["role"]
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            table.add_row(role, content)

        console.print(table)
    elif event["type"] == "error":
        rprint(f"[red]✗ Error: {event.get('message', 'Unknown error')}[/red]")
    else:
        rprint(f"[yellow]? Received event: {event}[/yellow]")

    return event


async def get_user_input(prompt: str = "") -> str:
    """Get user input asynchronously."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, input, prompt)


async def main():
    """Main function for interactive websocket testing."""
    rprint("[bold cyan]FastAPI WebSocket Chat Tester[/bold cyan]")
    rprint(f"Connecting to {WS_URL}...\n")

    try:
        async with websockets.connect(WS_URL) as websocket:
            # Receive the initial connected message
            connected_event = await receive_and_display_event(websocket)
            session_id = connected_event["session_id"]

            rprint("\n[yellow]Commands: /start, /history, /end, /help, or type a message[/yellow]\n")

            while True:
                try:
                    # Get user input
                    user_input = await get_user_input("[bold]You:[/bold] ")

                    if user_input.strip() == "":
                        continue

                    # Handle special commands
                    if user_input.lower() == "/help":
                        rprint("\n[cyan]Available Commands:[/cyan]")
                        rprint("[green]/start[/green]    - Start a new conversation")
                        rprint("[green]/history[/green]  - Request the full message history")
                        rprint("[green]/end[/green]      - End the conversation")
                        rprint("[green]/help[/green]     - Show this help message\n")
                        continue

                    elif user_input.lower() == "/start":
                        system_prompt = await get_user_input(
                            "Enter system prompt (or press Enter for default): "
                        )
                        msg = {
                            "type": "start",
                            "system_prompt": system_prompt or "You are a helpful assistant.",
                        }
                        await send_message(websocket, msg)
                        event = await receive_and_display_event(websocket)
                        rprint()
                        continue

                    elif user_input.lower() == "/history":
                        msg = {"type": "history_request"}
                        await send_message(websocket, msg)
                        event = await receive_and_display_event(websocket)
                        rprint()
                        continue

                    elif user_input.lower() == "/end":
                        msg = {"type": "end"}
                        await send_message(websocket, msg)
                        rprint("[yellow]Conversation ended. Closing connection...[/yellow]")
                        break

                    else:
                        # Send as a regular user message
                        msg = {"type": "user_message", "content": user_input}
                        await send_message(websocket, msg)
                        rprint("[cyan]Assistant:[/cyan] ", end="")

                        # Receive chunks and the final message
                        while True:
                            event = await receive_and_display_event(websocket)
                            if event["type"] == "assistant_message":
                                break

                        rprint()  # New line after response

                except KeyboardInterrupt:
                    rprint("\n[yellow]Interrupted by user.[/yellow]")
                    msg = {"type": "end"}
                    await send_message(websocket, msg)
                    break

    except ConnectionRefusedError:
        rprint(
            f"[red]✗ Could not connect to {WS_URL}[/red]"
        )
        rprint("[yellow]Make sure the FastAPI server is running on http://localhost:8080[/yellow]")
        sys.exit(1)
    except Exception as e:
        rprint(f"[red]✗ Error: {e}[/red]")
        sys.exit(1)
    finally:
        rprint("[cyan]Connection closed.[/cyan]")


if __name__ == "__main__":
    asyncio.run(main())

