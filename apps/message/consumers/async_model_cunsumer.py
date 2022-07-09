import json
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from apps.message.models import MessageGroup, Message
from apps.users.models import User, UserProfile

logger = logging.getLogger('django')


class AsyncModelConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.filter(id=user_id, is_delete=False).first()

    @database_sync_to_async
    def get_user_profile(self, user_id):
        return UserProfile.objects.filter(user__id=user_id).first()

    @database_sync_to_async
    def get_user_followers(self, user_id):
        """
        获取用户的所有关注者
        """
        user_profile = UserProfile.objects.filter(user__id=user_id).first()
        if not user_profile:
            logger.error("获取user profile失败，userId={}".format(user_id))
            return None
        followers = user_profile.follow.all()
        return followers

    @database_sync_to_async
    def get_followed(self, user_id):
        """
        获取被这个用户关注的人
        """
        user = User.objects.filter(id=user_id).first()
        profiles = UserProfile.objects.filter(follow__id=user.id)
        followers = User.objects.filter(id__in=[profile.user_id for profile in profiles])
        return followers

    @database_sync_to_async
    def save_group(self, group_name, user_ids=None):
        """
        记录用户加入的group
        """
        mg = MessageGroup.logic_objects.filter(group_name=group_name).first()
        if not mg:
            mg = MessageGroup()
            mg.group_name = group_name
            mg.save()
        users = User.objects.filter(id__in=user_ids, is_delete=False)
        for user in users:
            mg.users.add(user)
        return mg

    @database_sync_to_async
    def save_message(self, from_user_id: int, to_user_id: int, source_type: str, message_content: dict):
        """
        记录消息的发送
        """
        from_user = User.objects.filter(id=from_user_id, is_delete=False).first()
        to_user = User.objects.filter(id=to_user_id, is_delete=False).first()

        if not from_user or not to_user:
            logger.error("发送端用户或接受端用户查不到")
            return None

        msg = Message()
        msg.from_user = from_user
        msg.to_user = to_user
        msg.message_content = message_content
        msg.source_type = source_type
        msg.save()

        return msg

    async def system_message(self, event):
        """
        系统消息的callback
        """
        message = event['message']
        logger.info("已经发送消息: {}".format(message))
        await self.send(text_data=json.dumps({
            'message': message
        }, ensure_ascii=False))
