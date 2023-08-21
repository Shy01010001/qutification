# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 20:13:11 2023

@author: hongyu
"""
import baostock as bs
import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_bond_yield_rate(date: str) -> list:
    # 登录系统
    bs.login()
    
    # 获取国债收益率数据
    bond_data = bs.query_bond_yield_data(start_date=date, end_date=date)
    
    # 登出系统
    bs.logout()

    # 将数据存储为 DataFrame
    bond_df = bond_data.get_data()

    # 如果数据不为空，将收益率数据存储为列表并返回
    if not bond_df.empty:
        yield_rates = bond_df["yield_rate"].tolist()
        return yield_rates
    else:
        return []
    
    
def get_stock_data(stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    bs.login()

    stock_data = bs.query_history_k_data_plus(
        stock_code,
        "date,close",
        start_date=start_date,
        end_date=end_date,
        frequency="d",
        adjustflag="3",
    )

    bs.logout()

    stock_df = stock_data.get_data()
    stock_df["date"] = pd.to_datetime(stock_df["date"])
    stock_df["close"] = stock_df["close"].astype(float)
    stock_df.set_index("date", inplace=True)

    return stock_df 
   
    
import pandas as pd

class renew_data:
    def __init__(self, file_path):
        self.xls = pd.ExcelFile(file_path)
        self.sheets_list = self.xls.sheet_names
    
    def drop_columns(self, df):
        df = df.dropna(axis = 1, how = 'all')
        return df
    
    
    def get_latest_date(self):
        for sheet in self.sheets_list:
            used_sheet = sheet
            df = self.xls.parse(sheet)
            df = self.drop_columns(df)
            # print(df.columns)
            if 'sz' in sheet or 'sh' in sheet:
                return self.xls.parse(used_sheet).iloc[-1].iloc[0]
        print('no stock sheet, return None')
        return
    
# excel_file_path = './涨跌幅.xlsx'
# get_date = renew_data(excel_file_path)
# date = get_date.get_latest_date()   

# excel_file_path = ''
# get_date = renew_data(excel_file_path)
# date = get_date.get_latest_date()