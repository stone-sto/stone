# -*- coding: utf-8 -*-

__author__ = 'wgx'

import logging
import os
import time

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filemode='a')

log_path_root = '/Users/wgx/workspace/logs/stone/'

# 根据时间log的初始化
t_date_file_path = os.path.join(log_path_root, time.strftime('%Y-%m-%d') + '.log')
date_logger = logging.getLogger('date_logger')
date_file_handler = logging.FileHandler(t_date_file_path)
date_logger.addHandler(date_file_handler)


def log_by_time(t_target_str):
    """
    根据时间，每天产生一份日志
    """
    date_logger.info(t_target_str)