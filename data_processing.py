import numpy as np
import time
import threading
import queue
from parse_serial_data import SerialDataParser

class DataProcessor:
    def __init__(self, parser):
        self.parser = parser
        self.target_rate = 33  # 目标采样率 33Hz
        self.interval = 1.0 / self.target_rate

        # 用于存储处理后的数据
        self.processed_data_A = queue.Queue(maxsize=1000)
        self.processed_data_B = queue.Queue(maxsize=1000)
        self.processed_data_C = queue.Queue(maxsize=1000)

        self.is_running = False
        self.lock = threading.Lock()

    def start(self):
        self.is_running = True
        threading.Thread(target=self.process_data, daemon=True).start()

    def stop(self):
        self.is_running = False

    def process_data(self):
        while self.is_running:
            start_time = time.time()
            raw_data = self.parser.get_data()

            if raw_data['A']:
                self.process_data_A(raw_data['A'])
            if raw_data['B']:
                self.process_data_B(raw_data['B'])
            if raw_data['C']:
                self.process_data_C(raw_data['C'])

            elapsed_time = time.time() - start_time
            sleep_time = max(0, self.interval - elapsed_time)
            time.sleep(sleep_time)

    def process_data_A(self, data):
        with self.lock:
            if self.processed_data_A.full():
                self.processed_data_A.get()
            self.processed_data_A.put(data[-1])

    def process_data_B(self, data):
        with self.lock:
            if self.processed_data_B.full():
                self.processed_data_B.get()
            self.processed_data_B.put(data[-1])

    def process_data_C(self, data):
        with self.lock:
            if self.processed_data_C.full():
                self.processed_data_C.get()
            self.processed_data_C.put(data[-1])

    def get_processed_data(self):
        with self.lock:
            data_A_list = list(self.processed_data_A.queue)
            data_B_list = list(self.processed_data_B.queue)
            data_C_list = list(self.processed_data_C.queue)
        return {
            'A': data_A_list,
            'B': data_B_list,
            'C': data_C_list
        }

# 示例使用
if __name__ == "__main__":
    parser = SerialDataParser()
    parser.start()
    processor = DataProcessor(parser)
    processor.start()

    try:
        while True:
            processed_data = processor.get_processed_data()
            print(f"Processed Data A: {processed_data['A'][-1] if processed_data['A'] else 'N/A'}, "
                  f"B: {processed_data['B'][-1] if processed_data['B'] else 'N/A'}, "
                  f"C: {processed_data['C'][-1] if processed_data['C'] else 'N/A'}")
            time.sleep(1.0 / 33)  # 33Hz
    except KeyboardInterrupt:
        processor.stop()
        parser.stop()
