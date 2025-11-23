"""
Chatbot Agent - Natural Language Interface
Handles natural language requests, extracts Partner IDs, and routes to appropriate agents
"""

from .fraud_agent import FraudAgent
from .enhanced_fraud_agent import EnhancedFraudAgent
from .rag_agent import RAGAgent
from .llama_client import LlamaClient
from typing import Dict, Optional, List
import re


class ChatbotAgent:
    """
    Chatbot Agent that handles natural language requests.
    Can extract Partner IDs from messages and route to appropriate handlers.
    """
    
    def __init__(self, data_dir: str = "data", llama_url: str = "http://127.0.0.1:8080"):
        """
        Initialize Chatbot Agent.
        
        Args:
            data_dir: Path to data directory
            llama_url: URL of llama-server
        """
        self.fraud_agent = FraudAgent(data_dir=data_dir, llama_url=llama_url)
        self.enhanced_fraud_agent = EnhancedFraudAgent(data_dir=data_dir, llama_url=llama_url)
        self.rag_agent = RAGAgent(data_dir=data_dir, llama_url=llama_url)
        self.llama_client = LlamaClient(base_url=llama_url)
        
        self.system_message = (
            "You are a helpful compliance assistant for a Swiss bank. "
            "You help users assess fraud risk and answer questions about customers. "
            "Be conversational, clear, and helpful."
        )
    
    def process_message(self, message: str, conversation_history: Optional[List[Dict]] = None) -> Dict:
        """
        Process a natural language message.
        
        Args:
            message: User's message
            conversation_history: Previous messages in the conversation
            
        Returns:
            Dictionary with:
            - response: The response text
            - action: Type of action performed (risk_assessment, question, error)
            - partner_id: Partner ID if extracted/used
            - data: Additional data (risk assessment, Q&A answer, etc.)
        """
        # Extract Partner ID from message
        partner_id = self._extract_partner_id(message, conversation_history)
        
        # Determine intent
        intent = self._determine_intent(message)
        
        if intent == "risk_assessment":
            if not partner_id:
                return {
                    "response": "I'd be happy to assess fraud risk! Please provide a Partner ID (UUID format) in your message. For example: 'Assess risk for partner 96a660ff-08e0-49c1-be6d-bb22a84e742e'",
                    "action": "error",
                    "partner_id": None,
                    "data": None
                }
            
            # Perform risk assessment using enhanced agent to get UCP data with transactions
            try:
                result = self.enhanced_fraud_agent.assess_risk(partner_id)
                
                # Format response in a human-friendly way
                rationale = self._clean_markdown(result['rationale'])
                risk_score = result['risk_score']
                
                # Create compelling, natural response
                risk_level = "low" if risk_score < 40 else "moderate" if risk_score < 70 else "high"
                response = f"Risk assessment completed.\n\nRisk Score: {risk_score}/100 ({risk_level.capitalize()} risk)\n\n{rationale}\n\nYou can now ask questions about this customer."
                
                return {
                    "response": response,
                    "action": "risk_assessment",
                    "partner_id": partner_id,
                    "data": result
                }
            except Exception as e:
                return {
                    "response": f"Error assessing risk: {str(e)}",
                    "action": "error",
                    "partner_id": partner_id,
                    "data": None
                }
        
        elif intent == "question":
            if not partner_id:
                return {
                    "response": "I'd be happy to answer your question! However, I need a Partner ID to look up the customer information. Please include a Partner ID in your message, or provide one first. For example: 'What is the name of client 96a660ff-08e0-49c1-be6d-bb22a84e742e?'",
                    "action": "error",
                    "partner_id": None,
                    "data": None
                }
            
            # Check for predefined query types
            message_lower = message.lower()
            
            # 1. Profile details request
            if any(keyword in message_lower for keyword in ["profile details", "profile information", "customer profile", "client profile", "profile"]):
                try:
                    response_text = self._get_profile_details(partner_id)
                    return {
                        "response": response_text,
                        "action": "question",
                        "partner_id": partner_id,
                        "data": {"type": "profile_details"}
                    }
                except Exception as e:
                    return {
                        "response": f"Error retrieving profile details: {str(e)}",
                        "action": "error",
                        "partner_id": partner_id,
                        "data": None
                    }
            
            # 2. Suspicious activity check
            elif any(keyword in message_lower for keyword in ["suspicious activity", "suspicious", "any suspicious", "suspicious transactions", "fraudulent activity", "suspicious behavior"]):
                try:
                    response_text = self._check_suspicious_activity(partner_id)
                    return {
                        "response": response_text,
                        "action": "question",
                        "partner_id": partner_id,
                        "data": {"type": "suspicious_activity"}
                    }
                except Exception as e:
                    return {
                        "response": f"Error checking suspicious activity: {str(e)}",
                        "action": "error",
                        "partner_id": partner_id,
                        "data": None
                    }
            
            # 3. Reasoning with exact transactions
            elif any(keyword in message_lower for keyword in ["why", "reason", "reasoning", "explain", "justification", "why suspicious", "why assume", "why detected"]):
                try:
                    response_text = self._get_suspicious_reasoning(partner_id)
                    return {
                        "response": response_text,
                        "action": "question",
                        "partner_id": partner_id,
                        "data": {"type": "suspicious_reasoning"}
                    }
                except Exception as e:
                    return {
                        "response": f"Error retrieving reasoning: {str(e)}",
                        "action": "error",
                        "partner_id": partner_id,
                        "data": None
                    }
            
            # Default: Answer question using RAG
            try:
                result = self.rag_agent.answer_query(partner_id, message)
                return {
                    "response": result["answer"],
                    "action": "question",
                    "partner_id": partner_id,
                    "data": result
                }
            except Exception as e:
                return {
                    "response": f"Error answering question: {str(e)}",
                    "action": "error",
                    "partner_id": partner_id,
                    "data": None
                }
        
        else:
            # General query - try to be helpful
            return {
                "response": "I can help you with:\n\n1. Risk Assessment: 'Assess risk for partner [ID]'\n2. Profile Details: 'Show profile details for [ID]' or 'Profile information for [ID]'\n3. Suspicious Activity: 'Does [ID] have any suspicious activity?' or 'Check suspicious activity for [ID]'\n4. Detailed Reasoning: 'Why is [ID] suspicious?' or 'Explain reasoning for [ID]'\n5. General Questions: 'What is the name of client [ID]?' or 'How much did [ID] spend last month?'\n\nPlease include a Partner ID (UUID format) in your request.",
                "action": "help",
                "partner_id": None,
                "data": None
            }
    
    def _extract_partner_id(self, message: str, conversation_history: Optional[List[Dict]] = None) -> Optional[str]:
        """
        Extract Partner ID from message or conversation history.
        
        Args:
            message: Current message
            conversation_history: Previous messages
            
        Returns:
            Partner ID if found, None otherwise
        """
        # First, try to find UUID in current message
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        matches = re.findall(uuid_pattern, message, re.IGNORECASE)
        if matches:
            return matches[0]
        
        # Check conversation history for previously mentioned Partner ID
        if conversation_history:
            for msg in reversed(conversation_history):
                if msg.get("partner_id"):
                    return msg["partner_id"]
                # Check message content
                content = msg.get("content", "")
                matches = re.findall(uuid_pattern, content, re.IGNORECASE)
                if matches:
                    return matches[0]
        
        return None
    
    def _determine_intent(self, message: str) -> str:
        """
        Determine user intent from message.
        
        Args:
            message: User's message
            
        Returns:
            Intent: "risk_assessment", "question", or "general"
        """
        message_lower = message.lower()
        
        # Risk assessment keywords
        risk_keywords = ["assess", "risk", "fraud", "aml", "evaluate", "check", "analyze", "screening"]
        if any(keyword in message_lower for keyword in risk_keywords):
            return "risk_assessment"
        
        # Question keywords (including comprehensive info requests)
        question_keywords = ["what", "who", "when", "where", "how", "why", "which", "tell me", "show me", "name", "spending", "transaction", "info", "information", "data", "all", "everything", "profile", "give", "provide"]
        if any(keyword in message_lower for keyword in question_keywords) or message_lower.endswith("?"):
            return "question"
        
        # Default to question if it looks like a query
        if len(message.split()) > 2:
            return "question"
        
        return "general"
    
    def _clean_markdown(self, text: str) -> str:
        """Remove markdown formatting and make text more human-friendly."""
        import re
        
        # Remove markdown bold/italic
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold** -> bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)  # *italic* -> italic
        text = re.sub(r'__([^_]+)__', r'\1', text)  # __bold__ -> bold
        text = re.sub(r'_([^_]+)_', r'\1', text)  # _italic_ -> italic
        
        # Remove markdown headers
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        
        # Remove markdown list markers but keep content
        text = re.sub(r'^[-*+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # Clean up extra whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 newlines
        text = re.sub(r' +', ' ', text)  # Multiple spaces to single
        
        return text.strip()
    
    def _get_profile_details(self, partner_id: str) -> str:
        """Get comprehensive profile details for a customer."""
        from .ucp import UCPBuilder
        import os
        
        # Get data_dir from enhanced_fraud_agent
        data_dir = getattr(self.enhanced_fraud_agent.ucp_builder, 'data_dir', 'data')
        ucp_builder = UCPBuilder(data_dir=data_dir)
        ucp = ucp_builder.build_ucp(partner_id)
        
        identity = ucp.profile_data.get("identity", {})
        static_profile = ucp.profile_data.get("static_profile", {})
        account_data = ucp.profile_data.get("account_data", {})
        financial = ucp.transaction_aggregates
        
        # Build human-friendly profile response
        lines = []
        lines.append(f"Profile Details for Customer {partner_id[:8]}...")
        lines.append("")
        
        # Identity Section
        lines.append("Identity Information:")
        if identity.get("name"):
            lines.append(f"  Name: {identity.get('name')}")
        if identity.get("kyc_status"):
            lines.append(f"  KYC Status: {identity.get('kyc_status')}")
        if identity.get("onboarding_date"):
            lines.append(f"  Onboarding Date: {identity.get('onboarding_date')}")
        lines.append("")
        
        # Contact Information
        if static_profile:
            lines.append("Contact Information:")
            if static_profile.get("full_name"):
                lines.append(f"  Full Name: {static_profile.get('full_name')}")
            if static_profile.get("primary_address"):
                lines.append(f"  Address: {static_profile.get('primary_address')}")
            if static_profile.get("phone"):
                lines.append(f"  Phone: {static_profile.get('phone')}")
            if static_profile.get("email"):
                lines.append(f"  Email: {static_profile.get('email')}")
            lines.append("")
        
        # Account Information
        if account_data and account_data.get("accounts"):
            lines.append("Account Information:")
            for acc in account_data.get("accounts", [])[:5]:  # Show up to 5 accounts
                acc_id = acc.get("account_id", "N/A")
                balance = acc.get("balance", "N/A")
                currency = acc.get("currency", "CHF")
                lines.append(f"  Account {acc_id[:8]}...: {balance} {currency}")
            lines.append("")
        
        # Financial Summary
        if financial:
            lines.append("Financial Summary:")
            if financial.get("total_spending_30d"):
                lines.append(f"  Total Spending (30 days): {financial.get('total_spending_30d', 0):.2f}")
            if financial.get("total_spending_90d"):
                lines.append(f"  Total Spending (90 days): {financial.get('total_spending_90d', 0):.2f}")
            if financial.get("tx_count_30d"):
                lines.append(f"  Transaction Count (30 days): {financial.get('tx_count_30d', 0)}")
            lines.append("")
        
        # Onboarding Notes
        onboarding_notes = ucp.profile_data.get("onboarding_notes", "")
        if onboarding_notes:
            lines.append("Onboarding Notes:")
            lines.append(f"  {onboarding_notes[:200]}")
        
        return "\n".join(lines)
    
    def _check_suspicious_activity(self, partner_id: str) -> str:
        """Check if customer has suspicious activity."""
        from .ucp import UCPBuilder
        
        # Get data_dir from enhanced_fraud_agent
        data_dir = getattr(self.enhanced_fraud_agent.ucp_builder, 'data_dir', 'data')
        ucp_builder = UCPBuilder(data_dir=data_dir)
        ucp = ucp_builder.build_ucp(partner_id)
        
        # Perform risk assessment to get risk score
        risk_result = self.enhanced_fraud_agent.assess_risk(partner_id)
        risk_score = risk_result['risk_score']
        
        financial = ucp.transaction_aggregates
        all_transactions = ucp.profile_data.get("all_transactions", [])
        
        # Determine if suspicious
        is_suspicious = risk_score >= 40  # Moderate or high risk
        
        lines = []
        lines.append(f"Suspicious Activity Assessment for Customer {partner_id[:8]}...")
        lines.append("")
        
        if is_suspicious:
            lines.append("Status: Suspicious activity detected")
            lines.append(f"Risk Score: {risk_score}/100 (Moderate to High Risk)")
            lines.append("")
            lines.append("This customer has been flagged due to:")
            
            # Check specific indicators
            indicators = []
            if financial.get("velocity_tx_per_hour", 0) > 10:
                indicators.append(f"High transaction velocity ({financial.get('velocity_tx_per_hour', 0):.2f} transactions per hour)")
            if financial.get("max_tx_amount", 0) > financial.get("avg_tx_value_90d", 0) * 3:
                indicators.append("Large transaction amounts compared to average")
            if financial.get("total_spending_30d", 0) > financial.get("total_spending_90d", 0) * 0.5:
                indicators.append("Recent spending spike (30-day spending exceeds 50% of 90-day total)")
            
            if indicators:
                for indicator in indicators:
                    lines.append(f"  • {indicator}")
            else:
                lines.append("  • Risk assessment indicates elevated risk level")
        else:
            lines.append("Status: No suspicious activity detected")
            lines.append(f"Risk Score: {risk_score}/100 (Low Risk)")
            lines.append("")
            lines.append("This customer shows normal transaction patterns and low risk indicators.")
        
        return "\n".join(lines)
    
    def _get_suspicious_reasoning(self, partner_id: str) -> str:
        """Get detailed reasoning for suspicious activity with exact transactions."""
        from .ucp import UCPBuilder
        
        # Get data_dir from enhanced_fraud_agent
        data_dir = getattr(self.enhanced_fraud_agent.ucp_builder, 'data_dir', 'data')
        ucp_builder = UCPBuilder(data_dir=data_dir)
        ucp = ucp_builder.build_ucp(partner_id)
        
        # Perform risk assessment
        risk_result = self.enhanced_fraud_agent.assess_risk(partner_id)
        risk_score = risk_result['risk_score']
        rationale = self._clean_markdown(risk_result['rationale'])
        
        financial = ucp.transaction_aggregates
        all_transactions = ucp.profile_data.get("all_transactions", [])
        
        lines = []
        lines.append(f"Detailed Reasoning for Suspicious Activity Assessment")
        lines.append(f"Customer: {partner_id[:8]}...")
        lines.append(f"Risk Score: {risk_score}/100")
        lines.append("")
        
        # Overall assessment
        lines.append("Assessment Summary:")
        lines.append(rationale)
        lines.append("")
        
        # Financial indicators
        if financial:
            lines.append("Financial Indicators:")
            if financial.get("velocity_tx_per_hour", 0) > 10:
                lines.append(f"  • High Transaction Velocity: {financial.get('velocity_tx_per_hour', 0):.2f} transactions per hour")
                lines.append("    This indicates unusually frequent transaction activity, which may suggest automated or suspicious behavior.")
            
            if financial.get("max_tx_amount", 0) > 0:
                avg_tx = financial.get("avg_tx_value_90d", 0)
                max_tx = financial.get("max_tx_amount", 0)
                if max_tx > avg_tx * 3 and avg_tx > 0:
                    lines.append(f"  • Large Transaction Detected: {max_tx:.2f} (Average: {avg_tx:.2f})")
                    lines.append("    This transaction is significantly larger than the customer's typical spending pattern.")
            
            if financial.get("total_spending_30d", 0) > financial.get("total_spending_90d", 0) * 0.5:
                spending_30d = financial.get("total_spending_30d", 0)
                spending_90d = financial.get("total_spending_90d", 0)
                lines.append(f"  • Spending Spike: {spending_30d:.2f} in last 30 days vs {spending_90d:.2f} in last 90 days")
                lines.append("    Recent spending represents more than 50% of total 90-day spending, indicating a sudden increase in activity.")
            lines.append("")
        
        # Exact transactions that are suspicious
        if all_transactions:
            lines.append("Relevant Transactions:")
            
            # Sort by amount (descending) to show largest transactions
            sorted_tx = sorted(
                [tx for tx in all_transactions if tx.get('Amount')],
                key=lambda x: abs(float(x.get('Amount', 0))),
                reverse=True
            )[:10]  # Top 10 largest transactions
            
            for idx, tx in enumerate(sorted_tx[:5], 1):  # Show top 5
                date = tx.get('Date', 'N/A')
                amount = tx.get('Amount', 'N/A')
                currency = tx.get('Currency', 'CHF')
                debit_credit = tx.get('Debit/Credit', '')
                transfer_type = tx.get('Transfer_Type', '')
                
                lines.append(f"  {idx}. Date: {date}")
                lines.append(f"     Amount: {amount} {currency} ({debit_credit})")
                if transfer_type:
                    lines.append(f"     Type: {transfer_type}")
                
                # Add reasoning for why this transaction might be suspicious
                if isinstance(amount, (int, float)) and amount > 0:
                    avg_tx = financial.get("avg_tx_value_90d", 0) if financial else 0
                    if avg_tx > 0 and abs(amount) > avg_tx * 2:
                        lines.append(f"     Note: This transaction is {abs(amount) / avg_tx:.1f}x larger than the average transaction value.")
                lines.append("")
        
        # Feature contributions if available
        if risk_result.get('feature_contributions'):
            lines.append("Key Risk Factors:")
            for feature, contrib in risk_result.get('feature_contributions', {}).items():
                if isinstance(contrib, dict):
                    impact = contrib.get('impact', 'medium')
                    reason = contrib.get('reason', '')
                    lines.append(f"  • {feature.replace('_', ' ').title()}: {impact.capitalize()} impact")
                    if reason:
                        lines.append(f"    {reason}")
                else:
                    lines.append(f"  • {feature.replace('_', ' ').title()}: {contrib}")
            lines.append("")
        
        lines.append("Conclusion:")
        if risk_score >= 70:
            lines.append("This customer presents a high risk profile requiring immediate review and potential enhanced due diligence.")
        elif risk_score >= 40:
            lines.append("This customer shows moderate risk indicators that warrant closer monitoring and periodic review.")
        else:
            lines.append("This customer shows low risk indicators with normal transaction patterns.")
        
        return "\n".join(lines)

