import pytest
import main
from app.router import Router
from app import routes


class FakePage:
    def __init__(self):
        self.controls = []
        self.title = None
        self.vertical_alignment = None
        self.horizontal_alignment = None
        self.padding = None
        self.views = []

    def add(self, *controls):
        self.controls.extend(controls)

    def clean(self):
        self.controls = []

    def update(self):
        pass


@pytest.mark.asyncio
async def test_main_initializes_with_home_view(monkeypatch):
    """Test that main initializes router and navigates to home."""
    page = FakePage()

    await main.main(page)

    assert page.title == "Buzzosaurus"
    assert len(page.controls) >= 1


@pytest.mark.asyncio
async def test_router_navigates_to_home(monkeypatch):
    """Test that router can navigate to home view."""
    page = FakePage()
    router = Router(page)

    await router.navigate(routes.HOME)

    assert router.current_route == routes.HOME
    assert len(page.controls) == 1
    # Home view is a Column with title, subtitle, and two buttons
    column = page.controls[0]
    assert hasattr(column, "controls")
    buttons = [c for c in column.controls if hasattr(c, "on_click")]
    assert len(buttons) == 2


@pytest.mark.asyncio
async def test_router_navigate_server_from_home(monkeypatch):
    """Test that router navigates to server from home."""
    page = FakePage()
    router = Router(page)

    await router.navigate(routes.HOME)
    home_column = page.controls[0]
    buttons = [c for c in home_column.controls if hasattr(c, "on_click")]
    host_button = buttons[0]

    await host_button.on_click(None)

    assert router.current_route == routes.SERVER


@pytest.mark.asyncio
async def test_router_navigate_player_login_from_home(monkeypatch):
    """Test that router navigates to player login from home."""
    page = FakePage()
    router = Router(page)

    await router.navigate(routes.HOME)
    home_column = page.controls[0]
    buttons = [c for c in home_column.controls if hasattr(c, "on_click")]
    player_button = buttons[1]

    await player_button.on_click(None)

    assert router.current_route == routes.PLAYER_LOGIN

    await player_button.on_click(None)

    assert router.current_route == routes.PLAYER_LOGIN
