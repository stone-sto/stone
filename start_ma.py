# -*- encoding:utf-8 -*-
from algorithm.simple_ma import start_simple_ma, start_win_percent_ma

if __name__ == '__main__':
    # simple
    start_simple_ma(5, 10)
    start_simple_ma(10, 20)

    # win percent
    start_win_percent_ma(5, 10, 0.05)
    start_win_percent_ma(10, 20, 0.05)
    start_win_percent_ma(5, 10, 0.1)
    start_win_percent_ma(10, 20, 0.1)
