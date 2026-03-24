#!/bin/bash

# AI Tutor - Quick Start Script
# This script sets up and runs the AI Tutor application

set -e

echo "🚀 AI Tutor Quick Start"
echo "======================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "\n${BLUE}Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi
echo "✓ Python found"

if ! command -v npm &> /dev/null; then
    echo "❌ Node.js/npm not found. Please install Node.js 18+"
    exit 1
fi
echo "✓ Node.js found"

if ! command -v psql &> /dev/null; then
    echo "⚠ PostgreSQL not found. You may need to set up the database manually."
else
    echo "✓ PostgreSQL found"
fi

# Backend Setup
echo -e "\n${BLUE}Setting up backend...${NC}"
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate || . venv/Scripts/activate

echo "Installing dependencies..."
pip install -q -r requirements.txt

# Setup environment
if [ ! -f ".env" ]; then
    echo "Setting up .env file..."
    cp .env.example .env
    echo "⚠ Please edit .env with your configuration (especially OPENAI_API_KEY)"
    read -p "Press enter once you've updated .env..."
fi

echo "Initializing database..."
# Skip database init for now - using simple version
echo "⚠ Skipping database initialization (using simple version)"

echo -e "${GREEN}✓ Backend setup complete${NC}"

# Frontend Setup
echo -e "\n${BLUE}Setting up frontend...${NC}"
cd ../frontend

echo "Installing dependencies..."
npm install -q

echo -e "${GREEN}✓ Frontend setup complete${NC}"

echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "\n${BLUE}To start the application:${NC}"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend"
echo "  source venv/bin/activate  # or . venv/Scripts/activate on Windows"
echo "  uvicorn simple_main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then open http://localhost:3000 in your browser"
echo ""
echo -e "${BLUE}Demo Credentials:${NC}"
echo "Admin:   admin@example.com / adminpass123"
echo "Student: student@example.com / password123"
