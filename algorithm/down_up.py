# encoding:utf-8

# 基于下降之后必定回升原则
from data.db.db_helper import DBYahooDay
from data.info_utils import all_stock_and_clean_day_lines


def down_up_multi_opt(stock_name, down_start_percent=0.15, down_cell_percent=0.05, up_start_percent=0.1, up_cell_percent=0.05, repo_counts=5):
    """
    :param stock_name:
    :type stock_name: str
    :param down_start_percent: 跌到一定程度, 开始建仓
    :type down_start_percent: float
    :param down_cell_percent: 建仓之后, 每次再跌这个cell, 补一次仓
    :type down_cell_percent: float
    :param up_start_percent: returns到达这个值, 卖出第一仓
    :type up_start_percent: float
    :param up_cell_percent: returns每次上升一个cell, 卖出一仓
    :type up_cell_percent: float
    :param repo_counts:
    :type repo_counts: int
    """
    stock_line_groups = all_stock_and_clean_day_lines(stock_name)
    for stock_lines in stock_line_groups:
        for stock_line in stock_lines:
            cur_price = stock_line[DBYahooDay.line_close_index]
            cur_date = stock_line[DBYahooDay.line_date_index]