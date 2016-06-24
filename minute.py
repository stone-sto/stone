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

    # 拼出中场休息时间
    time_rest_start_time = datetime.datetime.strptime('2016-06-24 11-31-00', time_format)
    time_rest_start = datetime.datetime.combine(time_now.date(), time_rest_start_time.time())
    time_rest_end_time = datetime.datetime.strptime('2016-06-24 12-59-00', time_format)
    time_rest_end = datetime.datetime.combine(time_now.date(), time_rest_end_time.time())

    if time_now < time_start:
        print 'Time now : ' + str(time_now)
        sleep(time_start - time_now)
    if time_now > time_end:
        return

    sina_down = SinaDownload()
    # 在时间内下载
    while time_start <= time_now <= time_end:
        # 工作时间内, 两种可能, 下载, 睡觉
        # 下载的情况
        if time_start <= time_now <= time_rest_start or time_rest_end <= time_now <= time_end:
            log_by_time(time_now)
            sina_down.download_one_minute(sina_down.stock_names)
            # 休息10s, 继续下载
            sleep(10)
        else:
            # 休息半分中再次尝试
            print 'Sleeping ' + str(time_now)
            sleep(30)
        time_now = datetime.datetime.now()


if __name__ == '__main__':
    download_from_start_to_end()
