from enum import Enum

class LLMEnum(Enum):
    OPENROUTER = "OPENROUTER"
    DEEPSEEK = "DEEPSEEK"
    OPENAI = "OPENAI"
    QWEN = "QWEN"
    GEMINI = "gemini-3.1-pro-preview"


class DeepSeekEnum(Enum):
    SYSYEM = "system"
    USER = "user"
    
