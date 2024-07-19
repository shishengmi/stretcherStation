from flask import Flask, jsonify
import logging
from seria_receive import SerialData
from data_processing import DataProcessor
import time

app = Flask(__name__)

# 创建串口数据接收器和数据处理器实例
serial_parser = SerialData(port='COM4')
data_processor = DataProcessor(serial_parser)

@app.route('/ecg', methods=['GET'])
def get_ecg():
    try:
        web_ecg_data = data_processor.get_ecg_data_web()
        return jsonify(web_ecg_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    serial_parser.start()
    data_processor.start()
    try:
        app.run(debug=True)  # 启动 Flask 服务器
    except KeyboardInterrupt:
        data_processor.stop()
        serial_parser.stop()
