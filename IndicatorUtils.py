# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 21:45:09 2023

@author: hongyu
"""


import baostock as bs
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import numpy as np
from tqdm import tqdm
import yfinance as yf
from DataUtils import *
from datetime import datetime

def drawPlot(long, short, code):
    global short_window, long_window
    x = [i for i in range(1, len(long) + 1)]
    print('draw')
    plt.plot(x, short, label='short')
    plt.plot(x, long, label='long')

    plt.legend()
    plt.xlabel('days')
    plt.ylabel('meanVal')
    plt.title(f"{short_window},{long_window} plot")
    plt.savefig(f'./meanFig/{code}.jpg')
    plt.show()
    
    
def CalcRsiValue(data, n=14, buy_threshold=30, sell_threshold=70):
    """
    计算每只股票的RSI值并输出买卖信号
    :param stockHistData: 一个字典，键为股票代码，值为对应的历史数据
    :param n: RSI计算所需的天数，默认为14天
    :param buy_threshold: RSI低于此阈值则视为买入信号，默认为30
    :param sell_threshold: RSI高于此阈值则视为卖出信号，默认为70
    :return: 一个字典，键为股票代码，值为包含RSI值列表和对应的交易信号字典的元组
    """
    close_prices = data['close'].tolist()
    close_prices = [float(price) for price in close_prices]  # 将列表中的元素都转换为浮点数类型
    rsi_values = [np.nan] * n
    up_sum = 0
    down_sum = 0
    trade_signal_dict = {}
    for i in range(n, len(close_prices)):
        diff = close_prices[i] - close_prices[i-n]
        if diff > 0:
            up_sum += diff
        else:
            down_sum += abs(diff)
        if i == n:
            up_avg = up_sum / n
            down_avg = down_sum / n
        else:
            up_avg = (up_avg * (n-1) + max(diff, 0)) / n
            down_avg = (down_avg * (n-1) + abs(min(diff, 0))) / n
        if down_avg == 0:
            rsi_value = 100
        else:
            rs = up_avg / down_avg
            rsi_value = 100 - 100 / (1 + rs)
        rsi_values.append(rsi_value)
        if len(rsi_values) > n:
            if rsi_values[-1] < buy_threshold:
                trade_signal_dict[i] = 'buy'
            elif rsi_values[-1] > sell_threshold:
                trade_signal_dict[i] = 'sell'
            else:
                trade_signal_dict[i] = 'hold'
    return rsi_values, trade_signal_dict
    
    
def GetAllStockCodes(num = 100):
    lg = bs.login()
    if lg.error_code != '0':
        print("login failed:", lg.error_msg)
        return None
    global today
    today = datetime.today().date()
    today = today.strftime('%Y-%m-%d')
    # today = datetime.datetime.now().date()
    rs = bs.query_all_stock(day=today)
    stockList = []
    # rs = bs.query_all_stock(day=today)
    # flag = 0
    
    while (rs.error_code == '0') & rs.next():
        code = rs.get_row_data()[0]
        if "bj" in code:
            continue
        stockList.append(code)
        # if flag == 2:
        #     break
        # flag += 1
    bs.logout()
    x = np.random.randint(len(stockList) - num)
    return stockList[x:x+num]

def GetAllHistData(stockList):
    lg = bs.login()
    if lg.error_code != '0':
        print("login failed:", lg.error_msg)
        return None

    stockHistData = {}
    for stockCode in stockList:
        if 'bj' in stockCode:
            continue
        rs = bs.query_history_k_data_plus(stockCode,
                                          "date,open,high,low,close,volume",
                                          start_date="2018-5-01", end_date=str(today),
                                          frequency="d", adjustflag="3")
        if rs is None:
            print(f"查询股票代码{stockCode}的历史数据失败")
            continue
        if rs.error_code != '0':
            print(f"查询股票代码{stockCode}的历史数据失败，错误信息：{rs.error_msg}")
            continue


        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        result = pd.DataFrame(data_list, columns=rs.fields)
        result.set_index("date", inplace=True)

        stockHistData[stockCode] = result
        # flag += 1
    bs.logout()
    
    return stockHistData

def calculate_rsrs(stockData):
    stockRSRS = {}
    # 遍历每个股票代码
    for stockCode in stockData.keys():
        # 获取股票历史数据
        stock = stockData[stockCode]
        # 计算RSRS指标
        close = stock['close'].astype(float)
        sma_short = close.rolling(window=10).mean()
        sma_long = close.rolling(window=30).mean()
        resid = close - (sma_short + sma_long) / 2
        std_resid = resid.rolling(window=30).std()
        rsrs = resid / std_resid
        # 添加RSRS值到字典中
        stockRSRS[stockCode] = rsrs
    return stockRSRS



def calculate_obv(stock_data):
    stock_data['OBV'] = 0
    obv_values = [0]
    signal_dict = {}
    
    for i in range(1, len(stock_data)):
        if stock_data['close'][i] > stock_data['close'][i-1]:
            obv_values.append(obv_values[-1] + stock_data['volume'][i])
        elif stock_data['close'][i] < stock_data['close'][i-1]:
            obv_values.append(obv_values[-1] - stock_data['volume'][i])
        else:
            obv_values.append(obv_values[-1])

        if obv_values[i] > obv_values[i-1]:
            signal_dict[i] = 'buy'
        elif obv_values[i] < obv_values[i-1]:
            signal_dict[i] = 'sell'
        else:
            signal_dict[i] = 'hold'

    stock_data['OBV'] = obv_values
    
    return stock_data['OBV'], signal_dict


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

def visualize_rsrs(stockRSRS):
    for stockCode, rsrs in stockRSRS.items():
        plt.plot(rsrs, label=stockCode)
        plt.axhline(y=1, color='r', linestyle='--')
        plt.axhline(y=-1, color='g', linestyle='--')
        plt.title(stockCode + ' RSRS')
        plt.legend()
        plt.show()
        
def generate_signals(stockRSRS):
    signals = {}
    for stockCode, rsrs in stockRSRS.items():
        if rsrs[-1] > 1:
            signals[stockCode] = 'BUY'
            plt.plot(rsrs, label=stockCode)
            plt.axhline(y=1, color='r', linestyle='--')
            plt.axhline(y=-1, color='g', linestyle='--')
            plt.title(stockCode + ' RSRS, BUY')
            plt.legend()
            plt.show()            
        elif rsrs[-1] < -1:
            signals[stockCode] = 'BUY'
            # plt.plot(rsrs, label=stockCode)
            # plt.axhline(y=1, color='r', linestyle='--')
            # plt.axhline(y=-1, color='g', linestyle='--')
            # plt.title(stockCode + ' RSRS, SELL')
            # plt.legend()
            # plt.show()              
        else:
            signals[stockCode] = 'HOLD'
    return signals

def CalcNDayMa(hist_data, n):
    """
    计算每一支股票的N日均线
    :param hist_data: 一个字典，键为股票代码，值为对应的历史数据
    :param n: N日均线的天数
    :return: 一个字典，键为股票代码，值为对应的N日均线数据
    """
    ma_dict = {}
    # hist_data[1] = hist_data[1].set_index('date')
    for stock_code, data in hist_data.items():
        
        close_prices = data['close'].tolist()
        close_prices = [float(price) for price in close_prices]  # 将列表中的元素都转换为浮点数类型
        ma_values = []
        for i in range(len(close_prices)):
            if i < n-1:
                continue
            else:
                ma_value = sum(close_prices[i-n+1:i+1]) / n
                ma_values.append(ma_value)
        ma_dict[stock_code] = ma_values
    return ma_dict


def calculate_capm(stock_code: str):
    # 获取股票历史数据
    stock_df = get_stock_data(stock_code, "2020-01-01", "2021-12-31")

    # 计算股票收益率
    stock_returns = stock_df.pct_change().dropna()

    # 获取市场指数历史数据
    market_df = get_stock_data("sh.000300", "2020-01-01", "2021-12-31") # 使用沪深300指数作为市场指数代表

    # 计算市场指数收益率
    market_returns = market_df.pct_change().dropna()

    # 计算股票与市场指数收益率的协方差和市场指数收益率的方差
    covariance = np.cov(stock_returns["close"], market_returns["close"])[0][1]
    market_variance = np.var(market_returns["close"])

    # 计算贝塔系数
    beta = covariance / market_variance

    # 获取国债收益率作为无风险利率
    risk_free_rate = get_bond_yield_rate("2021-12-31")
    if risk_free_rate:
        risk_free_rate = float(risk_free_rate[0]) / 100
    else:
        risk_free_rate = 0.0

    # 计算市场指数历史平均收益率
    expected_market_return = market_returns.mean()[0]

    # 使用 CAPM 计算预期收益率
    capm_return = risk_free_rate + beta * (expected_market_return - risk_free_rate)

    return capm_return

def SelectCross(short, long):
    l = []
    for code in short:
        
        try:
            if short[code][-1] > long[code][-1] and short[code][-2] < long[code][-2]:
                print('cross stock:', code)
                l.append(code)
        except:
            print('error:', code)
    return l

stocks = GetAllStockCodes()
short_window = 10;
long_window = 50;
# 获取股票列表
# stockCode = 'sh.600000'
stockData = GetAllHistData(stocks)
short = CalcNDayMa(stockData, short_window)
long = CalcNDayMa(stockData, long_window)
sd = SelectCross(short, long)
for cd in sd:
    data = stockData[cd]
    print(cd,' Rsi:',CalcRsiValue(data)[0][-1])
# calculate_capm(stockCode)
