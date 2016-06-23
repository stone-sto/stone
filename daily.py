#! -*- encoding:utf-8 -*-

# 每天下午3:30执行,负责收集每日的数据
from data.download import run_every_day

if __name__ == '__main__':
    run_every_day()
