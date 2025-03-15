"""
WebSocket routing for game events.
This module provides WebSocket routing for game events.
"""

from django.urls import re_path
from .consumers import GameConsumer

websocket_urlpatterns = [
    re_path(r'ws/games/(?P<game_id>[^/]+)/$', GameConsumer.as_asgi()),
]
