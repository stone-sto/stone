#! -*- encoding:utf-8 -*-
import datetime
from time import sleep

from data.download import SinaDownload
from log.log_utils import log_by_time


def download_from_start_to_end():
    """
    在指定时间段,下分钟的数据
    """
    time_format = '%Y-%m-%d %H-%M-%S'
    # 计算时间, 判定需要等待多久
    time_now = datetime.datetime.now()
    # 拼出开始时间和结束时间
    time_start_time = datetime.datetime.strptime('2016-06-23 08-59-00', time_format)
    time_start = datetime.datetime.combine(time_now.date(), time_start_time.time())
    time_end_time = datetime.datetime.strptime('2016-06-23 15-01-00', time_format)
    time_end = datetime.datetime.combine(time_now.date(), time_end_time.time())

    if time_now < time_start:
        print 'Time now : ' + str(time_now)
        sleep(time_start - time_now)
    if time_now > time_end:
        return

    sina_down = SinaDownload()
    # 在时间内下载
    while time_start <= time_now <= time_end:
        log_by_time(time_now)
        sina_down.download_one_minute(sina_down.stock_names)
        time_now = datetime.datetime.now()
        # 休息10s, 继续下载
        sleep(10)


if __name__ == '__main__':
    download_from_start_to_end()
