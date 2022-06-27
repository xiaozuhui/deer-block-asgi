import json
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from apps.users.models import User, UserProfile

logger = logging.getLogger('django')


class NewIssuesMessages(AsyncWebsocketConsumer):
    """新动态的消息
    主要有以下集中通知范围

    1、个人消息的通知，直接点对点即可
    2、登录用户为主的通知
    3、系统登录
    """

    def __init__(self, *args, **kwargs):
        self.group_name = ""
        self.group_names = []
        super().__init__(*args, **kwargs)

    async def connect(self):
        """
        连接websocket
        """
        raw_path = self.scope['path']  # 获取到请求地址
        user_id = self.scope.get("url_route", {}).get("kwargs", {}).get("user_id", None)
        if not user_id:
            await self.close()
        user = await self.get_user(user_id)
        profile = await self.get_user_profile(user_id)
        if not user or not profile:
            await self.close()
        if 'system' in raw_path:
            # 是wsgi系统请求的，目标在于给所有符合需求的用户发送消息
            self.group_name = "Group_{username}_{phone_number}".format(username=user.username,
                                                                       phone_number=user.phone_number)
            print(self.group_name)
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
        else:
            # 是用户侧的请求，在于连接和加入各个组
            follower_list = profile.follow.all()
            for follower in follower_list:
                # "我"关注的用户，他们发布消息我需要接收到
                gn = "Group_{username}_{phone_number}".format(username=follower.username,
                                                              phone_number=follower.phone_number)
                print(gn)
                self.group_names.append(gn)
                await self.channel_layer.group_add(
                    gn,
                    self.channel_name
                )
        await self.accept()

    async def disconnect(self, close_code):
        """
        断开连接
        """
        raw_path = self.scope['path']
        if 'system' in raw_path:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
        else:
            for gn in self.group_names:
                await self.channel_layer.group_discard(
                    gn,
                    self.channel_name
                )

    async def receive(self, text_data=None, bytes_data=None):
        # TODO 系统使用group_name，但是用户连接不能使用self.group_name
        # TODO 还有一点，要对所有group中的用户进行记录，他们可能没有收到信息，但是记录是需要的，后续可以反过来搜索
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        message_type = text_data_json.get("message_type", "system_message")
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': message_type,
                'message': message
            }
        )

    async def system_message(self, event):
        message = event['message']
        logger.info("已经发送消息: {}".format(message))
        await self.send(text_data=json.dumps({
            'message': message
        }, ensure_ascii=False))

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.filter(id=user_id).first()

    @database_sync_to_async
    def get_user_profile(self, user_id):
        return UserProfile.objects.filter(user__id=user_id).first()


class CommentIssuesMessage(AsyncWebsocketConsumer):
    """
    评论回复的消息
    """
    pass
