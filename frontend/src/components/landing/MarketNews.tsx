import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight, PlusCircle, Rocket, ChevronUp, ChevronDown } from "lucide-react";
import { LineChart, Line, YAxis, ResponsiveContainer } from "recharts";

// Helper for generating fake sparkline data
const generateSparkline = (isPositive: boolean) => {
  let val = 100;
  return Array.from({ length: 20 }, () => {
    val += (Math.random() - (isPositive ? 0.3 : 0.7)) * 5;
    return { value: val };
  });
};

const marketData = [
  { name: "Bitcoin", ticker: "BTC", price: "60 780,99", change: "+0,82%", isPositive: true, data: generateSparkline(true) },
  { name: "Ethereum", ticker: "ETH", price: "1 857,19", change: "+1,42%", isPositive: true, data: generateSparkline(true) },
  { name: "BNB", ticker: "BNB", price: "554,27", change: "+0,62%", isPositive: true, data: generateSparkline(true) },
  { name: "Cardano", ticker: "ADA", price: "0,23", change: "+0,72%", isPositive: true, data: generateSparkline(true) },
  { name: "XRP", ticker: "XRP", price: "1,24", change: "+0,64%", isPositive: true, data: generateSparkline(true) },
];

const breakingNews = [
  {
    id: 1,
    source: "Bloomberg Politics • il y a 2 h",
    title: "Politique US : La Maison Blanche annonce un plan de soutien massif face à la volatilité des marchés",
    image: "https://images.unsplash.com/photo-1580128660010-fd027e1e587a?q=80&w=1200&auto=format&fit=crop",
    priceTag: "DOW +1,24%",
    isPositive: true
  },
  {
    id: 2,
    source: "Vibe Trade • il y a 5 h",
    title: "Le Bitcoin rebondit fortement face aux annonces d'adoption institutionnelle",
    image: "https://images.unsplash.com/photo-1518546305927-5a555bb7020d?q=80&w=1200&auto=format&fit=crop",
    priceTag: "BTC +2,41%",
    isPositive: true
  },
  {
    id: 3,
    source: "Capital France • il y a 1 j",
    title: "CAC 40 : la Bourse « surveille les développements visant à apaiser l'Iran ! »",
    image: "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=1200&auto=format&fit=crop",
    priceTag: "PX1 -1,82%",
    isPositive: false
  },
  {
    id: 4,
    source: "BFM Business • il y a 7 h",
    title: "La guerre en Iran propulse l'Algérie et la Libye comme des alternatives possibles...",
    image: "/iran-news.png",
    priceTag: "OIL +4,15%",
    isPositive: true
  }
];

