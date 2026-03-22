from app.stores.LLM.LLMInterface import LLMInterface
from app.stores.LLM.LLMEnum import LLMEnum, DeepSeekEnum
from app.core.logger import Logger, logger
from app.models.pydantic.LLMResponseValidator import LLMResponseValidator

from openai import AsyncOpenAI
import json
from pydantic import ValidationError

class DeepSeekProvider(LLMInterface):

    def __init__(self, api_key: str, base_url:str):
        self.api_key = api_key
        self.base_url = base_url if base_url else "https://api.deepseek.com/v1"
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
    
    async def aggregate_responses(self, prompt_text:str):
        try :
            if not self.client:
                logger.error("DeepSeekProvider Client is None")
                return None
            
            response = await self.client.chat.completions.create(
                model = LLMEnum.DEEPSEEK.value,
                messages=[
                    {"role": DeepSeekEnum.USER.value, "content": prompt_text},
                ],
            )

            return self.Text_To_JSON(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"DeepSeekProvider Error: {e}")
            return None
    
    def Text_To_JSON(self,response:str):
        if not response:
            logger.error("DeepSeekProvider Response is None")
            return None
        try:
            # 5. NETTOYAGE DU MARKDOWN (Comme pour Gemini)
            clean = response.strip()
            if clean.startswith("```json"):
                clean = clean[7:]
            elif clean.startswith("```"):
                clean = clean[3:]
            if clean.endswith("```"):
                clean = clean[:-3]
        
            parsed_json = json.loads(clean.strip())
            
            validated_response = LLMResponseValidator(**parsed_json)
            return validated_response.model_dump()
        except json.JSONDecodeError as e:
            logger.error(f"DeepSeekProvider JSON parse error: {e}")
            logger.error(f"DeepSeekProvider Raw response: {response}")
            
            return {
                "action": "HOLD",
                "confidence_score": 0.0,
                "risk_assessment": "EXTREME",
                "reasoning": f"Parse Error: {str(e)}"
            }
        except ValidationError as e:
            logger.error(f"DeepSeekProvider Validation error: {e}")
            logger.error(f"DeepSeekProvider Raw response: {response}")
            
            return {
                "action": "HOLD",
                "confidence_score": 0.0,
                "risk_assessment": "EXTREME",
                "reasoning": f"Validation Error: {str(e)}"
            }
