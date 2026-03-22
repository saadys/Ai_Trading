import { Search, ChevronLeft, ChevronRight } from "lucide-react";

const tickerItems = [
  { symbol: "AAPL", change: "-0,39%", isPositive: false },
  { symbol: "BTC", change: "+0,82%", isPositive: true },
  { symbol: "FCHISET", change: "-2,29%", isPositive: false },
  { symbol: "ETH", change: "+1,42%", isPositive: true },
  { symbol: "BNB", change: "+0,62%", isPositive: true },
];

const MarketTicker = () => {
  return (
    <div className="border-b border-border bg-background py-1.5 px-6 shadow-[0_2px_10px_rgba(0,0,0,0.02)] hidden md:flex items-center justify-center">
      <div className="max-w-[1400px] mx-auto w-full flex items-center justify-between gap-4">
        
        {/* Partie Gauche : Ticker des marchés */}
        <div className="flex items-center gap-6 overflow-hidden flex-nowrap shrink-0">
          <span className="text-[13.5px] text-muted-foreground mr-1 font-medium shrink-0">Populaire</span>
          
          <div className="flex items-center gap-5 shrink-0">
            {tickerItems.map((item, idx) => (
              <div key={idx} className="flex items-center gap-2 shrink-0 bg-muted/30 px-3 py-1 rounded-full cursor-pointer hover:bg-muted/60 transition-colors">
                <span className="text-[13px] font-bold text-foreground">{item.symbol}</span>
                <span className={`flex items-center text-[12px] font-bold ${item.isPositive ? 'text-green-600' : 'text-red-600'}`}>
                  {item.isPositive ? '▲' : '▼'} {item.change}
                </span>
              </div>
            ))}
          </div>
          
          {/* Boutons de navigation du ticker */}
          <div className="flex items-center gap-1.5 ml-1">
            <button className="w-7 h-7 rounded-full border border-border bg-background flex items-center justify-center hover:bg-muted transition-colors shadow-sm">
              <ChevronLeft className="w-[14px] h-[14px]" />
            </button>
            <button className="w-7 h-7 rounded-full border border-border bg-background flex items-center justify-center hover:bg-muted transition-colors shadow-sm">
              <ChevronRight className="w-[14px] h-[14px]" />
            </button>
          </div>
        </div>

        {/* Partie Droite : Barre de recherche */}
        <div className="relative shrink-0 w-[280px]">
           <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground stroke-[2]" />
           <input 
             type="text" 
             placeholder="Actions, fonds côtés en bourse, etc." 
             className="w-full bg-muted/40 border border-border rounded-full pl-10 pr-4 py-1.5 text-[13.5px] text-foreground focus:outline-none focus:ring-1 focus:ring-blue-500 transition-all placeholder:text-muted-foreground/70 shadow-inner"
           />
        </div>

      </div>
    </div>
  );
};

export default MarketTicker;
