import queue
import threading
import numpy as np
import lttb
import time


class DataProcessor:
    def __init__(self, parser):
        self.parser = parser
        self.processed_data_ecg_web = queue.Queue()
        self.processed_data_ecg_monitor = queue.Queue()
        self.is_running = False
        self.lock = threading.Lock()
        self.ecg_data_original_list = []
        self.lttb_n_count = 40
        self.frequency = 500
        self.heart_rate = 0
        self.rr_interval = 0

        self.bodyTemperature = 0
        self.bloodOxygenSaturation = 0

    def start(self):
        self.is_running = True
        threading.Thread(target=self.process_ecg_data, daemon=True).start()

    def stop(self):
        self.is_running = False

    def process_body_temperature(self):
        while self.is_running:
            try:
                temp_value = self.parser.data_C.get(timeout=1)  # 从传递的串口对象的消息队列中获取一个温度值
            except queue.Empty:
                continue

    def process_blood_oxygen(self):
        while self.is_running:
            try:
                temp_value = self.parser.data_B.get(timeout=1)  # 从传递的串口对象的消息队列中获取一个血氧值
            except queue.Empty:
                continue

    def process_ecg_data(self):
        ecg_point_max = float('-inf')
        ecg_point_min = float('inf')
        ecg_point_max_new = 0
        ecg_point_min_new = 0
        ticks_old = time.time()
        ticks_new = 0
        ecg_points = [3]
        ticks_heart_rate = time.time()
        ticks_heart_rate_new = 0
        peak_interval_num = 0  # 波峰的间隔点个数

        while self.is_running:
            try:
                ecg_value = self.parser.data_A.get(timeout=1)
                self.ecg_data_original_list.append(ecg_value)

                ticks_new = time.time()
                # 刷新最大值与最小值
                if ecg_value > ecg_point_max_new:
                    ecg_point_max_new = ecg_value
                if ecg_value < ecg_point_min_new:
                    ecg_point_min_new = ecg_value

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

                # ------------------------------心率的计算
                elif len(ecg_points) < 3:  # 小于3代表数据初始数据未收集完成
                    ecg_points.append(ecg_value)
                if len(ecg_points) >= 3:  # 大于等于代表可以用于波峰检测
                    ecg_points.pop(0)
                    ecg_points.append(ecg_value)
                    if ecg_points[0] < ecg_points[1] > ecg_points[2]:  # 检测到波峰处理逻辑
                        peak_interval_num = 0  # 波峰间隔点个数清零
                        self.heart_rate = 60 / (1 / self.frequency * peak_interval_num)  # 计算心率
                        self.rr_interval = 1 / self.heart_rate  # 计算RR间隔计算
                    else:  # 未检测到波峰
                        peak_interval_num += 1

                # ------------------------------HRV心率变异度是否需要再开一个线程

                # ------------------------------图像的压缩与队列处理
                if len(self.ecg_data_original_list) == 500:
                    times = np.linspace(0, 499, num=500)
                    temp_list = lttb.downsample(np.column_stack((times, self.ecg_data_original_list)),
                                                self.lttb_n_count)
                    ecg_data_reduced_list = [float(point[1]) for point in temp_list]
                    for point in ecg_data_reduced_list:
                        self.processed_data_ecg_web.put(point)
                        self.processed_data_ecg_monitor.put(point)
                    print(f"Processed and stored data A: {ecg_data_reduced_list}")  # 调试信息
                    self.ecg_data_original_list = []

            except queue.Empty:
                continue

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

    def get_heart_rate(self):
        return self.heart_rate

    def get_rr_interval(self):
        return self.rr_interval

    def get_body_temperature(self):
        return self.bodyTemperature

    def get_blood_oxygen(self):
        return self.bloodOxygenSaturation
