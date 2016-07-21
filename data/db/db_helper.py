#! -*- encoding:utf-8 -*-

# 所有的数据库打开都写在这里, 每个数据库对应一个类
import sqlite3
import traceback
import os

from log.log_utils import log_by_time


class DBBase(object):
    """
    封装基本的数据库操作
    """

    def __init__(self):
        super(DBBase, self).__init__()
        self.cursor = None
        self.connection = None

    def _db_file_path(self):
        """
        数据库存放位置
        :return: 绝对路径
        """
        return ''

    def _open_connection(self):
        """
        打开数据库
        """
        self.connection = sqlite3.connect(self._db_file_path())
        self.cursor = self.connection.cursor()

    def _close_connection(self):
        """
        关闭数据库
        """
        self.cursor.close()
        self.connection.close()

    def _create_table(self, table_name, table_columns):
        """
        创建表
        :param table_name:     表名
        :param table_columns:  列名和描述信息的list
        """
        self.cursor.execute('create table ' + table_name + ' (' + ','.join(table_columns) + ')')

    def insert_into_table(self, table_name, column_names, column_values):
        """
        向某一个表插入数据
        :param table_name:  表名
        :param column_names:       列名
        :param column_values:      列值
        """
        self.cursor.execute(
            'insert into %s (%s) values (%s)' % (table_name, ','.join(column_names), ','.join(column_values)))


