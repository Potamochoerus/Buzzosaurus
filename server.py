"""
Buzzosaurus - Server
--------------------

Minimal WebSocket server for a local-network buzzer app.

The server is the single source of truth for timing: it timestamps every
"buzz" the instant it receives it, so players' phone clocks (which may be
slightly out of sync) never matter.

Run:
    python server.py
"""
import asyncio
import contextlib
import json
import time

import websockets
from websockets.asyncio.server import ServerConnection

HOST = "0.0.0.0"
PORT = 8766


class BuzzosaurusServer:
    """Holds all the game state and the logic to update it."""

    def __init__(self):
        # websocket -> player name
        self.players: dict[ServerConnection, str] = {}
        # ordered list of (name, timestamp) for the current round
        self.buzzes: list[tuple[str, float]] = []

    @property
    def locked(self) -> bool:
        """True once someone has buzzed this round."""
        return len(self.buzzes) > 0

    async def broadcast(self, message: dict) -> None:
        if not self.players:
            return
        data = json.dumps(message)
        await asyncio.gather(
            *(ws.send(data) for ws in list(self.players.keys())),
            return_exceptions=True,
        )

    async def send_player_list(self) -> None:
        await self.broadcast({
            "type": "player_list",
            "players": list(self.players.values()),
        })
        print(f"Connected players: {", ".join(list(self.players.values()))}")

    async def handle_join(self, ws: ServerConnection, name: str) -> None:
        self.players[ws] = name
        await self.send_player_list()

    async def handle_buzz(self, ws: ServerConnection) -> None:
        name = self.players.get(ws)
        if name is None:
            return

        if any(existing_name == name for existing_name, _ in self.buzzes):
            return  # this player already buzzed this round, ignore
        

        # Timepoint for this buzz
        now = time.monotonic()

        # Add to the buzz stack
        self.buzzes.append((name, now))

        # First player buzz timepoint
        first_ts = self.buzzes[0][1]

        # Delta of this buzz
        this_buzz_delay = round((now - first_ts) * 1000)

        # Rank all buzz
        ranking = [
            {"name": n, "delta_ms": round((ts - first_ts) * 1000)}
            for n, ts in self.buzzes
        ]

        print(f"[BUZZ] : {name}, + {this_buzz_delay} ms")

        await self.broadcast({
            "type": "buzz_result",
            "winner": self.buzzes[0][0],
            "ranking": ranking,
        })

    async def handle_reset(self) -> None:
        self.buzzes.clear()
        await self.broadcast({"type": "reset"})

    async def handler(self, ws: ServerConnection) -> None:
        try:
            async for raw in ws:
                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    continue

                msg_type = msg.get("type")
                if msg_type == "join":
                    await self.handle_join(ws, msg.get("name", "Anonyme"))
                elif msg_type == "buzz":
                    await self.handle_buzz(ws)
        finally:
            self.players.pop(ws, None)
            await self.send_player_list()


async def admin_console(server: BuzzosaurusServer) -> None:
    """Type 'r' + Enter in the terminal running the server to reset a round."""
    loop = asyncio.get_event_loop()
    while True:
        try:
            line = await loop.run_in_executor(None, input)
        except EOFError:
            await asyncio.Event().wait()
            return
        if line.strip().lower() == "r":
            await server.handle_reset()
            print("-> Round reset")


async def main() -> None:
    server = BuzzosaurusServer()
    async with websockets.serve(server.handler, HOST, PORT):
        print(f"Buzzosaurus server listening on {HOST}:{PORT}")
        print("Type 'r' + Enter to reset a round.")
        await admin_console(server)


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
