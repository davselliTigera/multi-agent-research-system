#!/bin/bash
# Build and deploy multi-agent research system to Kubernetes

set -e

echo "🚀 Building Multi-Agent Research System"

# Configuration
REGISTRY=${DOCKER_REGISTRY:-"multi-agent-research"}
TAG=${IMAGE_TAG:-"latest"}
KIND_CLUSTER=${KIND_CLUSTER:-"kind"}

# Detect cluster type
CLUSTER_TYPE="unknown"
if kubectl config current-context | grep -q "kind"; then
    CLUSTER_TYPE="kind"
    echo "📦 Detected Kind cluster"
elif kubectl config current-context | grep -q "minikube"; then
    CLUSTER_TYPE="minikube"
    echo "📦 Detected Minikube cluster"
else
    CLUSTER_TYPE="cloud"
    echo "☁️  Detected cloud/remote cluster"
fi

# Create Google API key secret
echo "📝 Creating Google API key secret..."
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ Error: GOOGLE_API_KEY environment variable not set"
    echo "Run: export GOOGLE_API_KEY='your-api-key'"
    exit 1
fi

kubectl create secret generic google-api-secret \
  --from-literal=api-key="${GOOGLE_API_KEY}" \
  --dry-run=client -o yaml | kubectl apply -f -

# Build base agent image
echo "🏗️  Building base agent image..."
docker build -f docker/Dockerfile.agent -t ${REGISTRY}/base-agent:${TAG} .

# Build each agent service
services=(
  "agents/topic_refiner_service.py:topic-refiner:8001"
  "agents/question_architect_service.py:question-architect:8002"
  "agents/search_strategist_service.py:search-strategist:8003"
  "agents/data_analyst_service.py:data-analyst:8004"
  "agents/report_writer_service.py:report-writer:8005"
)

images_to_load=()

for service in "${services[@]}"; do
  IFS=':' read -r file name port <<< "$service"
  echo "🏗️  Building ${name}..."
  docker build \
    --build-arg SERVICE_FILE=${file} \
    --build-arg PORT=${port} \
    -f docker/Dockerfile.agent \
    -t ${REGISTRY}/${name}:${TAG} .
  
  images_to_load+=("${REGISTRY}/${name}:${TAG}")
done

# Build coordinator
echo "🏗️  Building coordinator..."
docker build -f docker/Dockerfile.coordinator -t ${REGISTRY}/coordinator:${TAG} .
images_to_load+=("${REGISTRY}/coordinator:${TAG}")

# Build Streamlit frontend
echo "🏗️  Building Streamlit frontend..."
docker build -f docker/Dockerfile.streamlit -t ${REGISTRY}/streamlit:${TAG} .
images_to_load+=("${REGISTRY}/streamlit:${TAG}")

# Load images into cluster based on type
if [ "$CLUSTER_TYPE" = "kind" ]; then
    echo "📦 Loading images into Kind cluster..."
    for image in "${images_to_load[@]}"; do
        echo "  Loading: $image"
        kind load docker-image "$image" --name "$KIND_CLUSTER"
    done
elif [ "$CLUSTER_TYPE" = "minikube" ]; then
    echo "📦 Loading images into Minikube..."
    # For minikube, we can use the docker daemon inside minikube
    echo "  Using minikube docker daemon (images already available)"
    eval $(minikube docker-env)
else
    echo "☁️  Pushing images to registry..."
    for image in "${images_to_load[@]}"; do
        echo "  Pushing: $image"
        docker push "$image"
    done
fi

# Deploy to Kubernetes
echo "☸️  Deploying to Kubernetes..."
kubectl apply -f kubernetes/deployments.yaml

# Wait for deployments
echo "⏳ Waiting for deployments..."
kubectl wait --for=condition=available --timeout=300s \
  deployment/redis \
  deployment/topic-refiner \
  deployment/question-architect \
  deployment/search-strategist \
  deployment/data-analyst \
  deployment/report-writer \
  deployment/coordinator \
  deployment/streamlit-frontend

# Get service URL
echo "✅ Deployment complete!"
echo ""
echo "📊 Service Status:"
kubectl get pods
echo ""
echo "🌐 Access the application:"

if [ "$CLUSTER_TYPE" = "kind" ]; then
    echo ""
    echo "Kind cluster detected. To access the application:"
    echo "  kubectl port-forward service/streamlit-service 8501:80"
    echo ""
    echo "Then open: http://localhost:8501"
elif [ "$CLUSTER_TYPE" = "minikube" ]; then
    echo ""
    echo "Minikube detected. To access the application:"
    echo "  minikube service streamlit-service"
else
    kubectl get service streamlit-service
    echo ""
    echo "Or port-forward: kubectl port-forward service/streamlit-service 8501:80"
fi
