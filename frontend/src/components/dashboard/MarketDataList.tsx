import { Plus } from "lucide-react";

// Use external reliable SVG icon links for crypto logos to match the screenshot quality
const marketData = [
  { id: 1, symbol: "BTC", name: "Bitcoin", price: "€60 795,46", h24: "+0,26%", d7: "-0,51%", icon: "https://cryptologos.cc/logos/bitcoin-btc-logo.svg?v=024" },
  { id: 2, symbol: "ETH", name: "Ethereum", price: "€1 858,48", h24: "+0,80%", d7: "+3,50%", icon: "https://cryptologos.cc/logos/ethereum-eth-logo.svg?v=024" },
  { id: 3, symbol: "USDT", name: "Tether USDt", price: "€0,8641", h24: "-0,03%", d7: "-0,03%", icon: "https://cryptologos.cc/logos/tether-usdt-logo.svg?v=024" },
  { id: 4, symbol: "USDC", name: "USDC", price: "€0,8641", h24: "+0,01%", d7: "+0,01%", icon: "https://cryptologos.cc/logos/usd-coin-usdc-logo.svg?v=024" },
];

const MarketDataList = () => {
  return (
    <div className="w-full bg-card rounded-xl border border-border shadow-sm p-6 overflow-x-auto">
      {/* Header */}
      <div className="grid grid-cols-[minmax(200px,3fr)_1fr_1fr_1fr_auto] gap-4 px-6 py-3 text-[13px] font-semibold text-muted-foreground uppercase tracking-widest mb-2">
        <div>Symbole</div>
        <div className="text-right">Prix</div>
        <div className="text-right">24H %</div>
        <div className="text-right">7D %</div>
        <div className="w-8"></div>
      </div>

      {/* List */}
      <div className="space-y-3 min-w-[600px]">
        {marketData.map((coin) => (
          <div key={coin.id} className="grid grid-cols-[minmax(200px,3fr)_1fr_1fr_1fr_auto] gap-4 items-center bg-[#f8f9fa] dark:bg-muted/30 hover:bg-muted/50 transition-colors rounded-xl px-6 py-[18px]">
            {/* Left part */}
            <div className="flex items-center gap-5">
              <span className="text-muted-foreground font-medium text-sm w-4">{coin.id}</span>
              <img src={coin.icon} alt={coin.name} className="w-10 h-10 object-contain rounded-full bg-white p-0.5" />
              <div className="flex flex-col">
                <span className="font-bold text-foreground text-[16px] leading-tight">{coin.symbol}</span>
                <span className="text-muted-foreground text-[13px] font-medium mt-0.5">{coin.name}</span>
              </div>
            </div>

            {/* Price */}
            <div className="text-right font-medium text-foreground text-[15px]">
              {coin.price}
            </div>

            {/* 24h% */}
            <div className={`text-right font-bold text-[15px] ${coin.h24.startsWith('+') ? 'text-green-600' : 'text-red-500'}`}>
              {coin.h24}
            </div>

            {/* 7d% */}
            <div className={`text-right font-bold text-[15px] ${coin.d7.startsWith('+') ? 'text-green-600' : 'text-red-500'}`}>
              {coin.d7}
            </div>

            {/* Plus btn */}
            <div className="flex justify-end pl-4">
              <button className="w-[34px] h-[34px] rounded-full border-2 border-border/80 text-foreground flex items-center justify-center hover:bg-background hover:border-border transition-all">
                <Plus className="w-[20px] h-[20px] stroke-[1.5]" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MarketDataList;
