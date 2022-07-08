import json
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from apps.message.models import MessageGroup
from apps.users.models import User, UserProfile

logger = logging.getLogger('django')


class AsyncModelConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.filter(id=user_id).first()

    @database_sync_to_async
    def get_user_profile(self, user_id):
        return UserProfile.objects.filter(user__id=user_id).first()

    @database_sync_to_async
    def save_group(self, group_name, user_ids=None):
        """
        记录用户加入的group
        """
        mg = MessageGroup.logic_objects.filter(group_name=group_name).first()
        if not mg:
            mg = MessageGroup()
            mg.group_name = group_name
        users = User.objects.filter(user_ids)
        if users:
            mg.users.add(*users)
        else:
            logger.error("保存group失败，UserIds = {}".format(user_ids))
            return None
        mg.save()
        return mg

    @database_sync_to_async
    def save_message(self, from_user, source_type):
        """
        记录消息的发送
        """

    async def system_message(self, event):
        """
        系统消息的callback
        """
        message = event['message']
        logger.info("已经发送消息: {}".format(message))
        await self.send(text_data=json.dumps({
            'message': message
        }, ensure_ascii=False))
