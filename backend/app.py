"""
Backend API for the KYC and Transaction Narration Agent
Fraud Detection using LLaMA 20B model
"""

from flask import Flask, request, jsonify
import os
import sys

# Add parent directory to path to import ai_service_level
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_service_level.fraud_agent import FraudAgent

app = Flask(__name__)

# Initialize Fraud Agent
# Set LLAMA_SERVER_URL environment variable if llama-server is not on localhost:8080
llama_url = os.getenv("LLAMA_SERVER_URL", "http://127.0.0.1:8080")
data_dir = os.getenv("DATA_DIR", "data")

fraud_agent = FraudAgent(data_dir=data_dir, llama_url=llama_url)


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "llama_server": llama_url
    })


@app.route("/api/assess-risk", methods=["POST"])
def assess_risk():
    """
    Assess fraud/AML risk for a partner using LLaMA 20B model.
    
    Request body:
    {
        "partner_id": "96a660ff-08e0-49c1-be6d-bb22a84e742e"
    }
    
    Returns:
    {
        "partner_id": "...",
        "risk_score": 45,
        "rationale": "Explanation of risk assessment...",
        "raw_response": "Full LLM response..."
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        partner_id = data.get("partner_id")
        
        if not partner_id:
            return jsonify({"error": "partner_id is required"}), 400
        
        # Assess risk using Fraud Agent
        result = fraud_agent.assess_risk(partner_id)
        
        return jsonify({
            "partner_id": result["partner_id"],
            "risk_score": result["risk_score"],
            "rationale": result["rationale"],
            "raw_response": result.get("raw_response", ""),
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


@app.route("/api/profile", methods=["POST"])
def get_profile():
    """
    Get profile data for a partner (Profile Agent output).
    
    Request body:
    {
        "partner_id": "96a660ff-08e0-49c1-be6d-bb22a84e742e"
    }
    
    Returns:
    {
        "partner_id": "...",
        "profile_text": "Formatted profile text..."
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        partner_id = data.get("partner_id")
        
        if not partner_id:
            return jsonify({"error": "partner_id is required"}), 400
        
        # Get profile from Profile Agent
        profile_text = fraud_agent.profile_agent.get_profile_text(partner_id)
        
        return jsonify({
            "partner_id": partner_id,
            "profile_text": profile_text,
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


@app.route("/api/generate", methods=["POST"])
def generate():
    """
    General text generation endpoint.
    
    Request body:
    {
        "prompt": "Your prompt here",
        "max_tokens": 512,
        "temperature": 0.7
    }
    """
    try:
        data = request.get_json()
        
        if not data or "prompt" not in data:
            return jsonify({"error": "Prompt is required"}), 400
        
        # TODO: Implement AI service integration
        return jsonify({
            "error": "Not implemented",
            "message": "AI service not configured"
        }), 501
    
    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    # Run the Flask app
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
