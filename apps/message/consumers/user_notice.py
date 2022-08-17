import logging

from apps.message.consumers.async_model_cunsumer import AsyncModelConsumer

logger = logging.getLogger('django')


class NoticeMessage(AsyncModelConsumer):
    """
    用户所加入的group如下：
        1、当前用户关注的用户所构成的group
        2、当前用户自己所构建的group，用于私信，包括回复和点赞通知
        3、当前用户所收藏的动态收到回复时 (此条适用于上一条)

        其实所谓的回复、收藏的提示都是系统与用户一对一的消息推送
    """

    def __init__(self, *args, **kwargs):
        self.group_names = []
        self.self_group_name = ""
        super().__init__(*args, **kwargs)

    async def connect(self):
        user_id = self.scope.get("url_route", {}).get("kwargs", {}).get("user_id", None)
        if not user_id:
            await self.close()
        c_user = await self.get_user(user_id)
        # 加入到我所关注的人的group中
        follower_list = await self.get_user_followers(user_id)
        for follower in follower_list:
            gn = f"Group_{follower.user_code}_{follower.phone_number}"
            self.group_names.append(gn)
            await self.channel_layer.group_add(
                gn,
                self.channel_name
            )
            await self.save_group(gn, [user_id])
        # 并且加入到我自己的group中去
        group_name = f"Group_Self_{c_user.user_code}_{c_user.phone_number}"
        self.self_group_name = group_name
        await self.channel_layer.group_add(
            group_name,
            self.channel_name
        )
        await self.save_group(group_name, [user_id])
        await self.accept()

    async def disconnect(self, close_code):
        # 退出所有的follow关系组
        for gn in self.group_names:
            await self.channel_layer.group_discard(gn, self.channel_name)
        # 推出自己的组
        await self.channel_layer.group_discard(self.self_group_name, self.channel_name)
