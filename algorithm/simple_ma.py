#! -*- encoding:utf-8 -*-
import os

from account.account import MoneyAccount
from algorithm.simu_utils import cal_return_level_with_account
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

def ma(ma_type, stock_name, repo_count=3, down_buy_percent=0.05, win_percent=0.05, n=5, m=10):
    """
    :param stock_name:
    :type stock_name: str
    :param ma_type: 上面几个之一, 0,1,2,3 0和2时, repo_count自动置1
    :type ma_type: int
    :param down_buy_percent: 以多少下跌作为补仓的单位
    :type down_buy_percent: float
    :param repo_count: 仓位数量
    :type repo_count: int
    :param win_percent: 收益
    :type win_percent: float
    :param n:
    :type n: int
    :param m:
    :type m: int
    :return: [(account, days)]
    :rtype: tuple[str|list[tuple[MoneyAccount|int]]]
    """
    # 搞定ma的类型
    if ma_type == 0:
        repo_count = 1
        al_tag = 'simple_ma_%d_%d' % (n, m)
    elif ma_type == 1:
        al_tag = 'multi_opt_ma_%d_%f_%d_%d' % (repo_count, down_buy_percent, n, m)
    elif ma_type == 2:
        repo_count = 1
        al_tag = 'win_percent_ma_%f_%d_%d' % (win_percent, n, m)
    elif ma_type == 3:
        al_tag = 'multi_opt_win_percent_ma_%d_%f_%f_%d_%d' % (repo_count, down_buy_percent, win_percent, n, m)
    else:
        print 'Unresolve type.'
        return

    # 存返回结果的list
    result_list = list()

    # 数据
    stock_lines_group = all_stock_and_clean_day_lines(stock_name)

    # chart 路径
    chart_dir_name = al_tag
    chart_dir_path = os.path.join(os.path.dirname(__file__), '../result', chart_dir_name)
    if not os.path.exists(chart_dir_path):
        os.system('mkdir -p "' + chart_dir_path + '"')

    # 开始loop
    for stock_lines in stock_lines_group:

        # 账户, 默认100000, 以后有需要可以改, 变量
        state = -1
        money_account = MoneyAccount(100000.0, repo_count)

        # 作图相关
        start_date = stock_lines[0][DBYahooDay.line_date_index]
        end_date = stock_lines[-1][DBYahooDay.line_date_index]
        chart_title = stock_name + '-' + start_date + '-' + end_date
        chart_values_n = list()
        chart_values_m = list()
        chart_price = list()
        chart_account_property = list()
        chart_grid_names = list()
        chart_tem_prices = list()

        # 数据量必须够, 否则没有意义
        if len(stock_lines) < m:
            continue

        # account的初始值, 必须与price相等, 所以这里记录转换的比例
        trans_percent = stock_lines[m - 1][DBYahooDay.line_close_index] / money_account.property

        # 在图表中加入上证作为参考
        stock_tem_lines = DBYahooDay().select_period_lines(stock_name, start_date, end_date)
        stock_tem_prices = [tem_line[DBYahooDay.line_close_index] for tem_line in stock_tem_lines]
        trans_percent_tem = stock_lines[m - 1][DBYahooDay.line_close_index] / stock_tem_prices[m - 1]

        # 开始这次模拟
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
            chart_tem_prices.append(stock_tem_prices[index] * trans_percent_tem)

            if ma_type == 0:
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

                # 更新下account的状态
                money_account.update_with_all_stock_one_line({stock_name: (cur_price, cur_date)})

            elif ma_type == 1:
                # 感觉没有任何意义, 不写了
                pass
            elif ma_type == 2:

                if state == 0:
                    if value_m >= value_n:
                        state = 1
                elif state == 1:
                    if value_n >= value_m:
                        # buy
                        if stock_name not in money_account.stocks:
                            money_account.buy_with_cash_percent_with_line(stock_name, 1.0, stock_lines[index])
                        state = 0
                else:
                    if value_m >= value_n:
                        state = 1
                    else:
                        state = 0

                # 更新下account的状态
                money_account.update_with_all_stock_one_line({stock_name: (cur_price, cur_date)})

                #  随时准备卖出
                # sell
                if stock_name in money_account.stocks and money_account.stocks[
                    stock_name].return_percent >= win_percent:
                    money_account.sell_with_hold_percent_with_line(stock_name, 1.0, stock_lines[index])
            elif ma_type == 3:

                stock_line = stock_lines[index]
                if state == 0:
                    if value_m >= value_n:
                        state = 1
                elif state == 1:
                    if value_n >= value_m:
                        # 出现向上交叉, 买入
                        if stock_name not in money_account.stocks:
                            money_account.buy_with_repos(stock_name, stock_line[DBYahooDay.line_close_index],
                                                         stock_line[DBYahooDay.line_date_index], 1)
                        state = 0
                else:
                    if value_m >= value_n:
                        state = 1
                    else:
                        state = 0

                # 更新下account的状态
                money_account.update_with_all_stock_one_line({stock_name: (cur_price, cur_date)})

                #  随时准备补仓和卖出
                # sell
                if stock_name in money_account.stocks:
                    # 到达盈利标准
                    if money_account.stocks[stock_name].return_percent >= win_percent / money_account.stock_repos[
                        stock_name]:
                        # 全部卖掉
                        money_account.sell_with_repos(stock_name, stock_line[DBYahooDay.line_close_index],
                                                      stock_line[DBYahooDay.line_date_index],
                                                      money_account.stock_repos[stock_name])
                    elif money_account.stocks[stock_name].return_percent < down_buy_percent:
                        # 买入一份
                        money_account.buy_with_repos(stock_name, stock_line[DBYahooDay.line_close_index],
                                                     stock_line[DBYahooDay.line_date_index], 1)

            # accout的价值加入图表变量中
            chart_account_property.append(money_account.property * trans_percent)

        # 画图
        draw_line_chart(chart_grid_names,
                        [chart_price, chart_values_n, chart_values_m, chart_account_property, chart_tem_prices],
                        ['price', 'ma5', 'ma10', 'account', 'shangzheng'], default_colors[0:5], chart_title,
                        output_dir=chart_dir_path)
        # log
        log_with_filename(chart_dir_name, money_account)
        # 保存结果
        result_list.append((money_account, len(stock_lines)))

    return al_tag, result_list


