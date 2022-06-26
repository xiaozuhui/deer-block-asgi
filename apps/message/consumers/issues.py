from channels.generic.websocket import AsyncWebsocketConsumer


class NewIssuesMessages(AsyncWebsocketConsumer):
    """新动态的消息
    主要有以下集中通知范围

    1、个人消息的通知，直接点对点即可
    2、登录用户为主的通知
    3、系统登录
    """

    async def connect(self):
        print(self.scope)
        await self.accept()


class CommentIssuesMessage(AsyncWebsocketConsumer):
    """
    评论回复的消息
    """
    pass
