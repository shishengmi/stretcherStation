import serial
import threading
import queue

class SerialDataParser:
    def __init__(self, port='COM7', baudrate=115200, buffer_size=1000000):
        self.port = port
        self.baudrate = baudrate
        self.buffer_size = buffer_size
        self.serial_port = None
        self.is_running = False
        self.data_A = queue.Queue(maxsize=buffer_size)
        self.data_B = queue.Queue(maxsize=buffer_size)
        self.data_C = queue.Queue(maxsize=buffer_size)
        self.lock = threading.Lock()

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
        while self.is_running and self.serial_port.is_open:
            try:
                line = self.serial_port.readline().decode('utf-8').strip()
                if line:
                    self.parse_data(line)
            except Exception as e:
                print(f"Error: {e}")
                self.is_running = False

    def parse_data(self, line):
        try:
            parts = line.split(',')
            with self.lock:
                for part in parts:
                    if part.startswith('A='):
                        a_value = int(part.split('=')[1])
                        if self.data_A.full():
                            self.data_A.get()
                        self.data_A.put(a_value)
                    elif part.startswith('B='):
                        b_value = int(part.split('=')[1])
                        if self.data_B.full():
                            self.data_B.get()
                        self.data_B.put(b_value)
                    elif part.startswith('C='):
                        c_value = int(part.split('=')[1])
                        if self.data_C.full():
                            self.data_C.get()
                        self.data_C.put(c_value)
        except Exception as e:
            print(f"Data parsing error: {e}")

    def get_data(self):
        with self.lock:
            data_A_list = list(self.data_A.queue)
            data_B_list = list(self.data_B.queue)
            data_C_list = list(self.data_C.queue)
        return {
            'A': data_A_list,
            'B': data_B_list,
            'C': data_C_list
        }

if __name__ == "__main__":
    parser = SerialDataParser()
    parser.start()

    try:
        while True:
            pass  # Keep the main thread alive
    except KeyboardInterrupt:
        parser.stop()
