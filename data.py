# -*- coding: utf-8 -*-
import math
import numpy as np
import pandas as pd

# 数据维度
class_length = 6
# 列名
columns = ['ResponseTime', 'Cost', 'Availability', 'Reliability', 'Reputation']


def base_data():
    """
    获取真实数据作为基本数据
    :return:
    """
    return pd.read_csv('data/base.data', header=None)


def generate_df(_length=100):
    """
    生成服从正态分布的数据,
    并写入文件
    :param _length:
    :return:
    """

    df = base_data()

    data = []
    for i in range(len(columns)):
        sigma = math.sqrt(df[i].describe()['std'])
        mu = df[i].describe()['mean']
        raw_data = pd.DataFrame(np.round(round(sigma ** 2) * np.random.randn(_length, 1) + mu, decimals=0))
        data.append(raw_data)

    df_result = pd.concat(data, axis=1)
    df_result.columns = columns

    # 归一化数据
    normalize(df_result)

    return df_result


def normalize(df):
    """
    归一化数据
    :param df:
    :return:
    """
    for i in range(len(columns)):
        # 响应时间和花费是越少越好,这里将其处理成原始数据越小,归一化之后的数据越大,便于后续处理
        if i == 0 or i == 1:
            df[columns[i]] = np.round(
                (df[columns[i]].max() - df[columns[i]]) / (df[columns[i]].max() - df[columns[i]].min()), 2)
        # 可用性,可靠性,名誉度归一化等比例放缩
        else:
            df[columns[i]] = np.round(
                (df[columns[i]] - df[columns[i]].min()) / (df[columns[i]].max() - df[columns[i]].min()), 2)


def denoise(df, threshold=3):
    """正态分布去噪"""
    for i in range(df.shape[1]):
        if i > 2:
            break
        sigma = math.sqrt(df[columns[i]].describe()['std'])
        mu = df[columns[i]].describe()['mean']
        print(df[np.abs(df[columns[i]] - mu) > threshold * sigma])
        df[columns[i]][np.abs(df[columns[i]] - mu) > threshold * sigma] = None
        return df


def dt_path(i):
    """
    获取仿真数据文件路径
    :param i:
    :return:
    """
    base_path = 'data/simulation_class'
    return base_path + str(i) + '.data'


if __name__ == '__main__':
    for j in range(class_length):
        path = dt_path(j)
        simulation_data = generate_df(_length=20)
        simulation_data.to_csv(path)
