"""
当一个用户的websocket加入进来时
1、服务会搜索其关注的所有的用户id，构建一个group
   发布的内容，将会直接推送给group中的用户
   会根据所有的用户创建对应的推送记录，对于已经登录的用户，推送相关的数据将会显示被消费
   但是没有阅读的用户，将会一直显示未被消费
2、当发布issues后，wsgi将会给asgi发送消息，获得消息后的服务将会将这个issues对应的评论发给所属者
3、评论同上

TODO 我们可能将使用pika+rabbitmq来获取消息
"""
from django.urls import re_path

from apps.message.consumers import issues

websocket_urlpatterns = [
    # 针对个人的通知，主要是系统通知
    # 以及会加入各个不同的组中
    re_path(r'ws/system/notice/(?P<user_id>\w+)/$', issues.NewIssuesMessages.as_asgi()),  # 系统连接，这里的user_id即是消息的源
    re_path(r'ws/notice/(?P<user_id>\w+)/$', issues.NewIssuesMessages.as_asgi()),  # 用户连接，这里携带的user_id即是用户自己的user_id
]