def start_simple_ma(n=5, m=10):
    """
    带统计, log输出的封装
    :param n:
    :type n:
    :param m:
    :type m:
    """
    yahoo_db = DBYahooDay()
    tag_name = 'simple_ma_%d_%d' % (n, m)
    stock_names = yahoo_db.select_all_stock_names()
    group_count = 0
    win_count = 0
    win_1_count = 0
    win_2_count = 0
    for stock_name in stock_names:
        res = simple_ma(stock_name, tag_name, n, m)
        group_count += res[0]
        win_count += res[1]
        win_1_count += res[2]
        win_2_count += res[3]

    res_str = 'result: \n>0: %f\n>1: %f\n>2:%f\n' % (
        float(win_count) / group_count, float(win_1_count) / group_count, float(win_2_count) / group_count)
    log_with_filename(tag_name, res_str)


def start_ma(ma_type, repo_count=3, down_buy_percent=0.05, win_percent=0.05, n=5, m=10):
    """
    带统计, log输出的封装
    :param down_buy_percent: 下跌补仓的百分比, 补仓条件 down_buy_percent/持有份数 + down_buy_percent
    :type down_buy_percent:
    :param repo_count:
    :type repo_count:
    :param ma_type:
    :type ma_type:
    :param win_percent:
    :type win_percent:
    :param n:
    :type n:
    :param m:
    :type m:
    """
    yahoo_db = DBYahooDay()
    stock_names = yahoo_db.select_all_stock_names()
    res0 = 0
    res1 = 0
    res2 = 0
    res3 = 0
    res4 = 0
    res5 = 0
    count = 0
    tag_name = ''
    for stock_name in stock_names:
        tag_name, res_group = ma(ma_type, stock_name, n=n, m=m, win_percent=win_percent, repo_count=repo_count,
                                 down_buy_percent=down_buy_percent)
        for res in res_group:
            res_level = cal_return_level_with_account(res[0], res[1])
            print res[0].returns
            count += 1
            if res[0].returns > 0:
                res0 += 1
            if res_level > 5:
                res5 += 1
            if res_level > 4:
                res4 += 1
            if res_level > 3:
                res3 += 1
            if res_level > 2:
                res2 += 1
            if res_level > 1:
                res1 += 1

    res_str = 'result: \n>0:%f\n>1: %f\n>2: %f\n>3:%f\n>4:%f\n>5:%f\n' % (
        float(res0) / count, float(res1) / count, float(res2) / count, float(res3) / count, float(res4) / count,
        float(res5) / count)
    log_with_filename(tag_name, res_str)


