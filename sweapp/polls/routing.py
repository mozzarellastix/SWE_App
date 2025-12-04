"""
WebSocket URL Routing

This is like urls.py but for WebSocket connections.
It maps WebSocket URLs to Consumer classes.
"""

from django.urls import re_path
from . import consumers

# WebSocket URL patterns
# These work like regular URL patterns but for ws:// connections
websocket_urlpatterns = [
    # When a user connects to ws://localhost:8000/ws/chat/5/
    # It will connect to ChatConsumer and pass user_id=5
    re_path(r'ws/chat/(?P<user_id>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
