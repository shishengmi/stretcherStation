import asyncio
import websockets
from typing import Set

connected_clients: Set[websockets.WebSocketServerProtocol] = set()

async def handler(websocket, path):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Received message: {message}")
            await websocket.send(f"Echo: {message}")
    finally:
        connected_clients.remove(websocket)

async def send_message_to_all(message: str):
    if connected_clients:
        await asyncio.gather(*(asyncio.create_task(client.send(message)) for client in connected_clients))
        print(f"Sent message to all clients: {message}")
    else:
        print("No connected clients to send the message.")

async def start_server():
    async with websockets.serve(handler, "localhost", 8765):
        print("WebSocket server started on ws://localhost:8765")
        await asyncio.Future()  # run forever
