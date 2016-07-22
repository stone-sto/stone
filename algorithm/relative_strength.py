#! encoding:utf-8
from account.account import MoneyAccount
from data.info import DBInfoCache
import numpy as np
import pandas as pd


def relative_strength_monentum(denominator=3, ma_length=5, tem_length=10):
    """
    第一个按照时间进行的算法, pandas 和numpy还不会用, 先随便写写, 回头一定要认真看看
    这个算法的a股验证: https://www.quantopian.com/algorithms/578dcb3a42af719b300007e4
    :param reweight_period: 调整持仓比例的时间间隔, 单位是 天
    :type reweight_period: int
    :param ma_length: 在这条均线之上, 认为可以买
    :type ma_length: int
    :param tem_length: 积累relative strength 的时间长度, 这段时间, 是决定选股的关键时间, 需要大于均线的时间间隔
    :type tem_length: int
    :param denominator: 权重数量
    :type denominator: int
    """
    fix_frame= DBInfoCache().get_fix()

    # 记下上证, 把其他几个指数都给删掉, 另外深证的数据有问题, 如果以后要用, 记得要clean
    s01 = fix_frame['s000001_ss']
    del fix_frame['s000001_ss']
    del fix_frame['s399001_sz']
    # 把几次牛熊转换的时间给干掉
    # # 2000年到2003年, 具体回去再确认下
    # fix_frame = fix_frame.drop(fix_frame.loc[:'2005-01-03'].index.values, axis='index')
    # # 2007年到2008年
    # fix_frame = fix_frame.drop(fix_frame.loc['2007-01-04':'2008-12-31'].index.values, axis='index')
    # # 2014年到2015年
    # fix_frame = fix_frame.drop(fix_frame.loc['2014-01-02':'2015-03-01'].index.values, axis='index')

    date_list = fix_frame.index.values

    # 账户
    account = MoneyAccount(1000000, repo_count=denominator)

    # st list
    stock_names = fix_frame.columns.values

    for date_str in date_list:
        # 开始循环, 然后根据tem_length分配权重,
        # 过去tem_length的
        tem_rows = fix_frame.loc[:date_str]
        if len(tem_rows.index) < tem_length:
            continue
        tem_rows = tem_rows[-tem_length:]
        # 排序
        ranks = tem_rows.iloc[-1] / tem_rows.iloc[0]
        stock_names = sorted(stock_names, key=lambda x : ranks[x], reverse=True)
        # 找出denominator个在均线之上的st
        # 均线
        ma_values = tem_rows.iloc[-ma_length:].mean()
        # 选出来
        res_weight = list()
        count = 0
        for index in range(0, len(stock_names)):
            if tem_rows.loc[date_str, stock_names[index]] > ma_values[stock_names[index]]:
                res_weight.append(stock_names[index])
                count += 1
            if count >= denominator:
                break

        print date_str
        print res_weight

        # 调整持仓比例
        # 先把不在top rank中的给卖了
        for stock_name in account.stocks.keys():
            if stock_name not in res_weight:
                # 先确认这个st还在, 有可能已经消失了, 如果已经消失, 用最后一次的价格, 直接卖掉
                if np.isnan(tem_rows.loc[date_str, stock_name]):
                    account.sell_with_repos(stock_name, account.stocks[stock_name].cur_price, date_str, repo_count=1)
                else:
                    account.sell_with_repos(stock_name, tem_rows.loc[date_str, stock_name], date_str, repo_count=1)
        # 然后把在top rank中, 但是还没买的给补上, 如果买了, 用新的价格update一下
        for stock_name in res_weight:
            if stock_name not in account.stocks.keys():
                account.buy_with_repos(stock_name, tem_rows.loc[date_str, stock_name], date_str, repo_count=1)
            else:
                account.update_with_all_stock_one_line({stock_name: (tem_rows.loc[date_str, stock_name], date_str)})

        print account.returns

if __name__ == '__main__':
    relative_strength_monentum()
