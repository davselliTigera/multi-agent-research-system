#!/bin/bash
# Setup script to create all necessary files for the multi-agent system

echo "📁 Setting up Multi-Agent Research System files..."

# Create requirements-agent.txt
cat > requirements-agent.txt << 'EOF'
fastapi==0.109.0
uvicorn[standard]==0.27.0
langchain-google-genai==1.0.10
redis==5.0.1
httpx==0.26.0
pydantic==2.5.3
duckduckgo-search==4.1.1
EOF

# Create requirements-coordinator.txt
cat > requirements-coordinator.txt << 'EOF'
fastapi==0.109.0
uvicorn[standard]==0.27.0
redis==5.0.1
httpx==0.26.0
pydantic==2.5.3
EOF

# Create requirements-streamlit.txt
cat > requirements-streamlit.txt << 'EOF'
streamlit==1.31.0
httpx==0.26.0
redis==5.0.1
pydantic==2.5.3
EOF

echo "✅ Requirements files created"

# Verify all Python files exist
required_files=(
    "shared_models.py"
    "base_agent.py"
    "topic_refiner_service.py"
    "question_architect_service.py"
    "search_strategist_service.py"
    "data_analyst_service.py"
    "report_writer_service.py"
    "coordinator_service.py"
    "streamlit_frontend.py"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo "⚠️  Missing Python files:"
    printf '%s\n' "${missing_files[@]}"
    echo ""
    echo "Please ensure all Python files from the artifacts are saved in the current directory."
    exit 1
fi

echo "✅ All Python files present"

# Verify Dockerfiles exist
if [ ! -f "Dockerfile.agent" ]; then
    echo "⚠️  Dockerfile.agent not found"
    exit 1
fi

if [ ! -f "Dockerfile.coordinator" ]; then
    echo "⚠️  Dockerfile.coordinator not found"
    exit 1
fi

if [ ! -f "Dockerfile.streamlit" ]; then
    echo "⚠️  Dockerfile.streamlit not found"
    exit 1
fi

echo "✅ All Dockerfiles present"

# Verify Kubernetes manifests
if [ ! -f "kubernetes-deployments.yaml" ]; then
    echo "⚠️  kubernetes-deployments.yaml not found"
    exit 1
fi

echo "✅ Kubernetes manifests present"

echo ""
echo "🎉 Setup complete! File structure:"
echo ""
ls -1 *.py *.txt Dockerfile.* *.yaml *.sh 2>/dev/null | grep -E '\.(py|txt|yaml|sh)$|^Dockerfile'

echo ""
echo "📋 Next steps:"
echo "1. Set your API key: export GOOGLE_API_KEY='your-key'"
echo "2. Make scripts executable: chmod +x *.sh"
echo "3. Run: ./build-and-deploy.sh"
