"""
Buzzosaurus - Server UI
-----------------------
Run with:
    python app/server_ui.py
"""

import asyncio
import socket

import flet as ft
import websockets

from src.server import BuzzosaurusServer, get_local_ip

HOST = "0.0.0.0"
PORT = 8766


class ServerUIState:
    def __init__(self):
        self.server = BuzzosaurusServer()
        self.ws_server = None
        self.running = False


async def main(page: ft.Page):
    page.title = "Buzzosaurus - Server"
    page.padding = 20
    page.vertical_alignment = ft.MainAxisAlignment.START

    state = ServerUIState()

    status_text = ft.Text("Server stopped", color=ft.Colors.GREY_700)
    players_text = ft.Text("Connected players: 0", size=16)
    log_text = ft.Text("", selectable=True)
    start_button = ft.Button("Start server", width=220)
    stop_button = ft.Button("Stop server", width=220, disabled=True)

    async def update_status(message: str):
        status_text.value = message
        page.update()

    async def append_log(message: str):
        log_text.value = (log_text.value + "\n" + message).strip()
        page.update()

    async def reset_log():
        log_text.value = ""
        page.update()

    async def handle_server_change():
        names = list(state.server.players.values())
        players_text.value = f"Connected players: {len(names)}"
        if names:
            players_text.value += f" ({', '.join(names)})"
        if state.server.buzzes:
            last_name, last_ts = state.server.buzzes[-1]
            first_ts = state.server.buzzes[0][1]
            delay_ms = round((last_ts - first_ts) * 1000)
            await append_log(f"[BUZZ] {last_name} +{delay_ms} ms")
        page.update()

    async def start_server(e):
        if state.running:
            return

        try:
            state.ws_server = await websockets.serve(state.server.handler, HOST, PORT)
            state.server.set_state_changed_callback(handle_server_change)
            state.running = True
            start_button.disabled = True
            stop_button.disabled = False
            await update_status(f"Server running on {get_local_ip()}:{PORT}")
            await append_log("Server started")
        except Exception as ex:
            await update_status(f"Failed to start server: {ex}")

    async def stop_server(e):
        if not state.running:
            return

        state.running = False
        if state.ws_server is not None:
            state.ws_server.close()
            await state.ws_server.wait_closed()
            state.ws_server = None
        state.server.set_state_changed_callback(None)
        start_button.disabled = False
        stop_button.disabled = True
        await update_status("Server stopped")
        await append_log("Server stopped")

    async def reset_round(e):
        await state.server.handle_reset()
        await reset_log()
        await append_log("New round")

    start_button.on_click = start_server
    stop_button.on_click = stop_server
    reset_button = ft.Button("Reset round", width=220)
    reset_button.on_click = reset_round

    page.add(
        ft.Column(
            controls=[
                ft.Text("Buzzosaurus Server", size=28, weight=ft.FontWeight.BOLD),
                status_text,
                ft.Row([start_button, stop_button, reset_button]),
                players_text,
                ft.Container(
                    content=ft.Column([log_text], scroll=ft.ScrollMode.AUTO),
                    width=600,
                    height=240,
                    border=ft.border.Border(
                        left=ft.border.BorderSide(1, ft.Colors.GREY_400),
                        right=ft.border.BorderSide(1, ft.Colors.GREY_400),
                        top=ft.border.BorderSide(1, ft.Colors.GREY_400),
                        bottom=ft.border.BorderSide(1, ft.Colors.GREY_400),
                    ),
                    padding=10,
                ),
            ],
            spacing=12,
        )
    )


if __name__ == "__main__":
    ft.run(main)
