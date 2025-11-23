#!/bin/bash
# Script to install all dependencies needed to build llama.cpp on RunPod
# Run this once when you first set up your RunPod instance

set -e  # Exit on error

echo "=========================================="
echo "Installing Dependencies for llama.cpp"
echo "=========================================="
echo ""

# Check disk space first
echo "💾 Checking disk space..."
df -h /
AVAILABLE_SPACE=$(df / | tail -1 | awk '{print $4}')
echo "Available space: $AVAILABLE_SPACE"
echo ""

# Check if we have enough space (at least 5GB recommended)
if [ $(df / | tail -1 | awk '{print $4}' | sed 's/[^0-9]//g') -lt 5000000 ] 2>/dev/null; then
    echo "⚠️  Warning: Low disk space detected!"
    echo "   You may need to free up space before continuing."
    echo ""
    echo "   Try cleaning up:"
    echo "   - sudo apt-get clean"
    echo "   - sudo rm -rf /var/lib/apt/lists/*"
    echo "   - Check for large files: du -sh ~/* | sort -h"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Clean apt cache to free up space
echo "🧹 Cleaning apt cache to free up space..."
sudo apt-get clean 2>/dev/null || true
sudo rm -rf /var/lib/apt/lists/partial/* 2>/dev/null || true

# Update package list
echo "📦 Updating package list..."
sudo apt-get update || {
    echo ""
    echo "❌ Error: Failed to update package list (likely no space left on device)"
    echo ""
    echo "🔧 Try these steps to free up space:"
    echo "   1. Clean apt cache: sudo apt-get clean"
    echo "   2. Remove old package lists: sudo rm -rf /var/lib/apt/lists/*"
    echo "   3. Check disk usage: df -h"
    echo "   4. Find large files: du -sh ~/* | sort -h | tail -10"
    echo "   5. Remove old logs: sudo journalctl --vacuum-time=1d"
    echo ""
    exit 1
}

# Install Git
echo ""
echo "📦 Installing Git..."
sudo apt-get install -y git

# Install CMake (need version ≥ 3.21)
echo ""
echo "📦 Installing CMake..."
sudo apt-get install -y cmake

# Verify CMake version
CMAKE_VERSION=$(cmake --version | head -n1 | cut -d' ' -f3)
echo "✓ CMake version: $CMAKE_VERSION"

# Install C/C++ toolchain (build-essential includes gcc, g++, make, etc.)
echo ""
echo "📦 Installing C/C++ toolchain (build-essential)..."
sudo apt-get install -y build-essential

# Install CUDA toolkit and cuBLAS (for GPU support)
echo ""
echo "📦 Installing CUDA toolkit and cuBLAS..."
echo "Note: This may take a while..."

# Check if CUDA is already installed
if command -v nvcc &> /dev/null; then
    echo "✓ CUDA already installed: $(nvcc --version | grep release)"
else
    # Install CUDA toolkit
    # Note: RunPod instances usually come with CUDA pre-installed
    # But we'll install the development tools if needed
    sudo apt-get install -y nvidia-cuda-toolkit
    
    # Install cuBLAS (usually comes with CUDA toolkit)
    sudo apt-get install -y libcublas-dev
fi

# Verify CUDA installation
if command -v nvcc &> /dev/null; then
    echo "✓ CUDA installed: $(nvcc --version | grep release)"
else
    echo "⚠ Warning: CUDA not found. GPU acceleration may not work."
    echo "  You can still build with CPU-only support."
fi

# Install Python 3.9+ and pip
echo ""
echo "📦 Installing Python 3.9+ and pip..."
sudo apt-get install -y python3 python3-pip

# Verify Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Python version: $PYTHON_VERSION"

# Install Python requests library
echo ""
echo "📦 Installing Python requests library..."
pip3 install requests

# Install additional useful tools
echo ""
echo "📦 Installing additional tools (screen, wget)..."
sudo apt-get install -y screen wget

# Verify installations
echo ""
echo "=========================================="
echo "Verification"
echo "=========================================="
echo "Git: $(git --version)"
echo "CMake: $(cmake --version | head -n1)"
echo "GCC: $(gcc --version | head -n1)"
echo "Python: $(python3 --version)"
echo ""

if command -v nvcc &> /dev/null; then
    echo "CUDA: $(nvcc --version | grep release)"
    echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader | head -n1)"
else
    echo "CUDA: Not installed (CPU-only mode)"
fi

echo ""
echo "=========================================="
echo "✅ All dependencies installed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Clone llama.cpp: git clone https://github.com/ggml-org/llama.cpp"
echo "2. Build llama.cpp: cd llama.cpp && cmake -S . -B build -DGGML_CUDA=ON && cmake --build build -j"
echo "3. Download the model: wget https://huggingface.co/ggml-org/gpt-oss-20b-GGUF/resolve/main/gpt-oss-20b-mxfp4.gguf"
echo "4. Start the server: Use start_llama_server.sh or run manually"
echo ""

