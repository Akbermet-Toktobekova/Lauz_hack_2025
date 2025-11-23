# 🔧 Quick Fix: Risk Assessment Endpoint

## Current Status

✅ **Backend is running** on port 5001  
✅ **Profile endpoint works** (no LLM needed)  
❌ **Risk assessment requires llama-server** (not running)

## Error Explanation

The error you're seeing:
```
Connection refused: [Errno 111] Connection refused
```

This means the **llama-server is not running** on port 8080. The risk assessment endpoint needs the LLM to analyze the customer data.

---

## Solution: Start llama-server

### Step 1: Check if you have a model file

```bash
# Look for model files
find /workspace -name "*.gguf" -type f | grep -v vocab | head -5
```

If you have a model file, note its path. If not, you'll need to download one.

### Step 2: Start llama-server

**Option A: If you have a model file**

```bash
cd /workspace/gpt-oss-20b/llama.cpp

# Start the server (replace MODEL_PATH with your actual model path)
./build/bin/llama-server \
    -m /path/to/your/model.gguf \
    --host 0.0.0.0 \
    --port 8080
```

**Option B: CPU-only (slower but works without GPU)**

```bash
cd /workspace/gpt-oss-20b/llama.cpp

./build/bin/llama-server \
    -m /path/to/your/model.gguf \
    --host 0.0.0.0 \
    --port 8080 \
    -c 2048
```

**Option C: With GPU acceleration (if available)**

```bash
cd /workspace/gpt-oss-20b/llama.cpp

./build/bin/llama-server \
    -m /path/to/your/model.gguf \
    --host 0.0.0.0 \
    --port 8080 \
    -ngl 99 \
    -c 4096
```

### Step 3: Verify llama-server is running

In a new terminal:

```bash
curl http://localhost:8080/health
```

Or check if it's listening:

```bash
netstat -tuln | grep 8080
# or
lsof -i :8080
```

### Step 4: Test risk assessment again

Once llama-server is running:

```bash
curl -X POST http://localhost:5001/api/assess-risk \
  -H "Content-Type: application/json" \
  -d '{"partner_id": "96a660ff-08e0-49c1-be6d-bb22a84e742e"}'
```

---

## What Works Without LLM

These endpoints work **right now** without llama-server:

### 1. Health Check
```bash
curl http://localhost:5001/health
```

### 2. Get Profile
```bash
curl -X POST http://localhost:5001/api/profile \
  -H "Content-Type: application/json" \
  -d '{"partner_id": "96a660ff-08e0-49c1-be6d-bb22a84e742e"}'
```

---

## What Requires LLM

These endpoints need llama-server running:

- ❌ `/api/assess-risk` - Basic risk assessment
- ❌ `/api/assess-risk-enhanced` - Enhanced risk with UCP
- ❌ `/api/qa` - Conversational Q&A

---

## Quick Test Without Model

If you don't have a model file yet, you can still test the API structure:

```bash
# This will work (no LLM needed)
curl -X POST http://localhost:5001/api/profile \
  -H "Content-Type: application/json" \
  -d '{"partner_id": "96a660ff-08e0-49c1-be6d-bb22a84e742e"}'

# This will show the error (needs LLM)
curl -X POST http://localhost:5001/api/assess-risk \
  -H "Content-Type: application/json" \
  -d '{"partner_id": "96a660ff-08e0-49c1-be6d-bb22a84e742e"}'
```

---

## Troubleshooting

### llama-server won't start
- Check if port 8080 is in use: `lsof -i :8080`
- Verify model file exists: `ls -lh /path/to/model.gguf`
- Check file permissions: `chmod +x gpt-oss-20b/llama.cpp/build/bin/llama-server`

### Connection still refused after starting server
- Make sure you used `--host 0.0.0.0` (not `127.0.0.1`)
- Check firewall settings
- Verify backend is looking at correct URL: `echo $LLAMA_SERVER_URL`

### Model file not found
You need to download a compatible model. Common options:
- GPT-OSS-20B (recommended for this project)
- Llama 2/3 models
- Any compatible GGUF format model

---

## Summary

**Current Status:**
- ✅ Backend API: Running
- ✅ Profile endpoint: Working
- ❌ Risk assessment: Needs llama-server

**Next Step:**
Start llama-server with a model file, then retry the risk assessment endpoint.

