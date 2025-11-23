"""
Enhanced Fraud Detection Agent with UCP and Explainable AI
Uses Unified Customer Profile for comprehensive risk assessment
"""

from .ucp import UCPBuilder, UnifiedCustomerProfile
from .llama_client import LlamaClient
from typing import Dict, Optional
import re
from datetime import datetime


class EnhancedFraudAgent:
    """
    Enhanced Fraud Detection Agent that:
    1. Builds Unified Customer Profile (UCP)
    2. Uses UCP features for risk assessment
    3. Provides explainable AI explanations
    4. Stores risk metadata back in UCP
    """
    
    def __init__(self, data_dir: str = "data", llama_url: str = "http://127.0.0.1:8080"):
        """
        Initialize Enhanced Fraud Agent.
        
        Args:
            data_dir: Path to data directory
            llama_url: URL of llama-server
        """
        self.ucp_builder = UCPBuilder(data_dir=data_dir)
        self.llama_client = LlamaClient(base_url=llama_url)
        self.model_version = "llama-20b-v1.0"
        
        self.system_message = (
            "Act as an investigator working for a Swiss bank and reviewing clients "
            "for AML relevant transactions, in compliance with FINMA and relevant Swiss regulations. "
            "You are an expert in anti-money laundering (AML) and fraud detection. "
            "Provide detailed, explainable risk assessments based on financial patterns, "
            "transaction velocity, and behavioral anomalies."
        )
    
    def assess_risk(self, partner_id: str) -> Dict:
        """
        Assess fraud/AML risk using Unified Customer Profile.
        
        Args:
            partner_id: The partner ID to assess
            
        Returns:
            Dictionary with:
            - partner_id: Partner ID
            - risk_score: Integer 0-100
            - rationale: Detailed explanation
            - feature_contributions: Key features that influenced the score
            - ucp: The Unified Customer Profile used
            - raw_response: Full LLM response
        """
        # Step 1: Build Unified Customer Profile
        ucp = self.ucp_builder.build_ucp(partner_id)
        
        # Step 2: Create enhanced prompt with UCP and feature analysis
        prompt = self._create_enhanced_prompt(ucp)
        
        # Step 3: Call LLaMA API for risk assessment
        response = self.llama_client.generate(
            prompt=prompt,
            system_message=self.system_message,
            max_tokens=1024,  # Increased for detailed explanations
            temperature=0.7
        )
        
        # Step 4: Parse response
        result = self._parse_enhanced_response(response["content"])
        
        # Step 5: Extract feature contributions (XAI-like explanation)
        feature_contributions = self._extract_feature_contributions(ucp, result["risk_score"])
        
        # Step 6: Store risk metadata back in UCP
        ucp.risk_metadata = {
            "risk_score": result["risk_score"],
            "model_version": self.model_version,
            "last_alert_ts": datetime.now().isoformat(),
            "explanation": result["rationale"],
            "feature_contributions": feature_contributions
        }
        
        return {
            "partner_id": partner_id,
            "risk_score": result["risk_score"],
            "rationale": result["rationale"],
            "feature_contributions": feature_contributions,
            "ucp": ucp.to_dict(),
            "raw_response": response["content"],
            "model_version": self.model_version,
            "timestamp": datetime.now().isoformat()
        }
    
    def _create_enhanced_prompt(self, ucp: UnifiedCustomerProfile) -> str:
        """Create enhanced prompt with UCP data and feature analysis."""
        financial = ucp.transaction_aggregates
        
        # Analyze key risk indicators
        risk_indicators = []
        
        if financial.get("velocity_tx_per_hour", 0) > 10:
            risk_indicators.append(f"High transaction velocity: {financial['velocity_tx_per_hour']:.2f} transactions/hour")
        
        if financial.get("total_spending_30d", 0) > financial.get("total_spending_90d", 0) * 0.5:
            risk_indicators.append("Recent spending spike (30d > 50% of 90d total)")
        
        if financial.get("max_tx_amount", 0) > financial.get("avg_tx_value_90d", 0) * 3:
            risk_indicators.append(f"Large transaction detected: {financial['max_tx_amount']:.2f} vs avg {financial['avg_tx_value_90d']:.2f}")
        
        indicators_text = "\n".join(risk_indicators) if risk_indicators else "No significant risk indicators detected"
        
        return f"""Analyze the following Unified Customer Profile for fraud/AML risk.

{ucp.to_text()}

KEY FINANCIAL FEATURES:
- Total Spending (30d): {financial.get('total_spending_30d', 0):.2f}
- Total Spending (90d): {financial.get('total_spending_90d', 0):.2f}
- Average Transaction Value (90d): {financial.get('avg_tx_value_90d', 0):.2f}
- Transaction Velocity: {financial.get('velocity_tx_per_hour', 0):.2f} tx/hour
- Transaction Count (30d): {financial.get('tx_count_30d', 0)}
- Max Transaction Amount: {financial.get('max_tx_amount', 0):.2f}

RISK INDICATORS:
{indicators_text}

Provide a comprehensive risk assessment:
1. Risk Score (0-100): 0 = no risk, 100 = highest risk
2. Detailed Rationale: Explain the risk factors, patterns, and compliance concerns
3. Feature Contributions: Identify which specific features (velocity, amounts, patterns) contributed most to the risk score
4. Compliance Notes: Any FINMA/Swiss regulatory concerns

Format your response as:
RISK_SCORE: [number 0-100]
RATIONALE: [detailed explanation]
FEATURE_CONTRIBUTIONS: [list key features that influenced the score]
COMPLIANCE_NOTES: [regulatory concerns if any]"""
    
    def _parse_enhanced_response(self, response_text: str) -> Dict:
        """Parse enhanced LLM response."""
        # Extract risk score
        risk_score = None
        score_match = re.search(r'RISK_SCORE:\s*(\d+)', response_text, re.IGNORECASE)
        if score_match:
            risk_score = int(score_match.group(1))
        else:
            numbers = re.findall(r'\b([0-9]|[1-9][0-9]|100)\b', response_text)
            for num in numbers:
                score = int(num)
                if 0 <= score <= 100:
                    risk_score = score
                    break
        
        if risk_score is None:
            risk_score = 50
        
        # Extract rationale
        rationale_match = re.search(r'RATIONALE:\s*(.+?)(?:\n\n|FEATURE_CONTRIBUTIONS:)', response_text, re.IGNORECASE | re.DOTALL)
        if rationale_match:
            rationale = rationale_match.group(1).strip()
        else:
            rationale = response_text.strip()
        
        # Extract feature contributions
        feature_match = re.search(r'FEATURE_CONTRIBUTIONS:\s*(.+?)(?:\n\n|COMPLIANCE_NOTES:)', response_text, re.IGNORECASE | re.DOTALL)
        features = feature_match.group(1).strip() if feature_match else "Not specified"
        
        # Extract compliance notes
        compliance_match = re.search(r'COMPLIANCE_NOTES:\s*(.+?)(?:\n\n|\Z)', response_text, re.IGNORECASE | re.DOTALL)
        compliance = compliance_match.group(1).strip() if compliance_match else "No specific compliance concerns"
        
        return {
            "risk_score": risk_score,
            "rationale": rationale,
            "feature_contributions": features,
            "compliance_notes": compliance
        }
    
    def _extract_feature_contributions(self, ucp: UnifiedCustomerProfile, risk_score: int) -> Dict:
        """
        Extract feature contributions (XAI-like explanation).
        Identifies which UCP features are most significant for the risk score.
        """
        financial = ucp.transaction_aggregates
        
        contributions = {}
        
        # Velocity contribution
        velocity = financial.get("velocity_tx_per_hour", 0)
        if velocity > 10:
            contributions["transaction_velocity"] = {
                "value": velocity,
                "impact": "high" if velocity > 20 else "medium",
                "reason": "High transaction frequency may indicate suspicious activity"
            }
        
        # Spending pattern contribution
        spending_30d = financial.get("total_spending_30d", 0)
        spending_90d = financial.get("total_spending_90d", 0)
        if spending_90d > 0:
            ratio = spending_30d / spending_90d
            if ratio > 0.5:
                contributions["spending_spike"] = {
                    "value": ratio,
                    "impact": "high" if ratio > 0.75 else "medium",
                    "reason": "Recent spending spike relative to historical average"
                }
        
        # Large transaction contribution
        max_tx = financial.get("max_tx_amount", 0)
        avg_tx = financial.get("avg_tx_value_90d", 0)
        if avg_tx > 0 and max_tx > avg_tx * 3:
            contributions["large_transaction"] = {
                "value": max_tx,
                "impact": "high",
                "reason": f"Transaction amount ({max_tx:.2f}) significantly exceeds average ({avg_tx:.2f})"
            }
        
        return contributions

