"""
Fraud Detection Agent - LLM reasoning engine for AML risk assessment
Uses LLaMA 20B model to analyze client profiles and provide risk scores.
"""

from .profile_agent import ProfileAgent
from .llama_client import LlamaClient
from typing import Dict, Optional
import re


class FraudAgent:
    """
    Fraud Detection Agent that uses LLaMA 20B for AML risk assessment.
    Takes partner_id, gets profile data, and sends to LLM for zero-shot reasoning.
    """
    
    def __init__(self, data_dir: str = "data", llama_url: str = "http://127.0.0.1:8080"):
        """
        Initialize Fraud Agent.
        
        Args:
            data_dir: Path to data directory
            llama_url: URL of llama-server
        """
        self.profile_agent = ProfileAgent(data_dir=data_dir)
        self.llama_client = LlamaClient(base_url=llama_url)
        
        self.system_message = (
            "Act as an investigator working for a Swiss bank and reviewing clients "
            "for AML relevant transactions, in compliance with FINMA and relevant Swiss regulations. "
            "You are an expert in anti-money laundering (AML) and fraud detection."
        )
    
    def assess_risk(self, partner_id: str) -> Dict:
        """
        Assess fraud/AML risk for a partner.
        
        Args:
            partner_id: The partner ID to assess
            
        Returns:
            Dictionary with:
            - risk_score: Integer 0-100
            - rationale: Explanation string
            - raw_response: Full LLM response
        """
        # Step 1: Get profile data from Profile Agent
        profile_text = self.profile_agent.get_profile_text(partner_id)
        
        # Step 2: Create prompt for LLM
        prompt = self._create_prompt(profile_text)
        
        # Step 3: Call LLaMA API
        response = self.llama_client.generate(
            prompt=prompt,
            system_message=self.system_message,
            max_tokens=512,
            temperature=0.7
        )
        
        # Step 4: Parse response to extract risk score and rationale
        result = self._parse_response(response["content"])
        result["raw_response"] = response["content"]
        result["partner_id"] = partner_id
        
        return result
    
    def _create_prompt(self, profile_text: str) -> str:
        """Create the zero-shot prompt for fraud detection."""
        return f"""Review the following client profile and recent transactions. 

{profile_text}

Provide a risk assessment with:
1. A risk score from 0-100 (where 0 is no risk and 100 is highest risk)
2. A brief, compliant explanation for that score based on Swiss AML regulations

Format your response as:
RISK_SCORE: [number 0-100]
RATIONALE: [your explanation]"""
    
    def _parse_response(self, response_text: str) -> Dict:
        """
        Parse LLM response to extract risk score and rationale.
        
        Args:
            response_text: Raw LLM response
            
        Returns:
            Dictionary with risk_score and rationale
        """
        # Try to extract risk score
        risk_score = None
        
        # Look for "RISK_SCORE: X" pattern
        score_match = re.search(r'RISK_SCORE:\s*(\d+)', response_text, re.IGNORECASE)
        if score_match:
            risk_score = int(score_match.group(1))
        else:
            # Try to find any number 0-100 in the text
            numbers = re.findall(r'\b([0-9]|[1-9][0-9]|100)\b', response_text)
            if numbers:
                # Take the first number that could be a score
                for num in numbers:
                    score = int(num)
                    if 0 <= score <= 100:
                        risk_score = score
                        break
        
        # Default to 50 if no score found
        if risk_score is None:
            risk_score = 50
        
        # Extract rationale
        rationale_match = re.search(r'RATIONALE:\s*(.+?)(?:\n\n|\Z)', response_text, re.IGNORECASE | re.DOTALL)
        if rationale_match:
            rationale = rationale_match.group(1).strip()
        else:
            # If no explicit rationale section, use the whole response
            rationale = response_text.strip()
        
        return {
            "risk_score": risk_score,
            "rationale": rationale
        }


# Example usage
if __name__ == "__main__":
    agent = FraudAgent(data_dir="data")
    
    # Test with a sample partner_id
    test_partner_id = "96a660ff-08e0-49c1-be6d-bb22a84e742e"
    result = agent.assess_risk(test_partner_id)
    
    print(f"Partner ID: {result['partner_id']}")
    print(f"Risk Score: {result['risk_score']}/100")
    print(f"Rationale: {result['rationale']}")

