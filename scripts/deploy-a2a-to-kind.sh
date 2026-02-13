#!/bin/bash
# Deploy A2A Protocol version to Kind cluster

set -e

echo "🚀 Deploying Multi-Agent Research System (A2A Protocol)"
echo ""

# Configuration
REGISTRY="multi-agent-research"
TAG="a2a-latest"
KIND_CLUSTER=${KIND_CLUSTER:-$(kind get clusters | head -n 1)}

if [ -z "$KIND_CLUSTER" ]; then
    echo "❌ No Kind cluster found!"
    echo "Create one with: kind create cluster --name research-cluster"
    exit 1
fi

echo "📦 Using Kind cluster: $KIND_CLUSTER"
echo "🔧 Protocol: A2A v1.0"

# Check API key
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ Error: GOOGLE_API_KEY environment variable not set"
    echo "Run: export GOOGLE_API_KEY='your-api-key'"
    exit 1
fi

# Create requirements files if they don't exist
if [ ! -f "requirements/requirements-agent.txt" ]; then
    echo "📝 Creating requirements files..."
    ./scripts/create-requirements.sh 2>/dev/null || {
        mkdir -p requirements
        cat > requirements/requirements-agent.txt << 'EOF'
fastapi==0.109.0
uvicorn[standard]==0.27.0
langchain-google-genai==1.0.10
redis==5.0.1
httpx==0.26.0
pydantic==2.5.3
duckduckgo-search==4.1.1
EOF
        cat > requirements/requirements-coordinator.txt << 'EOF'
fastapi==0.109.0
uvicorn[standard]==0.27.0
redis==5.0.1
httpx==0.26.0
pydantic==2.5.3
EOF
        cat > requirements/requirements-streamlit.txt << 'EOF'
streamlit==1.31.0
httpx==0.26.0
redis==5.0.1
pydantic==2.5.3
EOF
    }
fi

# Create API key secret
echo "📝 Creating Google API key secret..."
kubectl create secret generic google-api-secret \
  --from-literal=api-key="${GOOGLE_API_KEY}" \
  --dry-run=client -o yaml | kubectl apply -f -

# Build all images
echo ""
echo "🏗️  Building Docker images (A2A Protocol)..."
echo ""

# A2A Agent services (using a2a versions)
services=(
  "agents/topic_refiner_a2a.py:topic-refiner:8001"
  "agents/question_architect_a2a.py:question-architect:8002"
  "agents/search_strategist_a2a.py:search-strategist:8003"
  "agents/data_analyst_a2a.py:data-analyst:8004"
  "agents/report_writer_a2a.py:report-writer:8005"
)

for service in "${services[@]}"; do
  IFS=':' read -r file name port <<< "$service"
  echo "Building ${name} (A2A)..."
  docker build \
    --build-arg SERVICE_FILE=${file} \
    --build-arg PORT=${port} \
    -f docker/Dockerfile.agent \
    -t ${REGISTRY}/${name}:${TAG} \
    --quiet .
done

# Build A2A coordinator
echo "Building coordinator (A2A)..."
docker build \
  --build-arg COORDINATOR_FILE=coordinator/coordinator_a2a.py \
  -f docker/Dockerfile.coordinator-a2a \
  -t ${REGISTRY}/coordinator:${TAG} \
  --quiet .

# Build Streamlit frontend (same for both)
echo "Building streamlit..."
docker build -f docker/Dockerfile.streamlit -t ${REGISTRY}/streamlit:${TAG} --quiet .

echo "✅ All images built"
echo ""
echo "📦 Loading images into Kind cluster..."
echo ""

# Load all images into Kind
images=(
  "${REGISTRY}/topic-refiner:${TAG}"
  "${REGISTRY}/question-architect:${TAG}"
  "${REGISTRY}/search-strategist:${TAG}"
  "${REGISTRY}/data-analyst:${TAG}"
  "${REGISTRY}/report-writer:${TAG}"
  "${REGISTRY}/coordinator:${TAG}"
  "${REGISTRY}/streamlit:${TAG}"
)

for image in "${images[@]}"; do
  echo "Loading: $image"
  kind load docker-image "$image" --name "$KIND_CLUSTER"
done

echo "✅ All images loaded into Kind"
echo ""
echo "☸️  Deploying to Kubernetes (A2A version)..."

# Deploy to Kubernetes (use A2A manifests)
kubectl apply -f kubernetes/deployments-a2a.yaml

echo ""
echo "⏳ Waiting for deployments to be ready..."
echo ""

# Wait for each deployment
deployments=(
  "redis"
  "topic-refiner"
  "question-architect"
  "search-strategist"
  "data-analyst"
  "report-writer"
  "coordinator"
  "streamlit-frontend"
)

for deployment in "${deployments[@]}"; do
  echo "  Waiting for $deployment..."
  kubectl wait --for=condition=available --timeout=120s deployment/$deployment 2>/dev/null || {
    echo "  ⚠️  $deployment taking longer than expected, continuing..."
  }
done

echo ""
echo "✅ Deployment complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Pod Status:"
kubectl get pods
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎯 A2A Protocol Endpoints:"
echo ""
echo "  Coordinator:  http://coordinator-service:8006"
echo "  - List agents:     GET  /agents"
echo "  - Start research:  POST /start_research"
echo "  - Task status:     GET  /task/{id}"
echo ""
echo "  Agent Capabilities (any agent):"
echo "  - GET http://topic-refiner-service:8001/capabilities"
echo "  - GET http://question-architect-service:8002/capabilities"
echo ""
echo "  A2A Messages:"
echo "  - POST http://<agent-service>:800x/message"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 To access the application:"
echo ""
echo "  kubectl port-forward service/streamlit-service 8501:80"
echo ""
echo "Then open: http://localhost:8501"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Useful commands:"
echo ""
echo "  # View coordinator logs (A2A messages)"
echo "  kubectl logs -f deployment/coordinator"
echo ""
echo "  # Check agent capabilities"
echo "  kubectl port-forward service/topic-refiner-service 8001:8001"
echo "  curl http://localhost:8001/capabilities | jq"
echo ""
echo "  # Test A2A message"
echo "  curl -X POST http://localhost:8001/message -d @test-a2a-message.json"
echo ""
echo "  # Switch back to REST API version"
echo "  ./scripts/cleanup.sh && ./scripts/deploy-to-kind.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
