#! -*- encoding:utf-8 -*-

# 所有的下载方式都写在这里, 每种方式对应一个类
import threading
import traceback
import urllib2

import requests
import thread

from data.db.db_helper import DBYahooDay, DBSinaMinute
from log.log_utils import log_by_time


class SinaDownload(object):
    """
    负责从新浪下载数据
    """

    def __init__(self):
        super(SinaDownload, self).__init__()
        self.yahoo_db = DBYahooDay()
        self.sina_db = DBSinaMinute(2015)
        self.stock_names = self.yahoo_db.select_all_stock_names()

    def download_one_minute(self, stock_names):
        """
        下载一次
        :param stock_names: 要下载的st列表
        """
        for stock_name in stock_names:
            stock_info = self.download_one_minute_for_one_stock(stock_name)
            if stock_info:
                self.sina_db.add_one_line_to_table(stock_name, stock_info)

    def get_sina_download_url(self, stock_name):
        """
        获得sina的下载链接
        :param stock_name: 名称
        :return: url
        """
        # 搞定链接
        if stock_name.endswith('ss'):
            tag = 'sh'
        else:
            tag = 'sz'
        return 'http://hq.sinajs.cn/list=%s' % (tag + stock_name[1:-3])

    def download_one_minute_for_one_stock(self, stock_name):
        """
        下载一个st的一次, 并生成可以写入分钟表的数据
        :param stock_name:  st名称
        :return: 一个st的一行数据, 格式是整理好的
        """
        sina_url = self.get_sina_download_url(stock_name)
        try:
            stock_request = requests.get(sina_url, timeout=30)
            if stock_request.status_code == 200:
                stock_info = stock_request.text.split('"')[1].split(',')
                stock_info[-2] = '"%s"' % stock_info[-2]
                stock_info[-3] = '"%s"' % stock_info[-3]
                return ','.join(stock_info[1:-1])
            else:
                log_by_time(stock_name + ' minute update failed with status code ' + str(stock_request.status_code))
                return None
        except:
            log_by_time(stock_name + ' minite update faied.')
            traceback.print_exc()
            return None

    def update_cur_day(self):
        """
        从新浪更新当天的数据, 必须收盘之后执行
        """
        self.yahoo_db.open()
        for stock_name in self.stock_names:
            self.update_one_stock(stock_name)
        self.yahoo_db.close()

    def update_one_stock(self, stock_name):
        """
        更新当天的st, 不过只一支
        :param stock_name:   名称
        """
        # 搞定链接
        sina_url = self.get_sina_download_url(stock_name)
        log_by_time(sina_url)

        # 搞定下载
        try:
            stock_request = requests.get(sina_url)
            if stock_request.status_code == 200:

                stock_info = stock_request.text.split('"')[1].split(',')
                # print stock_info
                # 开始存数据库
                self.yahoo_db.insert_into_table(stock_name,
                                                [
                                                    DBYahooDay.line_date,
                                                    DBYahooDay.line_open,
                                                    DBYahooDay.line_high,
                                                    DBYahooDay.line_low,
                                                    DBYahooDay.line_close,
                                                    DBYahooDay.line_volume,
                                                    DBYahooDay.line_adj_close,
                                                ],
                                                [
                                                    # date
                                                    '"%s"' % stock_info[-3],
                                                    # open
                                                    stock_info[1],
                                                    # high
                                                    stock_info[4],
                                                    # low
                                                    stock_info[5],
                                                    # close, 实际上是现价, 所以一定要收盘之后才能运行
                                                    stock_info[3],
                                                    # volume
                                                    stock_info[8],
                                                    # adj close, 新浪没有这个字段, 存个-1, 以后如果用了再想办法
                                                    '-1',
                                                ])
                self.yahoo_db.connection.commit()
            else:
                log_by_time(stock_name + ' daily update failed with http code ' + str(stock_request.status_code))
        except:
            log_by_time(stock_name + ' daily update failed.')
            traceback.print_exc()


