#! -*- encoding:utf-8 -*-

from account.account import HoldStock
from datetime import datetime, date
import unittest

from log.time_utils import resolve_date


class TradeInput(object):
    def __init__(self, type, date, stock_name, price, count):
        """
        :param type:买 0 卖 1
        :type type: int
        :param date:
        :type date: date
        :param stock_name:
        :type stock_name: str
        :param price:
        :type price: float
        :param count:
        :type count: int
        """
        super(TradeInput, self).__init__()
        self.type = type
        self.date = date
        self.stock_name = stock_name
        self.price = price
        self.count = count


class TestHoldStock(unittest.TestCase):
    def dealWithTradeInput(self, trade_input_list, hold_stock):
        """
        执行一次trade
        :param trade_input_list: trade list
        :type trade_input_list: list
        :param hold_stock: 一个用来操作的实例
        :type hold_stock: HoldStock
        """
        for trade in trade_input_list:
            if trade.type == 0:
                hold_stock.buy(trade.price, trade.count, trade.date)
            elif trade.type == 1:
                hold_stock.sell(trade.price, trade.count, trade.date)

    def testProcess(self):
        """
        测试流程
        """
        trade_list = list()

        # 第一阶段
        trade_list.append(TradeInput(0, resolve_date('2000-1-1'), '', 100.0, 10000))
        # 卖出失败,因为是当天
        trade_list.append(TradeInput(1, resolve_date('2000-1-1'), '', 100.0, 10000))
        # 110买入一次, 成本价105
        trade_list.append(TradeInput(0, resolve_date('2000-1-1'), '', 110.0, 10000))
        # 120卖出, 赚了15.0/105
        trade_list.append(TradeInput(1, resolve_date('2000-1-2'), '', 120.0, 20000))
        trading_stock = HoldStock('')

        self.dealWithTradeInput(trade_list, trading_stock)
        # 第一阶段 确认结果
        self.assertEqual(trading_stock.cost_price, 105, 'cost price error')
        self.assertEqual(trading_stock.cur_price, 120, 'cur price error')
        self.assertEqual(trading_stock.cur_date, resolve_date('2000-1-2'), 'cur date price error')
        self.assertEqual(trading_stock.return_percent, 15.0/105, 'return percent error')
        self.assertEqual(trading_stock.count, 0, 'count error')
        self.assertEqual(trading_stock.avail_count, 0, 'avail count error')
        self.assertEqual(trading_stock.unavail_stock_count_dict, dict(), 'unavail error ')

    def testProcess1(self):
        """
        测试流程
        """
        trading_stock = HoldStock('test')
        # 首次更新
        trading_stock.update(10.0, resolve_date('2000-1-1'))

        # 当前的日期和价格发生变化, avail为0和空, returns为0, 其他也均为0
        self.assertEqual(trading_stock.cost_price, 0, 'cost price error')
        self.assertEqual(trading_stock.cur_price, 10, 'cur price error')
        self.assertEqual(trading_stock.cur_date, resolve_date('2000-1-1'), 'cur date price error')
        self.assertEqual(trading_stock.return_percent, 0, 'return percent error')
        self.assertEqual(trading_stock.count, 0, 'count error')
        self.assertEqual(trading_stock.avail_count, 0, 'avail count error')
        self.assertEqual(trading_stock.unavail_stock_count_dict, dict(), 'unavail error ')

        # 执行一次买入
        trading_stock.buy(12.0, 100, resolve_date('2000-1-1'))

        self.assertEqual(trading_stock.cost_price, 12, 'cost price error')
        self.assertEqual(trading_stock.cur_price, 12, 'cur price error')
        self.assertEqual(trading_stock.cur_date, resolve_date('2000-1-1'), 'cur date price error')
        self.assertEqual(trading_stock.return_percent, 0, 'return percent error')
        self.assertEqual(trading_stock.count, 100, 'count error')
        self.assertEqual(trading_stock.avail_count, 0, 'avail count error')
        self.assertEqual(trading_stock.unavail_stock_count_dict, {resolve_date('2000-1-1'): 100}, 'unavail error ')

        trading_stock.update(14.0, resolve_date('2000-1-2'))

        self.assertEqual(trading_stock.cost_price, 12, 'cost price error')
        self.assertEqual(trading_stock.cur_price, 14, 'cur price error')
        self.assertEqual(trading_stock.cur_date, resolve_date('2000-1-2'), 'cur date price error')
        self.assertEqual(trading_stock.return_percent,  2.0/12, 'return percent error')
        self.assertEqual(trading_stock.count, 100, 'count error')
        self.assertEqual(trading_stock.avail_count, 100, 'avail count error')
        self.assertEqual(trading_stock.unavail_stock_count_dict, {}, 'unavail error ')

        # 在执行一次买入
        trading_stock.buy(15.0, 100, resolve_date('2000-1-3'))

        # 当前的日期和价格发生变化, avail为0和空, returns为0, 其他也均为0
        self.assertEqual(trading_stock.cost_price, 13.5, 'cost price error')
        self.assertEqual(trading_stock.cur_price, 15, 'cur price error')
        self.assertEqual(trading_stock.cur_date, resolve_date('2000-1-3'), 'cur date price error')
        self.assertEqual(trading_stock.return_percent, 1.5/13.5, 'return percent error')
        self.assertEqual(trading_stock.count, 200, 'count error')
        self.assertEqual(trading_stock.avail_count, 100, 'avail count error')
        self.assertEqual(trading_stock.unavail_stock_count_dict, {resolve_date('2000-1-3'): 100}, 'unavail error ')

        # 执行一次买入
        trading_stock.sell(16.0, 100, resolve_date('2000-1-3'))

        # 当前的日期和价格发生变化, avail为0和空, returns为0, 其他也均为0
        self.assertEqual(trading_stock.cost_price, 13.5, 'cost price error')
        self.assertEqual(trading_stock.cur_price, 16, 'cur price error')
        self.assertEqual(trading_stock.cur_date, resolve_date('2000-1-3'), 'cur date price error')
        self.assertEqual(trading_stock.return_percent, 2.5/13.5, 'return percent error')
        self.assertEqual(trading_stock.count, 100, 'count error')
        self.assertEqual(trading_stock.avail_count, 0, 'avail count error')
        self.assertEqual(trading_stock.unavail_stock_count_dict, {resolve_date('2000-1-3'): 100}, 'unavail error ')




if __name__ == '__main__':
    unittest.main()
