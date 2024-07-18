import matplotlib.pyplot as plt
from seria_receive import SerialData
from data_processing import DataProcessor
import time

def plot_data(data):
    plt.figure()  # 创建一个新的图形
    plt.plot(data, marker='o', linestyle='-')  # 画出数据点，线性连接
    plt.title('Processed Data A')
    plt.xlabel('Sample Index')
    plt.ylabel('Value')
    plt.grid(True)  # 显示网格
    plt.show(block=False)  # 显示图形，但不阻塞代码运行
    plt.pause(0.001)  # 暂停一段很短的时间，以便更新图形
    plt.close()  # 关闭图形以避免太多开放的窗口

if __name__ == "__main__":
    serial_parser = SerialData(port='COM4')
    serial_parser.start()

    data_processor = DataProcessor(serial_parser)
    data_processor.start()

    try:
        while True:
            processed_data = data_processor.get_processed_data()
            if processed_data:
                # 转换np.float64值为标准浮点数，并格式化输出
                formatted_data = [float(value) for value in processed_data[0]]  # 假设数据是列表的列表
                print(f"Processed Data A: {formatted_data}")
                plot_data(formatted_data)  # 调用绘图函数
            time.sleep(1)  # 刷新率，根据需要调整
    except KeyboardInterrupt:
        data_processor.stop()
        serial_parser.stop()
