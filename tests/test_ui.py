import asyncio
import contextlib
import json

import pytest

from app.views import player_login, player_playing, home, server
from app.router import Router
from app import routes


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

    def clean(self):
        self.controls = []

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

    async def close(self):
        self.closed = True


class FakeServerHandle:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True

    async def wait_closed(self):
        self.closed = True


@pytest.mark.asyncio
async def test_home_view_has_buttons():
    """Test that home view has host and join buttons."""
    page = FakePage()
    router = Router(page)

    view = await home.build_home_view(page, router)

    assert view is not None
    buttons = [c for c in view.controls if hasattr(c, "on_click")]
    assert len(buttons) == 2


@pytest.mark.asyncio
async def test_player_login_view_connect_flow(monkeypatch):
    """Test player login view connection flow."""
    page = FakePage()

    # Create a mock router that tracks navigation calls
    class MockRouter:
        def __init__(self):
            self.navigated_to = None
            self.nav_params = None

        async def navigate(self, route, params=None):
            self.navigated_to = route
            self.nav_params = params

    router = MockRouter()
    fake_ws = FakeWebSocket()

    async def fake_connect(uri):
        return fake_ws

    monkeypatch.setattr(player_login.websockets, "connect", fake_connect)

    view = await player_login.build_player_login_view(page, router)

    # Find input fields
    name_field = view.controls[1]
    ip_field = view.controls[2]
    port_field = view.controls[3]
    connect_button = view.controls[4]

    name_field.value = "Zac"
    ip_field.value = "127.0.0.1"
    port_field.value = "8766"

    await connect_button.on_click(None)

    assert fake_ws.sent_messages == ['{"type": "join", "name": "Zac"}']
    assert router.navigated_to == routes.PLAYER_PLAYING
    assert router.nav_params["player_name"] == "Zac"


@pytest.mark.asyncio
async def test_player_login_validation():
    """Test that player login validates inputs."""
    page = FakePage()

    class MockRouter:
        async def navigate(self, route, params=None):
            pass

    router = MockRouter()

    view = await player_login.build_player_login_view(page, router)

    name_field = view.controls[1]
    ip_field = view.controls[2]
    port_field = view.controls[3]
    connect_button = view.controls[4]
    status_text = view.controls[5]

    # Try to connect without filling fields
    name_field.value = ""
    ip_field.value = ""

    await connect_button.on_click(None)

    assert "Please fill" in status_text.value


@pytest.mark.asyncio
async def test_player_playing_view_buzz_functionality(monkeypatch):
    """Test player playing view buzz button functionality."""
    page = FakePage()

    class MockRouter:
        async def navigate(self, route, params=None):
            pass

    router = MockRouter()
    fake_ws = FakeWebSocket()

    connection_data = {"ws": fake_ws, "player_name": "Alice"}

    view = await player_playing.build_player_playing_view(page, router, connection_data)

    assert view is not None
    buzzer_button = view.controls[1]

    await buzzer_button.on_click(None)

    assert fake_ws.sent_messages == ['{"type": "buzz"}']
    assert buzzer_button.disabled is True


@pytest.mark.asyncio
async def test_server_view_has_controls():
    """Test that server view has start/stop and reset controls."""
    page = FakePage()

    class MockRouter:
        async def navigate(self, route, params=None):
            pass

    router = MockRouter()

    view = await server.build_server_view(page, router)

    assert view is not None
    assert len(view.controls) == 6


@pytest.mark.asyncio
async def test_server_ui_reset_round_updates_log(monkeypatch):
    page = FakePage()

    class MockRouter:
        async def navigate(self, route, params=None):
            pass

    router = MockRouter()

    view = await server.build_server_view(page, router)

    reset_button = view.controls[2].controls[2]
    log_text = view.controls[4].content.controls[0]

    await reset_button.on_click(None)

    assert log_text.value == "New round"
