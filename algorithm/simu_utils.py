# encoding:utf-8

from account.account import MoneyAccount


def cal_return_level(returns, days):
    """
    用 收益/总天数， 这样没什么意义， 因为5天5%和50天50%差别很大
    所以这里设定几个标准， 即
    5天收益这个标准，
    层1. 5天按照1%，1.01^（天数/5），到达这个收益视为到达层次1， 保持这个收益， 全年51%收益
    层2. 5天按照2%，1.02^（天数/5），到达这个收益视为到达层次2， 保持这个收益， 全年130%收益
    层3. 5天按照3%，1.03^（天数/5），到达这个收益视为到达层次3， 保持这个收益， 全年246%收益
    层4. 5天按照4%，1.04^（天数/5），到达这个收益视为到达层次4， 保持这个收益， 全年419%收益
    层5. 5天按照5%，1.05^（天数/5），到达这个收益视为到达层次5， 保持这个收益， 全年676%收益
    :param returns:收益
    :type returns:float
    :param days:天数
    :type days:int
    :return:收益层级
    :rtype:int
    """
    level1 = 1.01 ** (days/5)
    level2 = 1.02 ** (days/5)
    level3 = 1.03 ** (days/5)
    level4 = 1.04 ** (days/5)
    level5 = 1.05 ** (days/5)

    if returns > level5:
        return 5
    if returns > level4:
        return 4
    if returns > level3:
        return 3
    if returns > level2:
        return 2
    if returns > level1:
        return 1

    return 0


def cal_return_level_with_account(account, days):
    """
    计算算法结果
    :param account: 账户信息
    :type account: MoneyAccount
    :param days: 天数
    :type days: int
    :return: 收益层级
    :rtype: int
    """
    return cal_return_level(account.returns, days)
