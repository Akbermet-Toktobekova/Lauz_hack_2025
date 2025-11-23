#!/bin/bash
# Script to start llama.cpp server on RunPod
# Based on GPT-OSS + llama.cpp Onboarding Guide
# Make this executable: chmod +x start_llama_server.sh

# Configuration
MODEL_PATH="/path/to/gpt-oss-20b-mxfp4.gguf"  # Update this path
PORT=8080
HOST="0.0.0.0"  # Important: Use 0.0.0.0 to make it accessible from outside (not 127.0.0.1)
NGL=99  # Offload as many layers as possible to GPU (reduce if limited VRAM)

# Check if model file exists
if [ ! -f "$MODEL_PATH" ]; then
    echo "Error: Model file not found at $MODEL_PATH"
    echo "Please update MODEL_PATH in this script"
    exit 1
fi

# Check if llama-server exists (try both common locations)
LLAMA_SERVER="./build/bin/llama-server"
if [ ! -f "$LLAMA_SERVER" ]; then
    LLAMA_SERVER="./llama-server"
    if [ ! -f "$LLAMA_SERVER" ]; then
        echo "Error: llama-server not found"
        echo "Expected locations: ./build/bin/llama-server or ./llama-server"
        echo "Make sure you're in the llama.cpp directory and have built the project"
        exit 1
    fi
fi

echo "Starting llama.cpp server..."
echo "Model: $MODEL_PATH"
echo "Port: $PORT"
echo "Host: $HOST"
echo "GPU Layers: $NGL"
echo ""
echo "Server will be accessible at: http://<your-runpod-ip>:$PORT"
echo "OpenAI-compatible API: http://<your-runpod-ip>:$PORT/v1/chat/completions"
echo ""

# Start the server with GPU offloading
# -ngl 99 tells llama.cpp to offload as many layers as possible to the GPU
# Lower this number if you have limited VRAM, or drop it entirely for CPU-only runs
$LLAMA_SERVER \
    -m "$MODEL_PATH" \
    -ngl $NGL \
    --host $HOST \
    --port $PORT

