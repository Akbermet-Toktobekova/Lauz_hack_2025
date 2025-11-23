# AI Service Level - Complete Usage Analysis

## Overview
This document analyzes all files in `ai_service_level/` and their usage in `backend/app.py`.

---

## Files Used in app.py

### ✅ **Directly Imported & Used**

#### 1. **FraudAgent** (`fraud_agent.py`)
**Import:** `from ai_service_level.fraud_agent import FraudAgent`  
**Instantiation:** `fraud_agent = FraudAgent(data_dir=data_dir, llama_url=llama_url)`  
**Usage in app.py:**
- **Line 111:** `fraud_agent.assess_risk(partner_id)` - `/api/assess-risk` endpoint
- **Line 156:** `fraud_agent.profile_agent.get_profile_text(partner_id)` - `/api/profile` endpoint

**What it does:**
- Basic fraud risk assessment using LLM
- Uses ProfileAgent internally to get customer data
- Uses LlamaClient to call llama-server
- Returns risk score (0-100) and rationale

**Dependencies:**
- `ProfileAgent` (internal)
- `LlamaClient` (internal)

---

#### 2. **EnhancedFraudAgent** (`enhanced_fraud_agent.py`)
**Import:** `from ai_service_level.enhanced_fraud_agent import EnhancedFraudAgent`  
**Instantiation:** `enhanced_fraud_agent = EnhancedFraudAgent(data_dir=data_dir, llama_url=llama_url)`  
**Usage in app.py:**
- **Line 204:** `enhanced_fraud_agent.assess_risk(partner_id)` - `/api/assess-risk-enhanced` endpoint

**What it does:**
- Advanced fraud detection with explainable AI
- Uses UCP (Unified Customer Profile) for comprehensive analysis
- Provides feature contributions (XAI)
- Stores risk metadata back in UCP
- Returns detailed risk assessment with UCP data

**Dependencies:**
- `UCPBuilder` (internal)
- `UnifiedCustomerProfile` (internal)
- `LlamaClient` (internal)

---

#### 3. **RAGAgent** (`rag_agent.py`)
**Import:** `from ai_service_level.rag_agent import RAGAgent`  
**Instantiation:** `rag_agent = RAGAgent(data_dir=data_dir, llama_url=llama_url)`  
**Usage in app.py:**
- **Line 262:** `rag_agent.answer_query(partner_id, question)` - `/api/qa` endpoint

**What it does:**
- Conversational Q&A about customers
- Uses UCP to answer questions
- Extracts citations from customer data
- Provides factual answers based on profile data

**Dependencies:**
- `UCPBuilder` (internal)
- `UnifiedCustomerProfile` (internal)
- `LlamaClient` (internal)

---

## Indirectly Used (Dependencies)

### 4. **ProfileAgent** (`profile_agent.py`)
**Used by:** `FraudAgent` (internally)  
**How:**
- `FraudAgent` creates `ProfileAgent` in `__init__` (line 26)
- Used in `fraud_agent.assess_risk()` to get profile text (line 49)
- Also accessed directly: `fraud_agent.profile_agent.get_profile_text()` (app.py line 156)

**What it does:**
- Extracts customer data from CSV files
- Joins data across tables (partner → partner_role → business_rel → account → transactions)
- Formats into structured text profiles
- Returns: Identity, Onboarding Notes, Recent Transactions

**Dependencies:**
- Pandas (for CSV processing)
- No other ai_service_level dependencies

---

### 5. **LlamaClient** (`llama_client.py`)
**Used by:** `FraudAgent`, `EnhancedFraudAgent`, `RAGAgent`  
**How:**
- All three agents create `LlamaClient` in their `__init__` methods
- Used to make HTTP calls to llama-server API

**What it does:**
- Wraps OpenAI-compatible API calls to llama-server
- Makes POST requests to `/v1/chat/completions`
- Handles system/user messages
- Returns LLM response content

**Dependencies:**
- `requests` library
- No other ai_service_level dependencies

---

### 6. **UCPBuilder** (`ucp.py`)
**Used by:** `EnhancedFraudAgent`, `RAGAgent`  
**How:**
- Both agents create `UCPBuilder` in their `__init__` methods
- Used to build Unified Customer Profiles

**What it does:**
- Builds Unified Customer Profile (UCP) from raw CSV data
- Implements entity resolution
- Calculates financial aggregates (feature engineering)
- Extracts: Identity, Static Profile, Account Data, Transaction Aggregates

**Dependencies:**
- Pandas (for CSV processing)
- No other ai_service_level dependencies

---

### 7. **UnifiedCustomerProfile** (`ucp.py`)
**Used by:** `EnhancedFraudAgent`, `RAGAgent`  
**How:**
- Created by `UCPBuilder.build_ucp()`
- Used to store and format customer data

