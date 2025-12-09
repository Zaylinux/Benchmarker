"""
Ollama API client for querying models through the Ollama service.

This module provides a client class for interacting with Ollama's native API,
supporting chat completions and various model configurations.
"""

from typing import Dict, List, Optional, Any
import requests


class OllamaClient:
    """
    Client for querying models through the Ollama API.
    
    This client handles communication with Ollama's native API endpoint,
    supporting message-based chat completions with optional formatting
    and configuration options.
    
    Attributes:
        host: Base URL for the Ollama service (without trailing slash)
        timeout: Request timeout in seconds
    """
    
    def __init__(self, host: str = "http://localhost:11434", timeout: int = 120):
        """
        Initialize the Ollama client.
        
        Args:
            host: Base URL for the Ollama service (default: http://localhost:11434)
            timeout: Request timeout in seconds (default: 120)
        """
        self.host = host.rstrip('/')
        self.timeout = timeout
    
    def query(
        self,
        model: str,
        messages: List[Dict[str, str]],
        stream: bool = False,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Query the Ollama model with a list of messages.
        
        Args:
            model: Name of the model to query (as shown in `ollama list`)
            messages: List of message dictionaries with 'role' and 'content' keys
            stream: Whether to stream the response (default: False)
            options: Optional dictionary of model-specific options (e.g., format, temperature)
        
        Returns:
            The model's response text, or an error message if the request fails
        
        Example:
            >>> client = OllamaClient()
            >>> messages = [
            ...     {"role": "system", "content": "You are a helpful assistant."},
            ...     {"role": "user", "content": "What is 2+2?"}
            ... ]
            >>> response = client.query("llama2", messages)
        """
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": stream,
        }
        
        if options:
            payload["options"] = options
        
        try:
            resp = requests.post(
                f"{self.host}/api/chat",
                json=payload,
                timeout=self.timeout
            )
            resp.raise_for_status()
            data = resp.json()
            text = data.get("message", {}).get("content", "")
            return text
        except Exception as e:
            return f"ERROR: {e}"
    
    def build_messages(
        self,
        user_content: str,
        system_prompt: str = "You are a helpful on-device assistant. Be concise.",
        context: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Build a message list for the Ollama API.
        
        Args:
            user_content: The user's input/question
            system_prompt: System prompt to set model behavior
            context: Optional context to prepend to the user content (for RAG tasks)
        
        Returns:
            List of message dictionaries ready for the Ollama API
        
        Example:
            >>> client = OllamaClient()
            >>> messages = client.build_messages(
            ...     "What is the capital of France?",
            ...     context="France is a country in Europe."
            ... )
        """
        if context:
            content = (
                f"Use the following context to answer the question.\n\n"
                f"CONTEXT:\n{context}\n\n"
                f"QUESTION:\n{user_content}"
            )
        else:
            content = user_content
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content}
        ]
