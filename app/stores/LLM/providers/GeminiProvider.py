from app.stores.LLM.LLMInterface import LLMInterface
from app.stores.LLM.LLMEnum import LLMEnum
from app.core.logger import Logger, logger
from google import genai
import json

class GeminiProvider(LLMInterface):
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = genai.Client(api_key=self.api_key)
    
    async def aggregate_responses(self, prompt_text:str):
        try :
            if not self.client:
                logger.error("GeminiProvider Client is None")
                return None

            response = await self.client.aio.models.generate_content(
                model = LLMEnum.GEMINI.value,
                contents=prompt_text,
            )

            return self.Text_To_JSON(response.text)
        except Exception as e:
            logger.error(f"GeminiProvider Error: {e}")
            return None

    def Text_To_JSON(self, response: str):

        if not response:
            logger.error("GeminiProvider Response is None")
            return None

        try:
            clean = response.strip()
            if clean.startswith("```json"):
                clean = clean[7:]
            elif clean.startswith("```"):
                clean = clean[3:]
            if clean.endswith("```"):
                clean = clean[:-3]
        
            return json.loads(clean.strip())

        except json.JSONDecodeError as e:
            print(f"GeminiProvider JSON parse error: {e}")
            print(f"GeminiProvider Raw response: {response}")
            return {
                "action": "HOLD",
                "confidence_score": 0.0,
                "risk_assessment": "EXTREME",
                "reasoning": f"Parse Error: {str(e)}"
            }