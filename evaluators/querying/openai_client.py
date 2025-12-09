"""
OpenAI-compatible API client for querying models.

This module provides a client class for interacting with OpenAI-compatible
API endpoints, supporting chat completions with standard parameters.
"""

from typing import Dict, List, Optional
import requests


class OpenAIClient:
    """
    Client for querying models through OpenAI-compatible APIs.
    
    This client handles communication with any OpenAI-compatible API endpoint,
    supporting standard chat completion requests with configurable parameters.
    
    Attributes:
        base_url: Base URL for the API endpoint (e.g., http://localhost:8080/v1)
        timeout: Request timeout in seconds
        session: Requests session for connection pooling
    """
    
    def __init__(self, base_url: str, timeout: int = 60):
        """
        Initialize the OpenAI-compatible client.
        
        Args:
            base_url: Base URL for the API endpoint (e.g., http://localhost:8080/v1)
            timeout: Request timeout in seconds (default: 60)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
    
    def query(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 256
    ) -> str:
        """
        Query the model with a list of messages.
        
        Args:
            model: Name of the model to query
            messages: List of message dictionaries with 'role' and 'content' keys
            temperature: Sampling temperature (default: 0.0 for deterministic output)
            max_tokens: Maximum number of tokens to generate (default: 256)
        
        Returns:
            The model's response text, or an error message if the request fails
        
        Example:
            >>> client = OpenAIClient("http://localhost:8080/v1")
            >>> messages = [
            ...     {"role": "system", "content": "You are a helpful assistant."},
            ...     {"role": "user", "content": "What is 2+2?"}
            ... ]
            >>> response = client.query("gpt-3.5-turbo", messages)
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            resp = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=self.timeout
            )
            resp.raise_for_status()
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
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
        Build a message list for the OpenAI-compatible API.
        
        Args:
            user_content: The user's input/question
            system_prompt: System prompt to set model behavior
            context: Optional context to prepend to the user content (for RAG tasks)
        
        Returns:
            List of message dictionaries ready for the API
        
        Example:
            >>> client = OpenAIClient("http://localhost:8080/v1")
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
    
    def close(self) -> None:
        """
        Close the underlying session.
        
        This should be called when the client is no longer needed to properly
        clean up connection resources.
        """
        self.session.close()
