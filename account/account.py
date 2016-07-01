#! -*- encoding:utf-8 -*-

# 这里管账户的相关信息
# 账户管钱和持仓的变化, 定义明确参数, 注释表明具体是什么意思

from datetime import date, datetime


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
        self.cur_date = datetime.strptime('1971-01-01 12:12:12')
        # 当前持仓的总收益, 去除已经卖出的部分, 因为已经结算到cash中了, 规则: cur_price / cost_price - 1
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
        for key_date in self.unavail_stock_count_dict:
            if (update_date - key_date).days >= 1:
                self.avail_count += self.unavail_stock_count_dict.get(key_date)
                self.unavail_stock_count_dict.pop(key_date)

        # 更新收益
        self.return_percent = (self.cur_price - self.cost_price) / self.cost_price



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
