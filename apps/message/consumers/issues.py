import datetime
import json
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from apps.users.models import User, UserProfile

logger = logging.getLogger('django')


class AsyncModelConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.filter(id=user_id).first()

    @database_sync_to_async
    def get_user_profile(self, user_id):
        return UserProfile.objects.filter(user__id=user_id).first()


class NewIssuesMessages(AsyncModelConsumer):
    """新动态的消息
    主要有以下集中通知范围

    1、个人消息的通知，直接点对点即可
    2、登录用户为主的通知
    3、系统登录
    """

    def __init__(self, *args, **kwargs):
        self.group_name = ""
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
        if not user:
            await self.close()
        self.group_name = "Group_{username}_{phone_number}".format(username=user.username,
                                                                   phone_number=user.phone_number)
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        """
        断开连接
        """
        raw_path = self.scope['path']
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        # TODO 系统使用group_name，但是用户连接不能使用self.group_name
        # TODO 还有一点，要对所有group中的用户进行记录，他们可能没有收到信息，但是记录是需要的，后续可以反过来搜索
        text_data_json = json.loads(text_data)
        """
        {
            "from_user": {
                "username": "",
                "user_id": 1,
                "phone_number": 1234567,
            },
            "callback": "system_message",
            "send_time": "2022-01-01 12:09:78", # 消息发送的日期
            "issues_title": "abc", # 动态的标题
            "content": "......", # 动态的精简内容
            "issues_url": "localhost:8080/issues/1",  # 对应的issues链接
        }
        """
        message = {
            "from_user": text_data_json.get("from_user", {}),
            "send_time": text_data_json.get("send_time", None),
            "receive_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "issues_title": text_data_json.get("issues_title", ""),  # 动态的标题
            "content": text_data_json.get("content", "..."),  # 动态的精简内容
            "issues_url": text_data_json.get("issues_url", ""),  # 对应的issues链接
        }
        message_type = text_data_json.get("callback", "system_message")
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': message_type,
                'message': message
            }
        )


class CommentIssuesMessage(AsyncModelConsumer):
    """
    评论回复的消息
    """
    pass


class NoticeMessage(AsyncModelConsumer):
    """
    用户所加入的group如下：
        1、当前用户关注的用户所构成的group
        2、当前用户自己所构建的group，用于私信
    """

    def __init__(self, *args, **kwargs):
        self.group_names = []
        super().__init__(*args, **kwargs)

    async def connect(self):
        user_id = self.scope.get("url_route", {}).get("kwargs", {}).get("user_id", None)
        if not user_id:
            await self.close()
        profile = await self.get_user_profile(user_id)
        if not profile:
            await self.close()
        follower_list = profile.follow.all()
        for follower in follower_list:
            gn = "Group_{username}_{phone_number}".format(username=follower.username,
                                                          phone_number=follower.phone_number)
            self.group_names.append(gn)
            await self.channel_layer.group_add(
                gn,
                self.channel_name
            )
        await self.accept()

    async def disconnect(self, close_code):
        for gn in self.group_names:
            await self.channel_layer.group_discard(gn, self.channel_name)

    async def system_message(self, event):
        message = event['message']
        logger.info("已经发送消息: {}".format(message))
        await self.send(text_data=json.dumps({
            'message': message
        }, ensure_ascii=False))