class DBSinaMinute(object):
    """
    掌管新浪格式的分钟数据库, 需要注意的是, 这并不是一个数据库, 而是一组数据库的通用接口
    依赖于DBYahooDay, 因为要从中获取所有st的名字
    数据库的命名方式, st名称_年份, 每个数据库只有一张表, 表明和数据库的名字一致
    """

    _db_file_dir = '/Users/wgx/workspace/data/minute/'

    line_id = 'id'  # 0
    line_open = 'open'  # 1
    line_last_close = 'last_close'  # 2
    line_cur = 'cur'  # 3
    line_high = 'high'  # 4
    line_low = 'low'  # 5
    line_try_buy = 'try_buy'  # 6竞买
    line_try_sell = 'try_sell'  # 7  竞卖
    line_volume = 'volume'  # 8 除了100, 如果和yahoo数据混用, 记得确定下yahoo的数据是不是也除了100
    line_volume_money = 'volume_money'  # 9

    # 依次为买1到买5 卖1到卖5的情况
    line_buy1_volume = 'buy1_volume'  # 10
    line_buy1 = 'buy1'  # 11
    line_buy2_volume = 'buy2_volume'  # 12
    line_buy2 = 'buy2'  # 13
    line_buy3_volume = 'buy3_volume'  # 14
    line_buy3 = 'buy3'  # 15
    line_buy4_volume = 'buy4_volume'  # 16
    line_buy4 = 'buy4'  # 17
    line_buy5_volume = 'buy5_volume'  # 18
    line_buy5 = 'buy5'  # 19

    line_sell1_volume = 'sell1_volume'  # 20
    line_sell1 = 'sell1'  # 21
    line_sell2_volume = 'sell2_volume'  # 22
    line_sell2 = 'sell2'  # 23
    line_sell3_volume = 'sell3_volume'  # 24
    line_sell3 = 'sell3'  # 25
    line_sell4_volume = 'sell4_volume'  # 26
    line_sell4 = 'sell4'  # 27
    line_sell5_volume = 'sell5_volume'  # 28
    line_sell5 = 'sell5'  # 29

    line_date = 'date'  # 30
    line_time = 'time'  # 31

    # 表的列, 不包含id
    columns = (
        line_open, line_last_close, line_cur, line_high,
        line_low, line_try_buy, line_try_sell,
        line_volume, line_volume_money, line_buy1_volume, line_buy1,
        line_buy2_volume, line_buy2, line_buy3_volume, line_buy3,
        line_buy4_volume, line_buy4, line_buy5_volume, line_buy5,
        line_sell1_volume, line_sell1, line_sell2_volume, line_sell2,
        line_sell3_volume, line_sell3, line_sell4_volume, line_sell4,
        line_sell5_volume, line_sell5, line_date, line_time,
    )

    column_dict = {
        line_id: 0,
        line_open: 1,
        line_last_close: 2,
        line_cur: 3,
        line_high: 4,
        line_low: 5,
        line_try_buy: 6,
        line_try_sell: 7,
        line_volume: 8,
        line_volume_money: 9,
        line_buy1_volume: 10,
        line_buy1: 11,
        line_buy2_volume: 12,
        line_buy2: 13,
        line_buy3_volume: 14,
        line_buy3: 15,
        line_buy4_volume: 16,
        line_buy4: 17,
        line_buy5_volume: 18,
        line_buy5: 19,
        line_sell1_volume: 20,
        line_sell1: 21,
        line_sell2_volume: 22,
        line_sell2: 23,
        line_sell3_volume: 24,
        line_sell3: 25,
        line_sell4_volume: 26,
        line_sell4: 27,
        line_sell5_volume: 28,
        line_sell5: 29,
        line_date: 30,
        line_time: 31,
    }

    line_id_index = 0
    line_open_index = 1
    line_last_close_index = 2
    line_cur_index = 3
    line_high_index = 4
    line_low_index = 5
    line_try_buy_index = 6
    line_try_sell_index = 7
    line_volume_index = 8
    line_volume_money_index = 9
    line_buy1_volume_index = 10
    line_buy1_index = 11
    line_buy2_volume_index = 12
    line_buy2_index = 13
    line_buy3_volume_index = 14
    line_buy3_index = 15
    line_buy4_volume_index = 16
    line_buy4_index = 17
    line_buy5_volume_index = 18
    line_buy5_index = 19
    line_sell1_volume_index = 20
    line_sell1_index = 21
    line_sell2_volume_index = 22
    line_sell2_index = 23
    line_sell3_volume_index = 24
    line_sell3_index = 25
    line_sell4_volume_index = 26
    line_sell4_index = 27
    line_sell5_volume_index = 28
    line_sell5_index = 29
    line_date_index = 30
    line_time_index = 31

    def __init__(self, db_year):
        super(DBSinaMinute, self).__init__()
        self.db_year = db_year
        self.stock_names = DBYahooDay().select_all_stock_names()

        # 临时记录打开的状态
        self.con = None
        self.cursor = None

    def clean_minute_date(self):
        """
        清除minute的数据, 慎用
        """
        for stock_name in self.stock_names:
            self.open_one_table(stock_name)
            self.cursor.execute('delete from ' + self.get_table_name(stock_name))
            self.con.commit()
            self.close_one_table()

    def add_one_line_to_table(self, stock_name, value_str):
        """
        向现有的表中添加一行, 需要手动打开和关闭, 手动commit
        :param stock_name: 名称
        :param value_str: 值的list, 顺序必须得对
        """
        self.open_one_table(stock_name)
        self.cursor.execute(
            'insert into %s (%s) values (%s)' % (self.get_table_name(stock_name), ','.join(self.columns), value_str))
        self.con.commit()
        self.close_one_table()

    def open_one_table(self, stock_name):
        """
        打开一张现有的表
        :param stock_name: 名称
        """
        self.con = sqlite3.connect(self.get_db_path(stock_name))
        self.cursor = self.con.cursor()

    def close_one_table(self):
        """
        关闭一张现有的表
        """
        self.cursor.close()
        self.con.close()

    def get_table_name(self, stock_name):
        """
        获取数据库名称
        :param stock_name: st名称
        :return: db名称
        """
        return '%s_%s' % (stock_name, self.db_year)

    def get_db_path(self, stock_name):
        """
        获取数据库的路径, 数据库名称就是数据库表名后面加上db后缀
        :param stock_name: st名称
        :return: st db路径
        """
        return os.path.join(self._db_file_dir, self.get_table_name(stock_name) + '.db')

    def create_all_db_all_tables(self):
        """
        创建所有st的表
        """
        for stock_name in self.stock_names:
            self.open_one_table(stock_name)
            db_columes = (
                self.line_id + ' integer primary key',
                self.line_open + ' double',
                self.line_last_close + ' double',
                self.line_cur + ' double',
                self.line_high + ' double',
                self.line_low + ' double',
                self.line_try_buy + ' double',
                self.line_try_sell + ' double',
                self.line_volume + ' bigint',
                self.line_volume_money + ' bigint',
                self.line_buy1_volume + ' bigint',
                self.line_buy1 + ' double',
                self.line_buy2_volume + ' bigint',
                self.line_buy2 + ' double',
                self.line_buy3_volume + ' bigint',
                self.line_buy3 + ' double',
                self.line_buy4_volume + ' bigint',
                self.line_buy4 + ' double',
                self.line_buy5_volume + ' bigint',
                self.line_buy5 + ' double',
                self.line_sell1_volume + ' bigint',
                self.line_sell1 + ' double',
                self.line_sell2_volume + ' bigint',
                self.line_sell2 + ' double',
                self.line_sell3_volume + ' bigint',
                self.line_sell3 + ' double',
                self.line_sell4_volume + ' bigint',
                self.line_sell4 + ' double',
                self.line_sell5_volume + ' bigint',
                self.line_sell5 + ' double',
                self.line_date + ' varchar(20)',
                self.line_time + ' varchar(20)',
            )
            self.cursor.execute('create table %s (%s)' % (self.get_table_name(stock_name), ','.join(db_columes)))
            self.close_one_table()


