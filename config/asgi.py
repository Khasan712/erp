"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from . import routing  # noqa isort:skip
from channels.routing import ProtocolTypeRouter, URLRouter  #

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_application = get_asgi_application()


application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        'websocket': URLRouter(routing.websocket_urlpatterns),
    }
)

