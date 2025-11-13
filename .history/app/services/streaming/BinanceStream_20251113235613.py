

class BinanceStream:
    def __init__(self, socket_url: str):
        self.socket_url = socket_url

    def on_message(ws, message):
    msg = json.loads(message)
    kline = msg['k']  # ← pas de ['data']
    timetamp = kline['t']
    symbol = kline['s']
    open_price = kline['o']
    high = kline['h']
    low = kline['l']
    close = kline['c']
    volume = kline['v']
    is_final = kline['x']

    print(f"[{kline['i']}] {symbol} |T: {timetamp} O: {open_price} | H: {high} | L: {low} | C: {close} | V: {volume} {'✅' if is_final else '🕒'}") 