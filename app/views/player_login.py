"""
Player login view - Connection setup for joining a game.
"""

import json
import flet as ft
import websockets
from app.routes import HOME, PLAYER_PLAYING


class PlayerLoginState:
    """State for the login view."""

    def __init__(self):
        self.ws: websockets.ClientConnection | None = None
        self.player_name = ""
        self.server_ip = ""
        self.server_port = ""


async def build_player_login_view(page: ft.Page, router):
    """Build and return the player login view."""

    page.title = "Buzzosaurus - Join Game"

    state = PlayerLoginState()

    name_field = ft.TextField(label="Player name", width=280, autofocus=True)
    ip_field = ft.TextField(
        label="Server IP (ex: 192.168.1.181)", value="192.168.1.181", width=280
    )
    port_field = ft.TextField(label="Port", value="8766", width=280)
    status_text = ft.Text("", color=ft.Colors.RED_400)
    connect_button = ft.Button("Log in", width=280)
    back_button = ft.Button("Back", width=120)

    view = ft.Column(
        controls=[
            ft.Text("Buzzosaurus", size=32, weight=ft.FontWeight.BOLD),
            name_field,
            ip_field,
            port_field,
            connect_button,
            status_text,
            back_button,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=15,
        expand=True,
    )

    async def on_connect_click(e):
        name = name_field.value.strip() if name_field.value else ""
        ip = ip_field.value.strip() if ip_field.value else ""
        port = (port_field.value or "8766").strip()

        if not name or not ip:
            status_text.value = "Please fill both player name and host server IP"
            page.update()
            return

        status_text.value = "Connection ..."
        connect_button.disabled = True
        page.update()

        try:
            state.ws = await websockets.connect(f"ws://{ip}:{port}")
            await state.ws.send(json.dumps({"type": "join", "name": name}))
            state.player_name = name
            state.server_ip = ip
            state.server_port = port
        except Exception as ex:
            status_text.value = f"Failed to connect : {ex}"
            connect_button.disabled = False
            page.update()
            return

        # Navigate to playing view with the connection state
        await router.navigate(PLAYER_PLAYING, {"ws": state.ws, "player_name": name})

    async def on_back_click(e):
        await router.navigate(HOME)

    connect_button.on_click = on_connect_click
    back_button.on_click = on_back_click

    return view
