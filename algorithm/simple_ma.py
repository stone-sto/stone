#! -*- encoding:utf-8 -*-
import os

from account.account import MoneyAccount
from chart.chart_utils import draw_line_chart, default_colors
from data.db.db_helper import DBYahooDay
from data.info import Infos
from data.info_utils import all_stock_and_clean_day_lines, resolve_ma
from log.log_utils import log_by_time, log_with_filename
from simu_base import SimuStOneByOne


# 几种ma
# 按照规则, 简单买卖, simple_ma
# 按照规则, 多仓位买卖, multi_opt_ma
# 按照规则, 指定盈利百分比买卖, win_percent_ma
# 按照规则, 多仓位, 指定盈利百分比买卖, multi_opt_win_percent_ma


def simple_ma(stock_name, n=10, m=20):
    """
    简单的基于ma, 5 10
    :param n: 均值中比较小的周期
    :type n: int
    :param m: 均值中比较大的周期
    :type m: int
    :param stock_name:
    :type stock_name:str
    """
    stock_lines_group = all_stock_and_clean_day_lines(stock_name)
    chart_dir_name = 'simple_ma_%d_%d' % (n, m)
    chart_dir_path = os.path.join(os.path.dirname(__file__), '../result', chart_dir_name)
    if not os.path.exists(chart_dir_path):
        os.system('mkdir -p "' + chart_dir_path + '"')
    for stock_lines in stock_lines_group:

        # 表示当前的n和m的状态, 0 n 上 1 m 上
        state = -1
        money_account = MoneyAccount(100000)

        # 关于作图
        chart_title = stock_name + '-' + stock_lines[0][DBYahooDay.line_date_index] + '-' + stock_lines[-1][
            DBYahooDay.line_date_index]
        chart_values_n = list()
        chart_values_m = list()
        chart_price = list()
        chart_account_property = list()
        chart_grid_names = list()

        # account的初始值, 必须与price相等, 所以这里记录转换的比例
        trans_percent = stock_lines[m - 1][DBYahooDay.line_close_index] / money_account.property
        for index in range(m - 1, len(stock_lines)):

            # 各种临时变量
            value_n = resolve_ma(stock_lines[index + 1 - n: index + 1], n)
            value_m = resolve_ma(stock_lines[index + 1 - m: index + 1], m)
            cur_price = stock_lines[index][DBYahooDay.line_close_index]
            cur_date = stock_lines[index][DBYahooDay.line_date_index]

            # 画表需要的值
            chart_values_n.append(value_n)
            chart_values_m.append(value_m)
            chart_price.append(cur_price)
            chart_grid_names.append(cur_date[6:])

            if state == 0:
                if value_m >= value_n:
                    # if not buy, then buy
                    if stock_name in money_account.stocks:
                        money_account.sell_with_hold_percent_with_line(stock_name, 1.0, stock_lines[index])
                    state = 1
            elif state == 1:
                if value_n >= value_m:
                    # if hold, then sell
                    if stock_name not in money_account.stocks:
                        money_account.buy_with_cash_percent_with_line(stock_name, 1.0, stock_lines[index])
                    state = 0
            else:
                if value_m >= value_n:
                    state = 1
                else:
                    state = 0

            money_account.update_with_all_stock_one_line({stock_name: (cur_price, cur_date)})
            chart_account_property.append(money_account.property * trans_percent)

        print 'chart path' + chart_dir_path
        draw_line_chart(chart_grid_names, [chart_price, chart_values_n, chart_values_m, chart_account_property],
                        ['price', 'ma5', 'ma10', 'account'], default_colors[0:4], chart_title,
                        output_dir=chart_dir_path)

        log_with_filename(chart_dir_name, money_account)


if __name__ == '__main__':
    simple_ma('s600119_ss')
