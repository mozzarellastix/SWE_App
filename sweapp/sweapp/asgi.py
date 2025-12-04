"""
ASGI config for sweapp project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from polls.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sweapp.settings')

# Initialize Django ASGI application early to ensure settings are loaded
django_asgi_app = get_asgi_application()

# The ProtocolTypeRouter decides what to do based on the connection type
# - HTTP requests go to Django (django_asgi_app)
# - WebSocket requests go to our custom WebSocket routes
application = ProtocolTypeRouter({
    "http": django_asgi_app,  # Handle traditional HTTP requests
    "websocket": AuthMiddlewareStack(  # Handle WebSocket connections
        URLRouter(
            websocket_urlpatterns  # Routes defined in polls/routing.py
        )
    ),
})