const MarketNews = () => {
  const [currentSlide, setCurrentSlide] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % breakingNews.length);
    }, 6000);
    return () => clearInterval(timer);
  }, []);

  const nextSlide = () => setCurrentSlide((sub) => (sub + 1) % breakingNews.length);
  const prevSlide = () => setCurrentSlide((sub) => (sub - 1 + breakingNews.length) % breakingNews.length);

  return (
    <section className="bg-background py-16 border-y border-border">
      <div className="max-w-[1400px] mx-auto px-6">
        
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 bg-card rounded-md border border-border overflow-hidden shadow-sm">
          
          {/* Gauche: Liste "Populaire" calquée sur la nouvelle capture d'écran */}
          <div className="lg:col-span-4 flex flex-col bg-background border-r border-border min-h-[500px]">
            {/* Header Populaire */}
            <div className="px-5 py-4 border-b border-border flex justify-between items-center bg-muted/10">
              <div className="flex items-center gap-3">
                <Rocket className="w-[18px] h-[18px] text-muted-foreground" />
                <span className="text-[17px] font-medium text-foreground">Populaire</span>
              </div>
              <ChevronUp className="w-5 h-5 text-muted-foreground" />
            </div>

            {/* Liste des prix */}
            <div className="divide-y divide-border/60 overflow-y-auto custom-scrollbar flex-1">
              {marketData.map((coin) => (
                <div 
                  key={coin.ticker} 
                  className="px-5 py-[18px] flex items-center justify-between cursor-pointer hover:bg-muted/30 transition-colors"
                >
                  {/* Titre et Ticker */}
                  <div className="flex flex-col w-[100px]">
                    <span className="text-[16px] text-foreground/90">{coin.name}</span>
                    <span className="text-[13.5px] text-muted-foreground/70 mt-0.5">{coin.ticker}</span>
                  </div>

                  {/* Sparkline Chart */}
                  <div className="w-[110px] h-[36px] -ml-2 relative">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={coin.data}>
                        <YAxis domain={['auto', 'auto']} hide />
                        <Line 
                          type="monotone" 
                          dataKey="value" 
                          stroke={coin.isPositive ? "#16a34a" : "#dc2626"} 
                          strokeWidth={1.5} 
                          dot={false}
                          isAnimationActive={false}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Prix et Variation + icone */}
                  <div className="flex items-center gap-4 text-right">
                    <div className="flex flex-col">
                      <span className="text-[16px] font-normal text-foreground">{coin.price}</span>
                      <span className={`text-[14.5px] font-medium mt-0.5 ${coin.isPositive ? 'text-green-600' : 'text-red-600'}`}>
                        {coin.change}
                      </span>
                    </div>
                    <button className="text-muted-foreground/40 hover:text-muted-foreground transition-colors">
                      <PlusCircle className="w-[22px] h-[22px] stroke-[1.2]" />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Footer "Voir plus" */}
            <div className="px-5 py-3 border-t border-border flex justify-center items-center cursor-pointer hover:bg-muted/30 transition-colors group">
              <span className="text-blue-600 text-[15px] font-medium flex items-center gap-1 group-hover:underline">
                Voir plus <ChevronDown className="w-4 h-4" />
              </span>
            </div>
          </div>

          {/* Droite: Panneau News Image */}
          <div className="lg:col-span-8 flex flex-col relative h-[500px] lg:h-auto bg-muted group overflow-hidden">
            <AnimatePresence mode="popLayout" initial={false}>
              <motion.div
                key={currentSlide}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.8, ease: "easeInOut" }}
                className="absolute inset-0"
              >
                {/* Image de fond couvrante */}
                <div 
                  className="absolute inset-0 bg-cover bg-center transition-transform duration-[15000ms] ease-out hover:scale-105"
                  style={{ backgroundImage: `url(${breakingNews[currentSlide].image})` }}
                />
                
                {/* Overlay inspiré de la capture "Euro numérique" (dégradé très léger en bas pour le texte) */}
                <div className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-white/95 via-white/80 to-transparent dark:from-black/95 dark:via-black/80" />

                {/* Contenu textuel adaptatif - texte foncé sur image claire */}
                <div className="absolute inset-x-0 bottom-0 px-8 py-8 flex flex-col">
                  {/* Titre de l'article */}
                  <h3 className="text-[26px] md:text-[32px] font-medium text-black dark:text-white mb-4 leading-[1.2] max-w-2xl drop-shadow-sm">
                    {breakingNews[currentSlide].title}
                  </h3>
                  
                  {/* Tag Source */}
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-[18px] h-[18px] rounded bg-black dark:bg-white text-white dark:text-black flex items-center justify-center font-bold text-[10px]">
                      CT
                    </div>
                    <span className="text-gray-800 dark:text-gray-200 text-[14px]">
                      {breakingNews[currentSlide].source} <span className="text-xl leading-none">...</span>
                    </span>
                  </div>

                  {/* Tag de prix */}
                  {breakingNews[currentSlide].priceTag && (
                    <div className="flex items-center mt-2">
                       <span className="text-gray-900 dark:text-white text-[14px] font-bold">
                          {breakingNews[currentSlide].priceTag.split(' ')[0]}
                       </span>
                       <span className={`ml-2 text-[14px] font-bold ${
                          breakingNews[currentSlide].isPositive ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                       }`}>
                          {breakingNews[currentSlide].priceTag.split(' ')[1]}
                       </span>
                    </div>
                  )}
                </div>
              </motion.div>
            </AnimatePresence>

            {/* Boutons de navigation (visibles latéralement comme sur l'image 1) */}
            <div className="absolute inset-y-0 left-0 flex items-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              <button 
                onClick={prevSlide}
                className="h-20 w-8 bg-black/20 text-white flex items-center justify-center hover:bg-black/40 transition-colors backdrop-blur-[2px]"
              >
                <ChevronLeft className="w-8 h-8" />
              </button>
            </div>
            <div className="absolute inset-y-0 right-0 flex items-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              <button 
                onClick={nextSlide}
                className="h-20 w-8 bg-black/20 text-white flex items-center justify-center hover:bg-black/40 transition-colors backdrop-blur-[2px]"
              >
                <ChevronRight className="w-8 h-8" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default MarketNews;
