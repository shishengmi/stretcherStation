from flask import Flask, jsonify
from seria_receive import SerialData
from data_processing import DataProcessor
import threading
import time

app = Flask(__name__)

# 实例化 SerialData 和 DataProcessor
serial_parser = SerialData(port='COM4')
data_processor = DataProcessor(serial_parser)

@app.route('/get_ecg_data', methods=['GET'])
def get_ecg_data():
    processed_data = data_processor.get_ecg_data_web()
    print(f"Retrieved processed data: {processed_data}")  # 调试信息
    return jsonify(processed_data)

def start_services():
    print("Starting serial parser and data processor...")
    serial_parser.start()
    data_processor.start()
    print("Serial parser and data processor started.")

# if __name__ == "__main__":
    # 启动串行和数据处理服务
service_thread = threading.Thread(target=start_services)
service_thread.start()

# 等待服务启动
time.sleep(3)

# 启动Flask应用
print("Starting Flask app...")
print("Starting Flask app...")
app.run(debug=True, host='0.0.0.0', port=5000)
