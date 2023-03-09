from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Permission, User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import datetime
from operator import attrgetter

from .classes import TimeIncome, Order
from .forms import TravelForm, UserForm
from .models import Train, Ticket

ADMIN_ID = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # 所有管理员包括超级的都要加id进来


def result(request):
    """ 搜索结果 """

    if request.method == 'POST':
        # 获取出行信息表单
        form = TravelForm(request.POST)
        form.is_valid()
        passenger_lcity = form.cleaned_data.get('leave_city')
        passenger_acity = form.cleaned_data.get('arrive_city')
        passenger_ldate = form.cleaned_data.get('leave_date')

        # 筛选可用的车次
        result_trains = []
        if passenger_lcity is not None and passenger_acity is not None and passenger_ldate is not None:
            all_trains = Train.objects.filter(leave_city=passenger_lcity, arrive_city=passenger_acity)  # 所有车次
            for train in all_trains:
                passenger_ltime = datetime.datetime.combine(passenger_ldate, datetime.time())  # 加上时分秒
                train.leave_time = train.leave_time.replace(tzinfo=None)  # 不要时区
                if train.leave_time.date() == passenger_ltime.date():
                    result_trains.append(train)

        if passenger_lcity is None and passenger_acity is not None and passenger_ldate is not None:
            all_trains = Train.objects.filter(arrive_city=passenger_acity)
            for train in all_trains:
                passenger_ltime = datetime.datetime.combine(passenger_ldate, datetime.time())
                train.leave_time = train.leave_time.replace(tzinfo=None)
                if train.leave_time.date() == passenger_ltime.date():
                    result_trains.append(train)
            passenger_lcity = ''

        if passenger_lcity is not None and passenger_acity is None and passenger_ldate is not None:
            all_trains = Train.objects.filter(leave_city=passenger_lcity)
            for train in all_trains:
                passenger_ltime = datetime.datetime.combine(passenger_ldate, datetime.time())
                train.leave_time = train.leave_time.replace(tzinfo=None)
                if train.leave_time.date() == passenger_ltime.date():
                    result_trains.append(train)
            passenger_acity = ''

        if passenger_lcity is not None and passenger_acity is not None and passenger_ldate is None:
            result_trains = Train.objects.filter(leave_city=passenger_lcity, arrive_city=passenger_acity)

        if passenger_lcity is None and passenger_acity is None and passenger_ldate is not None:
            passenger_ltime = datetime.datetime.combine(passenger_ldate, datetime.time())
            for train in Train.objects.all():
                train.leave_time = train.leave_time.replace(tzinfo=None)
                if train.leave_time.date() == passenger_ltime.date():
                    result_trains.append(train)
            passenger_lcity = ''
            passenger_acity = ''

        if passenger_lcity is None and passenger_acity is not None and passenger_ldate is None:
            result_trains = Train.objects.filter(arrive_city=passenger_acity)
            passenger_lcity  = ''

        if passenger_lcity is not None and passenger_acity is None and passenger_ldate is None:
            result_trains = Train.objects.filter(leave_city=passenger_lcity)
            passenger_acity = ''

        if passenger_lcity is None and passenger_acity is None and passenger_ldate is None:
            result_trains = Train.objects.all()
            passenger_lcity = ''
            passenger_acity = ''

        # 可用车次排序
        # 按出发时间
        result_trains_by_ltime = sorted(result_trains, key=attrgetter('leave_time'))
        # 按到达时间
        result_trains_by_atime = sorted(result_trains, key=attrgetter('arrive_time'))
        # 按二等座价格
        result_trains_by_price = sorted(result_trains, key=attrgetter('low_price'))

        # 提取小时分钟的时间，变成字符串
        time_format = '%H:%M'
        for train in result_trains_by_price:
            train.leave_time = train.leave_time.strftime(time_format)
            train.arrive_time = train.arrive_time.strftime(time_format)

        # 显示标题栏
        flag_search_title = 'block'
        flag_search_empty = 'none'
        flag_pic = 'none'
        # 如果没有符合条件的车次，显示搜索为空
        if len(result_trains_by_price) == 0:
            flag_search_title = 'none'
            flag_search_empty = 'block'
            flag_pic = 'none'

        webpage_info = {
            # 搜索框内容
            'leave_city': passenger_lcity,
            'arrive_city': passenger_acity,
            'leave_date': str(passenger_ldate),
            # 三种排序的搜索结果
            'result_trains_by_ltime': result_trains_by_ltime,
            'result_trains_by_atime': result_trains_by_atime,
            'result_trains_by_price': result_trains_by_price,
            # 显示标志
            'flag_search_title': flag_search_title,
            'flag_search_empty': flag_search_empty,
            'flag_pic': flag_pic
        }

        # 显示可用列车
        if request.user.is_authenticated:
            webpage_info['username'] = request.user.username
        return render(request, 'booksystem/result.html', webpage_info)

    else:
        webpage_info = {'flag_search_title': 'none', 'flag_search_empty': 'none'}
    return render(request, 'booksystem/result.html', webpage_info)


