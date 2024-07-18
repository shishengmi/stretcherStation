import serial
import threading
import queue

class SerialData:
    def __init__(self, port='COM4', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_port = None
        self.is_running = False
        self.data_A = queue.Queue()
        self.data_B = queue.Queue()
        self.data_C = queue.Queue()

    def start(self):
        try:
            self.serial_port = serial.Serial(self.port, self.baudrate)
            self.is_running = True
            threading.Thread(target=self.read_from_port, daemon=True).start()
            print(f"Successfully opened port {self.port} with baudrate {self.baudrate}")
        except Exception as e:
            print(f"Failed to open port {self.port}: {e}")

    def stop(self):
        if self.serial_port:
            self.is_running = False
            self.serial_port.close()
            print("Closed port")

    def read_from_port(self):
        while self.is_running:
            try:
                line = self.serial_port.readline().decode('utf-8').strip()
                if line:
                    self.parse_data(line)
            except Exception as e:
                print(f"Error reading from port: {e}")
                self.is_running = False

    def parse_data(self, line):
        try:
            # 去除可能的空格，分割每一条记录
            parts = line.split(',')
            a_part = parts[0].strip()
            b_part = parts[1].strip()
            c_part = parts[2].strip()

            # 分别从每部分中解析出数值
            a_value = int(a_part.split('=')[1])
            b_value = int(b_part.split('=')[1])
            c_value = int(c_part.split('=')[1])

            # 将解析后的数值放入对应的队列
            self.data_A.put(a_value)
            self.data_B.put(b_value)
            self.data_C.put(c_value)
        except Exception as e:
            print(f"Data parsing error: {e}")

