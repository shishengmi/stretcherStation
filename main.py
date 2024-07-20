import matplotlib.pyplot as plt
from seria_receive import SerialData
from data_processing import DataProcessor
import time


def plot_data(data):
    plt.cla()
    plt.figure()  # 创建一个新的图形
    plt.plot(data, marker='o', linestyle='-')  # 画出数据点，线性连接
    plt.title('Processed Data A')
    plt.xlabel('Sample Index')
    plt.ylabel('Value')
    plt.grid(True)  # 显示网格
    plt.show(block=False)  # 显示图形，但不阻塞代码运行
    plt.pause(1)  # 暂停一段时间，以便图形更新
    plt.close()  # 关闭图形以避免太多开放的窗口


if __name__ == "__main__":
    serial_parser = SerialData(port='COM4')
    serial_parser.start()

    data_processor = DataProcessor(serial_parser)
    data_processor.start()

    try:
        while True:
            processed_data = data_processor.get_ecg_data_web()
            if processed_data:
                print(f"Processed Data A: {processed_data}")
                plot_data(processed_data)  # 调用绘图函数
            time.sleep(3)  # 刷新率，根据需要调整
    except KeyboardInterrupt:
        data_processor.stop()
        serial_parser.stop()