@csrf_exempt
def book_ticket(request, train_name):
    """ 点购票之后 """

    # 如果没登录，登录
    if not request.user.is_authenticated:
        return render(request, 'booksystem/login.html')
    else:
        if request.method == 'POST':
            # 获取表单的level
            level = request.POST.get('inlineRadioOptions' + train_name, False)
            if level is False:
                level = request.POST.get('inlineRadioOptions1' + train_name, False)
                if level is False:
                    level = request.POST.get('inlineRadioOptions2' + train_name, False)

            # 查看该用户买了的票
            tickets = Ticket.objects.filter(user=request.user)
            # 同车次同等级只能买一张
            for t in tickets:
                if t.train_name == train_name and t.level == level and t.state == "True":
                    webpage_info = {'username': request.user.username}
                    return render(request, 'booksystem/already_booked.html', webpage_info)

            train = Train.objects.get(name=train_name)

            webpage_info = {'train': train,
                            'username': request.user.username,
                            'level': level}
            # 显示确认页，包含列车信息
            return render(request, 'booksystem/book_train.html', webpage_info)


@csrf_exempt
def book_ticket_again(request):
    """ 确认订票，数据库改变 """

    # 获取将购票信息
    if request.method == 'POST':
        train_name = request.POST.get('train_name')
        username = request.POST.get('username')
        level = request.POST.get('level')

        # 修改剩余座位数
        train = Train.objects.get(name=train_name)
        if level == "high" and train.high_capacity > 0:
            train.high_capacity -= 1
        elif level == "middle" and train.middle_capacity > 0:
            train.middle_capacity -= 1
        elif level == "low" and train.low_capacity > 0:
            train.low_capacity -= 1

        # 保存剩余座位的修改
        train.save()

        # 增加ticket
        the_user = User.objects.get_by_natural_key(username)
        ticket = Ticket.objects.create(user=the_user, train_name=train_name, level=level, state='True')

        return HttpResponseRedirect('/booksystem/result')


def user_center(request):
    """ 用户中心显示个人车票，管理员是财务信息 """

    if request.user.is_authenticated:
        # 如果是管理员，显示revenue
        if request.user.id in ADMIN_ID:
            webpage_info = revenue(request, request.user)  # 生成财务信息
            return render(request, 'booksystem/revenue.html', webpage_info)
        # 如果是用户，显示user_center
        else:
            infos = []
            # 获取该用户的车票放在infos
            tickets = Ticket.objects.filter(user=request.user)
            for t in tickets:
                tr = Train.objects.get(name=t.train_name)
                if t.level == "high":
                    price = tr.high_price
                elif t.level == "middle":
                    price = tr.middle_price
                else:
                    price = tr.low_price
                info = {'name': t.train_name,
                        'leave_city': tr.leave_city, 'leave_station': tr.leave_station,
                        'arrive_city': tr.arrive_city, 'arrive_station': tr.arrive_station,
                        'leave_time': tr.leave_time,
                        'arrive_time': tr.arrive_time,
                        'level': t.level,
                        'price': price,
                        'state': t.state}
                infos.append(info)

            webpage_info = {'infos': infos,
                            'username': request.user.username}

            return render(request, 'booksystem/user_center.html', webpage_info)
    return render(request, 'booksystem/login.html')  # 点用户中心但是没登录，登录


