class Order:
    """ 订单 """
    passenger_name = ''  # 乘客名
    train_name = ''  # 车次号
    train_route = ''  # 路程
    train_ltime = ''  # 离开时间
    train_level = ''  # 座次等级
    train_price = ''  # 订单价格
    train_state = ''  # 订单状态

    def __init__(self, pname, fname, froute, fltime, flevel, fprice, fstate):
        self.passenger_name = pname
        self.train_name = fname
        self.train_route = froute
        self.train_ltime = fltime
        self.train_level = flevel
        self.train_price = fprice
        self.train_state = fstate


class TimeIncome:
    """ 财务统计时用（周月年） """
    metric = '00'  # 时间段度量标准
    ticket_sum = 0  # 总票数
    high_incomes = 0  # high
    middle_incomes = 0  # middle
    low_incomes = 0  # low
    total_incomes = 0  # 总收入

    def __init__(self, metric, ticket_sum, high_incomes, middle_incomes, low_incomes, total_incomes):
        self.metric = metric
        self.ticket_sum = ticket_sum
        self.high_incomes = high_incomes
        self.middle_incomes = middle_incomes
        self.low_incomes = low_incomes
        self.total_incomes = total_incomes
