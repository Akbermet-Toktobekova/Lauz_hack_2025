# Fraud Detection & AML Risk Assessment System

## 🎯 Project Goal

This project implements an **AI-powered fraud detection and Anti-Money Laundering (AML) risk assessment system** for financial institutions. The system uses **LLaMA 20B** (GPT-OSS-20B) to analyze customer profiles, transaction patterns, and provide explainable risk assessments compliant with **Swiss FINMA regulations**.

### Key Objectives

- **Automated Risk Assessment**: Analyze customer profiles and transactions to assign risk scores (0-100)
- **Explainable AI**: Provide detailed rationales and feature contributions for risk decisions
- **Compliance-Focused**: Ensure assessments align with Swiss banking regulations (FINMA)
- **Unified Customer Profile (UCP)**: Create a single source of truth for all customer data
- **Conversational Q&A**: Enable compliance officers to query customer data using natural language

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────┐
│   Backend API (Flask)                    │
│   - RESTful endpoints                    │
│   - /api/assess-risk                     │
│   - /api/assess-risk-enhanced            │
│   - /api/qa                              │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   AI Service Level (Core Logic)          │
│   - FraudAgent (Basic)                   │
│   - EnhancedFraudAgent (UCP-based)       │
│   - RAGAgent (Q&A)                       │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   Data Layer + LLM                      │
│   - ProfileAgent (Data extraction)       │
│   - UCPBuilder (Feature engineering)      │
│   - LlamaClient (LLM API calls)         │
└─────────────────────────────────────────┘
```

---

## 📦 Components

### 1. **ProfileAgent** (`ai_service_level/profile_agent.py`)
- **Purpose**: Extracts and formats customer data from CSV files
- **Functionality**:
  - Loads customer data from multiple CSV files
  - Joins data across tables (partner → partner_role → business_rel → account → transactions)
  - Formats into structured text profiles
  - Extracts: Identity, Onboarding Notes, Recent Transactions

### 2. **FraudAgent** (`ai_service_level/fraud_agent.py`)
- **Purpose**: Basic fraud risk assessment using LLM
- **Flow**:
  1. Gets profile text from ProfileAgent
  2. Creates prompt for LLM risk assessment
  3. Calls LLaMA server via LlamaClient
  4. Parses response to extract risk score (0-100) and rationale
- **Output**: `{risk_score, rationale, partner_id}`

### 3. **UCPBuilder** (`ai_service_level/ucp.py`)
- **Purpose**: Builds Unified Customer Profile (UCP) - single source of truth
- **Creates**:
  - Canonical Identity (entity resolution)
  - Static Profile (demographics)
  - Account Data
  - **Financial Aggregates** (feature engineering):
    - `total_spending_30d`, `total_spending_90d`
    - `velocity_tx_per_hour` (transaction frequency)
    - `max_tx_amount`, `avg_tx_value_90d`
    - `tx_count_30d`, `tx_count_90d`

### 4. **EnhancedFraudAgent** (`ai_service_level/enhanced_fraud_agent.py`)
- **Purpose**: Advanced fraud detection with explainable AI
- **Features**:
  - Uses UCP for comprehensive analysis
  - Analyzes risk indicators (velocity spikes, large transactions)
  - Provides feature contributions (XAI)
  - Stores risk metadata back in UCP
- **Output**: Includes `feature_contributions`, `ucp`, `compliance_notes`

### 5. **RAGAgent** (`ai_service_level/rag_agent.py`)
- **Purpose**: Conversational Q&A about customers
- **Functionality**:
  - Answers questions using UCP context
  - Extracts citations from customer data
  - Provides factual answers based on profile data

### 6. **LlamaClient** (`ai_service_level/llama_client.py`)
- **Purpose**: HTTP client for llama-server API
- **Functionality**: Wraps OpenAI-compatible API calls to LLaMA 20B model

---

## 🚀 How to Run

### Prerequisites

1. **Python 3.x** with required packages:
   ```bash
   pip install flask requests pandas
   ```

2. **LLaMA Server** running on port 8080
   - Model: GPT-OSS-20B (or compatible)
   - Server: llama-server from llama.cpp

### Step 1: Start LLaMA Server

```bash
cd /workspace/gpt-oss-20b/llama.cpp

# Build server (if not already built)
cmake -B build
cmake --build build --config Release -t llama-server

# Start server
./build/bin/llama-server \
    -m /path/to/your/model.gguf \
    --host 0.0.0.0 \
    --port 8080
```

### Step 2: Start Backend API

```bash
cd /workspace

# Set environment variables (optional)
export LLAMA_SERVER_URL="http://127.0.0.1:8080"
export DATA_DIR="data"
export PORT=5001

# Start Flask backend
python backend/app.py
```

The API will be available at `http://localhost:5001`

### Step 3: Test the System

```bash
# Run test script
python test_fraud_detection.py

# Or test API directly
curl -X POST http://localhost:5001/api/assess-risk \
  -H "Content-Type: application/json" \
  -d '{"partner_id": "96a660ff-08e0-49c1-be6d-bb22a84e742e"}'
```

---

## 📡 API Endpoints

### Health Check
```http
GET /health
```
Returns system health and LLaMA server status.

### Basic Risk Assessment
```http
POST /api/assess-risk
Content-Type: application/json

{
  "partner_id": "96a660ff-08e0-49c1-be6d-bb22a84e742e"
}
```

**Response:**
```json
{
  "partner_id": "...",
  "risk_score": 45,
  "rationale": "Explanation of risk assessment...",
  "raw_response": "Full LLM response...",
  "status": "success"
}
```

### Enhanced Risk Assessment
```http
POST /api/assess-risk-enhanced
Content-Type: application/json

{
  "partner_id": "96a660ff-08e0-49c1-be6d-bb22a84e742e"
}
```

