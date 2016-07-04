#! -*- encoding:utf-8 -*-
from data.db.db_helper import DBYahooDay
from data.info import Infos
from simu_base import SimuStOneByOne


def simple_ma(stock_name):
    """
    简单的基于ma, 5 10
    :param stock_name:
    :type stock_name:str
    """
    # 用一个state表示当前5和10的关系, 0 5 大 1 10 大
    Infos.update_stock_days_list([stock_name, ])
    stock_lines = Infos.stock_days_list[stock_name]
    state = -1
    for index in range(10, len(stock_lines) + 1):
        Infos.update_one_stock_one_day_ma_with_data(stock_name, stock_lines[index - 10:index], d5=1, d10=1)
        avg5 = stock_lines[index - 1][DBYahooDay.line_date_index] + str(
            Infos.stock_ma_list_5[stock_name][stock_lines[index - 1][DBYahooDay.line_date_index]])
        avg10 = stock_lines[index - 1][DBYahooDay.line_date_index] + str(
            Infos.stock_ma_list_10[stock_name][stock_lines[index - 1][DBYahooDay.line_date_index]])

        if state == 0:
            if avg10 > avg5:
                # sell
                state = 1
        elif state == 1:
            if avg5 > avg10:
                # buy
                state = 0


if __name__ == '__main__':
    simple_ma('s600119_ss')
