import queue
import threading
import numpy as np
import lttb
from seria_receive import SerialData


class DataProcessor:
    def __init__(self, parser):
        self.parser = parser
        self.processed_data_A = queue.Queue()
        self.processed_data_ecg_web = queue.Queue()
        self.processed_data_ecg_monitor = queue.Queue()
        self.is_running = False
        self.data_A_list = []
        self.lock = threading.Lock()
        self.lttb_n_count = 40

    def start(self):
        self.is_running = True
        threading.Thread(target=self.process_data, daemon=True).start()

    def stop(self):
        self.is_running = False

    def process_data(self):
        while self.is_running:
            try:
                a_value = self.parser.data_A.get(timeout=1)
                self.data_A_list.append(a_value)
                print(f"Received data A: {a_value}")  # 调试信息

                if len(self.data_A_list) == 500:
                    times = np.linspace(0, 499, num=500)
                    simplified_data_A = lttb.downsample(np.column_stack((times, self.data_A_list)), self.lttb_n_count)
                    processed_A = [float(point[1]) for point in simplified_data_A]
                    self.process_data_A(processed_A)
                    for point in processed_A:
                        self.processed_data_ecg_web.put(point)
                        self.processed_data_ecg_monitor.put(point)
                    print(f"Processed and stored data A: {processed_A}")  # 调试信息
                    self.data_A_list = []

            except queue.Empty:
                continue

    def process_data_A(self, data):
        with self.lock:
            while not self.processed_data_A.empty():
                self.processed_data_A.get()
            self.processed_data_A.put(data)

    def get_processed_data(self):
        with self.lock:
            return list(self.processed_data_A.queue) if not self.processed_data_A.empty() else []

    def get_ecg_data_web(self):
        with self.lock:
            extracted_data = []
            while not self.processed_data_ecg_web.empty():
                extracted_data.append(self.processed_data_ecg_web.get())
            print(f"Extracted data for web: {extracted_data}")  # 调试信息
            return extracted_data

    def get_ecg_data_monitor(self, count):
        with self.lock:
            extracted_data = []
            for _ in range(count):
                if self.processed_data_ecg_web.empty():
                    break
                extracted_data.append(self.processed_data_ecg_web.get())
            return extracted_data
