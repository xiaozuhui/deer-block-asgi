from django.contrib.postgres.fields import JSONField
from django.db import models

from apps.base_model import BaseModel
from apps.users.models import User


class Message(BaseModel):
    """
    通知
    所有的通知将使用这个模型
    """
    SOURCE_TYPE = (
        ("issues", "动态消息"),
        ("user", "用户私信"),
        ("shop", "商城消息"),
        ("system", "系统消息")
    )

    # 消息源
    source_type = models.CharField(choices=SOURCE_TYPE, verbose_name="消息源", max_length=10)
    message_content = JSONField(verbose_name="消息内容", blank=True, null=True)
    # 消息是从哪个用户来的，默认系统用户将固定为system
    from_user = models.ForeignKey(User, related_name="from_user", on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name="to_user", on_delete=models.SET_NULL, null=True)  # 消息接受者
    has_consumed = models.BooleanField(verbose_name="是否已被消费", default=False)

    class Meta:
        verbose_name = "消息"
        verbose_name_plural = verbose_name
        db_table = "message"


class MessageGroup(BaseModel):
    group_name = models.CharField(max_length=225, verbose_name="组名称", unique=True)
    users = models.ManyToManyField(User, null=True)

    class Meta:
        verbose_name = "消息组"
        verbose_name_plural = verbose_name
        db_table = "message_group"
