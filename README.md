# 🤖 Multi-Agent Research System

A distributed AI research system with **two implementation versions**: Custom REST API and standards-compliant A2A Protocol. Each agent is an independent microservice with specialized expertise, collaborating to conduct comprehensive research on any topic.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)

## 🎯 Two Versions Available

This repository contains **two complete implementations**:

### **1. REST API Version** (Original)
- Custom REST endpoints
- Simpler architecture
- ~5-10% faster

### **2. A2A Protocol Version** (Standards-Compliant)
- Google's Agent-to-Agent protocol
- Standardized messages (`agent://` URIs)
- Capability discovery (`GET /capabilities`)

**Choose your version based on your needs!** See [REST-vs-A2A.md](docs/REST-vs-A2A.md) for detailed comparison.

## ✨ Features

- **🎯 Specialized AI Agents** - 5 independent agents with unique expertise
- **☸️ Kubernetes-Native** - Fully containerized, cloud-ready
- **🔄 Dual Protocols** - Choose REST or A2A
- **📊 State Management** - Redis-backed shared state
- **🎨 Interactive UI** - Streamlit interface
- **📈 Horizontal Scaling** - Scale agents independently
- **🔍 Real-time Monitoring** - Live agent activity tracking
- **🔄 Agent Reusability** - Use agents in other applications

## 🗂️ Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                          Kubernetes Cluster                              │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                     Frontend Layer                              │    │
│  │  ┌──────────────────────────────────────────────────────────┐  │    │
│  │  │  Streamlit UI (Pod)                                       │  │    │
│  │  │  - Port: 8501                                             │  │    │
│  │  │  - User Interface & Visualization                         │  │    │
│  │  └────────────────────┬─────────────────────────────────────┘  │    │
│  └───────────────────────┼────────────────────────────────────────┘    │
│                               │ HTTP/REST                               │
│  ┌───────────────────────▼────────────────────────────────────────┐    │
│  │                   Orchestration Layer                          │    │
│  │  ┌──────────────────────────────────────────────────────────┐  │    │
│  │  │  Coordinator Service (Pod)                                │  │    │
│  │  │  - Port: 8006                                             │  │    │
│  │  │  - REST: Custom messages                                  │  │    │
│  │  │  - A2A: agent:// URIs                                     │  │    │
│  │  │  - Workflow Management                                    │  │    │
│  │  └─────┬────────┬────────┬────────┬────────────────────────┘  │    │
│  └───────┼────────┼────────┼────────┼───────────────────────────┘    │
│          │        │        │        │        │                         │
│          │ REST   │ REST   │ REST   │ REST   │ REST                    │
│          │ or A2A │ or A2A │ or A2A │ or A2A │ or A2A                  │
│          │        │        │        │        │                         │
│  ┌───────▼────────▼────────▼────────▼────────▼───────────────────┐    │
│  │                      Agent Layer                               │    │
│  │                                                                 │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌────────────────────┐    │    │
│  │  │   Topic     │  │  Question   │  │      Search         │    │    │
│  │  │   Refiner   │  │  Architect  │  │    Strategist       │    │    │
│  │  │  🎯 :8001   │  │  ❓ :8002   │  │     🔍 :8003        │    │    │
│  │  │             │  │             │  │                     │    │    │
│  │  │ - Clarify   │  │ - Generate  │  │ - Optimize queries  │    │    │
│  │  │   topics    │  │   questions │  │ - Execute searches  │    │    │
│  │  │ - Refine    │  │ - Design    │  │ - DuckDuckGo API   │    │    │
│  │  │   scope     │  │   strategy  │  │ - Result parsing   │    │    │
│  │  │             │  │             │  │                     │    │    │
│  │  │ Temp: 0.5   │  │ Temp: 0.7   │  │   Temp: 0.3        │    │    │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬─────────────┘    │    │
│  │         │                │                 │                   │    │
│  │  ┌──────▼──────┐  ┌──────▼────────┐                           │    │
│  │  │    Data     │  │    Report     │                           │    │
│  │  │   Analyst   │  │    Writer     │                           │    │
│  │  │  📊 :8004   │  │   📝 :8005    │                           │    │
│  │  │             │  │               │                           │    │
│  │  │ - Analyze   │  │ - Synthesize  │                           │    │
│  │  │   results   │  │   findings    │                           │    │
│  │  │ - Extract   │  │ - Generate    │                           │    │
│  │  │   insights  │  │   reports     │                           │    │
│  │  │ - Quality   │  │ - Format      │                           │    │
│  │  │   scoring   │  │   output      │                           │    │
│  │  │             │  │               │                           │    │
│  │  │ Temp: 0.4   │  │  Temp: 0.6    │                           │    │
│  │  └──────┬──────┘  └──────┬────────┘                           │    │
│  │         │                │                                     │    │
│  └─────────┼────────────────┼─────────────────────────────────────┘    │
│            │                │                                           │
│            │ Redis Protocol │                                           │
│            │                │                                           │
│  ┌─────────▼────────────────▼─────────────────────────────────────┐    │
│  │                    State Layer                                  │    │
│  │  ┌──────────────────────────────────────────────────────────┐  │    │
│  │  │  Redis (Pod)                                              │  │    │
│  │  │  - Port: 6379                                             │  │    │
│  │  │  - Shared State Store                                     │  │    │
│  │  │  - Task Management                                        │  │    │
│  │  │  - Inter-Agent Communication                              │  │    │
│  │  │  - Research Progress Tracking                             │  │    │
│  │  └──────────────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  Legend:                                                                │
│  🎯 Topic Refiner    ❓ Question Architect    🔍 Search Strategist      │
│  📊 Data Analyst     📝 Report Writer                                   │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

         External Services
         ┌─────────────────┐
         │  Google Gemini  │
         │  API (LLM)      │
         └────────▲────────┘
                  │
         All Agents use LLM
         for intelligence
