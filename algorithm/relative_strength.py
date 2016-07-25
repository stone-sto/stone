#! encoding:utf-8
import datetime

from account.account import MoneyAccount
from chart.chart_utils import draw_line_chart, default_colors
from data.info import DBInfoCache
import numpy as np
import pandas as pd

from log.log_utils import log_with_filename


def relative_strength_monentum(denominator=5, ma_length=5, tem_length=3, reweight_period=None, win_percent=0.2,
                               need_up_s01=20, sell_after_reweight=False, lose_percent=0.3, rank_position=None,
                               rank_percent=0.35):
    """
    第一个按照时间进行的算法, pandas 和numpy还不会用, 先随便写写, 回头一定要认真看看
    这个算法的a股验证: https://www.quantopian.com/algorithms/578dcb3a42af719b300007e4
    :param rank_percent: 在rank中的位置, 以这个位置来选股, 因为有的时候并不一定是涨的最快的表现最好
    :type rank_percent: float
    :param rank_position: 在rank中的位置, 以这个位置来选股, 因为有的时候并不一定是涨的最快的表现最好
    :type rank_position: int
    :param lose_percent: 是否需要止损, 止损点是多少
    :type lose_percent: float
    :param sell_after_reweight: 在reweight之后,是否需要卖出股票
    :type sell_after_reweight: bool
    :param need_up_s01: 买入的时候, 上证指数必须处于n日均线之上
    :type need_up_s01: int
    :param win_percent: 坐实收入的比例r
    :type win_percent: float
    :param reweight_period: 调整持仓比例的时间间隔, 单位是 天
    :type reweight_period: int
    :param ma_length: 在这条均线之上, 认为可以买
    :type ma_length: int
    :param tem_length: 积累relative strength 的时间长度, 这段时间, 是决定选股的关键时间, 需要大于均线的时间间隔
    :type tem_length: int
    :param denominator: 权重数量
    :type denominator: int
    """
    time_before = datetime.datetime.now()
    fix_frame = DBInfoCache().get_fix()

    # 记下上证, 把其他几个指数都给删掉, 另外深证的数据有问题, 如果以后要用, 记得要clean
    s01 = fix_frame['s000001_ss']
    del fix_frame['s000001_ss']
    del fix_frame['s399001_sz']

    date_list = fix_frame.index.values

    # 账户
    account = MoneyAccount(1000000, repo_count=denominator)

    # st list
    stock_names = fix_frame.columns.values

    # 用来计数成功和失败的交易次数, 仅限于win_percent和lose_percent 生效的时候
    win_count = 0
    lose_count = 0

    # 作图相关的值, 暂时只需要上证和account
    chart_account_divider = s01[0] * 100 / account.property
    chart_account_value = list()
    chart_s01_value = list()
    import os
    chart_output_dir = os.path.join(os.path.dirname(__file__), '../result/relative_strength')
    if not os.path.exists(chart_output_dir):
        os.system('mkdir -p ' + chart_output_dir)

    # 搞定存图片的文件夹, 这次系统一点, 都保存下来, 用参数命名, 用收益/回撤做标题
    chart_title = 'denominator_%s_malength_%s_temlength_%s_reweightperiod_%s_winpercent_%s_' \
                  'needups01_%s_sellafterreweight_%s_losepercent_%s_rankposition_%s_rankpercent_%s' % (
                      str(denominator), str(ma_length), str(tem_length), str(reweight_period), str(win_percent),
                      str(need_up_s01), str(sell_after_reweight), str(lose_percent), str(rank_position),
                      str(rank_percent))

    # reweight的计数
    reweight_count = 0

    # 回撤
    max_dd = 0
    max_property = 0
    for date_str in date_list:

        # 所有的历史数据
        tem_rows = fix_frame.loc[:date_str]

        # 不管怎么样, chart的值都是需要的
        chart_s01_value.append(s01[date_str])
        # 做一下update, 然后把account的值也放进去, 稍有误差, 不过无非就是操作过程中出现的手续费, 因为当天的价格只有一个
        for stock_name in account.stocks.keys():
            if not np.isnan(tem_rows.loc[date_str, stock_name]):
                account.update_with_all_stock_one_line({stock_name: (tem_rows.loc[date_str, stock_name], date_str)})
        chart_account_value.append(account.property * chart_account_divider / 100)

        # 计算回撤
        if account.property > max_property:
            max_property = account.property
        cur_dd = account.property / max_property - 1
        if cur_dd < max_dd:
            max_dd = cur_dd
        log_with_filename(chart_title, 'max dd : ' + str(max_dd))

        # 开始循环
        # 过去tem_length的
        if len(tem_rows.index) < tem_length:
            continue
        tem_rows = tem_rows[-tem_length:]

        rank_place = 0
        if rank_position:
            rank_place = rank_position

        # 更新账户, 发现收益超过win_percent,就撤
        if win_percent:
            for stock_name in account.stocks.keys():
                if not np.isnan(tem_rows.loc[date_str, stock_name]):
                    account.update_with_all_stock_one_line({stock_name: (tem_rows.loc[date_str, stock_name], date_str)})
                    if account.stocks[stock_name].return_percent > win_percent:
                        account.sell_with_repos(stock_name, tem_rows.loc[date_str, stock_name], date_str, 1)
                        win_count += 1
                else:
                    if account.stocks[stock_name].return_percent > 0:
                        win_count += 1
                    else:
                        lose_count += 1
                    account.sell_with_repos(stock_name, account.stocks[stock_name].cur_price, date_str, 1)

        if lose_percent:
            for stock_name in account.stocks.keys():
                if not np.isnan(tem_rows.loc[date_str, stock_name]):
                    account.update_with_all_stock_one_line({stock_name: (tem_rows.loc[date_str, stock_name], date_str)})
                    if account.stocks[stock_name].return_percent < -lose_percent:
                        account.sell_with_repos(stock_name, tem_rows.loc[date_str, stock_name], date_str, 1)
                        lose_count += 1
                else:
                    if account.stocks[stock_name].return_percent > 0:
                        win_count += 1
                    else:
                        lose_count += 1
                    account.sell_with_repos(stock_name, account.stocks[stock_name].cur_price, date_str, 1)

        log_with_filename(chart_title, 'win_count, lose_count : %d %d' % (win_count, lose_count))

        # 是否需要根据reweight period进行reweight
        if reweight_period:
            reweight_count += 1
            # 每隔reweight进行一次就可以
            if reweight_count < reweight_period:
                continue
            reweight_count = 0

        # 如果需要上证均线之上, 在这里进行检查, 不满足, 直接跳过
        if need_up_s01:
            if len(s01.loc[:date_str]) > need_up_s01:
                if s01[date_str] < s01.loc[:date_str].iloc[-need_up_s01].mean():
                    continue
            else:
                continue

        # 排序
        ranks = tem_rows.iloc[-1] / tem_rows.iloc[0]

        # 找到排在rank_percent 的st
        rank_count = 0
        if rank_percent:
            # 去除为nan的部分
            for stock_name in stock_names:
                if not np.isnan(ranks[stock_name]):
                    rank_count += 1

            rank_place = int(rank_count * rank_percent)
            log_with_filename(chart_title, 'rank place : ' + str(rank_place))

        stock_names = sorted(stock_names, key=lambda x: ranks[x] if not np.isnan(ranks[x]) else -1, reverse=True)

        # 找出denominator个在均线之上的st, 且不是涨停的
        # 均线
        ma_values = tem_rows.iloc[-ma_length:].mean()
        percent_values = tem_rows.iloc[-1] / tem_rows.iloc[-2]
        # 选出来
        res_weight = list()
        count = 0

        for index in range(rank_place, len(stock_names)):
            if tem_rows.loc[date_str, stock_names[index]] > \
                    ma_values[stock_names[index]] and -0.095 < percent_values[stock_names[index]] - 1 < 0.095:
                res_weight.append(stock_names[index])
                count += 1
            if count >= denominator:
                break

        log_with_filename(chart_title, date_str)
        log_with_filename(chart_title, res_weight)

        # # 调整持仓比例
        # # 先把不在top rank中的给卖了
        if sell_after_reweight:
            for stock_name in account.stocks.keys():
                if stock_name not in res_weight:
                    # 先确认这个st还在, 有可能已经消失了, 如果已经消失, 用最后一次的价格, 直接卖掉
                    if np.isnan(tem_rows.loc[date_str, stock_name]):
                        account.sell_with_repos(stock_name, account.stocks[stock_name].cur_price, date_str,
                                                repo_count=1)
                    else:
                        account.sell_with_repos(stock_name, tem_rows.loc[date_str, stock_name], date_str, repo_count=1)

        # 然后把在top rank中, 但是还没买的给补上, 如果买了, 用新的价格update一下
        for stock_name in res_weight:
            if stock_name not in account.stocks.keys():
                account.buy_with_repos(stock_name, tem_rows.loc[date_str, stock_name], date_str, repo_count=1)
            else:
                account.update_with_all_stock_one_line({stock_name: (tem_rows.loc[date_str, stock_name], date_str)})

        log_with_filename(chart_title, account.returns)

    chart_file_name = 'returns_%f_maxdd_%f' % (account.returns, max_dd)
    draw_line_chart(date_list, [chart_s01_value, chart_account_value], ['s01', 'account'], default_colors[:2],
                    chart_file_name, title=chart_title, output_dir=chart_output_dir)
    log_with_filename(chart_title, account)
    log_with_filename(chart_title, account.returns)
    log_with_filename(chart_title, 'max dd' + str(max_dd))
    log_with_filename(chart_title, 'time cose : ' + str(datetime.datetime.now() - time_before))


if __name__ == '__main__':
    win_percent_list = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]
    lose_percent_list = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
    for win_percent in win_percent_list:
        for lose_percent in lose_percent_list:
            relative_strength_monentum(denominator=5, win_percent=win_percent, lose_percent=lose_percent,
                                       rank_percent=0.4)
