# llm.py
"""
LLM configuration for CrewAI agents.
CrewAI uses litellm under the hood – we just export the model string.
The GEMINI_API_KEY env var is picked up automatically by litellm.
"""
from config import GEMINI_LLM_MODEL

LLM_MODEL = GEMINI_LLM_MODEL