class YahooDownload(object):
    """
    从雅虎下载数据
    """

    def __init__(self):
        super(YahooDownload, self).__init__()
        self.stock_names = []

    def init_stock_names(self):
        """
        # 编号顺序
        # 上证sh600000 ~ 604000
        # 深证sz000001 ~ 003000
        # 创业sz300001 ~ 300600
        # 上证指数 sh000001
        # 深证成指 sz399001
        # 创业板指 sz399006
        ** 先按照编号顺序, 创建所有的表, 不管是否可用, 然后用多线程的方式, 下载, 遇到断掉的或者数据有问题的, 去同花顺或者新浪确认一下
        """
        # 上证
        start_num = 600000
        for i in range(0, 4000):
            self.stock_names.append('s' + str(start_num + i) + '_ss')
        start_num = 000001
        for i in range(0, 2999):
            self.stock_names.append('s%06d_sz' % (start_num + i))
        start_num = 300001
        for i in range(0, 599):
            self.stock_names.append('s' + str(start_num + i) + '_sz')

        self.stock_names.append('s000001_ss')
        self.stock_names.append('s399001_sz')
        self.stock_names.append('s399006_sz')

    @staticmethod
    def get_yahoo_format_name(name):
        return name[1:].replace('_', '.')

    def download_target_range_names(self, stock_range):
        """
        下载指定区间的stock
        :param stock_range: st代码范围
        """
        for i in stock_range:
            stock_name = self.stock_names[i]
            print stock_name
            # 打开数据库
            db_mutex = threading.Lock()
            self.yahoo_db = DBYahooDay()
            if db_mutex.acquire(1):
                self.yahoo_db.open()

            # 检查是否已经处理过
            if not self.yahoo_db.check_if_is_done(stock_name):
                self.yahoo_db.close()
                db_mutex.release()
                stock_data_content = self.download_one_stock(stock_name)
                # 确认是否有返回
                if stock_data_content:
                    stock_lines = stock_data_content.split('\n')
                    if db_mutex.acquire(1):
                        self.yahoo_db.open()
                        self.yahoo_db.add_row_to_stock_name_table(stock_name)
                        self.fill_one_stock(stock_name, stock_lines[1:])
                        self.yahoo_db.close()
                        db_mutex.release()

                # 没有返回, 跳过
                else:
                    log_by_time(stock_name + ' skip.')
            else:
                self.yahoo_db.close()
                db_mutex.release()

        log_by_time('range from %d to %d done.' % (stock_range[0], stock_range[-1]))

    def fill_one_stock(self, stock_name, stock_data_lines):
        """
        增加一个st的数据
        :param stock_name:  名称
        :param stock_data_lines: 数据
        """
        self.yahoo_db.create_st_table(stock_name)
        for stock_data_line in stock_data_lines:
            table_names = (
                DBYahooDay.line_date,
                DBYahooDay.line_open,
                DBYahooDay.line_high,
                DBYahooDay.line_low,
                DBYahooDay.line_close,
                DBYahooDay.line_volume,
                DBYahooDay.line_adj_close,
            )
            values = stock_data_line.split(',')
            if len(values) >= 7:
                table_values = (
                    '"%s"' % str(values[0]),
                    values[1],
                    values[2],
                    values[3],
                    values[4],
                    values[5],
                    values[6],
                )
                self.yahoo_db.insert_into_table(stock_name, table_names, table_values)
        self.yahoo_db.connection.commit()

    def download_one_stock(self, name, start_year=2000, start_month=1, start_day=1, end_year=2016, end_month=6,
                           end_day=15):
        """
        下载指定股票
        :param name:        名称
        :param start_year:  起始年份
        :param start_month: 起始月份, 几月就写几月, 不用特意-1
        :param start_day:   起始日期
        :param end_year:    结束年份
        :param end_month:   结束月份
        :param end_day:     结束日期
        :return:
        """
        url_str = 'http://ichart.yahoo.com/table.csv?s=%s&a=%d&b=%d&c=%d&d=%d&e=%d&f=%d&g=d&ignore=.csv' % (
            self.get_yahoo_format_name(name), start_month - 1, start_day, start_year, end_month - 1, end_day, end_year)
        log_by_time(url_str)
        try:
            r = requests.get(url_str)
            if r.status_code == 200:
                return r.text
            else:
                log_by_time(name + ' failed with http code : ' + str(r.status_code))
        except:
            log_by_time(name + ' failed')
            traceback.print_exc()
            return None


def start_fill_datas(stock_range):
    """
    填充指定部分的数据, 一共7601, 从0开始
    :param stock_range: 范围
    """
    yahoo = YahooDownload()
    yahoo.init_stock_names()
    yahoo.download_target_range_names(stock_range)


