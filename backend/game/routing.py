from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Game-specific connection
    re_path(r'ws/game/(?P<game_uid>[^/]+)/$', consumers.GameConsumer.as_asgi()),
    # Player group-specific connection
    re_path(r'ws/group/(?P<group_uid>[^/]+)/$', consumers.GameConsumer.as_asgi()),
    # User's general connection for notifications and multi-game management
    re_path(r'ws/user/$', consumers.GameConsumer.as_asgi()),
]
