"""
Minimal LLaMA Client - Direct HTTP calls to llama-server API
Simple wrapper for llama-server OpenAI-compatible API.
"""

import requests
from typing import Optional, Dict


class LlamaClient:
    """
    Minimal client for llama-server API.
    Makes direct HTTP calls to local llama-server.
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:8080"):
        """
        Initialize LLaMA client.
        
        Args:
            base_url: Base URL of llama-server (default: http://127.0.0.1:8080)
        """
        self.base_url = base_url.rstrip('/')
        self.chat_endpoint = f"{self.base_url}/v1/chat/completions"
    
    def generate(self, prompt: str, system_message: Optional[str] = None, 
                 max_tokens: int = 512, temperature: float = 0.7) -> Dict:
        """
        Generate text using llama-server API.
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Dictionary with 'content' and 'usage' keys
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": "gpt-oss-20b",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(
                self.chat_endpoint,
                json=payload,
                timeout=300
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "content": data["choices"][0]["message"]["content"],
                "usage": data.get("usage", {})
            }
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error calling llama-server: {str(e)}")


# Example usage
if __name__ == "__main__":
    client = LlamaClient()
    
    result = client.generate(
        prompt="Hello, how are you?",
        system_message="You are a helpful assistant."
    )
    print(result["content"])

