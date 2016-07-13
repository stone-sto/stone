# -*- encoding:utf-8 -*-


def ema_n(pre_ema_n, close_price, n):
    """
    计算ema
    :param pre_ema_n: 前一天的ema
    :type pre_ema_n: float
    :param close_price: 收盘价
    :type close_price: float
    :param n: ema的天数, 默认12
    :type n: int
    :return: ema
    :rtype: float
    """
    return pre_ema_n * (n - 1) / (n + 1) + close_price * 2 / (n + 1)


def diff(pre_ema_12, pre_ema_26, close_price):
    """
    计算diff
    :param pre_ema_12: 前一天的ema12
    :type pre_ema_12: float
    :param pre_ema_26: 前一天的ema26
    :type pre_ema_26: float
    :param close_price:
    :type close_price: float
    :return:
    :rtype: float
    """
    return ema_n(pre_ema_12, close_price, 12) - ema_n(pre_ema_26, close_price, 26)


def dea(pre_dea, cur_diff):
    return pre_dea * 8 / 9.0 + cur_diff / 5


def macd_bar(cur_diff, cur_dea):
    return (cur_diff - cur_dea) * 2