def refund_ticket(request, train_name, user, level):
    """ 退票 """

    # 去数据库里找这张票
    the_user = User.objects.get_by_natural_key(user)
    ticket = Ticket.objects.get(train_name=train_name, user=the_user, level=level, state="True")
    train = Train.objects.get(name=train_name)
    # 修改余票
    if level == "high":
        train.high_capacity += 1
    elif level == "middle":
        train.middle_capacity += 1
    else:
        train.low_capacity += 1
    ticket.state = "False"  # 修改票状态

    train.save()  # 保存修改
    ticket.save()  # 保存修改

    return HttpResponseRedirect('/booksystem/user_center')


def revenue(request, user):
    """ 管理员的用户中心，统计周月年营收 """

    # 所有车票
    all_ticket = Ticket.objects.all()

    # 周月年集合
    week_set = set()
    month_set = set()
    year_set = set()

    # 将每条收入打上时间标签（周月年）
    week_day_high_incomes = []
    week_day_middle_incomes = []
    week_day_low_incomes = []

    month_day_high_incomes = []
    month_day_middle_incomes = []
    month_day_low_incomes = []

    year_day_high_incomes = []
    year_day_middle_incomes = []
    year_day_low_incomes = []

    # 已售出和已退票集合
    order_set = set()
    refund_set = set()

    for ticket in all_ticket:
        # 获取车票上的train信息
        train = Train.objects.get(name=ticket.train_name)
        if not user.groups.filter(name=str(train.agroup)).exists() and not user.username == "mfyj":  # 按照组名分配可以看的班次
            continue

        if ticket.state == "False":
            # 放在退票表里
            route = train.leave_city + ' → ' + train.arrive_city
            if ticket.level == "high":
                price = train.high_price
            elif ticket.level == "middle":
                price = train.middle_price
            else:
                price = train.low_price
            order = Order(ticket.user, ticket.train_name, route, train.leave_time, ticket.level, price, ticket.state)
            refund_set.add(order)
            continue

        # 放在购票表里
        route = train.leave_city + ' → ' + train.arrive_city
        if ticket.level == "high":
            price = train.high_price
        elif ticket.level == "middle":
            price = train.middle_price
        else:
            price = train.low_price
        order = Order(ticket.user, ticket.train_name, route, train.leave_time, ticket.level, price, ticket.state)
        order_set.add(order)

        # 周
        # 获取周
        this_week = train.leave_time.strftime('%W')
        # 添加该周到周集合
        week_set.add(this_week)
        # 添加元组(week, income)
        if ticket.level == "high":
            week_day_high_incomes.append((this_week, train.high_price))
        elif ticket.level == "middle":
            week_day_middle_incomes.append((this_week, train.middle_price))
        else:
            week_day_low_incomes.append((this_week, train.low_price))

        # 月
        # 获取月
        this_month = train.leave_time.strftime('%m')
        # 添加该月到月集合
        month_set.add(this_month)
        # 添加元组(month, income)
        if ticket.level == "high":
            month_day_high_incomes.append((this_month, train.high_price))
        elif ticket.level == "middle":
            month_day_middle_incomes.append((this_month, train.middle_price))
        else:
            month_day_low_incomes.append((this_month, train.low_price))

        # 年
        # 获取年
        this_year = train.leave_time.strftime('%Y')
        # 添加该年到年集合
        year_set.add(this_year)
        # 添加元组(year, income)
        if ticket.level == "high":
            year_day_high_incomes.append((this_year, train.high_price))
        elif ticket.level == "middle":
            year_day_middle_incomes.append((this_year, train.middle_price))
        else:
            year_day_low_incomes.append((this_year, train.low_price))

    # 一周的(week, income)整合为一条TimeIncome类型append在week_incomes中
    week_incomes = []
    for week in week_set:
        temp_high = [inc for (wee, inc) in week_day_high_incomes if wee == week]
        temp_middle = [inc for (wee, inc) in week_day_middle_incomes if wee == week]
        temp_low = [inc for (wee, inc) in week_day_low_incomes if wee == week]

        ticket_sum = len(temp_high) + len(temp_middle) + len(temp_low)  # 总票数
        high_income = sum(temp_high)  # 商务座收入
        middle_income = sum(temp_middle)  # 一等座收入
        low_income = sum(temp_low)  # 二等座收入
        total_income = high_income + middle_income + low_income  # 总收入

        week_income = TimeIncome(week, ticket_sum, high_income, middle_income, low_income, total_income)
        week_incomes.append(week_income)
    # week_incomes周升序排列
    week_incomes = sorted(week_incomes, key=attrgetter('metric'))

    # 一月的(month, income)整合为一条TimeIncome类型append在month_incomes中
    month_incomes = []
    for month in month_set:
        temp_high = [inc for (mon, inc) in month_day_high_incomes if mon == month]
        temp_middle = [inc for (mon, inc) in month_day_middle_incomes if mon == month]
        temp_low = [inc for (mon, inc) in month_day_low_incomes if mon == month]

        ticket_sum = len(temp_high) + len(temp_middle) + len(temp_low)  # 总票数
        high_income = sum(temp_high)  # 商务座收入
        middle_income = sum(temp_middle)  # 一等座收入
        low_income = sum(temp_low)  # 二等座收入
        total_income = high_income + middle_income + low_income  # 总收入

        month_income = TimeIncome(month, ticket_sum, high_income, middle_income, low_income, total_income)
        month_incomes.append(month_income)
    # month_incomes月升序排列
    month_incomes = sorted(month_incomes, key=attrgetter('metric'))

    # 一年的(year, income)整合为一条TimeIncome类型append在year_incomes中
    year_incomes = []
    for year in year_set:
        temp_high = [inc for (yea, inc) in year_day_high_incomes if yea == year]
        temp_middle = [inc for (yea, inc) in year_day_middle_incomes if yea == year]
        temp_low = [inc for (yea, inc) in year_day_low_incomes if yea == year]

        ticket_sum = len(temp_high) + len(temp_middle) + len(temp_low)  # 总票数
        high_income = sum(temp_high)  # 商务座收入
        middle_income = sum(temp_middle)  # 一等座收入
        low_income = sum(temp_low)  # 二等座收入
        total_income = high_income + middle_income + low_income  # 总收入

        year_income = TimeIncome(year, ticket_sum, high_income, middle_income, low_income, total_income)
        year_incomes.append(year_income)
    # year_incomes年升序排列
    year_incomes = sorted(year_incomes, key=attrgetter('metric'))

    webpage_info = {
        'username': user.username,
        'week_incomes': week_incomes,
        'month_incomes': month_incomes,
        'year_incomes': year_incomes,
        'order_set': order_set,
        'refund_set': refund_set
    }
    return webpage_info


