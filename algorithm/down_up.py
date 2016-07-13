# encoding:utf-8

# 基于下降之后必定回升原则
import os

from account.account import MoneyAccount
from chart.chart_utils import none_y_value, draw_line_chart, default_colors
from data.db.db_helper import DBYahooDay
from data.info_utils import all_stock_and_clean_day_lines
from log.log_utils import log_with_filename


def down_up_multi_opt(stock_name, down_start_percent=0.15, down_cell_percent=0.05, up_start_percent=0.15,
                      repo_counts=5):
    """
    :param stock_name:
    :type stock_name: str
    :param down_start_percent: 跌到一定程度, 开始建仓
    :type down_start_percent: float
    :param down_cell_percent: 建仓之后, 每次再跌这个cell, 补一次仓
    :type down_cell_percent: float
    :param up_start_percent: returns到达这个值, 卖出第一仓
    :type up_start_percent: float
    :param repo_counts:
    :type repo_counts: int
    :return: 结果的账户list
    :rtype: list[MoneyAccount]
    """
    stock_line_groups = all_stock_and_clean_day_lines(stock_name)

    # 图片路径
    chart_dir_name = 'down_up_multi_opt_%f_%f_%f_%d' % (
        down_start_percent, down_cell_percent, up_start_percent, repo_counts)
    chart_dir_path = os.path.join(os.path.dirname(__file__), '../result', chart_dir_name)
    if not os.path.exists(chart_dir_path):
        os.system('mkdir -p "' + chart_dir_path + '"')

    # log路径
    log_dir_name = chart_dir_name
    log_file_path = os.path.join(os.path.dirname(__file__), '../record', log_dir_name + '.log')

    # 保存结果
    account_res = list()

    for stock_lines in stock_line_groups:
        money_account = MoneyAccount(100000, repo_count=repo_counts)
        cur_max_price = -1

        # 关于表格
        horizontal_names = list()
        prices = [stock_line[DBYahooDay.line_close_index] for stock_line in stock_lines]
        account_values = list()
        buy_points = list()
        sell_points = list()
        # account的初始值, 必须与price相等, 所以这里记录转换的比例
        if len(stock_lines) <= 0:
            continue
        trans_percent = stock_lines[0][DBYahooDay.line_close_index] / money_account.property

        chart_title = '%s-%s-%s' % (
            stock_name, stock_lines[0][DBYahooDay.line_date_index], stock_lines[-1][DBYahooDay.line_date_index])

        for stock_line in stock_lines:
            cur_price = stock_line[DBYahooDay.line_close_index]
            cur_date = stock_line[DBYahooDay.line_date_index]

            # 关于表格
            horizontal_names.append(cur_date[5:].replace('-', ''))
            buyed = False
            selled = False

            # 空仓
            if len(money_account.stocks) <= 0:
                if cur_price > cur_max_price:
                    cur_max_price = cur_price

                if cur_price < cur_max_price * (1 - down_start_percent):
                    # 买入
                    if money_account.buy_with_repos(stock_name, cur_price, cur_date, 1):
                        buy_points.append(cur_price)
                        buyed = True
                else:
                    money_account.update_with_all_stock_one_line({stock_name: (cur_price, cur_date)})

            # 持仓
            else:
                money_account.update_with_all_stock_one_line({stock_name: (cur_price, cur_date)})
                cur_max_price = -1
                hold_stock = money_account.stocks[stock_name]
                if hold_stock.return_percent < -down_cell_percent * money_account.stock_repos[stock_name]:
                    # 买入
                    if money_account.buy_with_repos(stock_name, cur_price, cur_date, 1):
                        buy_points.append(cur_price)
                        buyed = True
                elif hold_stock.return_percent > up_start_percent / money_account.stock_repos[stock_name]:
                    # 执行卖出
                    if money_account.sell_with_repos(stock_name, cur_price, cur_date,
                                                     money_account.stock_repos[stock_name]):
                        sell_points.append(cur_price)
                        selled = True

            if not buyed:
                buy_points.append(none_y_value)

            if not selled:
                sell_points.append(none_y_value)

            account_values.append(money_account.property * trans_percent)

        draw_line_chart(horizontal_names, [prices, account_values], ['price', 'account'], default_colors[0:2],
                        chart_title, output_dir=chart_dir_path, buy_points=buy_points, sell_points=sell_points)
        account_res.append(money_account)
        log_with_filename(log_file_path, str(money_account))

    return account_res


if __name__ == '__main__':
    stock_names = DBYahooDay().select_all_stock_names()
    count = 0
    total_count = 0
    for stock_name in stock_names:
        print stock_name
        account_list = down_up_multi_opt(stock_name)
        total_count += len(account_list)
        for account in account_list:
            if account.returns > 0:
                count += 1

        print float(count) / total_count

    print float(count) / total_count
    # down_up_multi_opt('s600119_ss')
