# 🚀 Step-by-Step Instructions to Run and Test the Project

## Prerequisites Check

First, verify you have all dependencies installed:

```bash
cd /workspace
python3 -c "import flask, pandas, requests; print('✓ All dependencies installed')"
```

If you get an error, install dependencies:
```bash
pip install --ignore-installed flask flask-cors pandas requests
```

---

## Step 1: Verify Data Files

Check that all required data files exist:

```bash
cd /workspace
ls -la data/
```

You should see:
- `partner.csv`
- `transactions.csv`
- `client_onboarding_notes.csv`
- `partner_role.csv`
- `business_rel.csv`
- `br_to_account.csv`
- `account.csv`
- `partner_country.csv`

---

## Step 2: Start LLaMA Server (Required)

**Option A: If you have a model file ready**

```bash
cd /workspace/gpt-oss-20b/llama.cpp

# Build the server (if not already built)
cmake -B build
cmake --build build --config Release -t llama-server

# Start the server (replace MODEL_PATH with your actual model path)
./build/bin/llama-server \
    -m /path/to/your/model.gguf \
    --host 0.0.0.0 \
    --port 8080
```

**Option B: If you don't have a model yet**

The backend will still start but will show "degraded" status. You can test the API structure without the LLM.

**Keep this terminal open** - the server runs in the foreground.

---

## Step 3: Start the Backend API

Open a **new terminal** and run:

```bash
cd /workspace

# Set environment variables (optional - defaults are fine)
export LLAMA_SERVER_URL="http://127.0.0.1:8080"
export DATA_DIR="data"
export PORT=5001

# Start Flask backend
python3 backend/app.py
```

You should see output like:
```
 * Running on http://0.0.0.0:5001
 * Debug mode: on
```

**Keep this terminal open** - the Flask server runs in the foreground.

---

## Step 4: Test the System

Open a **third terminal** for testing.

### Test 4.1: Health Check (No LLM Required)

```bash
curl http://localhost:5001/health
```

**Expected Response:**
- If llama-server is running: `"status": "healthy"`
- If llama-server is NOT running: `"status": "degraded"`

### Test 4.2: Basic Risk Assessment (Requires LLM)

```bash
curl -X POST http://localhost:5001/api/assess-risk \
  -H "Content-Type: application/json" \
  -d '{"partner_id": "96a660ff-08e0-49c1-be6d-bb22a84e742e"}'
```

**Expected Response:**
```json
{
  "partner_id": "96a660ff-08e0-49c1-be6d-bb22a84e742e",
  "risk_score": 45,
  "rationale": "Explanation...",
  "raw_response": "...",
  "status": "success"
}
```

### Test 4.3: Enhanced Risk Assessment (Requires LLM)

```bash
curl -X POST http://localhost:5001/api/assess-risk-enhanced \
  -H "Content-Type: application/json" \
  -d '{"partner_id": "96a660ff-08e0-49c1-be6d-bb22a84e742e"}'
```

**Expected Response:**
```json
{
  "partner_id": "...",
  "risk_score": 45,
  "rationale": "Detailed explanation...",
  "feature_contributions": {...},
  "ucp": {...},
  "model_version": "llama-20b-v1.0",
  "timestamp": "...",
  "status": "success"
}
```

### Test 4.4: Get Profile (No LLM Required)

```bash
curl -X POST http://localhost:5001/api/profile \
  -H "Content-Type: application/json" \
  -d '{"partner_id": "96a660ff-080-49c1-be6d-bb22a84e742e"}'
```

### Test 4.5: Q&A Endpoint (Requires LLM)

```bash
curl -X POST http://localhost:5001/api/qa \
  -H "Content-Type: application/json" \
  -d '{
    "partner_id": "96a660ff-08e0-49c1-be6d-bb22a84e742e",
    "question": "What is the total spending for this customer in the last 30 days?"
  }'
```

---

## Step 5: Run Automated Test Script

The project includes a comprehensive test script:

```bash
cd /workspace
python3 test_fraud_detection.py
```

This will test:
1. ✅ Profile Agent (data extraction) - **Works without LLM**
2. ✅ LLaMA Connection - **Requires LLM**
3. ✅ Fraud Agent (full pipeline) - **Requires LLM**
4. ✅ Backend API - **Requires backend running**

---

## Quick Test Summary

### Minimal Test (No LLM Required)

```bash
# Terminal 1: Start backend
cd /workspace
python3 backend/app.py

# Terminal 2: Test health and profile endpoints
curl http://localhost:5001/health
curl -X POST http://localhost:5001/api/profile \
  -H "Content-Type: application/json" \
  -d '{"partner_id": "96a660ff-08e0-49c1-be6d-bb22a84e742e"}'
```

### Full Test (Requires LLM)

```bash
# Terminal 1: Start llama-server
cd /workspace/gpt-oss-20b/llama.cpp
./build/bin/llama-server -m /path/to/model.gguf --port 8080

# Terminal 2: Start backend
cd /workspace
python3 backend/app.py

# Terminal 3: Run full test
cd /workspace
python3 test_fraud_detection.py
```

---

## Troubleshooting

### Backend won't start
- Check if port 5001 is already in use: `lsof -i :5001`
- Change port: `export PORT=5002` then restart

### LLM endpoints return errors
- Verify llama-server is running: `curl http://localhost:8080/health`
- Check LLAMA_SERVER_URL matches your server: `echo $LLAMA_SERVER_URL`

### Import errors
- Make sure you're in `/workspace` directory
- Verify dependencies: `pip list | grep -E "flask|pandas|requests"`

### Data file errors
- Verify data directory exists: `ls -la data/`
- Check file permissions: `ls -l data/*.csv`

---

## Test Partner ID

The test partner ID used in examples:
```
96a660ff-08e0-49c1-be6d-bb22a84e742e
```

This partner exists in the sample data files.

---

## API Endpoints Summary

| Endpoint | Method | Requires LLM | Description |
|----------|--------|--------------|-------------|
| `/health` | GET | No | System health check |
| `/api/profile` | POST | No | Get customer profile data |
| `/api/assess-risk` | POST | Yes | Basic risk assessment |
| `/api/assess-risk-enhanced` | POST | Yes | Enhanced risk with UCP |
| `/api/qa` | POST | Yes | Conversational Q&A |

---

## Next Steps

Once everything is working:
1. Test with different partner IDs from your data
2. Integrate with frontend (if applicable)
3. Set up production deployment
4. Configure monitoring and logging

---

**Happy Testing! 🎉**