def simple_ma(stock_name, tag_name, n=5, m=10):
    """
    简单的基于ma, 5 10
    :param tag_name: 用来标记这次执行的tag
    :type tag_name: str
    :param n: 均值中比较小的周期
    :type n: int
    :param m: 均值中比较大的周期
    :type m: int
    :param stock_name:
    :type stock_name:str
    """
    stock_lines_group = all_stock_and_clean_day_lines(stock_name)
    chart_dir_name = tag_name
    chart_dir_path = os.path.join(os.path.dirname(__file__), '../result', chart_dir_name)
    if not os.path.exists(chart_dir_path):
        os.system('mkdir -p "' + chart_dir_path + '"')
    win_count = 0
    win_1_count = 0
    win_2_count = 0
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
        if len(stock_lines) < m:
            continue
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

        if money_account.returns > 0:
            win_count += 1
        if money_account.returns > 1:
            win_1_count += 1
        if money_account.returns > 2:
            win_2_count += 1

    return len(stock_lines_group), win_count, win_1_count, win_2_count


def win_percent_ma(stock_name, tag_name, n=10, m=20, win_percent=0.05):
    """
    简单的基于ma, 5 10
    :param tag_name:
    :type tag_name:
    :param win_percent: return
    :type win_percent: float
    :param n: 均值中比较小的周期
    :type n: int
    :param m: 均值中比较大的周期
    :type m: int
    :param stock_name:
    :type stock_name:str
    """
    stock_lines_group = all_stock_and_clean_day_lines(stock_name)
    chart_dir_name = tag_name
    chart_dir_path = os.path.join(os.path.dirname(__file__), '../result', chart_dir_name)
    if not os.path.exists(chart_dir_path):
        os.system('mkdir -p "' + chart_dir_path + '"')

    win_count = 0
    win_1_count = 0
    win_2_count = 0
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
        if len(stock_lines) < m:
            continue
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
                    if stock_name in money_account.stocks and money_account.stocks[
                        stock_name].return_percent >= win_percent:
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

        if money_account.returns > 0:
            win_count += 1
        if money_account.returns > 1:
            win_1_count += 1
        if money_account.returns > 2:
            win_2_count += 1

    return len(stock_lines_group), win_count, win_1_count, win_2_count


if __name__ == '__main__':
    # start_win_percent_ma(5, 10, 0.05)
    # repo 3 5
    # win 0.05 0.1
    # down 0.05 0.1
    # n, m 5,10 10,20
    start_ma(3, repo_count=3, win_percent=0.05, down_buy_percent=0.05, n=5, m=10)

    start_ma(3, repo_count=3, win_percent=0.05, down_buy_percent=0.05, n=10, m=20)

    start_ma(3, repo_count=3, win_percent=0.05, down_buy_percent=0.1, n=5, m=10)

    start_ma(3, repo_count=3, win_percent=0.05, down_buy_percent=0.1, n=10, m=20)

    start_ma(3, repo_count=3, win_percent=0.1, down_buy_percent=0.05, n=5, m=10)

    start_ma(3, repo_count=3, win_percent=0.1, down_buy_percent=0.05, n=10, m=20)

    start_ma(3, repo_count=3, win_percent=0.1, down_buy_percent=0.1, n=5, m=10)

    start_ma(3, repo_count=3, win_percent=0.1, down_buy_percent=0.1, n=10, m=20)

    # start_win_percent_ma(5, 10, 0.1)
    # start_win_percent_ma(10, 20, 0.1)
