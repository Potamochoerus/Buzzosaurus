"""
BuzzosaurusServer - Console test client
---------------------------------------

A throwaway terminal client used to test the server without any phone or UI.
Open several terminals, one per "player", to simulate a real game.

Usage:
    python client_test.py <name> [host] [port]
"""
import asyncio
import json
import sys

import websockets

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8766


async def receiver(ws) -> None:
    async for raw in ws:
        msg = json.loads(raw)
        msg_type = msg.get("type")

        if msg_type == "player_list":
            print(f"\n[Players connected] {', '.join(msg['players'])}")
        elif msg_type == "buzz_result":
            print(f"\n[BUZZED FIRST] : {msg['winner']}")
            for entry in msg["ranking"]:
                print(f"   {entry['name']}: +{entry['delta_ms']} ms")

        elif msg_type == "reset":
            print("\n[Round reset] Ready to buzz again.")
        print("> ", end="", flush=True)


async def sender(ws) -> None:
    loop = asyncio.get_event_loop()
    while True:
        await loop.run_in_executor(None, input, "> ")
        await ws.send(json.dumps({"type": "buzz"}))


async def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python client_test.py <name> [host] [port]")
        sys.exit(1)

    name = sys.argv[1]
    host = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_HOST
    port = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_PORT

    uri = f"ws://{host}:{port}"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"type": "join", "name": name}))
        print(f"Connected as '{name}'. Press enter to buzz.")
        await asyncio.gather(receiver(ws), sender(ws))


if __name__ == "__main__":
    asyncio.run(main())
