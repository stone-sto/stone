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


def all_stock_and_clean_day_lines(stock_name):
    """
    获取一个st的所有clean group
    :param stock_name:
    :type stock_name: str
    :return: clean group
    :rtype: list
    """
    yahoo_db = DBYahooDay()
    yahoo_db.open()
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
    # 测试clean_dsy_lines
    yahoo_db = DBYahooDay()
    yahoo_db.open()
    stock_lines = yahoo_db.select_stock_all_lines('s600153_ss')
    yahoo_db.close()
    res_list = clean_day_lines(stock_lines)
    for tmp_list in res_list:
        print [stock_line[DBYahooDay.line_date_index] for stock_line in tmp_list]
