"""
Buzzosaurus - Main entry point with routing.
"""

import flet as ft
import traceback
from app.router import Router
from app import routes


async def main(page: ft.Page):
    page.title = "Buzzosaurus"
    page.add(ft.Text("Booting...", color="white"))
    page.update()

    try:
        router = Router(page)
        await router.navigate(routes.HOME)
    except Exception as e:
        page.controls.clear()
        page.add(
            ft.Text(
                f"ERROR: {e}\n\n{traceback.format_exc()}",
                color="red",
                selectable=True,
                size=10,
            )
        )
        page.update()


if __name__ == "__main__":
    ft.run(main)
