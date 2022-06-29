from djongo import models


class UserEntity(models.Model):
    user_id = models.IntegerField(verbose_name="用户id")
    username = models.CharField(max_length=50, verbose_name="用户名")
    phone_number = models.CharField(max_length=15, verbose_name="手机号")

    class Meta:
        abstract = True


class Message(models.Model):
    """
    通知
    所有的通知将使用这个模型
    """
    FROM_TYPE = (
        ("issues", "动态消息"),
        ("user", "用户私信"),
        ("shop", "商城消息")
    )

    objects = models.DjongoManager()
    _id = models.ObjectIdField()
    # 消息源
    from_type = models.CharField(choices=FROM_TYPE, verbose_name="消息源", max_length=10)
    message_content = models.TextField(verbose_name="消息内容")
    # 消息是从哪个用户来的，默认系统用户将固定为system
    from_user = models.EmbeddedField(model_container=UserEntity, null=True, blank=True,
                                     default={"user_id": -1, "username": "system"})
    to_user = models.EmbeddedField(model_container=UserEntity)  # 消息接受者
    created_time = models.DateTimeField()
    has_consumed = models.BooleanField(verbose_name="是否已被消费", default=False)

    class Meta:
        verbose_name = "消息"
        verbose_name_plural = verbose_name


class GroupEntity(models.Model):
    group_name = models.CharField(max_length=225, verbose_name="组名称")

    class Meta:
        abstract = True


class WebsocketLog(models.Model):
    """
    连接记录
    """
    objects = models.DjongoManager()
    _id = models.ObjectIdField()
    user = models.EmbeddedField(model_container=UserEntity)
    connect_time = models.DateTimeField()
    disconnect_time = models.DateTimeField()
    groups = models.ArrayField(model_container=GroupEntity, null=True, blank=True)
