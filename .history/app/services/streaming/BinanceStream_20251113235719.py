

class BinanceStream:
    def __init__(self, socket_url: str):
        self.socket_url = socket_url

    def Connect_TO_Binance(self):
        ws = websocket.WebSocketApp(
            self.socket_url,
            on_message=self.on_message
        )
        ws.run_forever()