from flask import Flask, jsonify
from flask_cors import CORS  # 这是为了解决跨域问题
from seria_receive import SerialReceive  # 数据接受对象
from data_processing import DataProcessor  # 数据处理对象
import threading
import time

from serial_transport import SerialTransport  # 数据发送对象

app = Flask(__name__)
CORS(app)  # 允许所有域名的跨域请求

# 实例化 SerialData 和 DataProcessor

serial_parser = SerialReceive(port='COM7')  # 实例化数据接受对象，根据情况修改端口
data_processor = DataProcessor(serial_parser)  # 将实例化之后的对象传入数据处理对象，用于完善数据处理
serial_translate = SerialTransport(data_processor)  # 将数据处理对象传入数据发送对象


@app.route('/get_data', methods=['GET'])
def get_ecg_data():
    # 这里是异步处理
    # 从数据处理对象中获取各种数据的值，然后打包成json格式
    ecg_data = data_processor.get_ecg_data_web()
    heart_rate = int(data_processor.get_heart_rate() * 10)
    body_temperature = int(data_processor.get_body_temperature() * 10)
    blood_oxygen = int(data_processor.get_blood_oxygen() * 10)

    # 将所有数据打包成一个字典
    response_data = {
        'ecg_data': ecg_data,
        'heart_rate': heart_rate,
        'body_temperature': body_temperature,
        'blood_oxygen': blood_oxygen
    }

    print(f"Retrieved processed data: {response_data}")  # 调试信息
    return jsonify(response_data)


def start_services():
    # 开启三个线程
    serial_parser.start()
    data_processor.start()
    serial_translate.start(port='COM12', baudrate=115200)


# 启动串行和数据处理服务，这里相当于用一个线程套用了三个线程？？
service_thread = threading.Thread(target=start_services)
service_thread.start()

# 等待服务启动
time.sleep(2)

# 启动Flask应用
print("Starting Flask app...")
app.run(debug=False, host='0.0.0.0', port=5000)

# TODO,添加一个按键监听，实现重定向数据处理对象
