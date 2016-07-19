#! -*- encoding:utf-8 -*-

# 这里管各种各样的信息, 比如时间, 价格等, 根据需求来实现接口

from datetime import date, time

from data.db.db_helper import DBYahooDay
from data.info_utils import average


def make_all_stock_lines_as_dict(start_day=None, end_day=None):
    """
    把指定区间的雅虎日数据做成一个dict返回
    :param start_day:
    :type start_day: str
    :param end_day:
    :type end_day: str
    :return: 格式{st_name:{date: stock_line}}
    :rtype: dict[str, dict[str, list]]
    """


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
    # DBYahooDay格式的日数据{stock_name: stock_lines}
    stock_days_list = dict()

    # 均线{stock_name: {date_str: stock_ma_value}}
    stock_ma_list_5 = dict()
    stock_ma_list_10 = dict()
    stock_ma_list_20 = dict()
    stock_ma_list_30 = dict()
    stock_ma_list_60 = dict()
    stock_ma_list_120 = dict()
    stock_ma_list_250 = dict()

    def __init__(self):
        """
        数据格式的简单定义
        st日数据的保存方式, {stock_name: stock_lines}, stock_line 通过DBYahooDay定义的line_xxx_index字段访问
        如stock_line[DBYahooDay.line_id_index]
        """
        super(Infos, self).__init__()
        self.yahoo_db = DBYahooDay()
        self.stock_names = None

        # 另一种格式的st数据, {date, {stock_name: stock_line}}
        self.date_stock_dict = dict()
        """:type: dict[str, dict[str, list[float|str|int]]]"""

        self.resolve_stock_names()

    def resolve_stock_names(self):
        self.stock_names = self.yahoo_db.select_all_stock_names()

    def resolve_date_stock_dict(self, start_date=None, end_date=None):
        """
        搞定date_stock_dict, 略慢
        :param end_date:
        :type end_date: str
        :param start_date:
        :type start_date: str
        """
        print 'resolve date stock dict ...'
        for stock_name in self.stock_names:
            if start_date and end_date:
                stock_lines = self.yahoo_db.select_period_lines(stock_name, start_date, end_date)
            else:
                stock_lines = self.yahoo_db.select_stock_all_lines(stock_name, need_open=True)

            for stock_line in stock_lines:
                cur_date = stock_line[DBYahooDay.line_date_index]
                if cur_date not in self.date_stock_dict:
                    self.date_stock_dict[cur_date] = dict()
                # make一个stock_name dict
                self.date_stock_dict[cur_date][stock_name] = stock_line

    @classmethod
    def update_stock_days_list(cls, stock_list):
        """
        更新日数据(stock_days), 并做成索引
        :param stock_list:
        :type stock_list: list
        """
        yahoo_db = DBYahooDay()
        yahoo_db.open()
        for stock_name in stock_list:
            # 发现数据如果在, 就不更新了, 因为只要更新一次, 就有了所有的数据, 所以没必要多次更新, 两次更新之前数据不会有任何变化
            if stock_name in cls.stock_days_list:
                continue

            # 取出数据
            stock_lines = yahoo_db.select_stock_all_lines(stock_name)
            cls.stock_days_list[stock_name] = stock_lines
        yahoo_db.close()

    @classmethod
    def update_one_stock_one_day_ma_with_data(cls, stock_name, stock_lines, d5=0, d10=0, d20=0, d30=0, d60=0, d120=0,
                                              d250=0):
        """
        设置均线数据(stock_ma_list[stock_name])
        :param stock_name: 名称, 一次一个
        :type stock_name: str
        :param stock_lines: 数据, 必须是按照日期排好序的, 更新的时候回更新stock_lines[-1]对应日期的数据
        :type stock_lines: list[float|str|int]
        :param d5: 是否需要更新5日均线, 是1 否0
        :type d5:int
        :param d10:
        :type d10:int
        :param d20:
        :type d20:int
        :param d30:
        :type d30:int
        :param d60:
        :type d60:int
        :param d120:
        :type d120:int
        :param d250:
        :type d250:int
        """
        # 暂时使用收盘价做均值
        price_list = [stock_line[DBYahooDay.line_close_index] for stock_line in stock_lines]

        # 解决5日
        if d5 and len(price_list) >= 5:
            if stock_name not in cls.stock_ma_list_5:
                cls.stock_ma_list_5[stock_name] = dict()
            cls.stock_ma_list_5[stock_name][stock_lines[-1][DBYahooDay.line_date_index]] = average(price_list[-5:])

        # 解决10日
        if d10 and len(price_list) >= 10:
            if stock_name not in cls.stock_ma_list_10:
                cls.stock_ma_list_10[stock_name] = dict()
            cls.stock_ma_list_10[stock_name][stock_lines[-1][DBYahooDay.line_date_index]] = average(price_list[-10:])

        # 解决20日
        if d20 and len(price_list) >= 20:
            if stock_name not in cls.stock_ma_list_20:
                cls.stock_ma_list_20[stock_name] = dict()
            cls.stock_ma_list_20[stock_name][stock_lines[-1][DBYahooDay.line_date_index]] = average(price_list[-20:])

        # 解决30日
        if d30 and len(price_list) >= 30:
            if stock_name not in cls.stock_ma_list_30:
                cls.stock_ma_list_30[stock_name] = dict()
            cls.stock_ma_list_30[stock_name][stock_lines[-1][DBYahooDay.line_date_index]] = average(price_list[-30:])

        # 解决60日
        if d60 and len(price_list) >= 60:
            if stock_name not in cls.stock_ma_list_60:
                cls.stock_ma_list_60[stock_name] = dict()
            cls.stock_ma_list_60[stock_name][stock_lines[-1][DBYahooDay.line_date_index]] = average(price_list[-60:])

        # 解决120日
        if d120 and len(price_list) >= 120:
            if stock_name not in cls.stock_ma_list_120:
                cls.stock_ma_list_120[stock_name] = dict()
            cls.stock_ma_list_120[stock_name][stock_lines[-1][DBYahooDay.line_date_index]] = average(price_list[-120:])

        # 解决30日
        if d250 and len(price_list) >= 250:
            if stock_name not in cls.stock_ma_list_250:
                cls.stock_ma_list_250[stock_name] = dict()
            cls.stock_ma_list_250[stock_name][stock_lines[-1][DBYahooDay.line_date_index]] = average(price_list[-250:])
