from enum import Enum

class StreamTypeEnum(Enum):
    TRADE = "trade" # Ce flux fournit en temps réel chaque transaction (trade) effectuée sur une paire de trading donnée.
    KLINE = "kline" # Ce flux fournit des informations de chandelier/candlestick (kline) pour un intervalle de temps donné (par exemple, 1min, 15min...). 
    TICKER = "ticker"
    BOOK_TICKER = "bookTicker"
    # ...autres types selon la doc