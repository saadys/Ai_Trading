from typing import Callable, Awaitable
import websockets
import asyncio
import logging

logger = logging.getLogger(__name__)

class BinanceStream:
    def __init__(self, socket_url: str,on_message_callback: Callable[[str], Awaitable[None]] = None):
        self.socket_url = socket_url
        self.ws = None
        self.on_message_callback = on_message_callback
        self.is_running = False

    async def connect_to_binance_stream(self):
        self.ws = await websockets.connect(self.socket_url)
        self.is_running = True
        while self.is_running:
            try:
                message = await self.ws.recv()
                if self.on_message_callback:
                    await self.on_message_callback(message)
                else:
                    print(f"Message reçu (pas de callback configuré): {message}")
            except websockets.exceptions.ConnectionClosed:
                logger.error("Connection closed by the server")
                break
            except Exception as e:
                logger.error(f"Error : {e}")
                await asyncio.sleep(5)
            
    def on_message(self, message):
        print(message)
    
    async def disconnect(self):
        self.is_running = False
        if self.ws:
            await self.ws.close()

    async def reconnect(self):
        await self.disconnect()
        await self.connect_to_binance_stream()
