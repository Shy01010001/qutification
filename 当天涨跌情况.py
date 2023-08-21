# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 19:18:20 2023

@author: hongyu
"""
import baostock as bs
import pandas as pd
import datetime


today = datetime.datetime.now().date()
ret = pd.read_excel('./selectedStocks.xlsx',header = None)
bs.login()
cnt = 0


pos = 0
num = ret.shape[1]
for i in range(num):
    code = list(ret[:][i])[0]
    selected = list(ret[:][i])[1]
    if selected == 0:
        continue
    print(selected)
    pos += 1
    rs = bs.query_history_k_data(code, "date,code,open,high,low,close,volume", start_date=f'{today}', end_date=f'{today}', frequency="d", adjustflag="3")
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    stock_data = pd.DataFrame(data_list, columns=rs.fields)
    print('rate： ',(float(stock_data['close'].values[0]) - float(stock_data['open'])) / float(stock_data['open']))
    if float(stock_data['close'].values[0]) - float(stock_data['open']) > 0 :
        cnt+=1
       
# 打印前几行数据
