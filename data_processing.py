import queue
import threading
import numpy as np
import lttb
import time


class DataProcessor:
    def __init__(self, parser):
        self.parser = parser
        self.processed_data_ecg_web = queue.Queue(maxsize=100)
        self.processed_data_ecg_monitor = queue.Queue(maxsize=100)
        self.is_running = False
        self.lock = threading.Lock()
        self.ecg_data_original_list = []
        self.lttb_n_count = 40
        self.frequency = 250
        self.heart_rate = 0
        self.rr_interval = 0

        self.bodyTemperature = 0
        self.bloodOxygenSaturation = 0

    def start(self):
        self.is_running = True
        threading.Thread(target=self.process_ecg_data, daemon=True).start()
        threading.Thread(target=self.process_body_temperature, daemon=True).start()
        threading.Thread(target=self.process_blood_oxygen, daemon=True).start()

    def stop(self):
        self.is_running = False

    def process_body_temperature(self):
        temperatures = []  # 用于存储体温的列表
        max_samples = 10000  # 滑动窗口的大小
        scale_factor = 0.85  # 用于调整温度的缩放因子
        offset = 0.0  # 用于调整温度的偏移量
        deviation_threshold = 5.0  # 允许的最大偏差
        alpha = 0.9  # EMA 平滑系数
        ema_temp = None  # 初始化EMA温度
        max_temp = 37.2  # 最大温度限制
        room_temperature = 23.2  # 室温

        while self.is_running:
            try:
                raw_temp_value = self.parser.data_C.get(timeout=1) / 10  # 获取原始温度值
                temp_value = raw_temp_value * scale_factor + offset  # 调整温度

                # 初始化EMA温度或更新
                if ema_temp is None:
                    ema_temp = temp_value
                else:
                    ema_temp = alpha * temp_value + (1 - alpha) * ema_temp

                # 将EMA温度添加到列表中
                temperatures.append(ema_temp)
                if len(temperatures) > max_samples:
                    temperatures.pop(0)  # 维持窗口大小

                self.bodyTemperature = temp_value
            except queue.Empty:
                continue

    def process_blood_oxygen(self):
        while self.is_running:
            try:
                temp_value = self.parser.data_B.get(timeout=1)  # 从传递的串口对象的消息队列中获取一个血氧值
                if temp_value < 1:
                    temp_value = 0
                self.bloodOxygenSaturation = temp_value
            except queue.Empty:
                continue

    def process_ecg_data(self):
        ecg_point_max = float('-inf')
        ecg_point_min = float('inf')
        ecg_point_max_new = 0
        ecg_point_min_new = 0xffffffff
        ticks_old = time.time()
        ticks_new = 0
        ecg_points = [3]
        ticks_heart_rate = time.time()
        ticks_heart_rate_new = 0
        peak_interval_num = 0  # 波峰的间隔点个数
        i = 0

        while self.is_running:
            try:
                ecg_value = self.parser.data_A.get(timeout=1)
                self.ecg_data_original_list.append(ecg_value)

                # ------------------------------心率的计算
                # 刷新最大值与最小值
                if ecg_value > ecg_point_max_new:
                    ecg_point_max_new = ecg_value
                if ecg_value < ecg_point_min_new:
                    ecg_point_min_new = ecg_value

                # 每隔三百个数据点
                if i >= 300:
                    ecg_point_max = ecg_point_max_new
                    ecg_point_min = ecg_point_min_new
                    # 重置最大值和最小值
                    ecg_point_max_new = 0
                    ecg_point_min_new = 0xffffffff
                    i = 0
                else:
                    i += 1

                if len(ecg_points) < 3:  # 小于3代表数据初始数据未收集完成
                    ecg_points.append(ecg_value)
                elif len(ecg_points) >= 3:  # 大于等于代表可以用于波峰检测
                    ecg_points.pop(0)
                    ecg_points.append(ecg_value)
                    if ((ecg_points[0] < ecg_points[1] > ecg_points[2]) &
                            (ecg_points[1] - ecg_point_min > (ecg_point_max - ecg_point_min) / 2)):  # 检测到波峰处理逻辑
                        if peak_interval_num != 0:
                            self.heart_rate = 60 / (1 / self.frequency * peak_interval_num)  # 计算心率

                            self.rr_interval = 1 / self.heart_rate  # 计算RR间隔计算
                            peak_interval_num = 0  # 波峰间隔点个数清零

                    else:  # 未检测到波峰
                        peak_interval_num += 1

                # ------------------------------HRV心率变异度是否需要再开一个线程

                # ------------------------------图像的压缩与队列处理
                if len(self.ecg_data_original_list) == 500:
                    times = np.linspace(0, 499, num=500)
                    temp_list = lttb.downsample(np.column_stack((times, self.ecg_data_original_list)), self.lttb_n_count)
                    ecg_data_reduced_list = [float(point[1]) for point in temp_list]
                    for point in ecg_data_reduced_list:
                        if self.processed_data_ecg_web.full():
                            self.processed_data_ecg_web.get()  # 丢弃前面的数据
                        self.processed_data_ecg_web.put(point)

                        if self.processed_data_ecg_monitor.full():
                            self.processed_data_ecg_monitor.get()  # 丢弃前面的数据
                        self.processed_data_ecg_monitor.put(point)
                    self.ecg_data_original_list = []

            except queue.Empty:
                continue

    def get_ecg_data_web(self):
        with self.lock:
            extracted_data = []
            while not self.processed_data_ecg_web.empty():
                extracted_data.append(self.processed_data_ecg_web.get())
            # print(f"Extracted data for web: {extracted_data}")  # 调试信息
            return extracted_data


    def get_ecg_data_monitor(self, count):
        extracted_data = []
        while True:
            with self.lock:
                try:
                    # 阻塞直到获取到消息或超时2秒
                    data = self.processed_data_ecg_monitor.get(timeout=2)
                    extracted_data.append(data)
                    # 检查是否已获取到指定数量的数据
                    if len(extracted_data) >= count:
                        break
                except queue.Empty:
                    # 超时处理，继续尝试获取数据
                    continue
        return extracted_data


    def get_heart_rate(self):
        return self.heart_rate

    def get_rr_interval(self):
        return self.rr_interval

    def get_body_temperature(self):
        return self.bodyTemperature

    def get_blood_oxygen(self):
        return self.bloodOxygenSaturation
