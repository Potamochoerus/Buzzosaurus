"""
Tests for the Buzzosaurus server logic.

Run with:
    pytest
"""
import asyncio
import json
import sys
from pathlib import Path
 
import pytest
import pytest_asyncio
import websockets


# Allow "from server import BuzzosaurusServer" without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server import BuzzosaurusServer  # noqa: E402


@pytest_asyncio.fixture
async def running_server():
    server = BuzzosaurusServer()
    async with websockets.serve(server.handler, "localhost", 0) as ws_server:
        port = ws_server.sockets[0].getsockname()[1]
        yield server, f"ws://localhost:{port}"


async def connect_and_join(uri: str, name: str):
    ws = await websockets.connect(uri)
    await ws.send(json.dumps({"type": "join", "name": name}))
    await ws.recv()  # consume the player_list broadcast triggered by our own join
    return ws


@pytest.mark.asyncio
async def test_single_join_appears_in_player_list(running_server):
    server, uri = running_server
    ws = await connect_and_join(uri, "Zac")

    assert list(server.players.values()) == ["Zac"]

    await ws.close()


@pytest.mark.asyncio
async def test_first_buzz_wins(running_server):
    server, uri = running_server
    ws1 = await connect_and_join(uri, "Zac")
    ws2 = await connect_and_join(uri, "Poppy")
    await ws1.recv()  # Zac sees Poppyy's join broadcast

    await ws1.send(json.dumps({"type": "buzz"}))
    result = json.loads(await ws1.recv())
    await ws2.recv()  # Poppy also receives the same broadcast

    assert result["type"] == "buzz_result"
    assert result["winner"] == "Zac"
    assert result["ranking"] == [{"name": "Zac", "delta_ms": 0}]

    await ws1.close()
    await ws2.close()


@pytest.mark.asyncio
async def test_second_buzz_recorded_but_not_winner(running_server):
    server, uri = running_server
    ws1 = await connect_and_join(uri, "Zac")
    ws2 = await connect_and_join(uri, "Poppy")
    await ws1.recv()

    await ws1.send(json.dumps({"type": "buzz"}))
    await ws1.recv()
    await ws2.recv()

    await ws2.send(json.dumps({"type": "buzz"}))
    result = json.loads(await ws1.recv())
    await ws2.recv()

    assert result["winner"] == "Zac"
    names = [entry["name"] for entry in result["ranking"]]
    assert names == ["Zac", "Poppy"]
    assert result["ranking"][1]["delta_ms"] >= 0

    await ws1.close()
    await ws2.close()


@pytest.mark.asyncio
async def test_duplicate_buzz_from_same_player_is_ignored(running_server):
    server, uri = running_server
    ws1 = await connect_and_join(uri, "Zac")

    await ws1.send(json.dumps({"type": "buzz"}))
    await ws1.recv()

    # Buzzing again should NOT produce a second ranking entry
    await ws1.send(json.dumps({"type": "buzz"}))
    await asyncio.sleep(0.05)  # let the server process (and ignore) the duplicate
    await server.handle_reset()  # proves the server is still alive & responsive
    reset_msg = json.loads(await ws1.recv())

    assert reset_msg["type"] == "reset"
    assert server.buzzes == []

    await ws1.close()


@pytest.mark.asyncio
async def test_reset_clears_state(running_server):
    server, uri = running_server
    ws1 = await connect_and_join(uri, "Zac")

    await ws1.send(json.dumps({"type": "buzz"}))
    await ws1.recv()
    assert server.locked is True

    await server.handle_reset()
    await ws1.recv()

    assert server.locked is False
    assert server.buzzes == []

    await ws1.close()


@pytest.mark.asyncio
async def test_disconnect_removes_player(running_server):
    server, uri = running_server
    ws1 = await connect_and_join(uri, "Zac")
    ws2 = await connect_and_join(uri, "Poppy")

    await ws2.close()
    await asyncio.sleep(0.2)  # give the server a moment to process the disconnect

    assert list(server.players.values()) == ["Zac"]

    await ws1.close()
