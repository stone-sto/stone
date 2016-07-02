#! -*- encoding:utf-8 -*-

# 这里管账户的相关信息
# 账户管钱和持仓的变化, 定义明确参数, 注释表明具体是什么意思
from datetime import date, datetime

from log import time_utils


class HoldStock(object):
    """
    股票的信息, 应该只有变量就可以了
    """

    # 市场规则
    t_plus = 1

    def __init__(self, name):
        """
        :param name: 名称
        :type name: str
        """
        super(HoldStock, self).__init__()
        self.name = name
        # 成本价
        self.cost_price = 0
        # 现价
        self.cur_price = 0
        # 当前持有总数量
        self.count = 0
        # 日期对应的不可卖数量, 字典结构, {日期: 数量}
        self.unavail_stock_count_dict = dict()
        # 可以卖出的数量
        self.avail_count = 0
        # 当前日期, 初始化随便选择一个历史日期
        self.cur_date = datetime.strptime('1971-01-01 12:12:12', time_utils.datetime_format).date()
        # 当前持仓的总收益, 去除已经卖出的部分, 因为已经结算到cash中了, 规则: cur_price / cost_price - 1
        self.return_percent = 0

    def __eq__(self, other):
        """
        :type other: HoldStock
        :rtype: bool
        """
        return self.name == other.name and self.cost_price == other.cost_price and \
               self.cur_price == other.cost_price and self.count == other.count and \
               self.avail_count == other.avail_count and self.cur_date == other.cur_date and \
               self.return_percent == other.return_percent and self.unavail_stock_count_dict == other.unavail_stock_count_dict

    @property
    def stock_whole_property(self):
        """
        st现在的总价值
        """
        return self.cur_price * self.count

    def update_avail_by_date(self, update_date):
        """
        根据时间更新avail
        :param update_date: 日期
        :type update_date: date
        """
        # 更新avail信息
        for key_date in self.unavail_stock_count_dict.keys():
            if (update_date - key_date).days >= self.t_plus:
                self.avail_count += self.unavail_stock_count_dict.get(key_date)
                self.unavail_stock_count_dict.pop(key_date)

    def refresh_returns(self):
        """
        刷新收益, 成本和现价必须已经刷新
        """
        # 更新收益
        if self.cost_price != 0:
            self.return_percent = (self.cur_price - self.cost_price) / self.cost_price
        else:
            self.return_percent = 0

    def update(self, price, update_date):
        """
        根据日期和时间更新st的信息
        :param price: st的当前价格
        :type price: float
        :param update_date: 当前日期
        :type update_date: date
        """
        # 如果日期是过去的时间, 更新无效
        if update_date < self.cur_date:
            print 'HoldStock update failed since the date is passed.'
            return

        # 记录新的数据
        self.cur_price = price
        self.cur_date = update_date

        # 更新avail信息
        self.update_avail_by_date(update_date)
        self.refresh_returns()

    def buy(self, price, count, update_date):
        """
        买入操作
        :param price: 价格
        :type price: float
        :param count: 数量
        :type count: int
        :param update_date: 日期
        :type update_date: date
        :return: 是否成功
        :rtype: bool
        """
        # 同样如果日期是过去的话, 说明有问题, 买入失败
        if update_date < self.cur_date:
            print 'HoldStock buy failed since the date is passed.'
            return False

        # 记录新的数据
        self.cur_price = price
        self.cur_date = update_date

        # 计算成本
        self.cost_price = (self.cost_price * self.count + self.cur_price * count) / (self.count + count)
        # 数量增加
        self.count += count
        # 计算avail
        if update_date in self.unavail_stock_count_dict:
            self.unavail_stock_count_dict[update_date] += count
        else:
            self.unavail_stock_count_dict[update_date] = count
        self.update_avail_by_date(update_date)

        # 更新收益
        self.refresh_returns()

    def sell(self, price, count, update_date):
        """
        卖出操作
        :param price: 价格
        :type price: float
        :param count: 数量
        :type count: int
        :param update_date: 日期
        :type update_date:date
        :return: 是否成功
        :rtype: bool
        """
        # 同样如果日期是过去的话, 说明有问题, 买入失败
        if update_date < self.cur_date:
            print 'HoldStock sell failed since the date is passed.'
            return False

        # 更新avail先
        self.update_avail_by_date(update_date)

        # 确认是否够卖
        if self.avail_count < count:
            print 'HoldStock sell failed since the count is not enough'
            return False

        # 记录新的数据
        self.cur_price = price
        self.cur_date = update_date

        # 搞定数量
        self.count -= count
        self.avail_count -= count

        # 因为时间可能变了, 所以还要更新下收益
        self.refresh_returns()


class MoneyAccount(object):
    """
    账户的信息都在这里了
    """

    def __init__(self, cash, returns):
        super(MoneyAccount, self).__init__()
        # 账户中可用的现金
        self.cash = cash
        # 创建账户开始, 到目前的总收益
        self.returns = returns
        # 账户中的持股情况, 用name做key
        self.stocks = dict()
        # 账户当前总价值
        self.property = cash
        # 账户原始价值
        self.origin_property = cash
        