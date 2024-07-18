# 定义了一个SerialData类，实例化之后使用.start方法开始串口接收数据，
# 数据使用


import serial
import threading
import queue


class SerialData:
    # __init__函数，在对象被创建的时候自动执行一次，这里传递了两个参数，一个是端口，一个是波特率
    # 他有一个默认值，可传，可不传
    def __init__(self, port='COM4', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_port = None
        self.is_running = False

        # 实例化对象
        self.data_A = queue.Queue()
        self.data_B = queue.Queue()
        self.data_C = queue.Queue()

    def start(self):
        try:
            # 初始化串口对象，连接指定的端口和波特率
            self.serial_port = serial.Serial(self.port, self.baudrate)
            # 设置is_running标志为True，表示串口已经打开并正在运行
            self.is_running = True
            # 这里创建了一个线程，执行rade_from_prot这个函数，这里有个start方法表示打开这个线程，target参数代码
            # 这里thread是一个类，这个类传递了两个参数，target参数指定了需要执行的函数，daemon=True将线程设置为守护线程，表示该线程会在主线程结束时自动结束
            threading.Thread(target=self.read_from_port, daemon=True).start()
            print(f"Successfully opened port {self.port} with baudrate {self.baudrate}")
        except Exception as e:
            # 异常处理，这里没有仔细学过是个很重要的内容
            print(f"Failed to open port {self.port}: {e}")

    def stop(self):
        if self.serial_port:
            self.is_running = False
            self.serial_port.close()
            print("Closed port")

    def read_from_port(self):
        # 这函数异步执行，
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
            # 按照逗号分隔

            # strip方法，用于去字符串两边的空白字符，包括但不限于回车，制表符，空格等等
            a_part = parts[0].strip()
            b_part = parts[1].strip()
            c_part = parts[2].strip()

            # 分别从每部分中解析出数值
            # 这里又利用split方法按照等于号风格，提取列表中的第二个元素转变成int类型
            a_value = int(a_part.split('=')[1])
            b_value = int(b_part.split('=')[1])
            c_value = int(c_part.split('=')[1])

            # 将解析后的数值放入对应的队列
            # 调用queue类的put方法
            self.data_A.put(a_value)
            self.data_B.put(b_value)
            self.data_C.put(c_value)
        except Exception as e:
            print(f"Data parsing error: {e}")
