import itertools
import json
import logging
from typing import List

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

    @database_sync_to_async
    def save_many_message(self, data: List[dict]):
        """
        批量保存消息
        """
        from_user_ids = list(set([d.get("from_user_id", None) for d in data]))
        to_user_ids = list(set([d.get("to_user_id", None) for d in data]))

        from_users = User.objects.filter(id__in=from_user_ids, is_delete=False)
        to_users = User.objects.filter(id__in=to_user_ids, is_delete=False)

        from_user_map = dict(itertools.zip_longest([fu.id for fu in from_users], from_users))
        to_user_map = dict(itertools.zip_longest([tu.id for tu in to_users], to_users))

        # 需要保存的message
        messages = []
        for d in data:
            from_user_id = d.get("from_user_id", None)
            to_user_id = d.get("to_user_id", None)
            from_user = from_user_map.get(from_user_id, None)
            to_user = to_user_map.get(to_user_id, None)

            if not from_user or not to_user:
                logger.error("发送端用户{}或接受端用户{}查不到".format(from_user_id, to_user_id))
            msg = Message()
            msg.from_user = from_user
            msg.to_user = to_user
            msg.message_content = d.get("message_content", {})
            msg.source_type = d.get("source_type", "")
            messages.append(msg)

        Message.objects.bulk_create(messages)
        return messages

    async def system_message(self, event):
        """
        系统消息的callback
        """
        message = event['message']
        logger.info("已经发送消息: {}".format(message))
        await self.send(text_data=json.dumps({
            'message': message
        }, ensure_ascii=False))


class MessageConsumer(AsyncModelConsumer):
    def __init__(self, *args, **kwargs):
        self.group_name = ""
        self.self_group_name = ""  # 这个是用来一对一的消息的
        super().__init__(*args, **kwargs)

    async def connect(self):
        """
        连接websocket
        username可能是中文，而group_name必须是acsii
        """
        user_id = self.scope.get("url_route", {}).get("kwargs", {}).get("user_id", None)
        if not user_id:
            await self.close()
        user = await self.get_user(user_id)
        if not user:
            await self.close()
        self.group_name = f"Group_{user.user_code}_{user.phone_number}"
        self.self_group_name = f"Group_Self_{user.user_code}_{user.phone_number}"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.channel_layer.group_add(
            self.self_group_name,
            self.channel_name
        )
        # 保存对应的group
        await self.save_group(self.group_name, [user_id])
        await self.save_group(self.self_group_name, [user_id])
        await self.accept()

    async def disconnect(self, close_code):
        """
        断开连接
        """
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        await self.channel_layer.group_discard(
            self.self_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        pass

    async def check_message(self, data: dict) -> (dict, str):
        ...
