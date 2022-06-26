import datetime

from django.db import models
from django.db.models import QuerySet


class LogicDeleteModelQuerySet(QuerySet):
    def delete(self):
        self.update(is_delete=True, deleted_at=datetime.datetime.now())


class LogicDeleteModelManager(models.Manager):
    _queryset_class = LogicDeleteModelQuerySet

    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False)


class LogicDeleteModel(models.Model):
    """
    逻辑删除的主模型
    """
    is_delete = models.BooleanField(default=False, verbose_name="是否删除")
    # 逻辑删除的manager，大部分操作使用这个
    logic_objects = LogicDeleteModelManager()
    objects = models.Manager()

    def delete(self, using=None, keep_parents=False):
        """重写数据库删除方法实现逻辑删除"""
        self.is_delete = True
        self.delete_at = datetime.datetime.now()
        self.save()

    class Meta:
        abstract = True
