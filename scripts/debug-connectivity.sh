#!/bin/bash
# Debug connectivity issues in the multi-agent system

echo "🔍 Multi-Agent System Connectivity Debug"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check all pods
echo "📊 Pod Status:"
kubectl get pods
echo ""

# Check services
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Service Status:"
kubectl get services
echo ""

# Check coordinator specifically
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎭 Coordinator Health:"
COORDINATOR_POD=$(kubectl get pods -l app=coordinator -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -z "$COORDINATOR_POD" ]; then
    echo "❌ No coordinator pod found!"
    echo ""
    echo "Try: kubectl get pods | grep coordinator"
else
    echo "✅ Coordinator pod: $COORDINATOR_POD"
    
    # Check if pod is ready
    POD_STATUS=$(kubectl get pod $COORDINATOR_POD -o jsonpath='{.status.phase}')
    echo "   Status: $POD_STATUS"
    
    if [ "$POD_STATUS" != "Running" ]; then
        echo ""
        echo "⚠️  Pod is not running. Checking events:"
        kubectl describe pod $COORDINATOR_POD | tail -20
    else
        # Try to curl health endpoint
        echo ""
        echo "Testing coordinator health endpoint..."
        kubectl exec $COORDINATOR_POD -- curl -s http://localhost:8006/health || {
            echo "❌ Health check failed"
            echo ""
            echo "Coordinator logs:"
            kubectl logs $COORDINATOR_POD --tail=30
        }
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Streamlit Frontend:"
STREAMLIT_POD=$(kubectl get pods -l app=streamlit-frontend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -z "$STREAMLIT_POD" ]; then
    echo "❌ No streamlit pod found!"
else
    echo "✅ Streamlit pod: $STREAMLIT_POD"
    
    # Check COORDINATOR_URL env var
    echo ""
    echo "Checking COORDINATOR_URL environment variable:"
    kubectl exec $STREAMLIT_POD -- printenv COORDINATOR_URL
    
    # Try to reach coordinator from streamlit pod
    echo ""
    echo "Testing connectivity from Streamlit to Coordinator..."
    kubectl exec $STREAMLIT_POD -- curl -s -m 5 http://coordinator-service:8006/health && {
        echo "✅ Connectivity OK"
    } || {
        echo "❌ Cannot reach coordinator from streamlit pod"
        echo ""
        echo "Possible issues:"
        echo "  1. Coordinator service not ready"
        echo "  2. Network policy blocking traffic"
        echo "  3. DNS resolution issue"
    }
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔗 DNS Resolution Test:"
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup coordinator-service 2>/dev/null || {
    echo "Testing DNS resolution..."
    kubectl run debug-dns --image=busybox --restart=Never -- nslookup coordinator-service
    sleep 2
    kubectl logs debug-dns
    kubectl delete pod debug-dns --force --grace-period=0 2>/dev/null
}

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Recommendations:"
echo ""

# Check if all services are ready
NOT_READY=$(kubectl get pods --no-headers | grep -v "Running" | grep -v "Completed" | wc -l)

if [ "$NOT_READY" -gt 0 ]; then
    echo "⚠️  Some pods are not ready:"
    kubectl get pods | grep -v "Running" | grep -v "NAME"
    echo ""
    echo "Wait for all pods to be ready:"
    echo "  kubectl wait --for=condition=ready pod --all --timeout=300s"
else
    echo "✅ All pods are running"
    echo ""
    echo "If you still have connectivity issues:"
    echo ""
    echo "1. Restart the deployments:"
    echo "   kubectl rollout restart deployment/coordinator"
    echo "   kubectl rollout restart deployment/streamlit-frontend"
    echo ""
    echo "2. Check coordinator logs:"
    echo "   kubectl logs -f deployment/coordinator"
    echo ""
    echo "3. Port forward and test locally:"
    echo "   kubectl port-forward service/coordinator-service 8006:8006"
    echo "   curl http://localhost:8006/health"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
