#!/bin/bash

# Setup script for Ollama in Docker environment
# This script ensures the required model is available

set -e

echo "🚀 Setting up Ollama for Smart Kitchen Queue Management System..."

# Wait for Ollama service to be ready
echo "⏳ Waiting for Ollama service to be ready..."
until curl -f http://ollama:11434/api/tags >/dev/null 2>&1; do
    echo "Waiting for Ollama service..."
    sleep 5
done

echo "✅ Ollama service is ready!"

# Check if the model is already available
MODEL_NAME="llama3.1:8b"
echo "🔍 Checking if model $MODEL_NAME is available..."

if curl -s http://ollama:11434/api/tags | grep -q "$MODEL_NAME"; then
    echo "✅ Model $MODEL_NAME is already available!"
else
    echo "📥 Downloading model $MODEL_NAME..."
    echo "⚠️  This may take several minutes depending on your internet connection..."
    
    # Pull the model
    curl -X POST http://ollama:11434/api/pull \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"$MODEL_NAME\"}" \
        --max-time 1800  # 30 minutes timeout
    
    echo "✅ Model $MODEL_NAME downloaded successfully!"
fi

# Verify the model is working
echo "🧪 Testing model functionality..."
curl -X POST http://ollama:11434/api/generate \
    -H "Content-Type: application/json" \
    -d '{
        "model": "'$MODEL_NAME'",
        "prompt": "Hello, this is a test. Please respond with just: Model is working correctly.",
        "stream": false
    }' \
    --max-time 60

echo ""
echo "🎉 Ollama setup completed successfully!"
echo "📋 Available models:"
curl -s http://ollama:11434/api/tags | jq '.models[].name' 2>/dev/null || echo "Could not list models (jq not available)"
