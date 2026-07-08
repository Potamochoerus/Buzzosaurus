"""
Buzzosaurus - Main entry point with routing.
"""

import flet as ft
from app.router import Router
from app import routes


async def main(page: ft.Page):
    """Initialize the app with router."""
    page.title = "Buzzosaurus"

    # Create router
    router = Router(page)

    # Navigate to home view
    await router.navigate(routes.HOME)


if __name__ == "__main__":
    ft.run(main)
