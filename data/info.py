#! -*- encoding:utf-8 -*-

# 这里管各种各样的信息, 比如时间, 价格等, 根据需求来实现接口

from datetime import date, time

from data.db.db_helper import DBYahooDay


class Infos(object):
    """
    实时的信息

    因为开始的实现逻辑应该是按照st一个一个的往下进行下去, 所以数据也是一个一个st的,
    而更新数据的结构刚好反过来, 是按照时间, 一行一行的往下进行下去, 然后才是st, 一个一个的
    所以这里虽然用了可一个dict, 实际上, 可能还是一个st, 只是为以后预留一个接口

    如果按照时间-> st的方式来进行, 必须要建立 时间:stock_line 索引, 可能要占用大量内存
    但是现在是是按照 st -> 时间的方式进行, 所以暂时不用建立这个索引,
    """

    # 作为一个静态变量使用, 注意的是, 在任意函数中不能使用赋值操作, 否则, 会变成非静态变量
    stock_days_list = dict()

    def __init__(self):
        """
        数据格式的简单定义
        st日数据的保存方式, {stock_name: stock_lines}, stock_line 通过DBYahooDay定义的line_xxx_index字段访问
        如stock_line[DBYahooDay.line_id_index]
        """
        super(Infos, self).__init__()

    @classmethod
    def update_stock_days_list(cls, stock_list):
        """
        更新日数据(stock_days), 并做成索引
        :param stock_list:
        :type stock_list: list
        """
        yahoo_db = DBYahooDay()
        for stock_name in stock_list:
            # 发现数据如果在, 就不更新了, 因为只要更新一次, 就有了所有的数据, 所以没必要多次更新, 两次更新之前数据不会有任何变化
            if stock_name in cls.stock_days_list:
                continue

            # 取出数据
            stock_lines = yahoo_db.select_stock_all_lines(stock_name)
            cls.stock_days_list[stock_name] = stock_lines
