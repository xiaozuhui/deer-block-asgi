"""
ASGI config for deer_block_message project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

import django
from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deer_block_message.settings')
django.setup()

# Tips 导入INSTALLED_APP中的app时之前，不能在django.setup()之前加载
from apps.message import routing as message_routing

application = ProtocolTypeRouter({
    "http": AsgiHandler(),
    "websocket": URLRouter(
        # 不再设置权限，所有连接都允许
        # 但是用户连接只允许只读，而且会查看用户的信息
        message_routing.websocket_urlpatterns,
    ),
})
