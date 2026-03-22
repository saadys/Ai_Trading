import { useState } from "react";
import { ChevronDown, ChevronUp, ArrowUpRight, Activity, Clock } from "lucide-react";

/**
 * Composant Analyse & Screener IA
 * Remplace l'ancien affichage basique par un panneau professionnel
 * typé "Trading Intelligence".
 */
const StatsOverview = () => {
  const [activeTab, setActiveTab] = useState("Tous les signaux");
  // Expand "sentiment" by default to show some content
  const [expandedRow, setExpandedRow] = useState<string | null>("sentiment");

  const tabs = ["Tous les signaux", "Cryptos", "Forex", "Actions", "Matières Premières"];

  const toggleRow = (id: string) => {
    setExpandedRow(expandedRow === id ? null : id);
  };

  return (
    <div className="flex flex-col mb-8">
      <h2 className="text-[20px] font-bold text-foreground mb-4">Analyse des Signaux IA</h2>

      <div className="bg-white dark:bg-card text-card-foreground rounded-xl border border-border/80 p-5 shadow-[0_2px_10px_rgba(0,0,0,0.02)] mb-6">
        <h3 className="text-[15px] font-semibold mb-3 text-foreground/90">Filtrer par marché</h3>
        
        {/* Pills / Boutons de filtre */}
        <div className="flex flex-wrap gap-2">
           {tabs.map((tab) => (
             <button
               key={tab}
               onClick={() => setActiveTab(tab)}
               className={`px-4 py-1.5 rounded-full text-[13px] font-medium transition-colors ${
                 activeTab === tab 
                 ? "bg-blue-600 text-white shadow-[0_2px_4px_rgba(37,99,235,0.2)]"
                 : "bg-[#f3f4f6] dark:bg-muted text-foreground/80 hover:bg-gray-200 dark:hover:bg-muted/80"
               }`}
             >
               {tab}
             </button>
           ))}
        </div>
      </div>

      {/* Accordéons analytiques dédiés au trading */}
      <div className="flex flex-col w-full">
        
        {/* 1. Sentiment Analyst */}
        <div className="border-b border-border/60">
          <button 
            onClick={() => toggleRow("sentiment")}
            className="w-full flex justify-between items-center py-4 cursor-pointer group hover:bg-muted/10 transition-colors"
          >
            <span className="text-[16px] font-semibold text-foreground/90 group-hover:text-blue-600 transition-colors">Sentiment Analyst (IA)</span>
            {expandedRow === "sentiment" ? <ChevronUp className="w-5 h-5 text-muted-foreground stroke-[1.5]" /> : <ChevronDown className="w-5 h-5 text-muted-foreground stroke-[1.5]" />}
          </button>
          
          {expandedRow === "sentiment" && (
             <div className="pb-4 pt-1 animate-in fade-in slide-in-from-top-1 duration-200">
               <div className="grid grid-cols-2 gap-4">
                 <div className="bg-muted/20 p-3 rounded-lg border border-border/50">
                   <p className="text-[11px] text-muted-foreground mb-1 uppercase tracking-wider font-bold">Tendance Globale</p>
                   <p className="text-lg font-bold text-green-600 flex items-center gap-1"><ArrowUpRight className="w-5 h-5"/> FORTE HAUSSE</p>
                 </div>
                 <div className="bg-muted/20 p-3 rounded-lg border border-border/50">
                   <p className="text-[11px] text-muted-foreground mb-1 uppercase tracking-wider font-bold">Indice de Peur (VIX)</p>
                   <p className="text-lg font-bold text-orange-500 flex items-center gap-1"><Activity className="w-5 h-5"/> 18.4 (Volatil)</p>
                 </div>
                 <div className="col-span-2 bg-muted/20 p-3 rounded-lg border border-border/50">
                   <div className="flex justify-between mb-1.5">
                     <span className="text-[11px] font-bold text-muted-foreground uppercase tracking-wider">Pression du Carnet d'Ordres</span>
                     <span className="text-xs font-bold text-blue-600">76% Acheteurs</span>
                   </div>
                   <div className="w-full bg-border rounded-full h-1.5">
                     <div className="bg-blue-600 h-1.5 rounded-full" style={{ width: "76%" }}></div>
                   </div>
                 </div>
               </div>
             </div>
          )}
        </div>

        {/* 2. Historique des trades récents */}
        <div className="border-b border-border/60">
          <button 
            onClick={() => toggleRow("historique")}
            className="w-full flex justify-between items-center py-4 cursor-pointer group hover:bg-muted/10 transition-colors"
          >
            <span className="text-[16px] font-semibold text-foreground/90 group-hover:text-blue-600 transition-colors">Historique des Trades Récents</span>
            {expandedRow === "historique" ? <ChevronUp className="w-5 h-5 text-muted-foreground stroke-[1.5]" /> : <ChevronDown className="w-5 h-5 text-muted-foreground stroke-[1.5]" />}
          </button>

          {expandedRow === "historique" && (
            <div className="pb-4 pt-1 flex flex-col gap-3 animate-in fade-in slide-in-from-top-1 duration-200 px-1">
               {/* Trade 1 */}
               <div className="flex justify-between items-center bg-muted/20 p-2.5 rounded-md border border-border/50 shadow-sm">
                 <div className="flex items-center gap-3">
                   <div className="w-8 h-8 rounded shrink-0 bg-green-500/10 flex items-center justify-center text-green-600 font-bold text-[10px] tracking-wider">LONG</div>
                   <div className="flex flex-col">
                     <span className="text-sm font-bold text-foreground">BTC/USDT</span>
                     <span className="text-[11px] text-muted-foreground font-medium">Fermé il y a 2h</span>
                   </div>
                 </div>
                 <span className="text-sm font-bold text-green-600 bg-green-500/10 px-2 py-0.5 rounded">+4.20%</span>
               </div>
               {/* Trade 2 */}
               <div className="flex justify-between items-center bg-muted/20 p-2.5 rounded-md border border-border/50 shadow-sm">
                 <div className="flex items-center gap-3">
                   <div className="w-8 h-8 rounded shrink-0 bg-red-500/10 flex items-center justify-center text-red-600 font-bold text-[10px] tracking-wider">SHORT</div>
                   <div className="flex flex-col">
                     <span className="text-sm font-bold text-foreground">ETH/USDT</span>
                     <span className="text-[11px] text-muted-foreground font-medium">Fermé il y a 5h</span>
                   </div>
                 </div>
                 <span className="text-sm font-bold text-green-600 bg-green-500/10 px-2 py-0.5 rounded">+1.85%</span>
               </div>
               {/* Trade 3 */}
               <div className="flex justify-between items-center bg-muted/20 p-2.5 rounded-md border border-border/50 shadow-sm">
                 <div className="flex items-center gap-3">
                   <div className="w-8 h-8 rounded shrink-0 bg-green-500/10 flex items-center justify-center text-green-600 font-bold text-[10px] tracking-wider">LONG</div>
                   <div className="flex flex-col">
                     <span className="text-sm font-bold text-foreground">SOL/USDT</span>
                     <span className="text-[11px] text-muted-foreground font-medium">Fermé hier</span>
                   </div>
                 </div>
                 <span className="text-sm font-bold text-red-500 bg-red-500/10 px-2 py-0.5 rounded">-0.50%</span>
               </div>
            </div>
          )}
        </div>

        {/* 3. Résultats et Performance Globales */}
        <div className="border-b border-border/60">
          <button 
            onClick={() => toggleRow("performances")}
            className="w-full flex justify-between items-center py-4 cursor-pointer group hover:bg-muted/10 transition-colors"
          >
            <span className="text-[16px] font-semibold text-foreground/90 group-hover:text-blue-600 transition-colors">Mes Résultats & Performances</span>
            {expandedRow === "performances" ? <ChevronUp className="w-5 h-5 text-muted-foreground stroke-[1.5]" /> : <ChevronDown className="w-5 h-5 text-muted-foreground stroke-[1.5]" />}
          </button>
          
          {expandedRow === "performances" && (
             <div className="pb-4 pt-1 flex flex-col gap-1.5 animate-in fade-in slide-in-from-top-1 duration-200">
               <div className="flex justify-between items-center px-3 py-2 rounded-md bg-muted/20 border border-border/30">
                 <span className="text-[13px] text-muted-foreground font-medium">Win Rate IA (30J)</span>
                 <span className="text-[15px] font-bold text-blue-600">82.4%</span>
               </div>
               <div className="flex justify-between items-center px-3 py-2 rounded-md bg-muted/20 border border-border/30">
                 <span className="text-[13px] text-muted-foreground font-medium">Profit Total Généré</span>
                 <span className="text-[15px] font-bold text-green-600">+$12,450.00</span>
               </div>
               <div className="flex justify-between items-center px-3 py-2 rounded-md bg-muted/20 border border-border/30">
                 <span className="text-[13px] text-muted-foreground font-medium">Résultat Cumulé (ROI)</span>
                 <span className="text-[15px] font-bold text-green-600">+145%</span>
               </div>
               <div className="flex justify-between items-center px-3 py-2 rounded-md bg-muted/20 border border-border/30">
                 <span className="text-[13px] text-muted-foreground font-medium">Drawdown Max IA</span>
                 <span className="text-[15px] font-bold text-red-500">-2.1%</span>
               </div>
            </div>
          )}
        </div>

        {/* 4. Signaux en cours d'analyse */}
        <div className="border-b border-border/60">
          <button 
            onClick={() => toggleRow("signaux")}
            className="w-full flex justify-between items-center py-4 cursor-pointer group hover:bg-muted/10 transition-colors"
          >
            <span className="text-[16px] font-semibold text-foreground/90 group-hover:text-blue-600 transition-colors">Signaux & Analyses en direct</span>
            {expandedRow === "signaux" ? <ChevronUp className="w-5 h-5 text-muted-foreground stroke-[1.5]" /> : <ChevronDown className="w-5 h-5 text-muted-foreground stroke-[1.5]" />}
          </button>
          
          {expandedRow === "signaux" && (
            <div className="pb-4 pt-1 animate-in fade-in slide-in-from-top-1 duration-200 px-2 space-y-4">
               
               <div className="flex flex-col">
                  <div className="flex justify-between items-center mb-1.5">
                     <span className="text-[13px] font-semibold text-foreground flex items-center gap-1.5">
                       <Clock className="w-4 h-4 text-blue-500"/> AAPL (Attente de cassure)
                     </span>
                     <span className="text-[12px] font-bold text-muted-foreground bg-muted pt-0.5 pb-0.5 px-2 rounded">Confiance 92%</span>
                  </div>
                  <div className="w-full bg-border rounded-full h-1.5"><div className="bg-blue-500 h-1.5 rounded-full" style={{ width: "92%" }}></div></div>
               </div>

               <div className="flex flex-col">
                  <div className="flex justify-between items-center mb-1.5">
                     <span className="text-[13px] font-semibold text-foreground flex items-center gap-1.5">
                       <Clock className="w-4 h-4 text-orange-400"/> GOLD (Analyse du Volume)
                     </span>
                     <span className="text-[12px] font-bold text-muted-foreground bg-muted pt-0.5 pb-0.5 px-2 rounded">Confiance 78%</span>
                  </div>
                  <div className="w-full bg-border rounded-full h-1.5"><div className="bg-orange-400 h-1.5 rounded-full" style={{ width: "78%" }}></div></div>
               </div>

            </div>
          )}
        </div>

      </div>
    </div>
  );
};

export default StatsOverview;
