# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 19:12:49 2023

@author: hongyu
"""

import os
import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import torch
import DataUtils

data = list(np.random.random_sample((100, 100)) * 2. - 1.)
windows_sizes = [3, 7, 11, 15, 19, 23, 27]
topk = 5

def sample_data(data, num):
    
    sampled_data = {}
    code = np.random.randint(100)
    date = np.random.randint(100)
    for j in range(num + len(windows_sizes)):
        for s in windows_sizes:
            try:
                sampled_data[s].append(data[code][date:date + s])

            except:
                sampled_data[s] = []
    
    return sampled_data

def find_top5_similar_windows(correlation_dict, topk):
    
    top5_similar_windows = []
    top5_positions = []
    loca_record = {}
    for window_size in windows_sizes:
        loca_record[window_size] = []
    
    for j, window_size in enumerate(windows_sizes):
        correlation_list = correlation_dict[window_size]
        _, top5_indices = torch.topk(correlation_list.view(-1), topk)  # 获取相关系数最大的前5个窗口的索引
        l = correlation_dict[window_size].size(1)

        for k in range(1, topk):
            loca_record[window_size].append([int(top5_indices[k] / l), int(top5_indices[k] % l)])

    return loca_record


def plot_correlations(correlation_dict):
    # 获取所有窗口大小
    windows_sizes = list(correlation_dict.keys())

    # 确定最大相关系数列表长度
    max_length = max(len(correlation_list) for correlation_list in correlation_dict.values())

    # 绘制多幅图表，每幅图表显示一个时间点的相关系数曲线
    for i in range(max_length):
        plt.figure(figsize=(8, 6))
        plt.title(f"Day {i+1} Correlation")
        plt.xlabel("Days")
        plt.ylabel("Correlation")

        for window_size in windows_sizes:
            correlation_list = correlation_dict[window_size]
            if i < len(correlation_list):
                plt.plot(range(1, len(correlation_list[i]) + 1), correlation_list[i], label=f"Window {window_size}")

        plt.grid()
        plt.legend()
        plt.show()

def calculate_correlation(array, windows_size):
    data_trans = torch.tensor(data).unfold(1, windows_size, 1).cuda()
    
    array = torch.tensor(array).cuda()
    # array = torch.tensor(array).unsqueeze(0).unsqueeze(0).repeat(data_trans.size(0), data_trans.size(1), 1).cuda()  # Adjust array dimensions
    # print((array - array.mean(dim=-1)).squeeze(0).size())
    try:
        cov_matrix = torch.matmul((data_trans[i] - data_trans[i].mean(dim=-1).unsqueeze(-1)), (array - array.mean(dim=-1))) / (data_trans.size(dim=-1) - 1)
        
        #     print(array)
        #     print(data_trans)
        #     exit()
        # print(cov_matrix.size())
        var1 = array.var(dim=0)
        # print(var1)
        var2 = data_trans.var(dim=2)
        # print(var1.size())
        # print(var2.size())
        correlation_coefficient = cov_matrix / torch.sqrt(var1 * var2)
    except:
        print(array.size())
        print(data_trans.size())
    return correlation_coefficient

def find_matching_rows_count(tensor_a, tensor_b, max_diff=3):
    matching_indices = (tensor_a[:, 0, None] == tensor_b[:, 0])  # 使用广播查找匹配的元素
    matching_rows_a = tensor_a[matching_indices.any(dim=1)]  # 选择匹配行
    matching_rows_b = tensor_b[matching_indices.any(dim=0)]  # 选择匹配行

    element_diff = torch.abs(matching_rows_a[:, 1, None] - matching_rows_b[:, 1])
    matched_count = (element_diff <= max_diff).sum()

    return matched_count


length = len(windows_sizes)
num = 1
# 定义不同的窗口大小

 #### replace it with the rate data in list format
# 创建一个字典，用于保存每个窗口大小对应的相关系数列表
correlation_dict = {}
correlation_list = torch.tensor([])
# sampled_data = sample_data(data, num)
for window_size in windows_sizes:
    # 计算相关系数列表
    for i in range(num):
        cur = sampled_data[window_size][i]
        try:
            torch.cat((correlation_list, calculate_correlation(cur, window_size)), dim = 0)
        except:
            # print(window_size)
            correlation_list = calculate_correlation(cur, window_size)

    # 将相关系数列表保存到字典中
    correlation_dict[window_size] = correlation_list # samples num x topk x 2
data_record = find_top5_similar_windows(correlation_dict, topk + 1)
count = [[[torch.tensor(0) for _ in range(length)] for _ in range(length)] for _ in range(num)]
for no in range(num):
    for i in range(len(windows_sizes)):
        for j in range(i, len(windows_sizes)):
            tensor_a = torch.tensor(data_record[windows_sizes[i]])
            tensor_b = torch.tensor(data_record[windows_sizes[j]])
            print(tensor_a.size(), '   ', tensor_b.size())
            count[no][i][j]=find_matching_rows_count(tensor_a, tensor_b)
sum_count = torch.sum(count, dim = 0)
