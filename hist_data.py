# -*- coding: utf-8 -*-
"""
Created on Sun Aug  6 17:25:28 2023

@author: hongyu
"""
import pandas as pd
import os
def read_change_percentage_from_excel(file_path):
    # 读取Excel文件中的所有数据
    xls = pd.ExcelFile(file_path)
    
    # 创建一个空列表，用于存储所有股票的change_percentage数据
    change_percentage_list = []
    
    # 遍历每个sheet，每个sheet代表一个股票代码
    for sheet_name in xls.sheet_names:
        # 读取当前sheet的数据
        df = xls.parse(sheet_name)
        
        # 将change_percentage列转换为列表，并去除空值
        change_percentage = df['change_percentage'].tolist()
        change_percentage = [x for x in change_percentage if pd.notna(x)]
        
        # 将当前股票的change_percentage列表加入总列表
        change_percentage_list.append(change_percentage)
    
    return change_percentage_list

# 假设“涨跌幅.xlsx”文件在当前工作目录下
file_path = "涨跌幅.xlsx"

change_percentage_list = read_change_percentage_from_excel(file_path)