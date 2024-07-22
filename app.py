from flask import Flask, jsonify
from flask_cors import CORS
from seria_receive import SerialReceive
from data_processing import DataProcessor
import threading
import time

from serial_transport import SerialTransport

app = Flask(__name__)
CORS(app)  # 允许所有域名的跨域请求

# 实例化 SerialData 和 DataProcessor

serial_parser = SerialReceive(port='COM11')
data_processor = DataProcessor(serial_parser)
serial_translate = SerialTransport(data_processor)


@app.route('/get_data', methods=['GET'])
def get_ecg_data():
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
    serial_parser.start()
    data_processor.start()
    serial_translate.start(port='COM7', baudrate=115200)


# 启动串行和数据处理服务
service_thread = threading.Thread(target=start_services)
service_thread.start()

# 等待服务启动
time.sleep(2)

# 启动Flask应用
print("Starting Flask app...")
app.run(debug=False, host='0.0.0.0', port=5000)
