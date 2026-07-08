import asyncio
import contextlib
import json

import pytest

from app import player_ui, server_ui


class FakePage:
    def __init__(self):
        self.controls = []
        self.title = None
        self.vertical_alignment = None
        self.horizontal_alignment = None
        self.padding = None
        self.updated = False
        self.tasks = []

    def add(self, *controls):
        self.controls.extend(controls)

    def update(self):
        self.updated = True

    def run_task(self, coroutine):
        task = asyncio.create_task(coroutine() if callable(coroutine) else coroutine)
        self.tasks.append(task)
        return task


class FakeWebSocket:
    def __init__(self, messages=None):
        self.sent_messages = []
        self.closed = False
        self._messages = list(messages or [])

    async def send(self, data):
        self.sent_messages.append(data)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._messages:
            return self._messages.pop(0)
        raise StopAsyncIteration


class FakeServerHandle:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True

    async def wait_closed(self):
        self.closed = True


@pytest.mark.asyncio
async def test_player_ui_connect_and_buzz_flow(monkeypatch):
    page = FakePage()
    fake_ws = FakeWebSocket()

    async def fake_connect(uri):
        return fake_ws

    monkeypatch.setattr(player_ui.websockets, "connect", fake_connect)

    await player_ui.main(page)

    connection_view = page.controls[0]
    buzzer_view = page.controls[1]
    name_field = connection_view.controls[1]
    ip_field = connection_view.controls[2]
    port_field = connection_view.controls[3]
    connect_button = connection_view.controls[4]
    status_text = connection_view.controls[5]
    buzzer_button = buzzer_view.controls[1]

    name_field.value = "Zac"
    ip_field.value = "127.0.0.1"
    port_field.value = "8766"

    await connect_button.on_click(None)

    assert status_text.value == ""
    assert connection_view.visible is False
    assert buzzer_view.visible is True
    assert buzzer_button.disabled is False
    assert buzzer_view.controls[0].value == ""
    assert fake_ws.sent_messages == ['{"type": "join", "name": "Zac"}']

    await buzzer_button.on_click(None)

    assert fake_ws.sent_messages[-1] == '{"type": "buzz"}'
    assert buzzer_button.disabled is True


@pytest.mark.asyncio
async def test_player_ui_invalid_connect_shows_error(monkeypatch):
    page = FakePage()
    connect_attempted = False

    async def fake_connect(uri):
        nonlocal connect_attempted
        connect_attempted = True
        return FakeWebSocket()

    monkeypatch.setattr(player_ui.websockets, "connect", fake_connect)

    await player_ui.main(page)

    connection_view = page.controls[0]
    name_field = connection_view.controls[1]
    ip_field = connection_view.controls[2]
    connect_button = connection_view.controls[4]
    status_text = connection_view.controls[5]

    name_field.value = ""
    ip_field.value = ""

    await connect_button.on_click(None)

    assert connect_attempted is False
    assert status_text.value == "Please fill both player name and host server IP"


@pytest.mark.asyncio
async def test_player_ui_reenables_buzzer_after_reset(monkeypatch):
    page = FakePage()
    fake_ws = FakeWebSocket()

    async def fake_connect(uri):
        return fake_ws

    monkeypatch.setattr(player_ui.websockets, "connect", fake_connect)

    await player_ui.main(page)

    connection_view = page.controls[0]
    buzzer_view = page.controls[1]
    name_field = connection_view.controls[1]
    ip_field = connection_view.controls[2]
    port_field = connection_view.controls[3]
    connect_button = connection_view.controls[4]
    buzzer_button = buzzer_view.controls[1]
    result_text = buzzer_view.controls[2]

    name_field.value = "Zac"
    ip_field.value = "127.0.0.1"
    port_field.value = "8766"

    await connect_button.on_click(None)
    await buzzer_button.on_click(None)

    assert buzzer_button.disabled is True

    fake_ws._messages.append(json.dumps({"type": "reset"}))
    await asyncio.sleep(0)

    assert buzzer_button.disabled is False
    assert result_text.value == ""

    for task in page.tasks:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


@pytest.mark.asyncio
async def test_server_ui_start_and_stop_buttons_toggle_state(monkeypatch):
    page = FakePage()

    async def fake_serve(handler, host, port):
        return FakeServerHandle()

    monkeypatch.setattr(server_ui.websockets, "serve", fake_serve)

    await server_ui.main(page)

    root_column = page.controls[0]
    start_button = root_column.controls[2].controls[0]
    stop_button = root_column.controls[2].controls[1]
    status_text = root_column.controls[1]

    await start_button.on_click(None)

    assert start_button.disabled is True
    assert stop_button.disabled is False
    assert status_text.value.startswith("Server running on")

    await stop_button.on_click(None)

    assert start_button.disabled is False
    assert stop_button.disabled is True
    assert status_text.value == "Server stopped"


@pytest.mark.asyncio
async def test_server_ui_reset_round_updates_log(monkeypatch):
    page = FakePage()

    async def fake_serve(handler, host, port):
        return FakeServerHandle()

    monkeypatch.setattr(server_ui.websockets, "serve", fake_serve)

    await server_ui.main(page)

    root_column = page.controls[0]
    reset_button = root_column.controls[2].controls[2]
    log_text = root_column.controls[4].content.controls[0]

    await reset_button.on_click(None)

    assert log_text.value == "New round"
