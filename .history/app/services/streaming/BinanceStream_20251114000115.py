

class BinanceStream:
    def __init__(self, socket_url: str):
        self.socket_url = socket_url
        self.ws = None
        
    def Connect_TO_Binance_Stream(self):
        ws = websocket.WebSocketApp(
            self.socket_url,
            on_message=self.on_message
        )
        ws.run_forever()
    
    def disconnect(self):
        if ws:
            ws.close()
    