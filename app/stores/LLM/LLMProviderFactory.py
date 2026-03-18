from app.core.config import Settings
from app.stores.LLM.LLMInterface import LLMInterface
from app.stores.LLM.LLMEnum import LLMEnum
from app.stores.LLM.providers.GeminiProvider import GeminiProvider
from app.stores.LLM.providers.DeepSeekProvider import DeepSeekProvider
from app.stores.LLM.providers.MiniMaxProvider import MiniMaxProvider


class LLMProviderFactory:
    def __init__(self, config: Settings):
        self.config = config
    
    def create(self, provider: LLMEnum) -> LLMInterface:
        if provider == LLMEnum.DEEPSEEK:
            return DeepSeekProvider(
                api_key=self.config.DEEPSEEK_API_KEY,
                base_url=self.config.DEEPSEEK_BASE_URL,
            )
        elif provider == LLMEnum.GEMINI:
            return GeminiProvider(
                api_key=self.config.GEMINI_API_KEY,
            )
        elif provider == LLMEnum.MINIMAX_25:
            return MiniMaxProvider(
                api_key=self.config.MINIMAX_25_API_KEY,
            )
        elif provider == LLMEnum.QWEN:
            raise NotImplementedError("QwenProvider is not yet implemented.")
        else:
            raise ValueError(f"Unsupported provider: {provider}")
