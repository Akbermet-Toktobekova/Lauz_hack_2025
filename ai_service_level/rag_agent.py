"""
RAG (Retrieval-Augmented Generation) Agent for Compliance Q&A
Enables conversational queries about customer profiles and fraud cases
"""

from .ucp import UCPBuilder, UnifiedCustomerProfile
from .llama_client import LlamaClient
from typing import Dict, List, Optional
import json


class RAGAgent:
    """
    Conversational Compliance & Q&A Agent using RAG.
    Answers questions about customer profiles, transactions, and fraud cases.
    """
    
    def __init__(self, data_dir: str = "data", llama_url: str = "http://127.0.0.1:8080"):
        """
        Initialize RAG Agent.
        
        Args:
            data_dir: Path to data directory
            llama_url: URL of llama-server
        """
        self.ucp_builder = UCPBuilder(data_dir=data_dir)
        self.llama_client = LlamaClient(base_url=llama_url)
        
        self.system_message = (
            "You are a compliance officer working for a Swiss bank. "
            "You answer questions about customer profiles, transactions, and fraud cases "
            "based on the Unified Customer Profile (UCP) data provided. "
            "Always cite specific data points from the UCP in your answers. "
            "Be precise, factual, and compliant with FINMA regulations. "
            "If information is not available in the UCP, clearly state that."
        )
    
    def answer_query(self, partner_id: str, question: str) -> Dict:
        """
        Answer a compliance question about a customer.
        
        Args:
            partner_id: The partner ID to query about
            question: The question to answer
            
        Returns:
            Dictionary with:
            - answer: The answer to the question
            - citations: Data points cited
            - ucp_snapshot: Relevant UCP data used
        """
        # Step 1: Build UCP for the partner
        ucp = self.ucp_builder.build_ucp(partner_id)
        
        # Step 2: Create RAG prompt with UCP context
        prompt = self._create_rag_prompt(ucp, question)
        
        # Step 3: Generate answer using LLM
        response = self.llama_client.generate(
            prompt=prompt,
            system_message=self.system_message,
            max_tokens=1024,
            temperature=0.3  # Lower temperature for factual accuracy
        )
        
        # Step 4: Extract citations and format response
        answer = response["content"]
        citations = self._extract_citations(ucp, question)
        
        return {
            "partner_id": partner_id,
            "question": question,
            "answer": answer,
            "citations": citations,
            "ucp_snapshot": self._get_relevant_ucp_snapshot(ucp, question),
            "source": "Unified Customer Profile (UCP)"
        }
    
    def _create_rag_prompt(self, ucp: UnifiedCustomerProfile, question: str) -> str:
        """Create RAG prompt with UCP context."""
        return f"""Based on the following Unified Customer Profile, answer the question.

UNIFIED CUSTOMER PROFILE:
{ucp.to_text()}

QUESTION: {question}

Provide a clear, factual answer based on the UCP data. Include specific numbers, dates, and details from the profile.
If the information is not available in the UCP, state that clearly.

ANSWER:"""
    
    def _extract_citations(self, ucp: UnifiedCustomerProfile, question: str) -> List[Dict]:
        """Extract relevant citations from UCP based on the question."""
        citations = []
        ucp_dict = ucp.to_dict()
        
        # Simple keyword-based citation extraction
        question_lower = question.lower()
        
        if "spending" in question_lower or "transaction" in question_lower:
            financial = ucp.transaction_aggregates
            citations.append({
                "type": "financial_aggregate",
                "data": {
                    "total_spending_30d": financial.get("total_spending_30d", 0),
                    "total_spending_90d": financial.get("total_spending_90d", 0),
                    "tx_count_30d": financial.get("tx_count_30d", 0)
                }
            })
        
        if "name" in question_lower or "identity" in question_lower:
            identity = ucp.profile_data.get("identity", {})
            citations.append({
                "type": "identity",
                "data": {
                    "name": identity.get("name", ""),
                    "canonical_id": identity.get("canonical_id", "")
                }
            })
        
        if "risk" in question_lower or "fraud" in question_lower:
            risk = ucp.risk_metadata
            if risk:
                citations.append({
                    "type": "risk_assessment",
                    "data": {
                        "risk_score": risk.get("risk_score", "N/A"),
                        "explanation": risk.get("explanation", "")
                    }
                })
        
        return citations
    
    def _get_relevant_ucp_snapshot(self, ucp: UnifiedCustomerProfile, question: str) -> Dict:
        """Get relevant subset of UCP based on question."""
        question_lower = question.lower()
        ucp_dict = ucp.to_dict()
        
        # Return relevant sections
        snapshot = {
            "canonical_id": ucp_dict["canonical_id"]
        }
        
        if "spending" in question_lower or "transaction" in question_lower or "financial" in question_lower:
            snapshot["financial_aggregates"] = ucp_dict["financial_aggregates"]
            snapshot["recent_transactions"] = ucp_dict["recent_transactions"][:3]
        
        if "identity" in question_lower or "name" in question_lower or "profile" in question_lower:
            snapshot["identity"] = ucp_dict["identity"]
            snapshot["static_profile"] = ucp_dict["static_profile"]
        
        if "risk" in question_lower or "fraud" in question_lower or "alert" in question_lower:
            snapshot["risk_metadata"] = ucp_dict["risk_metadata"]
        
        return snapshot

