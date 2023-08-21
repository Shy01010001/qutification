# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 20:16:19 2023

@author: hongyu
"""
import baostock as bs
import pandas as pd
import matplotlib.pyplot as plt

def backtest(strategy_func, stock_code):
    """
    获取输入股票代码的历史3年数据，回测量化策略盈亏额，初始10000元
    :param strategy_func: 策略函数，有一个输入值，DataFrame结构的股票历史信息，有两个return值。
                          第一个是一个列表指标值，第二个是字典结构，key是第n天，value是第n天的操作，
                          包括sell，buy和hold信号。
    :param stock_code: 股票代码，字符串类型，如 'sh.600000'
    :return: 每一天资产+现金的总和，列表类型
    """
    # 登陆系统
    bs.login()
    # 获取股票历史数据
    rs = bs.query_history_k_data(stock_code, "date,open,high,low,close,volume", start_date='2022-03-28',
                                 end_date='2023-03-28', frequency="d", adjustflag="3")
    # 转换数据格式
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    df_stock = pd.DataFrame(data_list, columns=rs.fields)
    df_stock = df_stock.set_index('date')
    df_stock = df_stock.astype(float)
    # 执行策略函数
    indicators, signals = strategy_func(df_stock)
    df_stock = df_stock.reset_index()
    # 绘制股价和买卖标记的折线图
    plt.plot(df_stock.index, df_stock['close'])
    for day, signal in signals.items():
        if signal == 'buy':
            plt.plot(day, df_stock.loc[day, 'close'], '^', markersize=10, color='green')
        elif signal == 'sell':
            plt.plot(day, df_stock.loc[day, 'close'], 'v', markersize=10, color='red')
    plt.title('Stock Price with Buy/Sell Signals')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.show()
    # 进行回测
    cash = 10000  # 初始资金
    shares = 0  # 初始股票持仓
    profits = []  # 每天的盈利情况
    for day, signal in signals.items():
        close_price = df_stock.loc[day, 'close']
        if signal == 'buy':
            num_shares = min(int(cash / close_price), 10000 // int(close_price))  # 不买超过本金的股票
            shares += num_shares
            cash -= num_shares * close_price
        elif signal == 'sell':
            cash += shares * close_price
            shares = 0
        profits.append(cash + shares * close_price)
    # 退出系统
    bs.logout()
    return profits