def index(request):
    """ 主页 """
    return render(request, 'booksystem/index.html')


def login_user(request):
    """ 登录 """

    if request.method == "POST":
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        user = authenticate(username=username, password=password)
        if user is not None:  # 登录成功
            if user.is_active:
                login(request, user)
                webpage_info = {'username': request.user.username,
                                'flag_search_empty': "none",
                                'flag_search_title': 'none',
                                'flag_pic': 'block'}
                if user.id in ADMIN_ID:  # 如果是管理员显示revenue
                    webpage_info = revenue(request, user)  # 生成财务数据
                    return render(request, 'booksystem/revenue.html', webpage_info)
                else:  # 如果是用户显示user_center
                    return render(request, 'booksystem/result.html', webpage_info)
            else:  # 账号无效
                return render(request, 'booksystem/login.html', {'error_message': 'Your account has been disabled'})
        else:  # 登录失败
            return render(request, 'booksystem/login.html', {'error_message': 'Invalid login'})
    return render(request, 'booksystem/login.html')


def logout_user(request):
    """ 退出登录 """

    logout(request)
    form = UserForm(request.POST or None)
    webpage_info = {
        "form": form,
    }
    # 显示登录页
    return render(request, 'booksystem/login.html', webpage_info)


def register(request):
    """ 注册 """

    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                webpage_info = {'username': request.user.username,
                                'flag_search_empty': "none",
                                'flag_search_title': 'none',
                                'flag_pic': 'block'}
                return render(request, 'booksystem/result.html', webpage_info)  # 注册成功render result 页面
    webpage_info = {"form": form}
    return render(request, 'booksystem/register.html', webpage_info)
