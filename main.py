from seria_receive import SerialData
from data_processing import DataProcessor
import time


if __name__ == "__main__":
    serial_parser = SerialData(port='COM4')  # 实例化串口对象
    serial_parser.start()

    data_processor = DataProcessor(serial_parser)  # 将实例化的串口对象传入DataProcessor的构造函数中
    data_processor.start()

    try:
        while True:
            processed_data = data_processor.get_processed_data()
            if processed_data:
                # 转换np.float64值为标准浮点数，并格式化输出
                formatted_data = [float(value) for value in processed_data[0]]  # 假设数据是列表的列表
                print(f"Processed Data A: {formatted_data}")
            time.sleep(1)  # 刷新率，根据需要调整
    except KeyboardInterrupt:
        data_processor.stop()
        serial_parser.stop()
