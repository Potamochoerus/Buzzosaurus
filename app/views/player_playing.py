"""
Player playing view - Buzzer and game display.
"""

import json
import flet as ft
import websockets
from app.routes import HOME


class PlayerPlayingState:
    """State for the playing view."""

    def __init__(self, ws: websockets.ClientConnection, player_name: str):
        self.ws = ws
        self.player_name = player_name
        self.locked = False  # True once *this* player has buzzed this round


async def build_player_playing_view(page: ft.Page, router, connection_data=None):
    """Build and return the player playing view."""

    page.title = "Buzzosaurus - Game"

    if not connection_data or not connection_data.get("ws"):
        # No connection, go back to login
        await router.navigate("player_login")
        return ft.Column()

    state = PlayerPlayingState(
        connection_data["ws"], connection_data.get("player_name", "Player")
    )

    player_list_text = ft.Text("", size=14, color=ft.Colors.GREY_700)

    buzzer_button_label = ft.Text(
        "BUZZ", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER
    )
    buzzer_button = ft.Button(
        content=buzzer_button_label,
        width=220,
        height=220,
        style=ft.ButtonStyle(
            shape=ft.CircleBorder(),
            bgcolor={"": ft.Colors.RED_600, "disabled": ft.Colors.GREY_400},
            color={"": ft.Colors.WHITE, "disabled": ft.Colors.WHITE},
        ),
        disabled=True,
    )

    result_text = ft.Text(
        "", size=18, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER
    )

    quit_button = ft.Button("Quit", width=120)

    view = ft.Column(
        controls=[
            player_list_text,
            buzzer_button,
            result_text,
            quit_button,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
        expand=True,
    )

    buzzer_button_label.value = state.player_name

    def reset_buzzer_visuals():
        state.locked = False
        buzzer_button.disabled = False
        result_text.value = ""

    async def listen_to_server():
        try:
            async for raw in state.ws:
                msg = json.loads(raw)
                msg_type = msg.get("type")

                if msg_type == "player_list":
                    player_list_text.value = "Players: " + ", ".join(msg["players"])

                elif msg_type == "buzz_result":
                    if msg["winner"] == msg["current_buzz"]["name"]:
                        result_text.value = f"⭐ {msg['winner']} buzzed first!"
                    else:
                        result_text.value = f"{result_text.value} \n ❌ {msg['current_buzz']['name']} (+{msg['current_buzz']['delta_ms']} ms)"

                elif msg_type == "reset":
                    reset_buzzer_visuals()

                page.update()
        except websockets.exceptions.ConnectionClosed:
            await router.navigate(HOME)
            page.update()

    async def on_buzz_click(e):
        await state.ws.send(json.dumps({"type": "buzz"}))
        if state.locked or state.ws is None:
            return
        state.locked = True
        buzzer_button.disabled = True
        page.update()

    async def on_quit_click(e):
        if state.ws:
            await state.ws.close()
        await router.navigate(HOME)

    buzzer_button.on_click = on_buzz_click
    quit_button.on_click = on_quit_click

    # Start listening to server
    page.run_task(listen_to_server)

    return view
