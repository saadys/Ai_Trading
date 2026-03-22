import { useState } from "react";
import { BrainCircuit, Loader2 } from "lucide-react";
import axios from "axios";

const PredictAction = () => {
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState<{ action: string; confidence: number; risk: string } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handlePredict = async () => {
    setLoading(true);
    setPrediction(null);
    setError(null);
    
    try {
      // Nous simulons les 21 features requises par le backend avec des valeurs temporelles ou aléatoires
      // pour que le backend accepte la requête. Dans un usage réel, ces données viendraient du graphique/marché.
      const mockFeatures = Array.from({ length: 21 }, () => Math.random());
      
      const response = await axios.post("http://localhost:8000/api/v1/lstm/predict", {
        features: mockFeatures
      });

      if (response.data && response.data.SUCCESS) {
        const predData = response.data.prediction;
        setPrediction({
          action: predData.signal || predData.prediction || "HOLD",
          confidence: Math.round(predData.probability ? predData.probability * 100 : 80),
          risk: "MEDIUM" // À ajuster si le backend finit par renvoyer un niveau de risque
        });
      } else {
        setError("La prédiction a échoué.");
      }
    } catch (err) {
      console.error(err);
      setError("Erreur de connexion à l'API de prédiction. Vérifiez que le backend est lancé.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-card text-card-foreground rounded-xl border border-border p-6 shadow-sm">
      <h2 className="text-xl font-semibold mb-4">AI Assistant</h2>
      <p className="text-sm text-muted-foreground mb-4">
        Demandez à l'IA d'analyser les conditions actuelles du marché et de fournir une recommandation de trading en temps réel.
      </p>

      {error && (
        <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-sm text-red-500">
          {error}
        </div>
      )}
      
      <button
        onClick={handlePredict}
        disabled={loading}
        className="w-full flex items-center justify-center gap-2 bg-primary text-primary-foreground hover:bg-primary/90 py-3 rounded-lg font-medium transition-colors disabled:opacity-70 disabled:cursor-not-allowed"
      >
        {loading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Analyzing Market...
          </>
        ) : (
          <>
            <BrainCircuit className="w-5 h-5" />
            Lancer la Prédiction
          </>
        )}
      </button>

      {prediction && (
        <div className="mt-6 p-4 bg-muted/50 rounded-lg border border-border/50 animate-in fade-in slide-in-from-bottom-2">
          <h3 className="text-sm font-semibold text-muted-foreground mb-3 text-center uppercase tracking-wider">Résultat du Modèle</h3>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-white dark:bg-card rounded-md p-3 text-center shadow-sm border border-border/60">
              <span className="block text-[11px] text-muted-foreground font-bold uppercase tracking-wider mb-1">Action</span>
              <span className={`font-black text-xl ${
                prediction.action === 'BUY' ? 'text-green-600' : 
                prediction.action === 'SELL' ? 'text-red-500' : 'text-gray-600'
              }`}>
                {prediction.action}
              </span>
            </div>
            <div className="bg-white dark:bg-card rounded-md p-3 text-center shadow-sm border border-border/60">
              <span className="block text-[11px] text-muted-foreground font-bold uppercase tracking-wider mb-1">Confiance</span>
              <span className="font-black text-xl text-blue-600">{prediction.confidence}%</span>
            </div>
            <div className="col-span-2 bg-white dark:bg-card rounded-md p-3 text-center shadow-sm border border-border/60">
              <span className="block text-[11px] text-muted-foreground font-bold uppercase tracking-wider mb-1">Risk Level</span>
              <span className={`font-black text-xl flex items-center justify-center ${
                prediction.risk === 'LOW' ? 'text-green-600' : 
                prediction.risk === 'MEDIUM' ? 'text-orange-500' : 'text-red-500'
              }`}>{prediction.risk}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PredictAction;