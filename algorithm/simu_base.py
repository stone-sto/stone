#! -*- encoding:utf-8 -*-

# 一般的模拟流程,
# 有两种事件: 1. 时间更新, 刷新各个系统中的数据, info中的数据可以懒惰更新. 2. 买入/卖出操作, 更新各个系统中的数据.
from account.account import MoneyAccount
from data.info import Infos
from data.info_utils import all_stock_and_clean_day_lines


class SimuOneStock(object):
    """
    按照固定模式, simu一个st
    流程:
    1. 准备好数据, 按照数据迭代
    2. 设置好表格, 账户,
    """
    def __init__(self, stock_name, al_name):
        """
        :param stock_name:
        :type stock_name: str
        :param al_name: 算法名称
        :type al_name: str
        """
        super(SimuOneStock, self).__init__()
        self.stock_name = stock_name

    def start(self):
        stock_lines_group = all_stock_and_clean_day_lines(self.stock_name)
        for stock_lines in stock_lines_group:
            self.loop_for_one_group(stock_lines)

    def loop_for_one_group(self, stock_lines):
        """
        :param stock_lines: st的一个分组
        :type stock_lines: list
        """
        self.money_account = MoneyAccount(100000)




class SimuStOneByOne(object):
    """
    上面描述的实际上是一种理想的情况, 现在的情况是st都是单独进行的模拟, 没哟单独建立时间的索引, 无法按照 时间->st 的方式进行,
    只能是 st->时间 的方式, 这个类实现这种方式

    时间->st 的这种方式, 实际上要有选股的策略才能实施, 暂时只是想统计各种情况下的概率而已, 所以只针对一个st来进行就可以了
    流程,
    1. 在setup中告诉infos获取需要的数据

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