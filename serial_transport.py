import binascii
import serial
import threading
import queue
import struct
import time


class SerialTransport:
    """
    SerialTransport类用于通过串口发送处理器提供的ECG数据和其他生物指标数据。

    Attributes:
        port (str): 串口端口名称。
        baudrate (int): 波特率。
        serial_port (serial.Serial): 串口对象。
        is_running (bool): 标识串口传输是否正在进行。
        processor (object): 提供数据的处理器对象。
        data (queue.Queue): 数据队列。
    """

    def __init__(self, processor):
        """
        初始化SerialTransport类。

        Args:
            processor (object): 提供数据的处理器对象。
        """
        self.port = 'COM7'
        self.baudrate = 115200
        self.serial_port = None
        self.is_running = False
        self.processor = processor
        self.data = queue.Queue()

    def start(self, port='COM7', baudrate=115200):
        """
        启动串口传输。

        Args:
            port (str): 串口端口名称。
            baudrate (int): 波特率。
        """
        self.port = port
        self.baudrate = baudrate
        self.is_running = True
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        """
        停止串口传输。
        """
        self.is_running = False
        if self.serial_port:
            self.serial_port.close()
            self.serial_port = None
            print("Closed port")

    def _run(self):
        """
        运行串口传输，处理重连逻辑。
        """
        while self.is_running:
            try:
                if not self.serial_port or not self.serial_port.is_open:
                    self._open_port()
                self.translate_data()
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

    def translate_data(self):
        """
        从处理器获取数据并通过串口发送。
        """
        data_packet = self.prepare_data_packet()
        hex_data_packet = binascii.hexlify(data_packet)

        # 打印十六进制表示的数据包
        print(hex_data_packet)

        # 发送数据包
        self.serial_port.write(data_packet)

    def prepare_data_packet(self):
        """
        准备数据包。

        Returns:
            bytes: 打包后的数据包。
        """
        ecg_data = self.processor.get_ecg_data_monitor(40)
        ecg_data = [int(value) for value in ecg_data]  # 将浮点型数据转换为整型
        heart_rate = int(self.processor.get_heart_rate() * 10)
        body_temperature = int(self.processor.get_body_temperature() * 10)
        blood_oxygen = int(self.processor.get_blood_oxygen() * 10)

        # 组装数据包
        data_packet = struct.pack('40IIII',
                                  *ecg_data,
                                  heart_rate,
                                  body_temperature,
                                  blood_oxygen,
                                  )
        return data_packet
