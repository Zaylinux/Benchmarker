"""
Querying module for interacting with different model APIs.

This module provides client classes for querying various model endpoints,
including Ollama and OpenAI-compatible APIs.
"""

from evaluators.querying.ollama_client import OllamaClient
from evaluators.querying.openai_client import OpenAIClient

__all__ = ["OllamaClient", "OpenAIClient"]