**Response:**
```json
{
  "partner_id": "...",
  "risk_score": 45,
  "rationale": "Detailed explanation...",
  "feature_contributions": {
    "transaction_velocity": {
      "value": 15.2,
      "impact": "high",
      "reason": "High transaction frequency..."
    }
  },
  "ucp": {...},
  "model_version": "llama-20b-v1.0",
  "timestamp": "2024-01-01T12:00:00"
}
```

### Conversational Q&A
```http
POST /api/qa
Content-Type: application/json

{
  "partner_id": "96a660ff-08e0-49c1-be6d-bb22a84e742e",
  "question": "What is the total spending for this customer in the last 30 days?"
}
```

**Response:**
```json
{
  "partner_id": "...",
  "question": "...",
  "answer": "Based on the UCP data...",
  "citations": [...],
  "ucp_snapshot": {...},
  "source": "Unified Customer Profile (UCP)"
}
```

### Get Profile
```http
POST /api/profile
Content-Type: application/json

{
  "partner_id": "96a660ff-08e0-49c1-be6d-bb22a84e742e"
}
```

---

## 📁 Project Structure

```
/workspace/
├── backend/
│   └── app.py                    # Flask API server
├── ai_service_level/
│   ├── __init__.py               # Package exports
│   ├── profile_agent.py          # Data extraction
│   ├── fraud_agent.py            # Basic fraud detection
│   ├── enhanced_fraud_agent.py   # Enhanced fraud detection
│   ├── rag_agent.py              # Q&A agent
│   ├── llama_client.py           # LLaMA API client
│   └── ucp.py                    # Unified Customer Profile
├── data/                          # CSV data files
│   ├── partner.csv
│   ├── transactions.csv
│   ├── client_onboarding_notes.csv
│   ├── partner_role.csv
│   ├── business_rel.csv
│   ├── br_to_account.csv
│   ├── account.csv
│   └── partner_country.csv
├── frontend/                      # Frontend (if applicable)
├── gpt-oss-20b/                   # LLaMA model and server
├── test_fraud_detection.py        # Test script
└── README.md                      # This file
```

---

## 🔧 Configuration

### Environment Variables

- `LLAMA_SERVER_URL`: LLaMA server URL (default: `http://127.0.0.1:8080`)
- `DATA_DIR`: Path to data directory (default: `data`)
- `PORT`: Backend API port (default: `5001`)

### Data Files Required

The system requires the following CSV files in the `data/` directory:
- `partner.csv` - Customer identity information
- `transactions.csv` - Transaction history
- `client_onboarding_notes.csv` - KYC onboarding notes
- `partner_role.csv` - Partner-entity relationships
- `business_rel.csv` - Business relationships
- `br_to_account.csv` - Business relationship to account mapping
- `account.csv` - Account information
- `partner_country.csv` - Partner country data

---

## 🧪 Testing

Run the test script to verify the entire pipeline:

```bash
python test_fraud_detection.py
```

This will test:
1. ✅ Profile Agent (data extraction)
2. ✅ LLaMA Connection
3. ✅ Fraud Agent (full pipeline)
4. ✅ Backend API (if running)

---

## 📝 What We Did

### Session Summary

1. **Project Analysis**
   - Analyzed the fraud detection system architecture
   - Documented all components and their interactions
   - Identified data flow from CSV files → Profile Agent → LLM → Risk Assessment

2. **Code Review**
   - Reviewed `ai_service_level` components
   - Understood UCP (Unified Customer Profile) system
   - Analyzed Enhanced Fraud Agent with explainable AI features

3. **File Cleanup Analysis**
   - Identified unused/duplicate files:
     - `backend/app1.py` (old backup)
     - `ai_service_level/__init__1.py` (old version)
     - `ai_service_level/hello.py` (test script)
     - `ai_service_level/notebooks/model.ipynb` (empty)
   - Provided cleanup recommendations

4. **Git Setup Instructions**
   - Provided instructions for git workflow
   - Explained how to exclude model folder from git
   - Documented recovery process for deleted files

5. **Documentation**
   - Created comprehensive README.md
   - Documented API endpoints
   - Provided setup and running instructions

---

## 🔒 Security & Compliance

- **FINMA Compliance**: System designed for Swiss banking regulations
- **Data Privacy**: Customer data processed locally
- **Explainable AI**: All risk assessments include detailed rationales
- **Audit Trail**: Risk metadata stored in UCP for compliance tracking

---

## 🚧 Future Enhancements

- [ ] OCR Processor implementation for document processing
- [ ] Multimodal support (image analysis)
- [ ] Real-time transaction monitoring
- [ ] Advanced anomaly detection
- [ ] Integration with external KYC services
- [ ] Dashboard UI for compliance officers

---

## 📚 Technical Stack

- **Backend**: Flask (Python)
- **LLM**: LLaMA 20B (GPT-OSS-20B) via llama.cpp
- **Data Processing**: Pandas
- **API**: RESTful JSON API
- **Data Storage**: CSV files (can be migrated to database)

---

## 👥 Usage Example

```python
from ai_service_level.fraud_agent import FraudAgent

# Initialize agent
agent = FraudAgent(data_dir="data", llama_url="http://127.0.0.1:8080")

# Assess risk for a customer
result = agent.assess_risk("96a660ff-08e0-49c1-be6d-bb22a84e742e")

print(f"Risk Score: {result['risk_score']}/100")
print(f"Rationale: {result['rationale']}")
```

---

## 📄 License

[Add your license information here]

---

## 🤝 Contributing

[Add contribution guidelines if applicable]

---

## 📧 Contact

[Add contact information if needed]

---

**Last Updated**: 2024