class ThreadRunner(threading.Thread):
    def __init__(self, stock_range, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        super(ThreadRunner, self).__init__(group, target, name, args, kwargs, verbose)
        self.stock_range = stock_range

    def run(self):
        start_fill_datas(self.stock_range)


def run_every_day():
    """
    每天收盘之后执行这个函数就行了
    """
    # 每日下载
    SinaDownload().update_cur_day()
    # 更新percent和point
    yahoo_db = DBYahooDay()
    yahoo_db.fill_percent_for_all_stock(-1)
    yahoo_db.fill_point_for_all_stock(-1)


if __name__ == '__main__':
    pass

    # sina_down = SinaDownload()
    # sina_down.download_one_minute()
    # 补充漏掉的st
    # yahoo = YahooDownload()
    # yahoo.init_stock_names()
    # # for index in range(0,len(yahoo.stock_names)):
    # #     stock_name = yahoo.stock_names[index]
    # #     if stock_name == 's600198_ss':
    # #         print index
    # yahoo.download_target_range_names([198, 199])


    # 每日下载
    # SinaDownload().update_cur_day()
    # run_every_day()

    # 下载某个st
    # yahoo = YahooDownload()
    # yahoo.init_stock_names()
    # yahoo.download_target_range_names(range(len(yahoo.stock_names) - 1, len(yahoo.stock_names)))

    # 首次下载
    # ThreadRunner(range(0, 100)).start()
    # ThreadRunner(range(100, 200)).start()
    # ThreadRunner(range(200, 300)).start()
    # ThreadRunner(range(300, 400)).start()
    # ThreadRunner(range(400, 500)).start()
    # ThreadRunner(range(500, 600)).start()
    # ThreadRunner(range(600, 700)).start()
    # ThreadRunner(range(700, 800)).start()
    # ThreadRunner(range(800, 900)).start()
    # ThreadRunner(range(900, 1000)).start()
    # ThreadRunner(range(1000, 1100)).start()
    # ThreadRunner(range(1100, 1200)).start()
    # ThreadRunner(range(1200, 1300)).start()
    # ThreadRunner(range(1300, 1400)).start()
    # ThreadRunner(range(1400, 1500)).start()
    # ThreadRunner(range(1500, 1600)).start()
    # ThreadRunner(range(1600, 1700)).start()
    # ThreadRunner(range(1700, 1800)).start()
    # ThreadRunner(range(1800, 1900)).start()
    # ThreadRunner(range(1900, 2000)).start()

    # ThreadRunner(range(2000, 2100)).start()
    # ThreadRunner(range(2100, 2200)).start()
    # ThreadRunner(range(2200, 2300)).start()
    # ThreadRunner(range(2300, 2400)).start()
    # ThreadRunner(range(2400, 2500)).start()
    # ThreadRunner(range(2500, 2600)).start()
    # ThreadRunner(range(2600, 2700)).start()
    # ThreadRunner(range(2700, 2800)).start()
    # ThreadRunner(range(2800, 2900)).start()
    # ThreadRunner(range(2900, 3000)).start()

    # ThreadRunner(range(3000, 3100)).start()
    # ThreadRunner(range(3100, 3200)).start()
    # ThreadRunner(range(3200, 3300)).start()
    # ThreadRunner(range(3300, 3400)).start()
    # ThreadRunner(range(3400, 3500)).start()
    # ThreadRunner(range(3500, 3600)).start()
    # ThreadRunner(range(3600, 3700)).start()
    # ThreadRunner(range(3700, 3800)).start()
    # ThreadRunner(range(3800, 3900)).start()
    # ThreadRunner(range(3900, 4000)).start()

    # ThreadRunner(range(4000, 4100)).start()
    # ThreadRunner(range(4100, 4200)).start()
    # ThreadRunner(range(4200, 4300)).start()
    # ThreadRunner(range(4300, 4400)).start()
    # ThreadRunner(range(4400, 4500)).start()
    # ThreadRunner(range(4500, 4600)).start()
    # ThreadRunner(range(4600, 4700)).start()
    # ThreadRunner(range(4700, 4800)).start()
    # ThreadRunner(range(4800, 4900)).start()
    # ThreadRunner(range(4900, 5000)).start()

    # ThreadRunner(range(5000, 5100)).start()
    # ThreadRunner(range(5100, 5200)).start()
    # ThreadRunner(range(5200, 5300)).start()
    # ThreadRunner(range(5300, 5400)).start()
    # ThreadRunner(range(5400, 5500)).start()
    # ThreadRunner(range(5500, 5600)).start()
    # ThreadRunner(range(5600, 5700)).start()
    # ThreadRunner(range(5700, 5800)).start()
    # ThreadRunner(range(5800, 5900)).start()
    # ThreadRunner(range(5900, 6000)).start()

    # ThreadRunner(range(6000, 6100)).start()
    # ThreadRunner(range(6100, 6200)).start()
    # ThreadRunner(range(6200, 6300)).start()
    # ThreadRunner(range(6300, 6400)).start()
    # ThreadRunner(range(6400, 6500)).start()
    # ThreadRunner(range(6500, 6600)).start()
    # ThreadRunner(range(6600, 6700)).start()
    # ThreadRunner(range(6700, 6800)).start()
    # ThreadRunner(range(6800, 6900)).start()
    # ThreadRunner(range(6900, 7000)).start()

    # ThreadRunner(range(7000, 7100)).start()
    # ThreadRunner(range(7100, 7200)).start()
    # ThreadRunner(range(7200, 7300)).start()
    # ThreadRunner(range(7300, 7400)).start()
    # ThreadRunner(range(7400, 7500)).start()
    # ThreadRunner(range(7500, 7600)).start()
