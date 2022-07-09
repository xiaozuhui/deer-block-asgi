import datetime
import json
import logging

from apps.message.consumers.async_model_cunsumer import AsyncModelConsumer

logger = logging.getLogger('django')


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
        # 保存对应的group
        await self.save_group(self.group_name, [user_id])
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
        # 发送消息后，应该保存所有对象的消息
        user_id = text_data_json.get("from_user", {}).get("user_id", None)
        if not user_id:
            return
        followers = await self.get_followed(user_id)
        for follower in followers:
            await self.save_message(from_user_id=user_id,
                                    to_user_id=follower.id,
                                    message_content=message,
                                    source_type="issues")
