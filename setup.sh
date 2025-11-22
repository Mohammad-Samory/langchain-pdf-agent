#!/bin/bash
# Setup script for Linux/Mac

echo "🚀 Setting up PDF Q&A Agent..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your OPENAI_API_KEY"
    exit 1
fi

# Check if OpenAI key is set
if grep -q "your-openai-api-key-here" .env; then
    echo "⚠️  Please add your OPENAI_API_KEY to .env file"
    exit 1
fi

# Check if Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Prerequisites checked"
echo "🔨 Building Docker image..."

docker-compose build pdf-agent

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo ""
    echo "🚀 To start the service, run:"
    echo "   docker-compose up pdf-agent"
    echo ""
    echo "📚 Or run in background:"
    echo "   docker-compose up -d pdf-agent"
    echo ""
    echo "📖 Then visit: http://localhost:8200/docs"
else
    echo "❌ Build failed. Check the error messages above."
    exit 1
fi
