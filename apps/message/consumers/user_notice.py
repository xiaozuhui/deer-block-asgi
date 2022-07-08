import json
import logging

from apps.message.consumers.async_model_cunsumer import AsyncModelConsumer

logger = logging.getLogger('django')


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


