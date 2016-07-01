#! -*- encoding:utf-8 -*-

# 订单相关的在这里, 依赖于account
from account.account import MoneyAccount, HoldStock


class Order(object):
    """
    订单
    """

    order_type_buy = 0
    order_type_sell = 1

    def __init__(self, stock_name, deal_type, price, count, deal_date, deal_time):
        super(Order, self).__init__()
        # st名称
        self.stock_name = stock_name
        # 类型 0 买入 1 卖出
        self.type = deal_type
        # 交易价格
        self.price = price
        # 交易数量
        self.count = count
        # 交易日期
        self.date = deal_date
        # 交易时间
        self.time = deal_time
        # st的费用
        self.stock_cost = price * count
        # 税和手续费
        self.tax = self.all_tax()
        # 总流水
        self.all_cost = self.stock_cost + self.tax

    def all_tax(self):
        """
        所有的手续费, 税什么都都包含了
        :param cost_order: 产生手续费的order
        :return: 一个float的money
        """
        # 后续需要精确的时候再实现就可以, 现在有个意思一下就行
        return 10


class OrderSys(object):
    """
    定义买卖的接口
    """

    def __init__(self, opt_account):
        """
        :param opt_account:
        :type opt_account: MoneyAccount
        """
        super(OrderSys, self).__init__()
        #  暂时只支持一个账户, 所以直接用一个变量和list来存账户的相关信息
        self.account = opt_account
        self.order_list = list()
        self.err_msg = ''

    def buy(self, stock_name, count, price, buy_date, buy_time):
        """
        执行买入
        :param stock_name: 名称, 用yahoodb的表名
        :param count: 买入数量, 数量必须是100的整数倍, 如果不是, 自动舍去多余部分
        :param price: 买入价格
        :param buy_date: 日期
        :param buy_time: 时间
        :return: 成功与否, 主要就看账户余额够不够
        """
        # 创建一个订单, 不一定交易成功, 只是临时的
        create_order = Order(stock_name, Order.order_type_buy, price, count, buy_date, buy_time)

        # 判定是否能够买入
        if create_order.all_cost > self.account.cash:
            self.err_msg = 'No enough cash'
            return False

        # 可以买, 操作account
        self.account.cash -= create_order.all_cost
        # 建立持仓
        stock = HoldStock()


    def sell(self, stock_name, count, price, buy_date, buy_time):
        """
        执行卖出
        :param stock_name: 名称
        :param count: 卖出数量, 数量必须是100的整数倍, 如果不是, 自动舍去多余部分
        :param price: 卖出价格
        :param buy_date: 日期
        :param buy_time: 时间
        :return: 是否成功, 主要是判定是否有足够的数量来卖
        """

    def buy_with_cash_percent(self, stock_name, percent, buy_date, buy_time):
        """
        按照当前cash的比例买入
        :param stock_name: 名称
        :param percent: 比例, 小数, 乘以100之后才是百分比
        :param buy_date: 日期
        :param buy_time: 时间
        :return: 是否成功
        """

    def sell_with_hold_percent(self, stock_name, percent, buy_date, buy_time):
        """
        按照当前持有该st的比例卖出, 100的零头省略掉
        :param stock_name: 名称
        :param percent: 比例, 小数, 乘以100之后才是百分比
        :param buy_date: 日期
        :param buy_time: 时间
        :return: 是否成功
        """
