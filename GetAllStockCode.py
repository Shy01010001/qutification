# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 11:33:00 2023

@author: hongyu
"""

import baostock as bs
import pandas as pd

lg = bs.login()
rs = bs.query_all_stock(day = "2023-02-28")
print('query all stock error_code:'+rs.error_code)
print('query_all_stock respond  error_msg:'+rs.error_msg)
data_list = []

while (rs.error_code == '0') & rs.next():
    data_list.append(rs.get_row_data())
result = pd.DataFrame(data_list, columns = rs.fields)
result.to_csv("./all_stock.csv", encoding = 'gbk', index = False)
bs.logout()
    