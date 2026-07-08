"""
Router for managing navigation between views in Buzzosaurus app.
"""

import flet as ft
from app import routes
from app.views import home, player_login, player_playing, server


class Router:
    """Manages routing and view transitions."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.current_route = None
        self._current_view = None
        self._route_params = {}

        # View builders mapping
        self.views = {
            routes.HOME: home.build_home_view,
            routes.PLAYER_LOGIN: player_login.build_player_login_view,
            routes.PLAYER_PLAYING: player_playing.build_player_playing_view,
            routes.SERVER: server.build_server_view,
        }

    async def navigate(self, route: str, params=None):
        """Navigate to a new route with optional parameters."""
        if route not in self.views:
            raise ValueError(f"Unknown route: {route}")

        if route == self.current_route:
            return  # Already on this route

        # Clear current view
        self.page.clean()
        self.current_route = route
        self._route_params = params or {}

        # Build new view
        view_builder = self.views[route]
        if route == routes.PLAYER_PLAYING:
            # Player playing view needs connection data
            self._current_view = await view_builder(self.page, self, self._route_params)
        else:
            self._current_view = await view_builder(self.page, self)

        # Set page properties
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.padding = 20

        # Add new view
        self.page.add(self._current_view)
        self.page.update()

    async def go_home(self):
        """Convenience method to navigate to home."""
        await self.navigate(routes.HOME)
