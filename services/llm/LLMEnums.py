from enum import Enum

class LLMEnums(Enum):
  COHERE = "COHERE"
  GEMINI = "GEMINI"

class CohereEnums(Enum):
  SYSTEM  = "system"
  USER = "user"
  ASSISTANT ="assistant"

class GeminiEnums(Enum):
  SYSTEM  = "system"
  USER = "user"
  ASSISTANT ="model"
