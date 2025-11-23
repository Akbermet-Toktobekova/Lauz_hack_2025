"""
AI Service Level Package
Provides fraud detection agents using LLaMA 20B model with multimodal support.
"""

from .profile_agent import ProfileAgent
from .fraud_agent import FraudAgent
from .llama_client import LlamaClient
from .ucp import UnifiedCustomerProfile, UCPBuilder
from .enhanced_fraud_agent import EnhancedFraudAgent
from .rag_agent import RAGAgent
from .ocr_processor import OCRProcessor

__all__ = [
    "ProfileAgent", 
    "FraudAgent", 
    "LlamaClient",
    "UnifiedCustomerProfile",
    "UCPBuilder",
    "EnhancedFraudAgent",
    "RAGAgent",
    "OCRProcessor"
]
