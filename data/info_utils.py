# -*- encoding:utf-8 -*-

# 这里放用来计算各种param的工具
from data.db.db_helper import DBYahooDay
import pandas as pd


def all_dates():
    """
    返回yahoo数据中的所有date, 实际上以上证指数的数据为准
    :return: 时间的list
    :rtype: list[str]
    """
    yahoo_db = DBYahooDay()
    yahoo_db.open()
    date_list = yahoo_db.cursor.execute('select date from s000001_ss order by date').fetchall()
    yahoo_db.close()
    return date_list


def build_stock_name_dict():
    """
    返回所有st的name dict, 格式{stock_name, stock_lines}
    :return:
    :rtype: dict[str, list]
    """
    yahoo_db = DBYahooDay()
    stock_names = yahoo_db.select_all_stock_names()
    res_dict = dict()
    for stock_name in stock_names:
        res_dict[stock_name] = yahoo_db.select_stock_all_lines(stock_name, need_open=True)
    return res_dict


def build_stock_data_frame(column_name='close'):
    """
    用pandas和numpy做一个数据集合, 列名: st名称, 行名: 日期, 内容: 指定列的内容, 一次只能一列
    :param column_name:
    :type column_name:
    :return: 数据集
    :rtype: pd.DataFrame
    """
    yahoo_db = DBYahooDay()
    # 名称集合
    stock_names = yahoo_db.select_all_stock_names()

    yahoo_db.open()
    res_data = build_stock_data_frame_recursive(stock_names, yahoo_db.connection, column_name)
    yahoo_db.close()
    return res_data


def build_stock_data_frame_recursive(stock_names, connection, column_name):
    """
    递归的方式建立某一列的DataFrame
    :param stock_names:
    :type stock_names:
    :param connection:
    :type connection:
    :param column_name: DBYahooDay中对应的列名
    :type column_name: str
    :return: 数据矩阵
    :rtype: pd.DataFrame
    """
    name_len = len(stock_names)
    if name_len >= 2:
        left_part = build_stock_data_frame_recursive(stock_names[0: name_len / 2], connection, column_name)
        right_part = build_stock_data_frame_recursive(stock_names[name_len / 2:], connection, column_name)
        if left_part is None:
            return right_part
        elif right_part is None:
            return left_part
        else:
            return pd.merge(left_part, right_part, how='left', left_on='date', right_on='date')
    elif name_len == 1:
        return pd.read_sql(
            'select date, %s as %s from %s order by date' % (column_name, stock_names[0], stock_names[0]),
            connection)


def average(source_list):
    """
    求平均数
    :param source_list:
    :type source_list: list
    :return:
    :rtype: float
    """
    if len(source_list) > 0:
        return float(sum(source_list)) / len(source_list)
    else:
        return 0.0


def stock_date_dict(start_date=None, end_date=None):
    """
    :param start_date:
    :type start_date: str
    :param end_date:
    :type end_date: str
    :return:
    :rtype: dict[str, list]
    """
    yahoo_db = DBYahooDay()
    stock_names = yahoo_db.select_all_stock_names()
    res_dict = dict()
    """:type: dict[str, list]"""
    for stock_name in stock_names:
        print stock_name
        if start_date and end_date:
            stock_lines = yahoo_db.select_period_lines(stock_name, start_date, end_date)
        else:
            stock_lines = yahoo_db.select_stock_all_lines(stock_name, need_open=True)

        for stock_line in stock_lines:
            cur_date = stock_line[DBYahooDay.line_date_index]
            final_stock_line = list(stock_line)
            final_stock_line[0] = stock_name
            if not cur_date in res_dict:
                res_dict[cur_date] = list()
            res_dict[cur_date].append(final_stock_line)

    return res_dict


def all_stock_and_clean_day_dict(start_date=None, end_date=None):
    """
    把指定时间的雅虎日数据做成一个dict
    :param end_date:
    :type end_date: str
    :param start_date:
    :type start_date: str
    :return:
    :rtype: dict[str, dict[str, list[float|str|int]]]
    """
    yahoo_db = DBYahooDay()
    # 结果的dict, 保存st的相关分组的时间表
    res_dict = dict()
    stock_names = yahoo_db.select_all_stock_names()
    for stock_name in stock_names:
        print stock_name
        stock_lines_group = all_stock_and_clean_day_lines(stock_name, start_date, end_date)
        for stock_lines in stock_lines_group:
            # 分组的dict
            stock_group_dict = dict()
            # 分组的key
            stock_group_key = stock_name + stock_lines[0][DBYahooDay.line_date_index]
            res_dict[stock_group_key] = stock_group_dict
            # 开始建dict
            for stock_line in stock_lines:
                stock_group_dict[stock_line[DBYahooDay.line_date_index]] = stock_line

    return res_dict


def all_stock_and_clean_day_lines(stock_name, start_date=None, end_date=None):
    """
    获取一个st的所有clean group
    :param start_date:
    :type start_date: str
    :param end_date:
    :type end_date: str
    :param stock_name:
    :type stock_name: str
    :return: clean group
    :rtype: list
    """
    yahoo_db = DBYahooDay()
    yahoo_db.open()
    if start_date and end_date:
        res = yahoo_db.select_period_lines(stock_name, start_date, end_date)
    else:
        res = yahoo_db.select_stock_all_lines(stock_name)
    yahoo_db.close()
    return clean_day_lines(res)


def clean_day_lines(stock_lines, min_length=10):
    """
    将数据分段, 以divider字段为1进行分割, 每个为1的部分都是一段的开始, 除了第一段
    :param min_length: 最短的数据长度, 因为太少的数据来模拟没有任何意义
    :type min_length: int
    :param stock_lines: 数据原
    :type stock_lines: list
    :return: 数据分段的list
    :rtype: list[list]
    """
    tmp_res = list()
    final_res = list()
    for stock_line in stock_lines:

        # 如果出现divider
        if stock_line[DBYahooDay.line_divider_index] == 1:
            # 长度大于min_length, 才有意义
            if len(tmp_res) >= min_length:
                final_res.append(tmp_res)
            tmp_res = list()
            tmp_res.append(stock_line)

        # 否则
        else:
            tmp_res.append(stock_line)
    if len(tmp_res) >= min_length:
        final_res.append(tmp_res)
    return final_res


def resolve_ma(stock_lines, n):
    """
    计算均线,
    :param n: 周期
    :type n: int
    :param stock_lines: 数据, len必须超过period_list中的最大值, 且必须按照日期排好序
    :type stock_lines: list
    :return: 均值
    :rtype: float
    """
    if len(stock_lines) >= n:
        return average([stock_line[DBYahooDay.line_close_index] for stock_line in stock_lines][-n:])
    else:
        return 0


if __name__ == '__main__':
    import datetime

    time_before = datetime.datetime.now()
    print time_before

    print build_stock_data_frame()

    time_after = datetime.datetime.now()
    print time_after

    print time_after - time_before
