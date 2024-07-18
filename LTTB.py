import numpy as np
import lttb
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 设置字体以支持中文字符
rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
rcParams['axes.unicode_minus'] = False  # 解决负号显示为方块的问题

data = []

# 打开文件读取内容
with open('ecgdata.txt', 'r') as file:
    x = 0.0  # 初始 x 值
    for line in file:
        y = float(line.strip())  # 假设每行数据是一个浮点数
        data.append([x, y])
        x += 0.04  # 每次递增 0.04

# 将数据转换为 numpy 数组
data = np.array(data)

# 打印原始数据集
print("原始数据集:")
print(data)

# 将其下采样到 30 个点
small_data = lttb.downsample(data, n_out=60)

# 打印下采样后的数据集
print("下采样后的数据集:")
print(small_data)

# 确认下采样后的数据形状
assert small_data.shape == (60, 2)

# 分别绘制原始数据和下采样数据的图像

# 绘制原始数据图像
plt.figure(figsize=(10, 6))
plt.plot(data[:, 0], data[:, 1], label='原始数据', marker='o', markersize=3)
plt.xlabel('时间 (s)')
plt.ylabel('ECG 值')
plt.legend()
plt.title('原始数据')
plt.grid(True)
plt.show()

# 绘制下采样数据图像
plt.figure(figsize=(10, 6))
plt.plot(small_data[:, 0], small_data[:, 1], label='下采样数据', marker='x', linestyle='--', markersize=8)
plt.xlabel('时间 (s)')
plt.ylabel('ECG 值')
plt.legend()
plt.title('下采样数据')
plt.grid(True)
plt.show()
