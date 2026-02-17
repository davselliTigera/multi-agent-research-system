#!/bin/bash
# Deploy A2A Protocol version to kubeadm cluster with Azure Container Registry

set -e

echo "🚀 Deploying Multi-Agent Research System (A2A Protocol)"
echo ""

# Configuration
REGISTRY="davidepoc.azurecr.io/multi-agent-research"
TAG="a2a-$(date +%Y%m%d-%H%M%S)"

echo "📦 Using kubeadm cluster with Azure Container Registry"
echo "🔧 Registry: $REGISTRY"
echo "🔧 Protocol: A2A v1.0"

# Check API key
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ Error: GOOGLE_API_KEY environment variable not set"
    echo "Run: export GOOGLE_API_KEY='your-api-key'"
    exit 1
fi

# Check Azure Container Registry credentials
if [ -z "$ACR_USERNAME" ] || [ -z "$ACR_PASSWORD" ]; then
    echo "⚠️  Warning: ACR_USERNAME or ACR_PASSWORD not set"
    echo "If your Azure Container Registry requires authentication, set these variables:"
    echo "  export ACR_USERNAME='your-acr-username'"
    echo "  export ACR_PASSWORD='your-acr-password'"
    echo ""
    echo "For Azure CLI users, you can get credentials with:"
    echo "  az acr credential show --name davidepoc"
    echo ""
    read -p "Continue without ACR credentials? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "🔐 ACR credentials found"
    # Login to Azure Container Registry
    echo "🔑 Logging into Azure Container Registry..."
    echo "$ACR_PASSWORD" | sudo docker login davidepoc.azurecr.io -u "$ACR_USERNAME" --password-stdin
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
echo "🔐 Creating Google API key secret..."
kubectl create secret generic google-api-secret \
  --from-literal=api-key="${GOOGLE_API_KEY}" \
  --dry-run=client -o yaml | kubectl apply -f -

# Create ACR image pull secret if credentials are provided
if [ -n "$ACR_USERNAME" ] && [ -n "$ACR_PASSWORD" ]; then
    echo "🔐 Creating Azure Container Registry pull secret..."
    kubectl create secret docker-registry acr-secret \
      --docker-server=davidepoc.azurecr.io \
      --docker-username="$ACR_USERNAME" \
      --docker-password="$ACR_PASSWORD" \
      --dry-run=client -o yaml | kubectl apply -f -
    echo "✅ ACR pull secret created"
else
    echo "⚠️  Skipping ACR pull secret creation (no credentials provided)"
fi

# Build all images
echo ""
echo "🏗️  Building Docker images (A2A Protocol)..."
echo ""

docker buildx inspect --bootstrap

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
  sudo docker buildx build \
    --platform linux/amd64 \
    --build-arg SERVICE_FILE=${file} \
    --build-arg PORT=${port} \
    -f docker/Dockerfile.agent \
    -t ${REGISTRY}/${name}:${TAG} \
    --push \
    --no-cache \
    --quiet .
done

# Build A2A coordinator
echo "Building coordinator (A2A)..."
sudo docker buildx build \
  --platform linux/amd64 \
  --build-arg COORDINATOR_FILE=coordinator/coordinator_a2a.py \
  -f docker/Dockerfile.coordinator-a2a \
  -t ${REGISTRY}/coordinator:${TAG} \
  --push \
  --no-cache \
  --quiet .

# Build Streamlit frontend (same for both)
echo "Building streamlit..."
sudo docker buildx build -f docker/Dockerfile.streamlit --platform linux/amd64 -t ${REGISTRY}/streamlit:${TAG} --push --no-cache --quiet .

echo "✅ All images built and pushed to Azure Container Registry"
echo ""
echo "☸️  Deploying to Kubernetes (A2A version)..."

# Check if we need to patch deployments with imagePullSecrets
if [ -n "$ACR_USERNAME" ] && [ -n "$ACR_PASSWORD" ]; then
    echo "📝 Note: Deployments will need imagePullSecrets for ACR"
    echo "   Make sure your deployments-a2a.yaml includes:"
    echo "   imagePullSecrets:"
    echo "   - name: acr-secret"
fi

# Deploy to Kubernetes (use A2A manifests)
kubectl apply -f kubernetes/deployments-a2a-azure.yaml

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
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Pod Status:"
kubectl get pods
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
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
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 To access the application:"
echo ""
echo "  kubectl port-forward service/streamlit-service 8501:80"
echo ""
echo "Then open: http://localhost:8501"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
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
echo "  # View all images in Azure Container Registry"
echo "  az acr repository list --name davidepoc --output table"
echo ""
echo "  # Check image pull issues"
echo "  kubectl describe pod <pod-name> | grep -A5 'Events:'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"