"""
Test du flux LLM complet :
  ContextAggregator (données mockées) → PromptBuilder → LLMProvider → Décision JSON

Exécution :
    cd Ai_Trading
    python -m app.tests.test_llm_flow
"""

import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.core.config import get_settings
from app.core.logger import logger
from app.stores.LLM.PromptBuilder import PromptBuilder
from app.stores.LLM.LLMEnum import LLMEnum
from app.stores.LLM.LLMProviderFactory import LLMProviderFactory


# ---------------------------------------------------------------------------
# Contexte mocké : simule ce que retourne ContextAggregator.aggregate_functions()
# Permet de tester le flux LLM sans avoir besoin de RabbitMQ ni Binance actifs
# ---------------------------------------------------------------------------
MOCK_CONTEXT = {
    "timestamp": "2026-02-24T02:00:00",
    "symbol": "BTCUSDT",
    "market": {
        "open": 96500.0,
        "high": 97200.0,
        "low": 96100.0,
        "close": 96980.0,
        "volume": 1245.83,
        "is_closed": True,
    },
    "technical": {
        "ema_20": 96750.0,
        "ema_50": 95800.0,
        "ema_200": 92000.0,
        "rsi_14": 58.4,
        "atr_14": 420.5,
        "macd_line": 185.3,
        "macd_signal": 120.1,
        "macd_hist": 65.2,
    },
    "sentiment": {
        "sentiment_label": "Positive",
        "sentiment_score": 0.78,
        "source": "FinBERT",
    },
    "ml_prediction": {
        "direction": "UP",
        "probability": 72.5,
    },
    "account": {
        "balance": 5000.0,
        "open_positions": 0,
    },
}


async def test_prompt_builder():
    """Test 1 : Vérifier que le PromptBuilder génère un prompt non vide."""
    print("\n" + "="*60)
    print("TEST 1 : PromptBuilder")
    print("="*60)
    
    pb = PromptBuilder()
    prompt = pb.Construire_Prompt(MOCK_CONTEXT)
    
    assert prompt and len(prompt) > 100, "FAIL : Le prompt est vide ou trop court !"
    assert "BTCUSDT" in prompt, "FAIL : Le symbol n'est pas dans le prompt !"
    assert "BUY" in prompt, "FAIL : Les actions ne sont pas dans le prompt !"
    
    print("✅ Prompt généré avec succès")
    print(f"   Longueur : {len(prompt)} caractères")
    print(f"   Extrait  : {prompt[:200].strip()}...")
    return prompt


async def test_llm_provider(provider_enum: LLMEnum, prompt: str):
    """Test 2 : Envoyer le prompt au provider LLM et valider la réponse JSON."""
    print("\n" + "="*60)
    print(f"TEST 2 : LLM Provider → {provider_enum.name}")
    print("="*60)
    
    settings = get_settings()
    provider = LLMProviderFactory(settings).create(provider_enum)
    
    print(f"   Envoi du prompt au LLM... (peut prendre quelques secondes)")
    raw_response = await provider.aggregate_responses(prompt)
    
    assert raw_response is not None, "FAIL : La réponse du LLM est None !"
    
    print(f"   Réponse brute reçue (longueur: {len(str(raw_response))})")
    
    # Si aggregate_responses retourne déjà le JSON parsé (GeminiProvider passe par Text_To_JSON)
    if isinstance(raw_response, dict):
        decision = raw_response
    else:
        decision = provider.Text_To_JSON(raw_response)
    
    assert decision is not None, "FAIL : Impossible de parser la réponse en JSON !"
    assert "action" in decision, "FAIL : Clé 'action' manquante dans la décision !"
    assert decision["action"] in ["BUY", "SELL", "HOLD"], f"FAIL : Action invalide → {decision['action']}"
    assert "confidence_score" in decision, "FAIL : Clé 'confidence_score' manquante !"
    assert "risk_assessment" in decision, "FAIL : Clé 'risk_assessment' manquante !"
    assert "reasoning" in decision, "FAIL : Clé 'reasoning' manquante !"
    
    print("✅ Décision reçue et validée :")
    print(f"   Action          : {decision.get('action')}")
    print(f"   Confidence Score: {decision.get('confidence_score')}")
    print(f"   Risk Assessment : {decision.get('risk_assessment')}")
    print(f"   Reasoning       : {decision.get('reasoning')}")
    return decision


async def test_full_flow(provider_enum: LLMEnum = LLMEnum.GEMINI):
    """Test 3 : Flux complet de bout en bout (simulation de AGG_Decision_LLM)."""
    print("\n" + "="*60)
    print("TEST 3 : Flux complet (Mock ContextAggregator → LLM → JSON)")
    print("="*60)
    
    # Etape 1 : PromptBuilder
    pb = PromptBuilder()
    prompt_text = pb.Construire_Prompt(MOCK_CONTEXT)
    
    # Etape 2 : LLM
    settings = get_settings()
    provider = LLMProviderFactory(settings).create(provider_enum)
    decision = await provider.aggregate_responses(prompt_text)
    
    if decision:
        final = provider.Text_To_JSON(decision) if isinstance(decision, str) else decision
        logger.info(
            f"[LLM Decision] Action={final.get('action')} | "
            f"Confidence={final.get('confidence_score')} | "
            f"Risk={final.get('risk_assessment')} | "
            f"Reasoning={final.get('reasoning')}"
        )
        print("✅ Flux complet OK — Décision journalisée via logger")
    else:
        print("❌ FAIL : Aucune décision reçue du provider LLM.")


async def main():
    print("\n🔷 DÉBUT DES TESTS LLM")
    print("  Provider cible : GEMINI (modifiable dans main() ci-dessous)")
    print("  Données        : Contexte mocké (pas de RabbitMQ requis)")
    
    try:
        # Test 1 : Génération du prompt
        prompt = await test_prompt_builder()
        
        # Test 2 : Appel LLM isolé
        # ⬇️ Changer LLMEnum.GEMINI par LLMEnum.DEEPSEEK pour tester DeepSeek
        await test_llm_provider(LLMEnum.DEEPSEEK, prompt)
        
        # Test 3 : Flux complet de bout en bout
        await test_full_flow(LLMEnum.DEEPSEEK)
        
        print("\n" + "="*60)
        print("✅ TOUS LES TESTS ONT RÉUSSI")
        print("="*60)
        
    except AssertionError as ae:
        print(f"\n❌ ASSERTION ÉCHOUÉE : {ae}")
    except Exception as e:
        print(f"\n❌ ERREUR INATTENDUE : {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
