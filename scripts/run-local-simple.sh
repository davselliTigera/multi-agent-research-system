#!/bin/bash
# run-local-simple.sh
# Simple script to run everything locally for testing

set -e

echo "🚀 Multi-Agent Research System - Local Development Mode"
echo ""

# Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 required"; exit 1; }
command -v redis-server >/dev/null 2>&1 || { echo "❌ Redis required. Install with: brew install redis (macOS) or apt install redis-server (Linux)"; exit 1; }

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "Starting Redis..."
    redis-server --daemonize yes
    sleep 2
fi

echo "✅ Redis is running"

# Create venv if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Verify we're in venv
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "✅ Virtual environment activated: $VIRTUAL_ENV"

# Install deps if needed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing dependencies (this may take a minute)..."
    pip install -q --upgrade pip
    pip install -q fastapi uvicorn langchain-google-genai redis httpx pydantic duckduckgo-search streamlit
    echo "✅ Dependencies installed"
fi

# Check for Google API key
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ Please set GOOGLE_API_KEY:"
    echo "   export GOOGLE_API_KEY='your-key-here'"
    exit 1
fi

echo "✅ Environment ready"
echo ""

# Export variables
export REDIS_HOST=localhost
export REDIS_PORT=6379
export COORDINATOR_URL=http://localhost:8006

# Create logs directory
mkdir -p logs

echo "Starting services..."
echo ""

# Start all services in background
# Get the project root directory
PROJECT_ROOT=$(pwd)
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH}"

echo "  Starting coordinator on port 8006..."
PYTHONPATH="${PROJECT_ROOT}" python coordinator/coordinator_a2a.py > logs/coordinator.log 2>&1 &
sleep 3

echo "  Starting topic-refiner on port 8001..."
PYTHONPATH="${PROJECT_ROOT}" python agents/topic_refiner_a2a.py > logs/topic-refiner.log 2>&1 &
sleep 1

echo "  Starting question-architect on port 8002..."
PYTHONPATH="${PROJECT_ROOT}" python agents/question_architect_a2a.py > logs/question-architect.log 2>&1 &
sleep 1

echo "  Starting search-strategist on port 8003..."
PYTHONPATH="${PROJECT_ROOT}" python agents/search_strategist_a2a.py > logs/search-strategist.log 2>&1 &
sleep 1

echo "  Starting data-analyst on port 8004..."
PYTHONPATH="${PROJECT_ROOT}" python agents/data_analyst_a2a.py > logs/data-analyst.log 2>&1 &
sleep 1

echo "  Starting report-writer on port 8005..."
PYTHONPATH="${PROJECT_ROOT}" python agents/report_writer_a2a.py > logs/report-writer.log 2>&1 &
sleep 2

echo ""
echo "Checking service health..."
for port in 8001 8002 8003 8004 8005 8006; do
    if curl -s http://localhost:$port/health > /dev/null 2>&1; then
        echo "  ✅ Port $port: OK"
    else
        echo "  ❌ Port $port: FAILED"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ All services running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 View logs:"
echo "   tail -f logs/coordinator.log"
echo "   tail -f logs/topic-refiner.log"
echo ""
echo "🧪 Test A2A communication:"
echo "   python scripts/test_a2a_local.py"
echo ""
echo "🌐 Start Streamlit UI:"
echo "   streamlit run frontend/streamlit_frontend.py"
echo ""
echo "🛑 Stop all services:"
echo "   pkill -f 'python.*_a2a.py' && pkill -f 'python.*coordinator'"
echo ""