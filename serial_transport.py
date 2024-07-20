import serial
import threading
import queue


class SerialDataTransport:
    # __init__函数，在对象被创建的时候自动执行一次，这里传递了两个参数，一个是端口，一个是波特率
    # 他有一个默认值，可传，可不传
    def __init__(self, processor):
        self.port = 'COM5'
        self.baudrate = 115200
        self.serial_port = None
        self.is_running = False
        self.processor = processor
        self.data = queue.Queue()

    def start(self, port='COM4', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        try:
            self.serial_port = serial.Serial(self.port, self.baudrate)
            self.is_running = True
            threading.Thread(target=self.translate_data, daemon=True).start()
            print(f"Successfully opened port {self.port} with baudrate {self.baudrate}")
        except Exception as e:
            print(f"Failed to open port {self.port}: {e}")

    def stop(self):
        if self.serial_port:
            self.is_running = False
            self.serial_port.close()
            print("Closed port")

    def translate_data(self, data):
        if self.serial_port:
            while self.is_running:
                self.data = 0
                self.data += self.processor.get_ecg_data_monitor()
                self.data += self.processor.get_heart_rate()
                self.data += self.processor.get_body_temperature()
                self.data += self.processor.get_blood_oxygen
                print(self.data)
                self.serial_port.write(data.encode())

                # TODO 需要优化格式化字符转
