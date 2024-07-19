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
            web_ecg_data = data_processor.get_ecg_data_web()
            monitor_ecg_data = data_processor.get_ecg_data_monitor(40)
            print("webdata: " + ", ".join(web_ecg_data))
            print("ecgdata: " + ", ".join(monitor_ecg_data))
            time.sleep(1)  # 刷新率，根据需要调整
    except KeyboardInterrupt:
        data_processor.stop()
        serial_parser.stop()
