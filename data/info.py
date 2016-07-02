#! -*- encoding:utf-8 -*-

# 这里管各种各样的信息, 比如时间, 价格等, 根据需求来实现接口

from datetime import date, time

from data.db.db_helper import DBYahooDay


class Infos(object):
    """
    实时的信息
    """

    # 作为一个静态变量使用, 注意的是, 在任意函数中不能使用赋值操作, 否则, 会变成非静态变量
    stock_days = dict()

    def __init__(self):
        """
        数据格式的简单定义
        st日数据的保存方式, {stock_name: stock_lines}, stock_line 通过DBYahooDay定义的line_xxx_index字段访问
        如stock_line[DBYahooDay.line_id_index]
        """
        super(Infos, self).__init__()
        self.yahoo_db = DBYahooDay()

    def update_stock_days(self, stock_list):
        """
        更新日数据(stock_days), 并做成索引
        :param stock_list:
        :type stock_list: list
        """
        for stock_name in stock_list:
            # 发现数据如果在, 就不更新了, 因为只要更新一次, 就有了所有的数据, 所以没必要多次更新, 两次更新之前数据不会有任何变化
            if stock_name in self.stock_days:
                continue

            # 取出数据
            stock_lines = self.yahoo_db.select_stock_all_lines(stock_name)
            self.stock_days[stock_name] = stock_lines

    def update(self, update_date=None, update_time=None, stock_list=None, day=0, minute=0):
        """
        懒惰更新机制: 根据提供的查询的数据, 去数据库取出数据, 计算需要的目标, 放到内存里面

        本质上可能是根据日期, 做多次的存取, 因为一次都取出来, 可能爆内存并且很慢, 但是暂时不会操作太多数量的st, 所以还是都取出来,
        然后用时间做索引, 如果后续慢或者内存成为问题的时候, 再做一个按照时间访问数据库的版本就好.

        执行结束之后, Infos的相应项目会被更新, 直接用就好
        :param update_date:
        :type update_date: date
        :param update_time:
        :type update_time: time
        :param stock_list:
        :type stock_list: list
        :param day: 是否需要日数据, 0 不需要, 1 需要
        :type day: int
        :param minute: 是否需要分钟数据, 0 不需要, 1 需要
        :type minute: int
        """
        # 更新日数据
        if stock_list and day == 1:
            self.update_stock_days(stock_list)
