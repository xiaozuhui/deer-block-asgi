from django.db import models

from apps import custom_manager


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
