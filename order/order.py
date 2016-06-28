#! -*- encoding:utf-8 -*-

# 订单相关的在这里, 依赖于account


class Order(object):
    """
    订单
    """

    def __init__(self, deal_type, price, count, deal_time):
        super(Order, self).__init__()
        self.type = deal_type
        self.price = price
        self.count = count
        self.deal_time = deal_time


class OrderSys(object):
    """
    定义买卖的接口
    """

    def __init__(self, opt_account):
        super(OrderSys, self).__init__()
        self.account = opt_account
