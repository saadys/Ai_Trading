

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
    
    async def disconnect(self):
        if self.ws:
            await self.ws.close()
        
async def main():
"""Fonction principale pour tester la connexion."""
print("Initialisation du stream Binance...")
stream = BinanceStream()
await stream.connect_to_binance_stream()

if __name__ == "__main__":
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nArrêt du stream.")
    