**What it does:**
- Central artifact that unifies all customer data
- Stores: Identity, Profile, Accounts, Financial Aggregates, Risk Metadata
- Provides `to_dict()` and `to_text()` methods for serialization

**Dependencies:**
- No external dependencies

---

## Files NOT Used in app.py

### ❌ **OCRProcessor** (`ocr_processor.py`)
**Status:** Not imported or used anywhere in app.py  
**Reason:** Placeholder for future multimodal support  
**What it would do:**
- Extract text from document images
- Process ID cards, passports, etc.
- Currently just a stub implementation

**Note:** This is exported in `__init__.py` but not actually used in the application.

---

## Dependency Graph

```
app.py
│
├── FraudAgent
│   ├── ProfileAgent (data extraction)
│   └── LlamaClient (LLM API calls)
│
├── EnhancedFraudAgent
│   ├── UCPBuilder (builds UCP)
│   │   └── UnifiedCustomerProfile (data structure)
│   └── LlamaClient (LLM API calls)
│
└── RAGAgent
    ├── UCPBuilder (builds UCP)
    │   └── UnifiedCustomerProfile (data structure)
    └── LlamaClient (LLM API calls)
```

---

## API Endpoint Mapping

| Endpoint | Agent Used | Method Called | Returns |
|----------|-----------|---------------|---------|
| `POST /api/assess-risk` | `FraudAgent` | `assess_risk(partner_id)` | Risk score, rationale, raw response |
| `POST /api/profile` | `FraudAgent` | `profile_agent.get_profile_text(partner_id)` | Profile text |
| `POST /api/assess-risk-enhanced` | `EnhancedFraudAgent` | `assess_risk(partner_id)` | Risk score, rationale, UCP, feature contributions |
| `POST /api/qa` | `RAGAgent` | `answer_query(partner_id, question)` | Answer, citations, UCP snapshot |

---

## Data Flow Summary

### Basic Risk Assessment (`/api/assess-risk`)
```
Partner ID
  ↓
FraudAgent.assess_risk()
  ↓
ProfileAgent.get_profile_text() → CSV data → Formatted text
  ↓
LlamaClient.generate() → llama-server → LLM response
  ↓
Parse response → Extract risk_score & rationale
  ↓
Return JSON
```

### Enhanced Risk Assessment (`/api/assess-risk-enhanced`)
```
Partner ID
  ↓
EnhancedFraudAgent.assess_risk()
  ↓
UCPBuilder.build_ucp() → CSV data → UnifiedCustomerProfile
  ↓
Calculate financial aggregates (feature engineering)
  ↓
LlamaClient.generate() → llama-server → LLM response
  ↓
Extract feature contributions (XAI)
  ↓
Store risk metadata in UCP
  ↓
Return JSON with UCP, feature contributions, etc.
```

### Q&A Endpoint (`/api/qa`)
```
Partner ID + Question
  ↓
RAGAgent.answer_query()
  ↓
UCPBuilder.build_ucp() → CSV data → UnifiedCustomerProfile
  ↓
Create RAG prompt with UCP context
  ↓
LlamaClient.generate() → llama-server → LLM response
  ↓
Extract citations from UCP
  ↓
Return JSON with answer, citations, UCP snapshot
```

---

## Key Differences

### FraudAgent vs EnhancedFraudAgent

| Feature | FraudAgent | EnhancedFraudAgent |
|---------|-----------|-------------------|
| **Data Source** | ProfileAgent (simple text) | UCP (structured profile) |
| **Features** | Basic risk score | Financial aggregates, feature contributions |
| **Output** | Risk score + rationale | Risk score + rationale + UCP + XAI |
| **Complexity** | Simple | Advanced |
| **Use Case** | Quick risk check | Detailed analysis with explainability |

### ProfileAgent vs UCPBuilder

| Feature | ProfileAgent | UCPBuilder |
|---------|-------------|-------------|
| **Output Format** | Text string | Structured object (UCP) |
| **Data Included** | Identity, notes, last 3 transactions | Identity, profile, accounts, aggregates, all transactions |
| **Feature Engineering** | None | Financial aggregates, velocity, etc. |
| **Used By** | FraudAgent | EnhancedFraudAgent, RAGAgent |

---

## Summary

**Total Files in ai_service_level:** 8
- ✅ **Used in app.py:** 6 files (FraudAgent, EnhancedFraudAgent, RAGAgent, ProfileAgent, LlamaClient, UCP/UCPBuilder)
- ❌ **Not used:** 1 file (OCRProcessor - placeholder)
- 📦 **Package init:** 1 file (__init__.py)

**All core functionality is actively used in the backend API!**

