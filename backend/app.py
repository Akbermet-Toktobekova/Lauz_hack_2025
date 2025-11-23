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
from ai_service_level.enhanced_fraud_agent import EnhancedFraudAgent
from ai_service_level.rag_agent import RAGAgent

app = Flask(__name__)

# Initialize Agents
# Set LLAMA_SERVER_URL environment variable if llama-server is not on localhost:8080
llama_url = os.getenv("LLAMA_SERVER_URL", "http://127.0.0.1:8080")

# Get the workspace root directory (parent of backend/)
workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.getenv("DATA_DIR", os.path.join(workspace_root, "data"))

# Initialize both basic and enhanced fraud agents
fraud_agent = FraudAgent(data_dir=data_dir, llama_url=llama_url)
enhanced_fraud_agent = EnhancedFraudAgent(data_dir=data_dir, llama_url=llama_url)
rag_agent = RAGAgent(data_dir=data_dir, llama_url=llama_url)


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    # Check if llama-server is accessible
    llama_accessible = False
    try:
        # Try a simple request to check if server is up
        import requests
        test_response = requests.get(f"{llama_url}/health", timeout=2)
        llama_accessible = test_response.status_code == 200
    except:
        pass
    
    return jsonify({
        "status": "healthy" if llama_accessible else "degraded",
        "llama_server_url": llama_url,
        "llama_server_accessible": llama_accessible,
        "message": "llama-server is running" if llama_accessible else "llama-server not accessible - make sure it's running on port 8080"
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


@app.route("/api/assess-risk-enhanced", methods=["POST"])
def assess_risk_enhanced():
    """
    Enhanced fraud/AML risk assessment using Unified Customer Profile (UCP).
    
    Request body:
    {
        "partner_id": "96a660ff-08e0-49c1-be6d-bb22a84e742e"
    }
    
    Returns:
    {
        "partner_id": "...",
        "risk_score": 45,
        "rationale": "Detailed explanation...",
        "feature_contributions": {...},
        "ucp": {...},
        "model_version": "...",
        "timestamp": "..."
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        partner_id = data.get("partner_id")
        
        if not partner_id:
            return jsonify({"error": "partner_id is required"}), 400
        
        # Assess risk using Enhanced Fraud Agent
        result = enhanced_fraud_agent.assess_risk(partner_id)
        
        return jsonify({
            "partner_id": result["partner_id"],
            "risk_score": result["risk_score"],
            "rationale": result["rationale"],
            "feature_contributions": result["feature_contributions"],
            "compliance_notes": result.get("compliance_notes", ""),
            "ucp": result["ucp"],
            "model_version": result["model_version"],
            "timestamp": result["timestamp"],
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


@app.route("/api/qa", methods=["POST"])
def qa():
    """
    Conversational Q&A endpoint for compliance queries.
    Uses RAG (Retrieval-Augmented Generation) to answer questions about customers.
    
    Request body:
    {
        "partner_id": "96a660ff-08e0-49c1-be6d-bb22a84e742e",
        "question": "What is the total spending for this customer in the last 30 days?"
    }
    
    Returns:
    {
        "partner_id": "...",
        "question": "...",
        "answer": "...",
        "citations": [...],
        "source": "Unified Customer Profile (UCP)"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        partner_id = data.get("partner_id")
        question = data.get("question")
        
        if not partner_id:
            return jsonify({"error": "partner_id is required"}), 400
        
        if not question:
            return jsonify({"error": "question is required"}), 400
        
        # Answer question using RAG Agent
        result = rag_agent.answer_query(partner_id, question)
        
        return jsonify({
            "partner_id": result["partner_id"],
            "question": result["question"],
            "answer": result["answer"],
            "citations": result["citations"],
            "ucp_snapshot": result["ucp_snapshot"],
            "source": result["source"],
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    # Run the Flask app
    # Use port 5001 as default (5000 is often used by AirPlay on macOS)
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
