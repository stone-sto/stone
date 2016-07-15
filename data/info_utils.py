# -*- encoding:utf-8 -*-

# 这里放用来计算各种param的工具
from data.db.db_helper import DBYahooDay


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
    pass
    res_dict = stock_date_dict()
    for date_key in res_dict.keys():
        stock_lines = res_dict[date_key]
        print date_key
        for stock_line in stock_lines:
            print stock_line[0]
