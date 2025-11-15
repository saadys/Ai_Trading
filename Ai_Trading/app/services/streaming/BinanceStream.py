from typing import Callable, Awaitable
import websockets

import asyncio

class BinanceStream:
    def __init__(self, socket_url: str,on_message_callback: Callable[[str], Awaitable[None]] = None):
        self.socket_url = socket_url
        self.ws = None
        self.on_message_callback = on_message_callback

    async def connect_to_binance_stream(self):
        self.ws = await websockets.connect(self.socket_url)
        while True:
            try:
                message = await self.ws.recv()
                if self.on_message_callback:
                    await self.on_message_callback(message)
                else:
                    print(f"Message reçu (pas de callback configuré): {message}")
            except websockets.exceptions.ConnectionClosed:
                break
            
    def on_message(self, message):
        print(message)
        

    async def disconnect(self):
        if self.ws:
            await self.ws.close()

    async def reconnect(self):
        await self.disconnect()
        await self.connect_to_binance_stream()
