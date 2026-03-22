from app.stores.LLM.LLMInterface import LLMInterface
from app.stores.LLM.LLMEnum import LLMEnum
from app.core.logger import logger
from app.models.pydantic.LLMResponseValidator import LLMResponseValidator

from openai import AsyncOpenAI
import json
from pydantic import ValidationError


class MiniMaxProvider(LLMInterface):

    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

    async def aggregate_responses(self, prompt_text: str):
        try:
            if not self.client:
                logger.error("MiniMaxProvider Client is None")
                return None

            response = await self.client.chat.completions.create(
                model=LLMEnum.MINIMAX_25.value,
                messages=[
                    {"role": "user", "content": prompt_text},
                ],
                extra_body={"reasoning": {"enabled": True}},
            )

            content = response.choices[0].message.content if response and response.choices else None
            return self.Text_To_JSON(content)

        except Exception as e:
            logger.error(f"MiniMaxProvider Error: {e}")
            return None

    def Text_To_JSON(self, response: str):
        if not response:
            logger.error("MiniMaxProvider Response is None")
            return None

        try:
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
            logger.error(f"MiniMaxProvider JSON parse error: {e}")
            logger.error(f"MiniMaxProvider Raw response: {response}")
            return {
                "action": "HOLD",
                "confidence_score": 0.0,
                "risk_assessment": "EXTREME",
                "reasoning": f"Parse Error: {str(e)}"
            }
        except ValidationError as e:
            logger.error(f"MiniMaxProvider Validation error: {e}")
            logger.error(f"MiniMaxProvider Raw response: {response}")
            return {
                "action": "HOLD",
                "confidence_score": 0.0,
                "risk_assessment": "EXTREME",
                "reasoning": f"Validation Error: {str(e)}"
            }