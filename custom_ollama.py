from langchain_ollama import OllamaLLM
import requests
import json

class OllamaLLMWithMetadata(OllamaLLM):
    def invoke(self, prompt):
        """Override invoke method to include metadata"""
        url = "http://localhost:11434/api/generate"
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False  # Ensure we get full metadata in one response
        }
        
        response = requests.post(url, json=data)
        response_json = response.json()  # Parse JSON
        
        return {
            "model": response_json.get("model"),
            "response": response_json.get("response"),
            "created_at": response_json.get("created_at"),
            "total_duration": response_json.get("total_duration"),
            "prompt_tokens": response_json.get("prompt_eval_count"),
            "generated_tokens": response_json.get("eval_count")
        }
