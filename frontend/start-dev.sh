#!/bin/bash

# Mini-Me Frontend Development Startup Script

echo "🚀 Starting Mini-Me Frontend..."
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "⚠️  Warning: .env.local not found!"
    echo "📝 Creating from .env.local.example..."
    cp .env.local.example .env.local
    echo "✅ Created .env.local - please verify the values"
    echo ""
fi

# Check if API is running
echo "🔍 Checking if backend API is running..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API is running"
else
    echo "❌ Backend API not detected at http://localhost:8000"
    echo "   Please start the API first:"
    echo "   cd ../api && uvicorn app.main:app --reload"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "✨ Starting Next.js development server..."
echo "🌐 Frontend will be available at: http://localhost:3000"
echo "🔐 Firebase auth configured and ready"
echo ""
echo "Press Ctrl+C to stop"
echo ""

npm run dev
