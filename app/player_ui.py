"""
Buzzosaurus - Player UI
-----------------------
Run with:
    python app/player_ui.py
"""

import json

import flet as ft
import websockets


class PlayerState:
    """Small holder for the mutable state shared across UI callbacks."""

    def __init__(self):
        self.ws: websockets.ClientConnection | None = None
        self.locked = False  # True once *this* player has buzzed this round


async def main(page: ft.Page):
    page.title = "Buzzosaurus - Player"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20

    state = PlayerState()

    name_field = ft.TextField(label="Player name", width=280, autofocus=True)
    ip_field = ft.TextField(
        label="Server IP (ex: 192.168.1.181)", value="192.168.1.181", width=280
    )
    port_field = ft.TextField(label="Port", value="8766", width=280)
    status_text = ft.Text("", color=ft.Colors.RED_400)
    connect_button = ft.Button("Log in", width=280)

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
    player_list_text = ft.Text("", size=14, color=ft.Colors.GREY_700)
    result_text = ft.Text(
        "", size=18, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER
    )

    connection_view = ft.Column(
        controls=[
            ft.Text("Buzzosaurus", size=32, weight=ft.FontWeight.BOLD),
            name_field,
            ip_field,
            port_field,
            connect_button,
            status_text,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=15,
    )

    buzzer_view = ft.Column(
        controls=[
            player_list_text,
            buzzer_button,
            result_text,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
        visible=False,
    )

    page.add(connection_view, buzzer_view)

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
            status_text.value = "Connection lost..."
            connection_view.visible = True
            buzzer_view.visible = False
            connect_button.disabled = False
            page.update()

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
        except Exception as ex:
            status_text.value = f"Failed to connect : {ex}"
            connect_button.disabled = False
            page.update()
            return

        status_text.value = ""
        connection_view.visible = False
        buzzer_view.visible = True
        buzzer_button.disabled = False
        buzzer_button_label.value = f"{name}"
        page.update()

        page.run_task(listen_to_server)

    async def on_buzz_click(e):
        await state.ws.send(json.dumps({"type": "buzz"}))
        if state.locked or state.ws is None:
            return
        state.locked = True
        buzzer_button.disabled = True
        page.update()

    connect_button.on_click = on_connect_click
    buzzer_button.on_click = on_buzz_click


if __name__ == "__main__":
    ft.run(main)