```

### The Agent Team

Each agent is a specialized microservice with its own LLM instance, personality, and expertise:

#### 🎯 **Dr. Topic Refiner** (Port 8001)
- **Role**: Research Topic Specialist
- **Expertise**: Clarifying research objectives and scoping studies
- **Temperature**: 0.5 (More focused and consistent)
- **Responsibilities**:
  - Analyzes raw user input
  - Identifies core research questions
  - Refines topics to be specific and searchable
  - Ensures scope is neither too broad nor too narrow

#### ❓ **Prof. Question Architect** (Port 8002)
- **Role**: Research Question Designer
- **Expertise**: Formulating precise, investigable research questions
- **Temperature**: 0.7 (Balanced creativity)
- **Responsibilities**:
  - Generates 3 specific research questions per iteration
  - Designs questions that are directly searchable
  - Covers different aspects of the topic
  - Builds upon previous iterations progressively

#### 🔍 **Agent Search Strategist** (Port 8003)
- **Role**: Information Retrieval Specialist
- **Expertise**: Designing search strategies and executing queries
- **Temperature**: 0.3 (Very focused and precise)
- **Responsibilities**:
  - Optimizes research questions into effective search queries
  - Executes searches via DuckDuckGo API
  - Retrieves and parses search results
  - Handles rate limiting and errors gracefully

#### 📊 **Dr. Data Analyst** (Port 8004)
- **Role**: Research Data Analyst
- **Expertise**: Extracting insights and identifying patterns
- **Temperature**: 0.4 (Analytical and focused)
- **Responsibilities**:
  - Analyzes search results for key information
  - Extracts the 5 most important findings per iteration
  - Calculates quality scores for research completeness
  - Identifies patterns and relationships in data
  - Avoids redundancy across findings

#### 📝 **Dr. Report Writer** (Port 8005)
- **Role**: Research Report Specialist
- **Expertise**: Synthesizing findings into clear, structured reports
- **Temperature**: 0.6 (Moderately creative for readability)
- **Responsibilities**:
  - Synthesizes all findings into cohesive narrative
  - Generates structured reports with sections
  - Formats output professionally
  - Adds metadata and research statistics
  - Creates executive summaries

### Research Workflow

```
┌─────────┐
│  User   │
│ Input   │
└────┬────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        Research Workflow                             │
│                                                                      │
│  1. Topic Refiner (🎯)                                              │
│     Input: Raw topic                                                │
│     Output: Refined, focused research topic                         │
│     └───────────────────────────────────────────────                 │
│                                                    ▼                 │
│  2. Question Architect (❓)                                         │
│     Input: Refined topic                                            │
│     Output: 3 specific research questions                           │
│     └───────────────────────────────────────────────                 │
│                                                    ▼                 │
│  3. Search Strategist (🔍)                                          │
│     Input: Research questions                                       │
│     Process: Optimize queries → Execute searches                    │
│     Output: Search results from DuckDuckGo                          │
│     └───────────────────────────────────────────────                 │
│                                                    ▼                 │
│  4. Data Analyst (📊)                                               │
│     Input: Search results                                           │
│     Process: Extract insights → Calculate quality                   │
│     Output: Key findings + quality score                            │
│     └───────────────────────────────────────────────                 │
│                                                    ▼                 │
│  5. Coordinator Decision (🎭)                                       │
│     Evaluate: Quality score, iterations, findings count             │
│     Decision: Continue research OR Generate report                  │
│                                                                      │
│     ┌────────────────┐              ┌────────────────┐             │
│     │   Continue?    │──────NO─────▶│  Generate      │             │
│     │ (Loop back to  │              │  Final Report  │             │
│     │  step 2)       │              │                │             │
│     └────────────────┘              └────────┬───────┘             │
│            │                                  │                     │
│           YES                                 ▼                     │
│            │                        6. Report Writer (📝)          │
│            │                           Input: All findings          │
│            └──────────────────────────▶ Output: Formatted report    │
│                                                │                    │
└────────────────────────────────────────────────┼────────────────────┘
                                                 ▼
                                        ┌──────────────┐
                                        │   Report     │
                                        │   to User    │
                                        └──────────────┘
