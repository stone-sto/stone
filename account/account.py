#! -*- encoding:utf-8 -*-

# 这里管账户的相关信息
# 账户管钱和持仓的变化, 定义明确参数, 注释表明具体是什么意思


class HoldStock(object):
    """
    股票的信息, 应该只有变量就可以了
    """

    def __init__(self, name, cost, count, avail_count, returns):
        super(HoldStock, self).__init__()
        self.name = name
        # 成本价
        self.cost = cost
        # 当前持有总数量
        self.count = count
        # 可以卖出的数量
        self.avail_count = avail_count
        # 这个st的整体收入, 中间可能包含了多次的卖出, 买入, 包含可能出现了断档, 就是中间并没有持仓
        self.returns = returns
        # 这个st最近一次买入的收入
        self.returns_last_buy = 0
        # 这个st最近一次由持有0手, 到现在的收入
        self.returns_last_group_buy = 0


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
