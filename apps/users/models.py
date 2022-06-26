from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.users import custom_manager


class BaseModel(custom_manager.LogicDeleteModel):
    """
    基础模型，继承django的模型和逻辑删除主模型
    """
    created_at = models.DateTimeField(
        verbose_name="数据创建时间", auto_now=True, null=True)
    updated_at = models.DateTimeField(
        verbose_name="数据更新时间", auto_now_add=True, null=True)
    deleted_at = models.DateTimeField(
        verbose_name="数据失效时间", null=True, blank=True)

    class Meta:
        abstract = True


class User(AbstractUser, BaseModel):
    """
    自定义用户信息, 使用基本user, 加入手机号即可
    """
    phone_number = models.CharField(
        max_length=14, verbose_name="手机号", unique=True)

    class Meta:
        managed = False
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ['id']