```

### Key Architectural Features

#### 🔗 **Inter-Service Communication**
- **Synchronous**: HTTP/REST API calls between coordinator and agents
- **Asynchronous**: Background task processing for long-running research
- **State Management**: Redis for shared state across all services
- **Message Format**: 
  - REST: Custom JSON payload
  - A2A: Standardized `@type` based messages

#### 🔄 **Workflow Orchestration**
- **Dynamic Routing**: Coordinator decides when to continue or finalize research
- **Iterative Refinement**: Loops back to generate more questions based on findings
- **Quality Assessment**: Data Analyst calculates quality scores to determine completion
- **Error Handling**: Graceful degradation with detailed error propagation

#### 📦 **Microservices Benefits**
- **Independent Scaling**: Scale search agents separately from other agents
- **Fault Isolation**: One agent failure doesn't crash the entire system
- **Technology Flexibility**: Each agent can use different libraries/versions
- **Deployment Independence**: Update agents without system-wide restarts
- **Resource Optimization**: Each agent has tailored CPU/memory allocation

#### 🎚️ **Temperature Settings**
Each agent uses specific temperature settings for optimal performance:
- **0.2-0.3**: Deterministic (Search Strategist)
- **0.4-0.5**: Analytical (Data Analyst, Topic Refiner)
- **0.6-0.7**: Balanced creativity (Report Writer, Question Architect)

## 🚀 Quick Start

### Prerequisites

- **Kubernetes Cluster** - Either:
  - **[Kind](https://kind.sigs.k8s.io/)** (Kubernetes in Docker) for local development
  - **[kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/)** for production-ready clusters
- **[kubectl](https://kubernetes.io/docs/tasks/tools/)** - Kubernetes CLI
- **[Docker](https://docs.docker.com/get-docker/)** - Container runtime
- **Google API Key** - For Gemini LLM ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

#### Option 1: Kind Cluster (Development)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/multi-agent-research-system.git
   cd multi-agent-research-system
   ```

