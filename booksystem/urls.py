"""TrainTicket URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url

from . import views

app_name = 'booksystem'

urlpatterns = [
    url(r'^register/$', views.register, name='register'),  # 注册
    url(r'^login_user/$', views.login_user, name='login_user'),  # 登录
    url(r'^logout_user/$', views.logout_user, name='logout_user'),  # 退出登录
    url(r'^$', views.index, name='index'),  # 主页
    url(r'^result/$', views.result, name='result'),  # 搜索结果
    url(r'^user_center/$', views.user_center, name='user_center'),  # 个人中心
    url(r'^book/train/(?P<train_name>[a-zA-Z0-9]+)/$', views.book_ticket, name='book_ticket'),  # 确认购买车票
    url(r'^book_ticket_again/$', views.book_ticket_again, name='book_ticket_again'),  # 购买车票
    url(r'^refund/train/(?P<train_name>[a-zA-Z0-9]+)/(?P<user>[a-zA-Z0-9]+)/(?P<level>[a-zA-Z]+)/$',
        views.refund_ticket, name='refund_ticket'),  # 退票
]
