from django.db import models


class User(models.Model):
    """
    只需要user中的少部分信息即可
    都是可读状态
    """
    username = models.CharField(max_length=50, verbose_name="用户名")
    phone_number = models.CharField(max_length=14, verbose_name="手机号", unique=True)
    user_code = models.CharField(max_length=20, verbose_name="用户编码", unique=True)
    is_delete = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class UserProfile(models.Model):
    """
    用户概述
    """
    user = models.OneToOneField(User,
                                verbose_name="用户",
                                db_constraint=False,
                                on_delete=models.CASCADE,
                                related_name="profile_user")
    gender = models.CharField(max_length=20, verbose_name="性别")
    birthday = models.DateField(null=True, blank=True, verbose_name='生日')
    city = models.CharField(max_length=50, blank=True,
                            null=True, verbose_name="城市")
    address = models.CharField(
        max_length=215, blank=True, null=True, verbose_name="地址")

    # 关注与被关注
    follow = models.ManyToManyField(
        User, related_name="user_follow", verbose_name='关注', blank=True)
    followed = models.ManyToManyField(
        User, related_name="user_followed", verbose_name='被关注', blank=True)

    ip = models.GenericIPAddressField(
        verbose_name="注册时ip地址", blank=True, null=True)

    class Meta:
        verbose_name = "个人信息"
        verbose_name_plural = verbose_name
        db_table = "user_profile"
        managed = False
