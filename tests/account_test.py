#! -*- encoding:utf-8 -*-

import unittest

from account.account import MoneyAccount, Order
from log.time_utils import resolve_date


class AccountTest(unittest.TestCase):
    """
    测试Account相关
    """
    def testProcess1(self):
        """
        1
        """
        test_st_name = 'test_st_name'
        money_account = MoneyAccount(1000.0)
        money_account.buy(test_st_name, 2.0, 100, resolve_date('2000-1-1'))

        # account
        self.assertEqual(money_account.cash, 770, 'cash error')
        self.assertEqual(money_account.returns, - 30.0 / 1000, 'returns error')
        self.assertEqual(money_account.property, 970, 'property error')
        self.assertEqual(money_account.origin_property, 1000, 'origin property error')

        # order
        test_order = money_account.order_list[-1]
        self.assertEqual(len(money_account.order_list), 1, 'order list error')
        self.assertEqual(test_order.stock_name, test_st_name, 'order st name error')
        self.assertEqual(test_order.type, Order.order_type_buy, 'order type error')
        self.assertEqual(test_order.price, 2, 'order price error')
        self.assertEqual(test_order.count, 100, 'order count error')
        self.assertEqual(test_order.date, resolve_date('2000-1-1'), 'order date error')
        self.assertEqual(test_order.stock_cost, 200, 'order type error')
        self.assertEqual(test_order.tax, 30, 'order type error')
        self.assertEqual(test_order.all_cost, 230, 'order type error')

        # hold stock
        self.assertEqual(len(money_account.stocks), 1, 'hold stock count error')

        # 当天卖出, 一定失败, 结果不变
        money_account.sell(test_st_name, 2.0, 100, resolve_date('2000-1-1'))

        # account
        self.assertEqual(money_account.cash, 770, 'cash error')
        self.assertEqual(money_account.returns, - 30.0 / 1000, 'returns error')
        self.assertEqual(money_account.property, 970, 'property error')
        self.assertEqual(money_account.origin_property, 1000, 'origin property error')

        # order
        test_order = money_account.order_list[-1]
        self.assertEqual(len(money_account.order_list), 1, 'order list error')
        self.assertEqual(test_order.stock_name, test_st_name, 'order st name error')
        self.assertEqual(test_order.type, Order.order_type_buy, 'order type error')
        self.assertEqual(test_order.price, 2, 'order price error')
        self.assertEqual(test_order.count, 100, 'order count error')
        self.assertEqual(test_order.date, resolve_date('2000-1-1'), 'order date error')
        self.assertEqual(test_order.stock_cost, 200, 'order type error')
        self.assertEqual(test_order.tax, 30, 'order type error')
        self.assertEqual(test_order.all_cost, 230, 'order type error')

        # hold stock
        self.assertEqual(len(money_account.stocks), 1, 'hold stock count error')

        # 第二天卖出, 2.5
        money_account.sell(test_st_name, 2.5, 100, resolve_date('2000-1-2'))

        # account
        self.assertEqual(money_account.cash, 990, 'cash error')
        self.assertEqual(money_account.returns, - 10.0 / 1000, 'returns error')
        self.assertEqual(money_account.property, 990, 'property error')
        self.assertEqual(money_account.origin_property, 1000, 'origin property error')

        # order
        test_order = money_account.order_list[-1]
        self.assertEqual(len(money_account.order_list), 2, 'order list error')
        self.assertEqual(test_order.stock_name, test_st_name, 'order st name error')
        self.assertEqual(test_order.type, Order.order_type_sell, 'order type error')
        self.assertEqual(test_order.price, 2.5, 'order price error')
        self.assertEqual(test_order.count, 100, 'order count error')
        self.assertEqual(test_order.date, resolve_date('2000-1-2'), 'order date error')
        self.assertEqual(test_order.stock_cost, 250, 'order type error')
        self.assertEqual(test_order.tax, 30, 'order type error')
        self.assertEqual(test_order.all_cost, 30, 'order type error')

        # hold stock
        self.assertEqual(len(money_account.stocks), 0, 'hold stock count error')

        # 第二天买入, 2.0, 50% 实际上应为200
        money_account.buy_with_cash_percent(test_st_name, 2.0, 0.5, resolve_date('2000-1-2'))

        # account
        self.assertEqual(money_account.cash, 560, 'cash error')
        self.assertEqual(money_account.returns, - 40.0 / 1000, 'returns error')
        self.assertEqual(money_account.property, 960, 'property error')
        self.assertEqual(money_account.origin_property, 1000, 'origin property error')

        # order
        test_order = money_account.order_list[-1]
        self.assertEqual(len(money_account.order_list), 3, 'order list error')
        self.assertEqual(test_order.stock_name, test_st_name, 'order st name error')
        self.assertEqual(test_order.type, Order.order_type_buy, 'order type error')
        self.assertEqual(test_order.price, 2.0, 'order price error')
        self.assertEqual(test_order.count, 200, 'order count error')
        self.assertEqual(test_order.date, resolve_date('2000-1-2'), 'order date error')
        self.assertEqual(test_order.stock_cost, 400, 'order type error')
        self.assertEqual(test_order.tax, 30, 'order type error')
        self.assertEqual(test_order.all_cost, 430, 'order type error')

        # hold stock
        self.assertEqual(len(money_account.stocks), 1, 'hold stock count error')

        # 第三天, 涨到了4.0
        money_account.update_with_all_stock_one_line({test_st_name: (4.0, '2000-1-3')})

        # account
        self.assertEqual(money_account.cash, 560, 'cash error')
        self.assertEqual(money_account.returns, 360.0 / 1000, 'returns error')
        self.assertEqual(money_account.property, 1360, 'property error')
        self.assertEqual(money_account.origin_property, 1000, 'origin property error')

        # order
        test_order = money_account.order_list[-1]
        self.assertEqual(len(money_account.order_list), 3, 'order list error')
        self.assertEqual(test_order.stock_name, test_st_name, 'order st name error')
        self.assertEqual(test_order.type, Order.order_type_buy, 'order type error')
        self.assertEqual(test_order.price, 2.0, 'order price error')
        self.assertEqual(test_order.count, 200, 'order count error')
        self.assertEqual(test_order.date, resolve_date('2000-1-2'), 'order date error')
        self.assertEqual(test_order.stock_cost, 400, 'order type error')
        self.assertEqual(test_order.tax, 30, 'order type error')
        self.assertEqual(test_order.all_cost, 430, 'order type error')

        # hold stock
        self.assertEqual(len(money_account.stocks), 1, 'hold stock count error')

        # 第三天, 变成全仓
        money_account.buy_with_cash_percent(test_st_name, 5.0, 1.0, resolve_date('2000-1-3'))

        # account
        self.assertEqual(money_account.cash, 30, 'cash error')
        self.assertEqual(money_account.returns, 530.0 / 1000, 'returns error')
        self.assertEqual(money_account.property, 1530, 'property error')
        self.assertEqual(money_account.origin_property, 1000, 'origin property error')

        # order
        test_order = money_account.order_list[-1]
        self.assertEqual(len(money_account.order_list), 4, 'order list error')
        self.assertEqual(test_order.stock_name, test_st_name, 'order st name error')
        self.assertEqual(test_order.type, Order.order_type_buy, 'order type error')
        self.assertEqual(test_order.price, 5.0, 'order price error')
        self.assertEqual(test_order.count, 100, 'order count error')
        self.assertEqual(test_order.date, resolve_date('2000-1-3'), 'order date error')
        self.assertEqual(test_order.stock_cost, 500, 'order type error')
        self.assertEqual(test_order.tax, 30, 'order type error')
        self.assertEqual(test_order.all_cost, 530, 'order type error')

        # hold stock
        self.assertEqual(len(money_account.stocks), 1, 'hold stock count error')

        # 第三天, 卖掉0.3, 应该是90, 不足100, 应该有错误提示
        money_account.sell_with_hold_percent(test_st_name, 4.0, 0.3, resolve_date('2000-1-3'))

         # account
        self.assertEqual(money_account.cash, 30, 'cash error')
        self.assertEqual(money_account.returns, 530.0 / 1000, 'returns error')
        self.assertEqual(money_account.property, 1530, 'property error')
        self.assertEqual(money_account.origin_property, 1000, 'origin property error')

        # order
        test_order = money_account.order_list[-1]
        self.assertEqual(len(money_account.order_list), 4, 'order list error')
        self.assertEqual(test_order.stock_name, test_st_name, 'order st name error')
        self.assertEqual(test_order.type, Order.order_type_buy, 'order type error')
        self.assertEqual(test_order.price, 5.0, 'order price error')
        self.assertEqual(test_order.count, 100, 'order count error')
        self.assertEqual(test_order.date, resolve_date('2000-1-3'), 'order date error')
        self.assertEqual(test_order.stock_cost, 500, 'order type error')
        self.assertEqual(test_order.tax, 30, 'order type error')
        self.assertEqual(test_order.all_cost, 530, 'order type error')

        # hold stock
        self.assertEqual(len(money_account.stocks), 1, 'hold stock count error')

        # 第三天, 全仓卖出, 但是有部分是当天买的, 所以失败
        money_account.sell_with_hold_percent(test_st_name, 4.0, 1.0, resolve_date('2000-1-3'))

        # account
        self.assertEqual(money_account.cash, 30, 'cash error')
        self.assertEqual(money_account.returns, 530.0 / 1000, 'returns error')
        self.assertEqual(money_account.property, 1530, 'property error')
        self.assertEqual(money_account.origin_property, 1000, 'origin property error')

        # order
        test_order = money_account.order_list[-1]
        self.assertEqual(len(money_account.order_list), 4, 'order list error')
        self.assertEqual(test_order.stock_name, test_st_name, 'order st name error')
        self.assertEqual(test_order.type, Order.order_type_buy, 'order type error')
        self.assertEqual(test_order.price, 5.0, 'order price error')
        self.assertEqual(test_order.count, 100, 'order count error')
        self.assertEqual(test_order.date, resolve_date('2000-1-3'), 'order date error')
        self.assertEqual(test_order.stock_cost, 500, 'order type error')
        self.assertEqual(test_order.tax, 30, 'order type error')
        self.assertEqual(test_order.all_cost, 530, 'order type error')

        # hold stock
        self.assertEqual(len(money_account.stocks), 1, 'hold stock count error')

        # 第三天, 半仓卖出, 应该是100, 价格4.0
        money_account.sell_with_hold_percent(test_st_name, 4.0, 0.5, resolve_date('2000-1-3'))

        # account
        self.assertEqual(money_account.cash, 400, 'cash error')
        self.assertEqual(money_account.returns, 200.0 / 1000, 'returns error')
        self.assertEqual(money_account.property, 1200, 'property error')
        self.assertEqual(money_account.origin_property, 1000, 'origin property error')

        # order
        test_order = money_account.order_list[-1]
        self.assertEqual(len(money_account.order_list), 5, 'order list error')
        self.assertEqual(test_order.stock_name, test_st_name, 'order st name error')
        self.assertEqual(test_order.type, Order.order_type_sell, 'order type error')
        self.assertEqual(test_order.price, 4.0, 'order price error')
        self.assertEqual(test_order.count, 100, 'order count error')
        self.assertEqual(test_order.date, resolve_date('2000-1-3'), 'order date error')
        self.assertEqual(test_order.stock_cost, 400, 'order type error')
        self.assertEqual(test_order.tax, 30, 'order type error')
        self.assertEqual(test_order.all_cost, 30, 'order type error')

        # hold stock
        self.assertEqual(len(money_account.stocks), 1, 'hold stock count error')

        # 第三天, 再买半仓, 应该是还是100, 价格6.0
        money_account.sell_with_hold_percent(test_st_name, 6.0, 0.5, resolve_date('2000-1-3'))

        # account
        self.assertEqual(money_account.cash, 970, 'cash error')
        self.assertEqual(money_account.returns, 570.0 / 1000, 'returns error')
        self.assertEqual(money_account.property, 1570, 'property error')
        self.assertEqual(money_account.origin_property, 1000, 'origin property error')

        # order
        test_order = money_account.order_list[-1]
        self.assertEqual(len(money_account.order_list), 6, 'order list error')
        self.assertEqual(test_order.stock_name, test_st_name, 'order st name error')
        self.assertEqual(test_order.type, Order.order_type_sell, 'order type error')
        self.assertEqual(test_order.price, 6.0, 'order price error')
        self.assertEqual(test_order.count, 100, 'order count error')
        self.assertEqual(test_order.date, resolve_date('2000-1-3'), 'order date error')
        self.assertEqual(test_order.stock_cost, 600, 'order type error')
        self.assertEqual(test_order.tax, 30, 'order type error')
        self.assertEqual(test_order.all_cost, 30, 'order type error')

        # hold stock
        self.assertEqual(len(money_account.stocks), 1, 'hold stock count error')

        # 第四天, 全部卖掉, 应该是还是100, 价格6.0
        money_account.sell_with_hold_percent(test_st_name, 6.0, 1.0, resolve_date('2000-1-4'))

        # account
        self.assertEqual(money_account.cash, 1540, 'cash error')
        self.assertEqual(money_account.returns, 540.0 / 1000, 'returns error')
        self.assertEqual(money_account.property, 1540, 'property error')
        self.assertEqual(money_account.origin_property, 1000, 'origin property error')

        # order
        test_order = money_account.order_list[-1]
        self.assertEqual(len(money_account.order_list), 7, 'order list error')
        self.assertEqual(test_order.stock_name, test_st_name, 'order st name error')
        self.assertEqual(test_order.type, Order.order_type_sell, 'order type error')
        self.assertEqual(test_order.price, 6.0, 'order price error')
        self.assertEqual(test_order.count, 100, 'order count error')
        self.assertEqual(test_order.date, resolve_date('2000-1-4'), 'order date error')
        self.assertEqual(test_order.stock_cost, 600, 'order type error')
        self.assertEqual(test_order.tax, 30, 'order type error')
        self.assertEqual(test_order.all_cost, 30, 'order type error')

        # hold stock
        self.assertEqual(len(money_account.stocks), 0, 'hold stock count error')


if __name__ == '__main__':
    unittest.main()
