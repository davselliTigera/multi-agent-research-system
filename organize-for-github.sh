#!/bin/bash
# Script to organize files into proper GitHub repository structure

echo "📁 Organizing files for GitHub repository..."
echo ""

# Create directory structure
echo "Creating directories..."
mkdir -p agents
mkdir -p coordinator
mkdir -p frontend
mkdir -p shared
mkdir -p docker
mkdir -p kubernetes
mkdir -p requirements
mkdir -p scripts
mkdir -p docs
mkdir -p examples

# Move agent files
echo "Moving agent files..."
mv topic_refiner_service.py agents/ 2>/dev/null || true
mv question_architect_service.py agents/ 2>/dev/null || true
mv search_strategist_service.py agents/ 2>/dev/null || true
mv data_analyst_service.py agents/ 2>/dev/null || true
mv report_writer_service.py agents/ 2>/dev/null || true
mv base_agent.py agents/ 2>/dev/null || true

# Move coordinator
echo "Moving coordinator..."
mv coordinator_service.py coordinator/ 2>/dev/null || true

# Move frontend
echo "Moving frontend..."
mv streamlit_frontend.py frontend/ 2>/dev/null || true

# Move shared
echo "Moving shared files..."
mv shared_models.py shared/ 2>/dev/null || true

# Move Docker files
echo "Moving Docker files..."
mv Dockerfile.* docker/ 2>/dev/null || true

# Move Kubernetes files
echo "Moving Kubernetes files..."
mv kubernetes-deployments.yaml kubernetes/deployments.yaml 2>/dev/null || true

# Move requirements
echo "Moving requirements..."
mv requirements-*.txt requirements/ 2>/dev/null || true

# Move scripts
echo "Moving scripts..."
mv create-requirements.sh scripts/ 2>/dev/null || true
mv setup-files.sh scripts/ 2>/dev/null || true
mv build-and-deploy.sh scripts/ 2>/dev/null || true
mv deploy-to-kind.sh scripts/ 2>/dev/null || true
mv cleanup.sh scripts/ 2>/dev/null || true
mv debug-connectivity.sh scripts/ 2>/dev/null || true

# Create __init__.py files
echo "Creating __init__.py files..."
touch agents/__init__.py
touch coordinator/__init__.py
touch frontend/__init__.py
touch shared/__init__.py

# Create documentation files
echo "Creating documentation structure..."
cat > docs/architecture.md << 'EOF'
# Architecture Documentation

See the main README for architecture diagrams.

This document will contain detailed architecture information including:
- Component interactions
- Data flow diagrams
- State management
- Service communication patterns

(To be expanded)
EOF

cat > docs/deployment.md << 'EOF'
# Deployment Guide

Detailed deployment instructions for various environments.

## Local Development (Kind)
See main README Quick Start section.

## Production Kubernetes
(To be documented)

## Cloud Providers
- GKE (Google Kubernetes Engine)
- EKS (Amazon Elastic Kubernetes Service)
- AKS (Azure Kubernetes Service)

(To be expanded)
EOF

cat > docs/troubleshooting.md << 'EOF'
# Troubleshooting Guide

## Common Issues

### Image Pull Errors
**Symptom**: `ImagePullBackOff` or `ErrImagePull`

**Solution for Kind**:
```bash
kind load docker-image multi-agent-research/coordinator:latest
```

### Connection Timeouts
**Symptom**: "All connection attempts failed"

**Solution**:
```bash
./scripts/debug-connectivity.sh
```

### Pods Crash Looping
Check logs:
```bash
kubectl logs <pod-name>
kubectl describe pod <pod-name>
```

(To be expanded with more solutions)
EOF

cat > docs/contributing.md << 'EOF'
# Contributing Guidelines

Thank you for considering contributing to the Multi-Agent Research System!