2. **Create a Kind cluster**
   ```bash
   kind create cluster --name research-cluster
   kubectl cluster-info --context kind-research-cluster
   ```

3. **Set your Google API key**
   ```bash
   export GOOGLE_API_KEY="your-google-api-key-here"
   ```

4. **Deploy your chosen version**

   **REST API Version:**
   ```bash
   chmod +x scripts/deploy-to-kind.sh
   ./scripts/deploy-to-kind.sh
   ```

   **A2A Protocol Version:**
   ```bash
   chmod +x scripts/deploy-a2a-to-kind.sh
   ./scripts/deploy-a2a-to-kind.sh
   ```

5. **Access the application**
   ```bash
   kubectl port-forward service/streamlit-service 8501:80
   # Open http://localhost:8501
   ```

#### Option 2: kubeadm Cluster with Local Registry

For kubeadm clusters using a local registry (e.g., `lynx.tigera.local`):

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/multi-agent-research-system.git
   cd multi-agent-research-system
   ```

2. **Ensure your local registry is accessible**
   ```bash
   # Verify registry connectivity
   curl -X GET http://lynx.tigera.local/v2/_catalog
   
   # Ensure kubeconfig is set
   kubectl cluster-info
   ```

3. **Set your Google API key**
   ```bash
   export GOOGLE_API_KEY="your-google-api-key-here"
   ```

4. **Deploy A2A Protocol version**
   ```bash
   chmod +x scripts/deploy-a2a-to-kubeadm.sh
   ./scripts/deploy-a2a-to-kubeadm.sh
   ```

   This script will:
   - Build all container images
   - Tag them for your local registry (`lynx.tigera.local/multi-agent-research`)
   - Push images to the registry
   - Deploy to your kubeadm cluster

5. **Access the application**
   ```bash
   kubectl port-forward service/streamlit-service 8501:80
   # Open http://localhost:8501
   ```

> **Note:** The kubeadm deployment script uses the local registry at `lynx.tigera.local`. If you're using a different registry, modify the `REGISTRY` variable in `scripts/deploy-a2a-to-kubeadm.sh` accordingly.

## 📖 Usage

### Conducting Research

1. Open the Streamlit UI at `http://localhost:8501`
2. Enter your research topic (e.g., "Benefits of microservices architecture")
3. Adjust max iterations (1-5) in the sidebar
4. Click "🚀 Deploy Agents"
5. Watch the agents collaborate in real-time
6. Download your comprehensive research report

### Example Topics

- "Top 3 F1 drivers of all time"
- "Latest developments in quantum computing"
- "Benefits of Kubernetes for AI workloads"
- "Impact of microservices on system design"

## 📁 Repository Structure

```
multi-agent-research-system/
│
├── agents/                      # Agent implementations
│   ├── *_service.py            # REST API versions
│   ├── *_a2a.py                # A2A Protocol versions
│   ├── base_agent.py           # REST base class
│   └── a2a_base_agent.py       # A2A base class
│
├── coordinator/                 # Workflow orchestrators
│   ├── coordinator_service.py  # REST version
│   └── coordinator_a2a.py      # A2A version
│
├── frontend/                    # User interface
│   └── streamlit_frontend.py   # Streamlit web UI
│
├── shared/                      # Common code
│   ├── shared_models.py        # REST models
│   └── a2a_models.py           # A2A protocol models
│
├── kubernetes/                  # Deployment manifests
│   ├── deployments.yaml        # REST version
│   └── deployments-a2a.yaml    # A2A version
│
├── docker/                      # Container definitions
│   ├── Dockerfile.agent        # Agent services
│   ├── Dockerfile.coordinator  # REST coordinator
│   ├── Dockerfile.coordinator-a2a  # A2A coordinator
│   └── Dockerfile.streamlit    # Frontend
│
├── requirements/                # Python dependencies
│   ├── requirements-agent.txt
│   ├── requirements-coordinator.txt
│   └── requirements-streamlit.txt
│
├── scripts/                     # Automation scripts
│   ├── deploy-to-kind.sh       # Deploy REST version
│   ├── deploy-a2a-to-kind.sh   # Deploy A2A version (Kind)
│   ├── deploy-a2a-to-kubeadm.sh # Deploy A2A version (kubeadm)
│   ├── cleanup.sh              # Cleanup/management
│   └── debug-connectivity.sh   # Troubleshooting
│
├── docs/                        # Documentation
│   ├── architecture.md         # Detailed architecture
│   ├── REST-vs-A2A.md         # Version comparison
│   ├── deployment.md           # Deployment guide
│   └── troubleshooting.md      # Common issues
│
└── examples/                    # Usage examples
    ├── custom-workflows/       # Custom agent workflows
    └── integrations/           # Framework integrations
```

