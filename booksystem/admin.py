from django.contrib import admin

from .forms import TrainForm, TicketForm
from .models import Train, Ticket


# 管理系统后台自定义表单管理
class TrainAdmin(admin.ModelAdmin):
    # 需要显示的条目
    list_display = ('name', 'agroup',
                    'leave_city', 'arrive_city',
                    'leave_station', 'arrive_station',
                    'leave_time', 'arrive_time',
                    'high_capacity', 'middle_capacity', 'low_capacity',
                    'high_price', 'middle_price', 'low_price')
    # 需要的过滤器
    list_filter = ('name', 'agroup',
                   'leave_city', 'arrive_city',
                   'leave_station', 'arrive_station',
                   'leave_time', 'arrive_time',
                   'high_capacity', 'middle_capacity', 'low_capacity',
                   'high_price', 'middle_price', 'low_price')
    # 自定义的表
    form = TrainForm
    # 每页显示条目
    list_per_page = 10
    # 时间条索引
    date_hierarchy = 'leave_time'


class TicketAdmin(admin.ModelAdmin):
    # 需要显示的条目
    list_display = ('user',
                    'train_name',
                    'level',
                    'state')
    # 需要的过滤器
    list_filter = ('user',
                   'train_name',
                   'level',
                   'state')
    # 自定义的表
    form = TicketForm
    # 每页显示条目
    list_per_page = 10


# Register your models here.
admin.site.register(Train, TrainAdmin)
admin.site.register(Ticket, TicketAdmin)
