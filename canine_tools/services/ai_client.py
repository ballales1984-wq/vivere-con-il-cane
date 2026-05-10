"""
AI Client Service
Gestisce le chiamate a LLM Groq e fornisce fallback generico.
Fornisce prompt engineering standardizzato per i vari use-case.
"""

import os
import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def get_groq_api_key() -> str:
    """Return the configured Groq API key, supporting GROQ_API_KEY or GROK_API_KEY."""
    return os.environ.get("GROQ_API_KEY", "") or os.environ.get("GROK_API_KEY", "")


class AIClient:
    """Client per interagire con LLM Groq."""
    
    def __init__(self, groq_key: Optional[str] = None):
        self.groq_key = groq_key or get_groq_api_key()
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        
    def _is_valid_key(self, key: str) -> bool:
        """Verifica se la chiave API è valida (non placeholder)."""
        if not key or len(key) < 20:
            return False
        if '<' in key or '>' in key:
            return False
        if 'rimuovi' in key.lower() or 'placeholder' in key.lower():
            return False
        return True
    
    def call_groq(self, messages: list, model: str = "llama-3.3-70b-versatile",
                  temperature: float = 0.7, max_tokens: int = 1000,
                  response_format: Optional[Dict] = None) -> Optional[str]:
        """
        Chiama Groq API.
        
        Args:
            messages: Lista di dict {role, content}
            model: Modello da utilizzare
            temperature: Creatività (0-1)
            max_tokens: Token massimi risposta
            response_format: {"type": "json_object"} per JSON forzato
            
        Returns:
            Testo della risposta o None se errore
        """
        if not self._is_valid_key(self.groq_key):
            logger.warning("[AI] Groq API key non valida o mancante")
            return None
            
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format
            
        try:
            response = requests.post(
                self.groq_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.groq_key}",
                },
                json=payload,
                timeout=30,
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                logger.warning(
                    f"[AI] Groq API error {response.status_code}: {response.text[:200]}"
                )
        except Exception as e:
            logger.warning(f"[AI] Groq exception: {e}")
            
        return None
    
    def generate(self, messages: list, **kwargs) -> str:
        """
        Genera risposta con Groq.
        
        Args:
            messages: Lista messaggi per chat completion
            **kwargs: Parametri aggiuntivi per API (temperature, max_tokens, response_format, etc.)
            
        Returns:
            Testo della risposta (stringa)
        """
        response_text = self.call_groq(messages, **kwargs)
        if response_text:
            return response_text
        
        # Fallback finale - risposta generica
        return self._get_fallback_response(messages)
    
    def _get_fallback_response(self, messages: list) -> str:
        """
        Restituisce risposta generica quando entrambi i provider falliscono.
        Base sulla lingua dell'ultimo messaggio utente.
        """
        user_msg = messages[-1].get("content", "") if messages else ""
        
        # Simple heuristic: se contiene parole inglesi, rispondi in EN
        if any(word in user_msg.lower() for word in ["the", "is", "are", "what", "how"]):
            return """Based on the information provided:

1. **Most likely cause**: Without further details, behavioral problems are often linked to lack of exercise, inconsistent routine, or a need for attention.

2. **Suggested solutions**:
   - Establish a consistent daily routine
   - Increase physical and mental exercise
   - Reward desired behaviors

3. **Tip**: Observe the dog in different situations to identify specific triggers.

4. **When to see a professional**: If the problem persists beyond 2-3 weeks despite training, consult a dog trainer or a veterinary behaviorist."""
        else:
            return """Basandomi sulle informazioni fornite:

1. **Causa più probabile**: Senza ulteriori dettagli, i problemi comportamentali sono spesso legati a mancanza di esercizio, routine inconsistente o bisogno di attenzione.

2. **Soluzioni suggerite**:
   - Stabilisci una routine quotidiana coerente
   - Aumenta l'esercizio fisico e mentale
   - Premia i comportamenti desiderati

3. **Consiglio**: Osserva il cane in diverse situazioni per identificare i trigger specifici.

4. **Quando rivolgerti a un professionista**: Se il problema persiste oltre 2-3 settimane nonostante gli allenamenti, consulta un educatore cinofilo o un Veterinario comportamentalista."""


# Convenience function per usi diretti
def get_ai_client() -> AIClient:
    """Restituisce istanza AIClient configurata."""
    return AIClient()
