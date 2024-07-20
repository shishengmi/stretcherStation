import queue
import threading
import numpy as np
import lttb
import time
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
        self.frequency = 500

    def start(self):
        self.is_running = True
        threading.Thread(target=self.process_data, daemon=True).start()

    def stop(self):
        self.is_running = False

    def process_data(self):
        ecg_point_max = float('-inf')
        ecg_point_min = float('inf')
        ecg_point_max_new = 0
        ecg_point_min_new = 0
        ticks_old = time.time()
        ticks_new = 0
        ecg_points = [3]
        ticks_heart_rate = time.time()
        ticks_heart_rate_new = 0
        heart_rate = 0

        while self.is_running:
            try:
                a_value = self.parser.data_A.get(timeout=1)
                self.data_A_list.append(a_value)

                ticks_new = time.time()
                # 刷新最大值与最小值
                if a_value > ecg_point_max_new:
                    ecg_point_max_new = a_value
                if a_value < ecg_point_min_new:
                    ecg_point_min_new = a_value

                # 每隔两秒更新一次最大值和最小值
                if ticks_new - ticks_old >= 2:
                    ecg_point_max = ecg_point_max_new
                    ecg_point_min = ecg_point_min_new
                    print(f'Max Value in last 2 seconds: {ecg_point_max_new}')
                    print(f'Min Value in last 2 seconds: {ecg_point_min_new}')

                    # 重置最大值和最小值
                    ecg_point_max_new = float('-inf')
                    ecg_point_min_new = float('inf')
                    ticks_old = ticks_new

                if len(ecg_points) >= 3:
                    ecg_points.pop(0)
                    ecg_points.append(a_value)
                    if ecg_points[0] < ecg_points[1] > ecg_points[2]:
                        # ticks_heart_rate_new = time.time()
                        # heart_rate = 1 / (ticks_heart_rate_new - ticks_heart_rate)
                        # print(heart_rate)

                    # TODO 计算两次波峰的数据点，然后与已知频率计算
                elif len(ecg_points) < 3:
                    ecg_points.append(a_value)






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

    # TODO 计算心率
    # TODO 合理化体温与血氧

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
