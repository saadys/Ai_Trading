import websockets
import asyncio

class BinanceStream:
    def __init__(self, socket_url: str):
        self.socket_url = socket_url
        self.ws = None

    async def connect_to_binance_stream(self):
        self.ws = await websockets.connect(self.socket_url)
        while True:
            try:
                message = await self.ws.recv()
                self.on_message(message)
            except websockets.exceptions.ConnectionClosed:
                break
    def on_message(self, message):
        print(message)

    async def disconnect(self):
        if self.ws:
            await self.ws.close()
        

    