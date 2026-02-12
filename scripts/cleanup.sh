#!/bin/bash
# Cleanup script for multi-agent research system

set -e

echo "🧹 Multi-Agent Research System Cleanup"
echo ""

# Function to show menu
show_menu() {
    echo "What would you like to do?"
    echo ""
    echo "  1) Delete all deployments and services"
    echo "  2) Delete everything including secrets"
    echo "  3) Scale all deployments to 0 (keep deployed)"
    echo "  4) Scale all deployments to 1 (restart)"
    echo "  5) Delete just the pods (restart)"
    echo "  6) Cancel"
    echo ""
}

# Function to delete all resources
delete_all() {
    echo "🗑️  Deleting all deployments and services..."
    kubectl delete -f kubernetes/deployments.yaml --ignore-not-found=true
    echo "✅ All resources deleted"
}

# Function to delete everything including secrets
delete_everything() {
    echo "🗑️  Deleting everything including secrets..."
    kubectl delete -f kubernetes/deployments.yaml --ignore-not-found=true
    kubectl delete secret google-api-secret --ignore-not-found=true
    echo "✅ Everything deleted"
}

# Function to scale to 0
scale_to_zero() {
    echo "📉 Scaling all deployments to 0 replicas..."
    
    deployments=(
        "topic-refiner"
        "question-architect"
        "search-strategist"
        "data-analyst"
        "report-writer"
        "coordinator"
        "streamlit-frontend"
    )
    
    for deployment in "${deployments[@]}"; do
        echo "  Scaling $deployment to 0..."
        kubectl scale deployment/$deployment --replicas=0
    done
    
    echo "✅ All deployments scaled to 0"
    echo ""
    echo "To restart: ./cleanup.sh and choose option 4"
}

# Function to scale to 1
scale_to_one() {
    echo "📈 Scaling all deployments to 1 replica..."
    
    # Redis stays at 1
    kubectl scale deployment/redis --replicas=1
    
    # Scale agents to 1
    deployments=(
        "topic-refiner"
        "question-architect"
        "search-strategist"
        "data-analyst"
        "report-writer"
        "coordinator"
        "streamlit-frontend"
    )
    
    for deployment in "${deployments[@]}"; do
        echo "  Scaling $deployment to 1..."
        kubectl scale deployment/$deployment --replicas=1
    done
    
    echo "✅ All deployments scaled to 1"
    echo ""
    echo "⏳ Waiting for pods to be ready..."
    
    for deployment in "${deployments[@]}"; do
        kubectl wait --for=condition=available --timeout=60s deployment/$deployment 2>/dev/null || true
    done
    
    echo ""
    echo "📊 Current status:"
    kubectl get pods
}

# Function to delete pods (force restart)
delete_pods() {
    echo "🔄 Deleting all pods (they will restart automatically)..."
    
    kubectl delete pods -l app=topic-refiner
    kubectl delete pods -l app=question-architect
    kubectl delete pods -l app=search-strategist
    kubectl delete pods -l app=data-analyst
    kubectl delete pods -l app=report-writer
    kubectl delete pods -l app=coordinator
    kubectl delete pods -l app=streamlit-frontend
    
    echo "✅ Pods deleted, waiting for restart..."
    sleep 5
    kubectl get pods
}

# Show menu and get choice
show_menu
read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        read -p "⚠️  Delete all deployments and services? (y/n): " confirm
        if [ "$confirm" = "y" ]; then
            delete_all
        else
            echo "Cancelled"
        fi
        ;;
    2)
        read -p "⚠️  Delete EVERYTHING including secrets? (y/n): " confirm
        if [ "$confirm" = "y" ]; then
            delete_everything
        else
            echo "Cancelled"
        fi
        ;;
    3)
        scale_to_zero
        ;;
    4)
        scale_to_one
        ;;
    5)
        delete_pods
        ;;
    6)
        echo "Cancelled"
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Useful commands:"
echo ""
echo "  # Check status"
echo "  kubectl get pods"
echo "  kubectl get deployments"
echo ""
echo "  # Redeploy"
echo "  ./deploy-to-kind.sh"
echo ""
echo "  # Scale specific deployment"
echo "  kubectl scale deployment/search-strategist --replicas=3"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
