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
            "You are a helpful compliance assistant for a Swiss bank. "
            "Answer questions in a natural, human-friendly way using only the customer data provided. "
            "Write in plain, compelling language without markdown formatting (no **, no bullets, no headers). "
            "Do NOT include any thinking process, reasoning steps, or internal analysis. "
            "Do NOT use any special tokens or formatting. "
            "Focus on what's important and relevant. Be concise, clear, and engaging. "
            "If asked for a name, return only the name. If asked for a number, return only the number with brief context."
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
        
        # Step 2: Check if this is a simple factual question - answer directly from data
        question_lower = question.lower()
        
        # Check if user wants comprehensive/all information
        comprehensive_keywords = ["all info", "all information", "all data", "everything", "complete profile", "full profile", "comprehensive", "give all", "tell me everything"]
        is_comprehensive_request = any(keyword in question_lower for keyword in comprehensive_keywords)
        
        # Handle comprehensive information requests
        if is_comprehensive_request:
            prompt = self._create_comprehensive_prompt(ucp, question)
            response = self.llama_client.generate(
                prompt=prompt,
                system_message="You are a compliance assistant. Provide a comprehensive, well-organized summary of all available customer information. Structure your response clearly with sections. Be thorough and include all relevant details from the data provided.",
                max_tokens=2048,  # More tokens for comprehensive responses
                temperature=0.5
            )
            answer = self._clean_response(response["content"], question, preserve_structure=True)
        # Handle name questions directly
        elif 'name' in question_lower and ('what' in question_lower or 'who' in question_lower):
            identity = ucp.profile_data.get("identity", {})
            name = identity.get("name", "")
            if name:
                answer = name
            else:
                # Fall back to LLM if name not found
                prompt = self._create_rag_prompt(ucp, question)
                response = self.llama_client.generate(
                    prompt=prompt,
                    system_message=self.system_message,
                    max_tokens=1024,
                    temperature=0.3
                )
                answer = self._clean_response(response["content"], question)
        # Handle spending questions directly
        elif 'spending' in question_lower or ('spend' in question_lower and 'how much' in question_lower):
            financial = ucp.transaction_aggregates
            spending_30d = financial.get("total_spending_30d", 0)
            if spending_30d > 0:
                answer = f"{spending_30d:.2f}"
            else:
                answer = "0 (No spending recorded in the last 30 days)"
        else:
            # Step 3: Create RAG prompt with UCP context
            prompt = self._create_rag_prompt(ucp, question)
            
            # Step 4: Generate answer using LLM
            response = self.llama_client.generate(
                prompt=prompt,
                system_message=self.system_message,
                max_tokens=1024,
                temperature=0.3  # Lower temperature for factual accuracy
            )
            
            # Step 5: Clean up any thinking tokens or internal reasoning
            # For comprehensive requests, use less aggressive cleaning to preserve structure
            if is_comprehensive_request:
                answer = self._clean_response(response["content"], question, preserve_structure=True)
            else:
                answer = self._clean_response(response["content"], question)
        
        # Step 6: Extract citations
        
        # Extract citations
        citations = self._extract_citations(ucp, question)
        
        return {
            "partner_id": partner_id,
            "question": question,
            "answer": answer,
            "citations": citations,
            "ucp_snapshot": self._get_relevant_ucp_snapshot(ucp, question),
            "source": "Unified Customer Profile (UCP)"
        }
    
    def _create_comprehensive_prompt(self, ucp: UnifiedCustomerProfile, question: str) -> str:
        """Create comprehensive prompt with ALL UCP data for full profile analysis."""
        # Get full UCP text representation
        full_ucp_text = ucp.to_text()
        
        # Get all transactions (not just recent)
        all_transactions = ucp.profile_data.get("all_transactions", [])
        transactions_text = ""
        if all_transactions:
            transactions_text = "\n=== ALL TRANSACTIONS ===\n"
            # Show up to 50 transactions to avoid token limits
            for tx in all_transactions[:50]:
                date = tx.get('Date', 'N/A')
                amount = tx.get('Amount', 'N/A')
                currency = tx.get('Currency', '')
                debit_credit = tx.get('Debit/Credit', 'N/A')
                transactions_text += f"- {date}: {amount} {currency} ({debit_credit})\n"
            if len(all_transactions) > 50:
                transactions_text += f"... and {len(all_transactions) - 50} more transactions\n"
        
        # Get financial aggregates
        financial = ucp.transaction_aggregates
        financial_text = "\n=== FINANCIAL SUMMARY ===\n"
        for key, value in financial.items():
            if value is not None:
                financial_text += f"- {key}: {value}\n"
        
        # Get account data
        account_data = ucp.profile_data.get("account_data", {})
        accounts_text = ""
        if account_data and account_data.get("accounts"):
            accounts_text = "\n=== ACCOUNTS ===\n"
            for acc in account_data.get("accounts", [])[:10]:
                acc_id = acc.get("account_id", "N/A")
                balance = acc.get("balance", "N/A")
                currency = acc.get("currency", "N/A")
                accounts_text += f"- Account {acc_id}: Balance {balance} {currency}\n"
        
        # Get risk metadata
        risk_text = ""
        risk = ucp.risk_metadata
        if risk:
            risk_text = "\n=== RISK ASSESSMENT ===\n"
            risk_text += f"Risk Score: {risk.get('risk_score', 'N/A')}/100\n"
            if risk.get('explanation'):
                risk_text += f"Explanation: {risk.get('explanation')}\n"
            if risk.get('feature_contributions'):
                risk_text += "Feature Contributions:\n"
                for feat, contrib in risk.get('feature_contributions', {}).items():
                    risk_text += f"- {feat}: {contrib}\n"
        
        # Get onboarding notes
        onboarding_text = ""
        onboarding = ucp.profile_data.get("onboarding_notes", "")
        if onboarding:
            onboarding_text = f"\n=== ONBOARDING NOTES ===\n{onboarding}\n"
        
        full_context = f"""{full_ucp_text}{financial_text}{accounts_text}{transactions_text}{risk_text}{onboarding_text}"""
        
        return f"""Question: {question}

Complete Customer Profile Data:
{full_context}

Provide a comprehensive, well-organized summary of ALL available information about this customer. 
Write in natural, compelling language without markdown formatting (no **, no bullets, no headers). 
Structure your response with clear sections using natural language transitions:
- Identity & Profile
- Financial Summary
- Transaction History
- Account Information
- Risk Assessment (if available)
- Onboarding Notes (if available)

Be thorough but focus on what's important. Write in plain text, make it engaging and easy to read.

Comprehensive Analysis:"""
    
    def _create_rag_prompt(self, ucp: UnifiedCustomerProfile, question: str) -> str:
        """Create RAG prompt with UCP context."""
        # Extract relevant data sections based on question type
        question_lower = question.lower()
        
        # Build context string with only relevant information
        context_parts = []
        
        # Always include identity
        identity = ucp.profile_data.get("identity", {})
        if identity:
            context_parts.append(f"Customer: {identity.get('name', 'N/A')} (ID: {ucp.partner_id})")
        
        # Add financial data if question is about spending/transactions
        if any(word in question_lower for word in ["spending", "transaction", "money", "amount", "financial", "balance", "debit", "credit"]):
            financial = ucp.transaction_aggregates
            if financial:
                context_parts.append(f"Financial Summary:")
                context_parts.append(f"- Total spending (30 days): {financial.get('total_spending_30d', 0):.2f}")
                context_parts.append(f"- Total spending (90 days): {financial.get('total_spending_90d', 0):.2f}")
                context_parts.append(f"- Transaction count (30 days): {financial.get('tx_count_30d', 0)}")
                context_parts.append(f"- Average transaction value: {financial.get('avg_tx_value_90d', 0):.2f}")
                context_parts.append(f"- Transaction velocity: {financial.get('velocity_tx_per_hour', 0):.2f} per hour")
        
        # Add recent transactions if relevant
        if any(word in question_lower for word in ["recent", "last", "latest", "transaction"]):
            recent_tx = ucp.profile_data.get("recent_transactions", [])[:3]
            if recent_tx:
                context_parts.append("Recent Transactions:")
                for tx in recent_tx:
                    context_parts.append(f"- {tx.get('Date', 'N/A')}: {tx.get('Amount', 'N/A')} {tx.get('Currency', '')} ({tx.get('Debit/Credit', 'N/A')})")
        
        # Add risk data if question is about risk/fraud
        if any(word in question_lower for word in ["risk", "fraud", "alert", "suspicious", "compliance"]):
            risk = ucp.risk_metadata
            if risk:
                context_parts.append(f"Risk Assessment: Score {risk.get('risk_score', 'N/A')}/100")
                if risk.get('explanation'):
                    context_parts.append(f"Explanation: {risk.get('explanation', '')[:200]}")
        
        # Add profile details if question is about identity/profile
        if any(word in question_lower for word in ["name", "who", "identity", "address", "phone", "contact", "profile"]):
            static = ucp.profile_data.get("static_profile", {})
            if static:
                context_parts.append("Profile Details:")
                if static.get("full_name"):
                    context_parts.append(f"- Name: {static.get('full_name')}")
                if static.get("primary_address"):
                    context_parts.append(f"- Address: {static.get('primary_address')}")
                if static.get("phone"):
                    context_parts.append(f"- Phone: {static.get('phone')}")
        
        context = "\n".join(context_parts) if context_parts else ucp.to_text()
        
        return f"""Question: {question}

Customer Data:
{context}

Answer the question in a natural, human-friendly way. Write in plain text without markdown formatting (no **, no bullets, no headers). 
Be compelling and focus on what's important. Return ONLY the answer, no explanations, no thinking process, no special tokens.

If the question asks for a name, return just the name.
If the question asks for a number, return the number with brief context.
If the question asks for information not in the data, say "I don't have that information."

Answer:"""
    
    def _clean_response(self, response: str, question: str = "", preserve_structure: bool = False) -> str:
        """Clean response to remove thinking tokens and internal reasoning.
        
        Args:
            response: The raw response from LLM
            question: The original question (for context)
            preserve_structure: If True, preserve formatting and structure (for comprehensive responses)
        """
        import re
        
        # Remove markdown formatting first
        response = re.sub(r'\*\*([^*]+)\*\*', r'\1', response)  # **bold** -> bold
        response = re.sub(r'\*([^*]+)\*', r'\1', response)  # *italic* -> italic
        response = re.sub(r'__([^_]+)__', r'\1', response)  # __bold__ -> bold
        response = re.sub(r'_([^_]+)_', r'\1', response)  # _italic_ -> italic
        response = re.sub(r'^#+\s+', '', response, flags=re.MULTILINE)  # Headers
        
        # Remove all thinking tokens like <|channel|>, <|message|>, <|end|>, <|start|>, etc.
        response = re.sub(r'<\|[^|]+\|>', '', response)
        
        # Remove analysis/thinking patterns (less aggressive for comprehensive responses)
        if not preserve_structure:
            response = re.sub(r'analysis\s*', '', response, flags=re.IGNORECASE)
            response = re.sub(r'assistant\s*final\s*', '', response, flags=re.IGNORECASE)
        response = re.sub(r'analysis<\|[^>]+>', '', response, flags=re.IGNORECASE)
        response = re.sub(r'assistant<\|[^>]+>', '', response, flags=re.IGNORECASE)
        response = re.sub(r'channel<\|[^>]+>', '', response, flags=re.IGNORECASE)
        response = re.sub(r'message<\|[^>]+>', '', response, flags=re.IGNORECASE)
        if not preserve_structure:
            response = re.sub(r'We need to answer[^\.]+\.', '', response, flags=re.IGNORECASE | re.DOTALL)
            response = re.sub(r'The data:[^\.]+\.', '', response, flags=re.IGNORECASE | re.DOTALL)
            response = re.sub(r'So answer[^\.]+\.', '', response, flags=re.IGNORECASE | re.DOTALL)
            response = re.sub(r'We have no[^\.]+\.', '', response, flags=re.IGNORECASE | re.DOTALL)
        
        # Clean up extra whitespace
        response = re.sub(r'\n{3,}', '\n\n', response)  # Max 2 newlines
        response = re.sub(r' +', ' ', response)  # Multiple spaces to single
        response = response.strip()
        
        # Extract just the final answer if there's a pattern like "--- make this return only..."
        if '---' in response:
            # Take everything before the ---
            response = response.split('---')[0].strip()
        
        # If question asks for name, extract just the name
        question_lower = question.lower() if question else ""
        if 'name' in question_lower:
            # Look for the name in various patterns
            # Pattern 1: "is [Name]" or "Name: [Name]" or "client is [Name]"
            name_patterns = [
                r'(?:is|name:?|client:?)\s+([A-ZÄÖÜ][a-zäöüß\s]+(?:[A-ZÄÖÜ][a-zäöüß]+)?)',
                r'([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)+)',  # Just capitalized words
            ]
            for pattern in name_patterns:
                name_match = re.search(pattern, response, re.IGNORECASE)
                if name_match:
                    name = name_match.group(1).strip()
                    # Validate it looks like a name (2-4 words, capitalized)
                    words = name.split()
                    if 1 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
                        return name
        
        # Clean up extra whitespace and newlines
        response = re.sub(r'\s+', ' ', response).strip()
        
        return response
    
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