## 🔄 Switching Between Versions

```bash
# Clean current deployment
./scripts/cleanup.sh  # Choose option 1

# Deploy REST version (Kind)
./scripts/deploy-to-kind.sh

# OR deploy A2A version (Kind)
./scripts/deploy-a2a-to-kind.sh

# OR deploy A2A version (kubeadm with local registry)
./scripts/deploy-a2a-to-kubeadm.sh
```

## 🔄 Reusing Agents

Agents can be used in other applications! See [examples/](examples/) for:

- **FAQ Generator** - Auto-generate FAQs for any topic
- **Content Writer** - Create articles with AI assistance
- **Search Assistant** - Enhanced search with analysis
- **FastAPI Service** - Expose agents as REST APIs

Full guide: [docs/agent-reuse.md](docs/agent-reuse.md)

## 🛠️ Development

### Scaling Agents

```bash
# Scale search agent for more concurrent searches
kubectl scale deployment/search-strategist --replicas=3

# Scale all agents
kubectl scale deployment/topic-refiner --replicas=2
```

### Monitoring

```bash
# View all pods
kubectl get pods

# Watch coordinator logs
kubectl logs -f deployment/coordinator

# Check agent capabilities (A2A version)
kubectl port-forward service/topic-refiner-service 8001:8001
curl http://localhost:8001/capabilities
```

## 🧹 Management

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

## 📊 Resource Requirements

**Minimum (1 replica each):**
- Memory: ~6.5 GiB
- CPU: ~3.5 cores
- Storage: ~2 GiB

**Recommended (scaled):**
- Memory: ~14 GiB
- CPU: ~8 cores

## 🛠 Troubleshooting

```bash
# Debug connectivity
./scripts/debug-connectivity.sh

# Check pod status
kubectl get pods

# View logs
kubectl logs <pod-name>

# Describe pod
kubectl describe pod <pod-name>
```

See [docs/troubleshooting.md](docs/troubleshooting.md) for detailed solutions.

## 📚 Documentation

- [Architecture Details](docs/architecture.md) - System design and data flow
- [REST vs A2A Comparison](docs/REST-vs-A2A.md) - Version differences
- [Deployment Guide](docs/deployment.md) - Advanced deployment scenarios
- [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions
- [Agent Reusability](docs/agent-reuse.md) - Using agents in other apps

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

See [docs/contributing.md](docs/contributing.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspiration taken from [KodeCloud - LangGraph labs](https://learn.kodekloud.com/user/courses/youtube-labs-langgraph)
- Built with [LangChain](https://www.langchain.com/) and [Google Gemini](https://ai.google.dev/)
- UI powered by [Streamlit](https://streamlit.io/)
- Orchestrated with [Kubernetes](https://kubernetes.io/)
- Search via [DuckDuckGo](https://duckduckgo.com/)
- A2A Protocol by [Google](https://github.com/google/a2a)

---

**⭐ If you find this project useful, please consider giving it a star!**