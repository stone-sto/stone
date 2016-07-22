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
    fix_frame = DBInfoCache().get_fix()
    date_list = fix_frame.index.values

    print fix_frame[fix_frame == np.NaN]

    # # 记下上证, 把其他几个指数都给删掉
    # s01 = fix_frame['s000001_ss']
    # del fix_frame['s000001_ss']

    # # 账户
    # account = MoneyAccount(1000000)
    #
    # # st list
    # stock_names = fix_frame.columns.values
    #
    # for date_str in date_list:
    #     # 开始循环, 然后根据tem_length分配权重,
    #     # 过去tem_length的
    #     tem_rows = fix_frame.loc[:date_str]
    #     if len(tem_rows.index) < tem_length:
    #         continue
    #     tem_rows = tem_rows[-tem_length:]
    #     # 排序
    #     ranks = tem_rows.iloc[-1] / tem_rows.iloc[0]
    #     stock_names = sorted(stock_names, key=lambda x : ranks[x], reverse=True)
    #     # 找出denominator个在均线之上的st
    #     # 均线
    #     ma_values = tem_rows.iloc[-ma_length:].mean()
    #     # 选出来
    #     res_weight = list()
    #     count = 0
    #     for index in range(0, len(stock_names)):
    #         if tem_rows.loc[date_str, stock_names[index]] > ma_values[stock_names[index]]:
    #             res_weight.append(stock_names[index])
    #             count += 1
    #         if count >= denominator:
    #             break
    #
    #     print date_str
    #     print res_weight


if __name__ == '__main__':
    relative_strength_monentum()