class DBYahooDay(DBBase):
    """
    掌管雅虎格式的日数据的数据库
    """

    # 名称表的相关内容
    table_stock_name = 'stock_name'
    stock_name_id = 'id'
    stock_name_name = 'name'

    # st表的列名
    line_id = 'id'  # 0
    line_date = 'date'  # 1
    line_open = 'open'  # 2
    line_high = 'high'  # 3
    line_low = 'low'  # 4
    line_close = 'close'  # 5
    line_volume = 'volume'  # 6
    line_adj_close = 'adj_close'  # 7
    line_percent = 'percent'  # 8
    line_point = 'point'  # 9
    line_divider = 'divider'  # 10
    line_fix = 'fix'  # 11
    line_cur_fix_rate = 'cur_fix_rate'  # 12

    # st表的列和index的关系
    column_dict = {
        line_id: 0,
        line_date: 1,
        line_open: 2,
        line_high: 3,
        line_low: 4,
        line_close: 5,
        line_volume: 6,
        line_adj_close: 7,
        line_percent: 8,
        line_point: 9,
        line_divider: 10,
        line_fix: 11,
        line_cur_fix_rate: 12,
    }

    line_id_index = 0
    line_date_index = 1
    line_open_index = 2
    line_high_index = 3
    line_low_index = 4
    line_close_index = 5
    line_volume_index = 6
    line_adj_close_index = 7
    line_percent_index = 8
    line_point_index = 9
    line_divider_index = 10
    line_fix_index = 11
    line_cur_fix_rate_index = 12

    def __init__(self):
        super(DBYahooDay, self).__init__()

    def open(self):
        self._open_connection()

    def close(self):
        self._close_connection()

    def _db_file_path(self):
        return '/Users/wgx/workspace/data/db_yahoo_day.db'

    def add_column_to_table(self, table_name, column_name, column_desc):
        """
        :param column_desc:
        :type column_desc: str
        :param column_name:
        :type column_name: str
        :param table_name:
        :type table_name: str
        """
        self.cursor.execute('alter table %s add column "%s" %s' % (table_name, column_name, column_desc))

    def update_fix_and_fix_rate(self, stock_name, update_date, fix, rate):
        """
        :param stock_name:
        :type stock_name:str
        :param update_date:
        :type update_date: str
        :param fix:
        :type fix: float
        :param rate:
        :type rate: float
        """
        self.cursor.execute('update %s set fix = %f, cur_fix_rate = %f where date = "%s"' % (
            stock_name, fix, rate, update_date))

    def add_fix_value_to(self, stock_name):
        """
        给一个st加上fix value和fix rate, 表示当前从2000年开始之后的实际价值
        自动删除close为0的行, 因为没有意义
        方法: 遇到上涨或下跌超过10%的, 直接认为价格没变
        对比close, 两种情况:
        1. 正常, rate = last rate, fix = close * rate
        2. 不正常, rate = last_rate * last_close / close, fix = close * rate
        :param stock_name:
        :type stock_name: str
        """
        stock_lines = self.select_stock_all_lines(stock_name, need_open=True)
        # 记录第一天的价格, 并把fix设成close, rate设成1.0
        last_close = stock_lines[0][self.line_close_index]
        last_rate = 1.0
        last_date = stock_lines[0][self.line_date_index]
        self.open()

        self.update_fix_and_fix_rate(stock_name, last_date, last_close, last_rate)
        # 开始计算, 顺便把close 为0的行给删掉
        for stock_line in stock_lines:
            close_price = stock_line[self.line_close_index]
            cur_date = stock_line[self.line_date_index]

            # 如果前一天的close为0, 把数据删掉, 然后更新last close为今天的close
            if last_close == 0:
                self.cursor.execute('delete from %s where date = "%s"' % (stock_name, last_date))
                self.connection.commit()
                last_close = close_price
                last_date = cur_date
                continue

            # 如果当天为0, 没有意义, 所以直接pass就好
            if close_price == 0:
                last_close = close_price
                last_date = cur_date
                continue

            percent = close_price / last_close - 1
            # 不正常
            if percent > 0.11 or percent < - 0.11:
                rate = last_rate * last_close / close_price
                fix = close_price * rate
                self.update_fix_and_fix_rate(stock_name, cur_date, fix, rate)
                last_rate = rate

            # 正常
            else:
                rate = last_rate
                fix = close_price * rate
                self.update_fix_and_fix_rate(stock_name, cur_date, fix, rate)

            last_close = close_price
            last_date = cur_date

        self.connection.commit()
        self.close()

    def del_target_date_lines(self, target_date):
        """
        删除指定日期的行, 慎用
        """
        stock_names = self.select_all_stock_names()
        self.open()
        for stock_name in stock_names:
            self.cursor.execute('delete from ' + stock_name + ' where date = "' + target_date + '"')
        self.connection.commit()
        self.close()

    def select_all_stock_names(self):
        """
        查询所有的表名
        :return: 表名的list
        """
        self.open()
        res = [cell[0] for cell in
               self.cursor.execute('select %s from  %s order by %s' % (
                   self.stock_name_name, self.table_stock_name, self.stock_name_name)).fetchall()]
        self.close()
        return res

    def create_stock_name_table(self):
        """
        创建包含股票名称的表, 后续可以增加一些备注字段, 比如首先, 是否可用, 连续可用日期等
        """
        self._open_connection()
        self._create_table(self.table_stock_name,
                           [self.stock_name_id + ' integer primary key', self.stock_name_name + ' varchar(20)'])
        self._close_connection()

    def add_row_to_stock_name_table(self, name):
        """
        想保存表名称的表中插入一行
        :param name: 插入的st名称
        """
        self.insert_into_table(self.table_stock_name, (self.stock_name_name,), ("'%s'" % name,))
        self.connection.commit()

    def create_st_table(self, stock_name):
        """
        创建指定的st表
        :param stock_name: 表名
        """
        table_columns = (
            self.line_id + ' integer primary key',
            self.line_date + ' varchar(20)',
            self.line_open + ' double',
            self.line_high + ' double',
            self.line_low + ' double',
            self.line_close + ' double',
            self.line_volume + ' bigint',
            self.line_adj_close + ' double',
            self.line_percent + ' double',
            self.line_point + ' double',
            self.line_divider + ' integer',
        )
        self._create_table(stock_name, table_columns)

    def check_and_del_empty_table_name(self):
        """
        删除stock_name中对应名称表为空的行以及空表
        """
        self.open()
        stock_lines = self.cursor.execute('select * from ' + self.table_stock_name).fetchall()
        for stock_line in stock_lines:
            stock_name = stock_line[1]
            print stock_name
            try:
                data_lines = self.cursor.execute('select * from ' + stock_name).fetchall()
                if len(data_lines) <= 0:
                    print stock_name + ' table is empty'
                    self.cursor.execute('drop table ' + stock_name)
                    self.connection.commit()
                    print stock_name + ' table removed'
            except:
                print stock_name + ' table not exist'
                traceback.print_exc()
        self.close()

    def check_if_is_done(self, stock_name):
        """
        检查指定的st名称是否done
        :param stock_name: 名称
        :return:           是否done
        """
        res = self.cursor.execute('select %s from %s where %s="%s"' % (
            self.stock_name_name, self.table_stock_name, self.stock_name_name, stock_name))
        return not len(res.fetchall()) == 0

    def select_stock_all_lines(self, stock_name, order=0, need_open=False):
        """
        查询st的所有行, 需要手动打开数据库
        :param need_open: 是否需要打开数据库
        :type need_open: bool
        :param stock_name: 名称
        :param order:   是否排序 0 asc 1 desc
        :return: st line list
        """
        if need_open:
            self.open()
        sql_str = 'select * from ' + stock_name
        if order == 0:
            sql_str += ' order by date'
        elif order == 1:
            sql_str += ' order by date desc'

        res = self.cursor.execute(sql_str).fetchall()
        if need_open:
            self.close()

        return res

    def select_period_lines(self, stock_name, start_date, end_date):
        """
        查询st指定时间段的所有行
        :param stock_name:
        :type stock_name: str
        :param start_date:
        :type start_date: date
        :param end_date:
        :type end_date: str
        :return:
        :rtype: list
        """
        self.open()
        sql_str = 'select * from %s where %s >= "%s" and %s <= "%s" order by %s' % (
            stock_name, self.line_date, start_date, self.line_date, end_date, self.line_date)
        res = self.cursor.execute(sql_str).fetchall()
        self.close()
        return res

    def update_target_date_percent_and_divider(self, stock_name, date, percent, divider):
        """
        修改指定st的各个字段, 需要手动打开数据库,手动commit
        :param stock_name:名称
        :param percent: 增幅
        """
        self.cursor.execute(
            'update %s set %s=%f,%s=%d where %s="%s"' % (
                stock_name, self.line_percent, percent, self.line_divider, divider, self.line_date, date))

    def del_duplicate_lines_for_stock_days(self):
        """
        删除st表中的重复的行
        """
        stock_names = self.select_all_stock_names()
        for stock_name in stock_names:
            print stock_name
            stock_lines = self.select_stock_all_lines(stock_name, need_open=True)
            self.open()
            last_date = stock_lines[0][self.line_date_index]
            for index in range(1, len(stock_lines)):
                cur_date = stock_lines[index][self.line_date_index]
                if last_date == cur_date:
                    # 重复了, 干掉
                    cur_id = stock_lines[index][self.line_id_index]
                    self.cursor.execute('delete from %s where %s = %d' % (stock_name, self.line_id, cur_id))
                    self.connection.commit()
                last_date = cur_date
            self.close()

    def del_duplicate_lines_for_table_name(self):
        """
        删除stock_name表中出现的重复数据
        """
        self.open()
        # 获取所有数据
        stock_name_lines = self.cursor.execute(
            'select * from %s order by %s' % (self.table_stock_name, self.stock_name_name)).fetchall()
        last_name = stock_name_lines[0][1]
        for index in range(1, len(stock_name_lines)):
            cur_name = stock_name_lines[index][1]
            if last_name == cur_name:
                # 删除当前行
                cur_id = stock_name_lines[index][0]
                self.cursor.execute(
                    'delete from %s where %s = %d' % (self.table_stock_name, self.stock_name_id, cur_id))
                self.connection.commit()
            last_name = cur_name
        self.close()

    def do_clean_datas(self):
        """
        对日数据进行clean, close price 为0, 干掉, 成交量为0, 干掉(排除指数)
        """
        tem_list = ['s000001_ss', 's399001_sz', 's399006_sz']
        stock_names = self.select_all_stock_names()
        for stock_name in stock_names:

            print stock_name

            # 如果是指数, 不处理
            if stock_name in tem_list:
                continue

            # 删除
            self.open()
            self.cursor.execute('delete from %s where %s = 0 or %s=0' % (stock_name, self.line_close, self.line_volume))
            self.connection.commit()
            self.close()

    def update_target_date_point(self, stock_name, date, point):
        """
        修改指定st的point
        :param stock_name:名称
        :param point:评分
        """
        self.cursor.execute(
            'update %s set %s=%f where %s="%s"' % (stock_name, self.line_point, point, self.line_date, date))

    def fill_percent_for_all_stock(self, last_index=0):
        """
        处理percent
        """
        stock_names = self.select_all_stock_names()
        self.open()
        stock_count = 0
        if last_index == 0:
            start_index = 0
        else:
            start_index = last_index - 1
        for stock_name in stock_names:
            stock_lines = self.select_stock_all_lines(stock_name)

            # 用来记录上次出现的价格和日期
            last_close_price = -1
            last_date = None
            last_percent = None
            # 开始干活
            for stock_line in stock_lines[start_index:]:
                # 如果没保存过价格, 那么保存价格, 进入下一轮
                if not last_date:
                    last_date = stock_line[self.column_dict.get(self.line_date)]
                    last_close_price = stock_line[self.column_dict.get(self.line_close)]
                    # 第一天的percent写0, divider写0
                    # self.update_target_date_percent_and_divider(stock_name, last_date, 0, 0)

                # 上次的日期存在, 证明上一行是存在的
                else:
                    # 记录当前的价格, 日期
                    cur_price = stock_line[self.column_dict.get(self.line_close)]
                    cur_date = stock_line[self.column_dict.get(self.line_date)]

                    if last_close_price <= 0:
                        # 上次出现的价格有问题, 写入percent 为0, divider为1
                        self.update_target_date_percent_and_divider(stock_name, cur_date, 0, 1)
                    else:
                        last_percent = cur_price / last_close_price - 1
                        # percent超过了10%或者-10%, 证明出现了问题, percent照常记录, divider为1
                        if last_percent > 0.11 or last_percent < -0.11:
                            self.update_target_date_percent_and_divider(stock_name, cur_date, last_percent, 1)
                        else:
                            # 数据没问题,正常写入,divider为0
                            self.update_target_date_percent_and_divider(stock_name, cur_date, last_percent, 0)

                    # 保存当前日期为上次日期
                    last_date = cur_date
                    last_close_price = cur_price

                log_by_time(stock_name + ' ' + str(last_percent) + ' ' + str(stock_count))
            # 每完成一个st, commit一次
            self.connection.commit()
            stock_count += 1

        self.close()

    def select_stock_lines_by_date(self, stock_name, stock_date):
        """
        找到指定
        :param stock_name 名称
        :param stock_date 日期
        :return stock lines
        """
        return self.cursor.execute(
            'select * from %s where %s="%s"' % (stock_name, self.line_date, stock_date)).fetchall()

    def fill_point_for_all_stock(self, last_index=0):
        """
        处理point
        """
        stock_names = self.select_all_stock_names()
        self.open()
        # 先把三大指数做成字典{date:percent}
        # 指数的list
        # 创业板指数据找不到, 所以暂时用深证替换吧
        tem_names = ('s399001_sz', 's000001_ss')
        tem_ss = dict()
        tem_sz = dict()
        dicts = (tem_sz, tem_ss)
        for i in range(0, 2):
            tem_name = tem_names[i]
            tem_dict = dicts[i]
            stock_lines = self.select_stock_all_lines(tem_name)

            for stock_line in stock_lines:
                # 往字典中放值
                tem_dict[stock_line[self.column_dict.get(self.line_date)]] = stock_line[
                    self.column_dict[self.line_percent]]

        # 搞定每个st的percent
        stock_count = 0
        for stock_name in stock_names:

            # 先判定该用哪个dict
            if stock_name.endswith('ss'):
                use_dict = dicts[1]
            elif stock_name.startswith('s3'):
                use_dict = dicts[0]
            else:
                use_dict = dicts[0]

            # 填充每一行
            stock_lines = self.select_stock_all_lines(stock_name)
            for stock_line in stock_lines[last_index:]:
                cur_date = stock_line[self.column_dict.get(self.line_date)]
                if cur_date in use_dict:
                    cur_point = (stock_line[self.column_dict.get(self.line_percent)] - use_dict.get(cur_date)) * 100
                else:
                    cur_point = 0
                self.update_target_date_point(stock_name, cur_date, cur_point)

                log_by_time(
                    'set point for %s at %s with point %f num %d' % (stock_name, cur_date, cur_point, stock_count))
            stock_count += 1

            # 搞定一个st, commit一次
            self.connection.commit()

        self.close()


if __name__ == '__main__':
    pass

    # 删除重复的st行
    # DBYahooDay().del_duplicate_lines_for_stock_days()
    # 删除重复的st名称
    # DBYahooDay().del_duplicate_lines_for_table_name()

    # 填充fix和rate
    # yh = DBYahooDay()
    # stock_names = yh.select_all_stock_names()
    #
    # for stock_name in stock_names:
    #     print stock_name
    #     yh.add_fix_value_to(stock_name)

    # 删除某一日期的数据
    # yahoo_db = DBYahooDay()
    # yahoo_db.del_target_date_lines('2016-06-28')
    # 创建所有分钟的数据表
    # sina_db = DBSinaMinute(2015)
    # sina_db.clean_minute_date()

    # 更新前几天的percent
    # yahoo_db = DBYahooDay()
    # yahoo_db.fill_percent_for_all_stock(-1)
    # yahoo_db.fill_point_for_all_stock(-1)
