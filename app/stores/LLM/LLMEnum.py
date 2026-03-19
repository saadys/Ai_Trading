from enum import Enum

class LLMEnum(Enum):
    OPENROUTER = "OPENROUTER"
    DEEPSEEK = "DEEPSEEK"
    OPENAI = "OPENAI"
    QWEN = "QWEN"
    GEMINI = "gemini-2.5-flash"
    MINIMAX_25= "minimax/minimax-m2.5:free"


class DeepSeekEnum(Enum):
    SYSYEM = "system"
    USER = "user"
    
