#! -*- encoding:utf-8 -*-

# 一般的模拟流程,
# 有两种事件: 1. 时间更新, 刷新各个系统中的数据, info中的数据可以懒惰更新. 2. 买入/卖出操作, 更新各个系统中的数据.
from data.info import Infos


class SimuStOneByOne(object):
    """
    上面描述的实际上是一种理想的情况, 现在的情况是st都是单独进行的模拟, 没哟单独建立时间的索引, 无法按照 时间->st 的方式进行,
    只能是 st->时间 的方式, 这个类实现这种方式
    """

    def __init__(self, stock_list):
        """
        :param stock_list: 要尝试的所有st
        :type stock_list: list
        """
        super(SimuStOneByOne, self).__init__()
        self.stock_list = stock_list
        Infos.update_stock_days_list(stock_list)
        self.stock_days_list = Infos.stock_days_list

    def start(self):
        """
        开始执行模拟
        """
        for stock_name in self.stock_list:
            stock_lines = self.stock_days_list[stock_name]
            for stock_line in stock_lines:
                self.on_day_changed(stock_line)

    def on_day_changed(self, stock_line):
        """
        时间改变, 在这里进行数
        :param stock_line: day表中数据的一行, 格式和DBYahooDay一模一样
        :type stock_line: list[float|int|str]
        """