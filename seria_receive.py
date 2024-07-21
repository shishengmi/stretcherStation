import serial
import threading
import queue
import time


class SerialReceive:
    """
    SerialReceive类用于接收串口数据并解析。

    Attributes:
        port (str): 串口端口名称。
        baudrate (int): 波特率。
        serial_port (serial.Serial): 串口对象。
        is_running (bool): 标识串口传输是否正在进行。
        data_A (queue.Queue): 数据队列A。
        data_B (queue.Queue): 数据队列B。
        data_C (queue.Queue): 数据队列C。
    """

    def __init__(self, port='COM4', baudrate=115200):
        """
        初始化SerialReceive类。

        Args:
            port (str): 串口端口名称。
            baudrate (int): 波特率。
        """
        self.port = port
        self.baudrate = baudrate
        self.serial_port = None
        self.is_running = False

        # 实例化数据队列对象
        self.data_A = queue.Queue()
        self.data_B = queue.Queue()
        self.data_C = queue.Queue()

    def start(self):
        """
        启动串口接收。
        """
        self.is_running = True
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        """
        停止串口接收。
        """
        self.is_running = False
        if self.serial_port:
            self.serial_port.close()
            self.serial_port = None
            print("Closed port")

    def _run(self):
        """
        运行串口接收，处理重连逻辑。
        """
        while self.is_running:
            try:
                if not self.serial_port or not self.serial_port.is_open:
                    self._open_port()
                self.read_from_port()
            except Exception as e:
                print(f"Error: {e}")
                self._reconnect()

    def _open_port(self):
        """
        打开串口。
        """
        try:
            self.serial_port = serial.Serial(self.port, self.baudrate)
            print(f"Successfully opened port {self.port} with baudrate {self.baudrate}")
        except Exception as e:
            print(f"Failed to open port {self.port}: {e}")
            time.sleep(1)

    def _reconnect(self):
        """
        重连串口，间隔一秒。
        """
        if self.serial_port:
            self.serial_port.close()
        self.serial_port = None
        print("Attempting to reconnect...")
        time.sleep(1)

    def read_from_port(self):
        """
        从串口读取数据并解析。
        """
        while self.is_running and self.serial_port and self.serial_port.is_open:
            try:
                line = self.serial_port.readline().decode('utf-8').strip()
                if line:
                    self.parse_data(line)
            except Exception as e:
                print(f"Error reading from port: {e}")
                self._reconnect()

    def parse_data(self, line):
        """
        解析从串口读取的数据并放入对应的队列。

        Args:
            line (str): 从串口读取的一行数据。
        """
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
