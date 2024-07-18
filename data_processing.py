import queue
import threading
import numpy as np
import lttb
from seria_receive import SerialData

class DataProcessor:
    def __init__(self, parser):
        self.parser = parser
        self.processed_data_A = queue.Queue()
        self.is_running = False
        self.data_A_list = []
        self.lock = threading.Lock()  # Initialize the lock here

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

                if len(self.data_A_list) == 250:
                    # Process data A using LTTB to downsample to 40 points
                    times = np.linspace(0, 249, num=250)
                    simplified_data_A = lttb.downsample(np.column_stack((times, self.data_A_list)), 40)
                    processed_A = [point[1] for point in simplified_data_A]
                    self.process_data_A(processed_A)
                    self.data_A_list = []  # Clear list for next batch

            except queue.Empty:
                continue

    def process_data_A(self, data):
        with self.lock:  # Now the lock is correctly initialized and used
            while not self.processed_data_A.empty():
                self.processed_data_A.get()
            self.processed_data_A.put(data)

    def get_processed_data(self):
        # Return the latest processed data if available
        with self.lock:  # Use the lock here too for safe access
            return list(self.processed_data_A.queue) if not self.processed_data_A.empty() else []
