#! -*- encoding:utf-8 -*-

# 这里管各种各样的信息, 比如时间, 价格等, 根据需求来实现接口
import traceback
from datetime import date, time

import sqlite3

from data.db.db_helper import DBYahooDay
from data.info_utils import average, build_stock_data_frame
import pandas as pd
import numpy as np


class DBInfoCache(object):
    """
    一个用来放临时数据的db, 比如整个close price的DataFrame, 利用to_sql和read_sql来快速的读取到内存中
    使用set不断的更新, 实际上数据没必要一直是最新的, 所以无聊的时候更新一下就行
    用get直接从数据库中取出来, 应该比一下下merge要快得多
    fix的DataFrame是40m, 估计其他的也差不多这个规模
    """
    db_file_path = '/Users/wgx/workspace/data/cache_db.db'
    table_name_fix_part1 = 'fix_part1'
    table_name_fix_part2 = 'fix_part2'
    table_name_fix_part3 = 'fix_part3'

    def __init__(self):
        super(DBInfoCache, self).__init__()
        self.connection = None
        """:type:sqlite3.Connection"""
        self.cursor = None
        """:type:sqlite3.Cursor"""

    def open(self):
        self.connection = sqlite3.connect(self.db_file_path)
        self.cursor = self.connection.cursor()

    def close(self):
        self.cursor.close()
        self.connection.close()

    def set_fix(self):
        """
        设置fix的DataFrame
        """
        self.open()
        try:
            self.cursor.execute('drop table ' + self.table_name_fix_part1)
            self.cursor.execute('drop table ' + self.table_name_fix_part2)
            self.cursor.execute('drop table ' + self.table_name_fix_part3)
        except:
            traceback.print_exc()

        res_data = build_stock_data_frame(DBYahooDay.line_fix)
        res_data = res_data.sort_values(by='date')
        res_data.iloc[:, 0:1000].to_sql(self.table_name_fix_part1, self.connection)
        res_data.iloc[:, 1000:2000].to_sql(self.table_name_fix_part2, self.connection)
        res_data.iloc[:, 2000:].to_sql(self.table_name_fix_part3, self.connection)

        self.close()

    def get_fix(self):
        """
        获取fix的DataFrame
        :return:
        :rtype: pd.DataFrame
        """
        self.open()

        part1 = pd.read_sql('select * from %s' % self.table_name_fix_part1,
                            self.connection)
        part2 = pd.read_sql('select * from %s' % self.table_name_fix_part2,
                            self.connection)
        part3 = pd.read_sql('select * from %s' % self.table_name_fix_part3,
                            self.connection)

        res_data = part1.merge(part2, how='left', left_on='index', right_on='index')
        res_data = res_data.merge(part3, how='left', left_on='index', right_on='index')

        self.close()

        print res_data

        # 数据的格式还有点问题, 需要fix一下
        date_list = res_data['date']
        del res_data['date']
        del res_data['index']
        res_data.index = date_list

        # 上证的部分日期对应的数据无意义, 导致其他的数据都是NaN, 把这样的行都给干掉
        res_data = res_data.dropna(axis='index', thresh=2)

        return res_data


if __name__ == '__main__':
    # yh = DBYahooDay()
    # yh.open()
    # column_name = 'fix'
    # stock_name = 's300249_sz'
    # s300249 = pd.read_sql(
    #     'select date, %s as %s from %s order by date' % (column_name, stock_name, stock_name),
    #     yh.connection)
    # stock_name = 's603999_ss'
    # s3999 = pd.read_sql(
    #     'select date, %s as %s from %s order by date' % (column_name, stock_name, stock_name),
    #     yh.connection)
    #
    # print s300249
    # print s3999
    # merge_res = pd.merge(s300249, s3999, how='left', left_on='date', right_on='date')
    # merge_res.index = merge_res['date']
    # print merge_res.loc['2015-10-15', 's603999_ss']
    # yh.close()

    import datetime

    before = datetime.datetime.now()
    print before

    DBInfoCache().set_fix()

    after = datetime.datetime.now()
    print after

    print after - before


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
