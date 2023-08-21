# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 23:03:11 2023

@author: hongyu
"""

import baostock as bs
import pandas as pd

bs.login()

df = pd.read_csv('all_stock.csv', encoding = 'latin-1')
CodeList = list(df['code'])

ErrorRecord = []

for code in CodeList:
    if 'bj' in code:
        continue
    print('getting '+code+' data...')
    # rs = bs.query_history_k_data_plus(code,
    # "date,time,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST",
    # start_date='2010-02-28', end_date='2023-02-28',
    # frequency="d", adjustflag="3")
    rs = bs.query_history_k_data_plus(code,
    "date,time,code,close",
    start_date='2020-02-28', end_date='2023-02-28',
    frequency="d", adjustflag="3")
    if rs.error_code == '1':
        ErrorRecord.append(code)
        continue
    data_list = []
    while rs.next():
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns = rs.fields)
    stock_data = result.applymap(lambda x: x.decode('latin-1') if isinstance(x, bytes) else x)
    
    result.to_csv(f"./history_data/{code}.csv", index = False)
    break
bs.logout()
