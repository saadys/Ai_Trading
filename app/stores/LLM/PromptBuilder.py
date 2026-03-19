import logging

logger = logging.getLogger(__name__)

class PromptBuilder:
    def __init__(self):
        pass

    def Construire_Prompt(self, context: dict) -> str:
        market = context.get("market") or {}
        technical = context.get("technical") or {}
        sentiment = context.get("sentiment") or {}
        ml_prediction = context.get("ml_prediction") or {}
        account = context.get("account") or {}

        is_open = not market.get("is_closed", False)
        logger.info(f"[PromptBuilder] Building prompt for {context.get('symbol')} at {context.get('timestamp')}")

        prompt = f"""
            ROLE: Elite Quantitative Trading AI (Specializing in BTC/USDT)
            OBJECTIVE: Analyze the provided multi-dimensional market context to execute a strictly rational, mathematically sound decision (BUY, SELL, HOLD). Prioritize capital preservation and structural confluence. Emotion is completely disabled.

            --- MARKET CONTEXT ---
            Timestamp: {context.get("timestamp", "N/A")} | Asset: {context.get("symbol", "N/A")} | Market Open: {is_open}

            [1] PRICE ACTION & LIQUIDITY
            Open: {market.get("open", "N/A")}   | High: {market.get("high", "N/A")}
            Low: {market.get("low", "N/A")}     | Close: {market.get("close", "N/A")}
            Volume: {market.get("volume", "N/A")}

            [2] technical  ARCHITECTURE
            - Momentum (MACD): Line={technical.get("macd_line", "N/A")}, Signal={technical.get("macd_signal", "N/A")}, Hist={technical.get("macd_hist", "N/A")}
            - Relative Strength (RSI-14): {technical.get("rsi_14", "N/A")}
            - Volatility (ATR-14): {technical.get("atr_14", "N/A")}
            - Dynamic S/R (EMA): EMA20={technical.get("ema_20", "N/A")}, EMA50={technical.get("ema_50", "N/A")}, EMA200={technical.get("ema_200", "N/A")}

            [3] ALTERNATIVE ALPHA
            - Market Sentiment: {sentiment.get("sentiment_label", "N/A")} (Score: {sentiment.get("sentiment_score", "N/A")}) via {sentiment.get("source", "N/A")}
            - ML Prediction: {ml_prediction.get("prediction", "N/A")} (Confidence: {ml_prediction.get("probability", "N/A")})

            [4] PORTFOLIO STATE
            - Balance: ${account.get("balance", "N/A")} | Open Positions: {account.get("open_positions", "N/A")}

            --- EXECUTION LOGIC & CONSTRAINTS ---
            1. CONFLUENCE REQUIRED: A "BUY" requires alignment between technical momentum, ML prediction, and sentiment. Do not buy into major resistance without volume support.
            2. RISK AVERSION: A "SELL" triggers on structural breakdown or bearish ML divergence.
            3. DEFAULT TO SAFETY: "HOLD" if data conflicts, edge is absent, or ATR indicates exceptionally hostile noise.

            --- OUTPUT INSTRUCTIONS ---
            You are communicating directly with an automated parser. You must output ONLY a valid, raw JSON object. 
            Do NOT wrap the output in markdown formatting blocks (e.g., no ```json). Do NOT add any conversational text.

            REQUIRED JSON SCHEMA:
            {{
            "action": "BUY" | "SELL" | "HOLD",
            "confidence_score": <float 0.0-1.0>,
            "risk_assessment": "LOW" | "MEDIUM" | "HIGH" | "EXTREME",
            "reasoning": "<Concise 2-sentence technical justification highlighting specific indicators or confluences. e.g., 'Bullish MACD crossover aligned with 85% ML prediction and price holding above EMA-50.'>"
            }}
            """
        logger.info(f"[PromptBuilder] Prompt built successfully")
        return prompt.strip()