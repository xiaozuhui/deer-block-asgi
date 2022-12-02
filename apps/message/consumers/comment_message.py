import datetime
import json
import logging

from apps import const
from apps.message.consumers.async_model_cunsumer import MessageConsumer

logger = logging.getLogger('django')


class CommentIssuesMessage(MessageConsumer):
    """
    评论回复的消息
    """

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
        self.self_group_name = f"Group_Self_{user.user_code}_{user.phone_number}"
        await self.channel_layer.group_add(
            self.self_group_name,
            self.channel_name
        )
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        """
        传过之参数
        """
        text_data_json = json.loads(text_data)
        message, message_type = await self.check_message(text_data_json)
        await self.channel_layer.group_send(
            self.self_group_name,
            {
                'type': message_type,
                'message': message
            }
        )
        from_user_id = message.get("from_user", {}).get("user_id", None)
        to_user_id = message.get("to_user", {}).get("user_id", None)
        if not from_user_id or not to_user_id:
            return
        await self.save_message(from_user_id=from_user_id,
                                to_user_id=to_user_id,
                                message_content=message,
                                source_type=const.COMMENT)

    async def check_message(self, data: dict) -> (dict, str):
        """校验data的数据完整和正确性

        return:
            {
                "from_user": { # 发表评论的用户
                    "username": "",
                    "user_id": 1,
                    "phone_number": 1234567,
                },
                "to_user": { # 被评论的用户，可能是issues的作者，也可能是评论作者
                    "username": "",
                    "user_id": 2,
                    "phone_number": 1234567,
                },
                "send_time": "2022-01-01 12:09:78", # 消息发送的日期
                "issues_title": "abc", # 动态的标题
                "issues_id": "所对应的issues的id",
                "target_comment_id": "目标target评论id",
                "comment_id": "用户所评论id"
                "content": "......", # 评论的精简内容
                "issues_url": "localhost:8080/issues/1",  # 对应的issues链接
                "comment_url": "localhost:8080/comment/1"
            }
        """
        message = {}
        message_type = data.get("callback", "system_message")
        # 校验from_user
        from_user_id = data.get("from_user_id", None)
        if not from_user_id:
            raise ValueError("消息的【from_user_id】为空")
        from_user = await self.get_user(from_user_id)
        if not from_user:
            raise ValueError("ID 为 {} 的用户不存在".format(from_user_id))
        message.update({"from_user": {
            "username": from_user.username,
            "user_id": from_user_id,
            "phone_number": from_user.phone_number,
        }})

        # 校验to_user
        to_user_id = data.get("to_user_id", None)
        if not to_user_id:
            raise ValueError("消息的【to_user_id】为空")
        to_user = await self.get_user(to_user_id)
        if not to_user:
            raise ValueError("ID 为 {} 的用户不存在".format(to_user_id))
        message.update({"to_user": {
            "username": to_user.username,
            "user_id": to_user_id,
            "phone_number": to_user.phone_number,
        }})

        # 校验issues，即使是对评论的评论，那么issues也是存在的
        issues_id = data.get("issues_id", None)
        issues_title = data.get("issues_title", None)
        if issues_id is None or issues_title is None:
            raise ValueError("消息参数中issues相关数据不完整")

        message.update({
            "issues_title": issues_title,
            "issues_id": issues_id,
            "send_time": data.get("send_time", datetime.datetime.now()),
            "receive_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "issues_url": data.get("issues_url", ""),
            "content": data.get("content", ""),
            "source_type": "comment",
        })

        comment_id = data.get("comment_id", None)
        target_comment_id = data.get("target_comment_id", None)  # target_comment可以为空，因为不一定是针对评论做出的评论

        if not comment_id:
            raise ValueError("消息中comment_id参数错误")
        # if not target_comment_id:
        #     raise ValueError("消息中target_comment_id参数错误")

        message.update({
            "comment_id": comment_id,
            "target_comment_id": target_comment_id,
            "comment_url": data.get("comment_url", ""),
            "target_comment_url": data.get("target_comment_url", ""),
        })

        return message, message_type

    async def disconnect(self, close_code):
        """
        断开连接
        """
        await self.channel_layer.group_discard(
            self.self_group_name,
            self.channel_name
        )
