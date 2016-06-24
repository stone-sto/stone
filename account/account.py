#! -*- encoding:utf-8 -*-

# 这里管账户的相关信息
# 账户管钱和持仓的变化, 定义明确参数, 注释表明具体是什么意思


class Stock(object):
    """
    股票的信息, 应该只有变量就可以了
    """

    def __init__(self, name):
        super(Stock, self).__init__()
        self.name = name


class MoneyAccount(object):
    def __init__(self, cash):
        super(MoneyAccount, self).__init__()
        # 账户中可用的现金
        self.cash = cash
