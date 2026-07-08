"""
Home view - Main menu for Buzzosaurus app.
"""

import flet as ft
from app.routes import PLAYER_LOGIN, SERVER


async def build_home_view(page: ft.Page, router):
    """Build and return the home menu view."""

    title_text = ft.Text("Buzzosaurus", size=32, weight=ft.FontWeight.BOLD)
    subtitle_text = ft.Text("The buzz app for your quizzes or blindtests!", size=16)

    async def on_host_click(e):
        await router.navigate(SERVER)

    async def on_player_click(e):
        await router.navigate(PLAYER_LOGIN)

    host_button = ft.Button("Host a game", width=240, on_click=on_host_click)
    player_button = ft.Button("Join as player", width=240, on_click=on_player_click)

    view = ft.Column(
        controls=[
            title_text,
            subtitle_text,
            host_button,
            player_button,
        ],
        spacing=16,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    return view
