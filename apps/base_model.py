from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
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


class GenericModel(BaseModel):
    """通用类
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    @classmethod
    def get_instances(cls, obj):
        obj_model_ct = ContentType.objects.get_for_model(obj)
        ins = cls.logic_objects.filter(
            content_type=obj_model_ct, object_id=obj.id)
        return ins

    @classmethod
    def get_count(cls, obj):
        obj_model_ct = ContentType.objects.get_for_model(obj)
        count = cls.logic_objects.filter(
            content_type=obj_model_ct, object_id=obj.id).count()
        return count

    @classmethod
    def create_instance(cls, obj, *args, **kwargs):
        ins = cls(content_object=obj, *args, **kwargs)
        ins.save()
        return ins

    class Meta:
        abstract = True
