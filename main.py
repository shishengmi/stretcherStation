import time
import asyncio
import json
from websocket_server import start_server, send_message_to_all, connected_clients
from parse_serial_data import SerialDataParser
from data_processing import DataProcessor

async def send_data(processor):
    while True:
        if connected_clients:  # Check if there are connected clients
            processed_data = processor.get_processed_data()
            # 获取最新的33个A，一个B，一个C
            data_A = processed_data['A'][-33:] if len(processed_data['A']) >= 33 else processed_data['A']
            data_B = processed_data['B'][-1] if processed_data['B'] else 'N/A'
            data_C = processed_data['C'][-1] if processed_data['C'] else 'N/A'

            # 构建消息
            message = {
                'A': data_A,
                'B': data_B,
                'C': data_C
            }
            # 转换成JSON格式
            json_message = json.dumps(message)

            # 发送消息
            await send_message_to_all(json_message)
        await asyncio.sleep(1)  # 33Hz


async def main():
    parser = SerialDataParser()
    parser.start()

    processor = DataProcessor(parser)
    processor.start()

    server_task = asyncio.create_task(start_server())
    send_data_task = asyncio.create_task(send_data(processor))

    await asyncio.gather(server_task, send_data_task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
