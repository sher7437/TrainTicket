from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Train(models.Model):
    name = models.CharField(max_length=100)  # 车次号  D2846
    agroup = models.IntegerField(default=0, null=True)  # 列车组别

    leave_city = models.CharField(max_length=100, null=True)  # 离开城市
    arrive_city = models.CharField(max_length=100, null=True)  # 到达城市

    leave_station = models.CharField(max_length=100, null=True)  # 离开车站
    arrive_station = models.CharField(max_length=100, null=True)  # 到达车站

    leave_time = models.DateTimeField(null=True)  # 离开时间 DateTimeField:date+time
    arrive_time = models.DateTimeField(null=True)  # 到达时间 DateTimeField:date+time

    high_capacity = models.IntegerField(default=0, null=True)  # 商务座位数
    middle_capacity = models.IntegerField(default=0, null=True)  # 一等座位数
    low_capacity = models.IntegerField(default=0, null=True)  # 二等座位数

    high_price = models.FloatField(default=0, null=True)  # 商务座价格
    middle_price = models.FloatField(default=0, null=True)  # 一等座价格
    low_price = models.FloatField(default=0, null=True)  # 二等座价格

    def __str__(self):
        return self.name


class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 建立外键User
    train_name = models.CharField(max_length=100)  # 车次号  D2846
    level = models.CharField(max_length=10)  # 座次等级
    state = models.CharField(max_length=10)  # 车票状态（是否退票）
