# -*- coding: utf-8 -*-

from datetime import datetime, date

# 基本的日期,时间格式
time_format = '%H:%M:%S'
date_format = '%Y-%m-%d'
datetime_format = date_format + ' ' + time_format

# 一个历史时间, 不会影响当前的数据, 用来填充空数据, 判断是否是无效时间等
date_never_used = '1971-1-1'
time_never_used = '00:00:00'


def resolve_date(date_str):
    """
    从一个str中获取date
    :param date_str: 日期的str
    :type date_str: str
    :return: date
    :rtype: date
    """
    return datetime.strptime(date_str, date_format).date()