## How to Contribute

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/multi-agent-research-system.git

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements/requirements-agent.txt
```

## Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to functions
- Write descriptive commit messages

## Testing

(Testing guidelines to be added)

## Questions?

Open an issue or start a discussion!
EOF

cat > examples/sample-topics.md << 'EOF'
# Sample Research Topics

Try these topics to explore the system's capabilities:

## Technology
- "Benefits of microservices architecture"
- "Latest developments in quantum computing"
- "Kubernetes vs Docker Swarm comparison"
- "Impact of AI on software development"

## Science
- "Recent discoveries in astrophysics"
- "Climate change mitigation strategies"
- "CRISPR gene editing applications"
- "Renewable energy innovations"

## Sports
- "Top 3 F1 drivers of all time"
- "Evolution of basketball strategy"
- "Olympic record breakthroughs"

## Business
- "Digital transformation success stories"
- "Remote work productivity trends"
- "Sustainable business practices"

## General
- "History of the internet"
- "Future of urban transportation"
- "Benefits of lifelong learning"
EOF

# Update paths in scripts
echo "Updating paths in scripts..."

# Update build-and-deploy.sh
if [ -f scripts/build-and-deploy.sh ]; then
    sed -i.bak 's|Dockerfile.agent|docker/Dockerfile.agent|g' scripts/build-and-deploy.sh
    sed -i.bak 's|Dockerfile.coordinator|docker/Dockerfile.coordinator|g' scripts/build-and-deploy.sh
    sed -i.bak 's|Dockerfile.streamlit|docker/Dockerfile.streamlit|g' scripts/build-and-deploy.sh
    sed -i.bak 's|kubernetes-deployments.yaml|kubernetes/deployments.yaml|g' scripts/build-and-deploy.sh
    sed -i.bak 's|topic_refiner_service.py|agents/topic_refiner_service.py|g' scripts/build-and-deploy.sh
    sed -i.bak 's|question_architect_service.py|agents/question_architect_service.py|g' scripts/build-and-deploy.sh
    sed -i.bak 's|search_strategist_service.py|agents/search_strategist_service.py|g' scripts/build-and-deploy.sh
    sed -i.bak 's|data_analyst_service.py|agents/data_analyst_service.py|g' scripts/build-and-deploy.sh
    sed -i.bak 's|report_writer_service.py|agents/report_writer_service.py|g' scripts/build-and-deploy.sh
    rm scripts/build-and-deploy.sh.bak 2>/dev/null || true
fi

# Update deploy-to-kind.sh
if [ -f scripts/deploy-to-kind.sh ]; then
    sed -i.bak 's|Dockerfile.agent|docker/Dockerfile.agent|g' scripts/deploy-to-kind.sh
    sed -i.bak 's|Dockerfile.coordinator|docker/Dockerfile.coordinator|g' scripts/deploy-to-kind.sh
    sed -i.bak 's|Dockerfile.streamlit|docker/Dockerfile.streamlit|g' scripts/deploy-to-kind.sh
    sed -i.bak 's|kubernetes-deployments.yaml|kubernetes/deployments.yaml|g' scripts/deploy-to-kind.sh
    sed -i.bak 's|topic_refiner_service.py|agents/topic_refiner_service.py|g' scripts/deploy-to-kind.sh
    sed -i.bak 's|question_architect_service.py|agents/question_architect_service.py|g' scripts/deploy-to-kind.sh
    sed -i.bak 's|search_strategist_service.py|agents/search_strategist_service.py|g' scripts/deploy-to-kind.sh
    sed -i.bak 's|data_analyst_service.py|agents/data_analyst_service.py|g' scripts/deploy-to-kind.sh
    sed -i.bak 's|report_writer_service.py|agents/report_writer_service.py|g' scripts/deploy-to-kind.sh
    rm scripts/deploy-to-kind.sh.bak 2>/dev/null || true
fi

# Update cleanup.sh
if [ -f scripts/cleanup.sh ]; then
    sed -i.bak 's|kubernetes-deployments.yaml|kubernetes/deployments.yaml|g' scripts/cleanup.sh
    rm scripts/cleanup.sh.bak 2>/dev/null || true
fi

# Update Dockerfiles to use correct paths
echo "Updating Dockerfile paths..."

if [ -f docker/Dockerfile.agent ]; then
    cat > docker/Dockerfile.agent << 'EOF'
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements/requirements-agent.txt .
RUN pip install --no-cache-dir -r requirements-agent.txt

COPY shared/ shared/
COPY agents/base_agent.py agents/

ARG SERVICE_FILE
COPY ${SERVICE_FILE} service.py

ARG PORT=8000
EXPOSE ${PORT}

ENV PYTHONPATH=/app

CMD ["python", "service.py"]
EOF
fi

if [ -f docker/Dockerfile.coordinator ]; then
    cat > docker/Dockerfile.coordinator << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements/requirements-coordinator.txt .
RUN pip install --no-cache-dir -r requirements-coordinator.txt

COPY shared/ shared/
COPY coordinator/coordinator_service.py .

EXPOSE 8006

ENV PYTHONPATH=/app

CMD ["python", "coordinator_service.py"]
EOF
fi

if [ -f docker/Dockerfile.streamlit ]; then
    cat > docker/Dockerfile.streamlit << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements/requirements-streamlit.txt .
RUN pip install --no-cache-dir -r requirements-streamlit.txt

COPY shared/ shared/
COPY frontend/streamlit_frontend.py .

EXPOSE 8501

ENV PYTHONPATH=/app

CMD ["streamlit", "run", "streamlit_frontend.py", "--server.port=8501", "--server.address=0.0.0.0"]
EOF
fi

echo ""
echo "✅ Files organized successfully!"
echo ""
echo "📁 Directory structure:"
tree -L 2 -I '__pycache__|*.pyc' . 2>/dev/null || find . -maxdepth 2 -type d | sort

echo ""
echo "📋 Next steps:"
echo ""
echo "1. Review the new structure"
echo "2. Add .gitignore and LICENSE files"
echo "3. Update README.md with your information"
echo "4. Initialize git repository:"
echo "   git init"
echo "   git add ."
echo "   git commit -m 'Initial commit: Multi-Agent Research System'"
echo ""
echo "5. Create GitHub repository and push:"
echo "   git remote add origin https://github.com/yourusername/multi-agent-research-system.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
