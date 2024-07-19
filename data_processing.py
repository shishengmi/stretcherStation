import queue
import threading
import numpy as np
# 这个numpy
import lttb
from seria_receive import SerialData


class DataProcessor:
    # 传入的parser参数目前只有一个，实例变量，并不是实例化了一个对象
    def __init__(self, parser):
        self.parser = parser
        self.processed_data_A = queue.Queue()
        self.processed_data_ecg_web = queue.Queue()
        self.processed_data_ecg_monitor = queue.Queue()
        self.is_running = False
        self.data_A_list = []
        self.lock = threading.Lock()  # Initialize the lock here
        self.lttb_n_count = 40

    def start(self):
        self.is_running = True
        threading.Thread(target=self.process_data, daemon=True).start()

    def stop(self):
        self.is_running = False

    def process_data(self):
        while self.is_running:
            try:
                # 从传入的对象中访问data_A对象的get方法
                a_value = self.parser.data_A.get(timeout=1)
                self.data_A_list.append(a_value)

                if len(self.data_A_list) == 500:
                    # Process data A using LTTB to downs ample to 40 points
                    times = np.linspace(0, 499, num=500)
                    # 生成一个等间隔的二维数组
                    simplified_data_A = lttb.downsample(np.column_stack((times, self.data_A_list)), self.lttb_n_count)
                    # np.column_stack((times, self.data_A_list)) 合并数组生成一个二位数组
                    processed_A = [point[1] for point in simplified_data_A]
                    # 他是一个列表
                    self.process_data_A(processed_A)
                    for point in processed_A:
                        self.processed_data_ecg_web.put(point)
                        self.processed_data_ecg_monitor.put(point)
                    # 将处理好的数组放入消息队列中
                    self.data_A_list = []  # Clear list for next batch



            except queue.Empty:
                continue

    def process_data_A(self, data):
        with self.lock:  # Now the lock is correctly initialized and used
            while not self.processed_data_A.empty():
                self.processed_data_A.get()
                # 当processed_data_A非空时，丢弃一个
            self.processed_data_A.put(data)
            # 当processed_data_A为空时，放入


    def get_processed_data(self):
        with self.lock:  # 获取锁，如果锁被其他的函数调用则会阻塞，
            return list(self.processed_data_A.queue) if not self.processed_data_A.empty() else []
        # 这个方法保证了保证每次获取到的都只有一个最新的processed_data_A数组

    # 这个方法get了web_queue中的所有元素
    def get_ecg_data_web(self):
        with self.lock:
            extracted_data = []
            while not self.processed_data_ecg_web.empty():
                extracted_data.append(self.processed_data_ecg_web.get())
            return extracted_data

    # 这个方法提取count个数量的对象
    def get_ecg_data_monitor(self, count):
        with self.lock:
            extracted_data = []
            for _ in range(count):
                if self.processed_data_ecg_web.empty():
                    break
                extracted_data.append(self.processed_data_ecg_web.get())
            return extracted_data
