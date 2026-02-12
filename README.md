# 🤖 Multi-Agent Research System

A production-ready, distributed AI research system built with specialized agents running as Kubernetes microservices. Each agent is an independent service with specific expertise, collaborating to conduct comprehensive research on any topic.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)

## ✨ Features

- **🎯 Specialized AI Agents** - 5 independent agents, each with unique expertise and LLM configuration
- **☸️ Kubernetes-Native** - Fully containerized, cloud-ready architecture
- **🔄 Asynchronous Workflow** - Non-blocking research tasks with real-time progress updates
- **📊 State Management** - Redis-backed shared state for agent coordination
- **🎨 Interactive UI** - Beautiful Streamlit interface for research management
- **📈 Horizontal Scaling** - Scale individual agents based on workload
- **🔍 Real-time Monitoring** - Live agent activity tracking and logging
- **🛠️ Production Ready** - Health checks, error handling, and graceful degradation

## 🏗️ Architecture

The system uses a microservices architecture where each agent runs as an independent Kubernetes pod:

```
┌─────────────┐
│ Streamlit   │  User Interface (Port 8501)
│   Frontend  │
└──────┬──────┘
       │
┌──────▼──────┐
│ Coordinator │  Workflow Orchestrator (Port 8006)
└──────┬──────┘
       │
  ┌────┴────┐
  │         │
┌─▼─────┐ ┌─▼─────┐
│Agents │ │ Redis │  5 Specialized Agents + State Store
└───────┘ └───────┘
```

### Agent Team

1. **🎯 Dr. Topic Refiner** (Port 8001) - Clarifies research objectives
2. **❓ Prof. Question Architect** (Port 8002) - Designs research questions  
3. **🔍 Agent Search Strategist** (Port 8003) - Executes web searches
4. **📊 Dr. Data Analyst** (Port 8004) - Extracts insights from data
5. **📝 Dr. Report Writer** (Port 8005) - Synthesizes comprehensive reports

## 🚀 Quick Start

### Prerequisites

- **[Kind](https://kind.sigs.k8s.io/docs/user/quick-start/)** (Kubernetes in Docker) - Required for local deployment
- **[kubectl](https://kubernetes.io/docs/tasks/tools/)** - Kubernetes CLI
- **[Docker](https://docs.docker.com/get-docker/)** - Container runtime
- **Google API Key** - For Gemini LLM ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/multi-agent-research-system.git
   cd multi-agent-research-system
   ```

2. **Create a Kind cluster**
   ```bash
   # Create a new Kind cluster
   kind create cluster --name research-cluster
   
   # Verify cluster is running
   kubectl cluster-info --context kind-research-cluster
   ```

3. **Set your Google API key**
   ```bash
   export GOOGLE_API_KEY="your-google-api-key-here"
   ```

4. **Deploy the system**
   ```bash
   # Make scripts executable
   chmod +x scripts/*.sh
   
   # Deploy to Kind cluster
   ./scripts/deploy-to-kind.sh
   ```

5. **Access the application**
   ```bash
   # Port forward to access the UI
   kubectl port-forward service/streamlit-service 8501:80
   
   # Open in browser
   open http://localhost:8501
   ```

## 📖 Usage

### Conducting Research

1. Open the Streamlit UI at `http://localhost:8501`
2. Enter your research topic (e.g., "Benefits of multi-agent AI systems")
3. Adjust max iterations (1-5) in the sidebar
4. Click "🚀 Deploy Agents"
5. Watch the agents collaborate in real-time
6. Download your comprehensive research report

### Example Topics

- "Top 3 F1 drivers of all time"
- "Benefits of Kubernetes for AI workloads"
- "Latest developments in quantum computing"
- "Impact of microservices on system design"
- "Advantages of multi-agent architectures"

## 🛠️ Development

### Project Structure

```
multi-agent-research-system/
├── agents/              # Agent microservices
├── coordinator/         # Workflow orchestrator
├── frontend/           # Streamlit UI
├── shared/             # Common code
├── docker/             # Dockerfiles
├── kubernetes/         # K8s manifests
├── requirements/       # Python dependencies
├── scripts/            # Automation scripts
└── docs/              # Documentation
```

### Building Individual Services

```bash
# Build a specific agent
docker build --build-arg SERVICE_FILE=agents/topic_refiner_service.py \
  --build-arg PORT=8001 -f docker/Dockerfile.agent \
  -t multi-agent-research/topic-refiner:latest .

# Load into Kind
kind load docker-image multi-agent-research/topic-refiner:latest

# Restart deployment
kubectl rollout restart deployment/topic-refiner
```

### Scaling Agents

```bash
# Scale search agent for more concurrent searches
kubectl scale deployment/search-strategist --replicas=3

# Scale all agents
kubectl scale deployment/topic-refiner --replicas=2
kubectl scale deployment/question-architect --replicas=2
kubectl scale deployment/data-analyst --replicas=2
```

## 🧹 Management

### Cleanup

```bash
# Interactive cleanup menu
./scripts/cleanup.sh

# Options:
# 1. Delete all deployments
# 2. Delete everything including secrets
# 3. Scale to 0 (pause system)
# 4. Scale to 1 (resume system)
# 5. Restart all pods
```

### Monitoring

```bash
# View all pods
kubectl get pods

# Watch logs
kubectl logs -f deployment/coordinator

# Check service health
kubectl get services

# Debug connectivity
./scripts/debug-connectivity.sh
```

## 📊 Resource Requirements

**Minimum (1 replica each):**
- Memory: ~6.5 GiB
- CPU: ~3.5 cores
- Storage: ~2 GiB

**Recommended (scaled for production):**
- Memory: ~14 GiB  
- CPU: ~8 cores
- Storage: ~5 GiB

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GOOGLE_API_KEY` | Google Gemini API key | - | ✅ Yes |
| `REDIS_HOST` | Redis hostname | redis-service | No |
| `REDIS_PORT` | Redis port | 6379 | No |
| `COORDINATOR_URL` | Coordinator service URL | http://coordinator-service:8006 | No |

### Customizing Agents

Edit agent parameters in their respective service files:

```python
# agents/topic_refiner_service.py
class TopicRefinerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Dr. Topic Refiner",
            temperature=0.5,  # Adjust creativity
            # ...
        )
```

## 🐛 Troubleshooting

### Common Issues

**Pods not starting?**
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

**Connection errors?**
```bash
./scripts/debug-connectivity.sh
```

**Image pull errors in Kind?**
```bash
# Reload images
kind load docker-image multi-agent-research/coordinator:latest
```

See [docs/troubleshooting.md](docs/troubleshooting.md) for more details.

## 📚 Documentation

- [Architecture Details](docs/architecture.md)
- [Deployment Guide](docs/deployment.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Contributing](docs/contributing.md)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://www.langchain.com/) and [Google Gemini](https://ai.google.dev/)
- UI powered by [Streamlit](https://streamlit.io/)
- Orchestrated with [Kubernetes](https://kubernetes.io/)
- Search via [DuckDuckGo](https://duckduckgo.com/)

## 📧 Contact

- GitHub Issues: [Report a bug](https://github.com/yourusername/multi-agent-research-system/issues)
- Discussions: [Ask questions](https://github.com/yourusername/multi-agent-research-system/discussions)

---

**⭐ If you find this project useful, please consider giving it a star!**
