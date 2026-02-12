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

The system uses a microservices architecture where each agent runs as an independent Kubernetes pod with specialized responsibilities.

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Kubernetes Cluster                              │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                     Frontend Layer                              │    │
│  │  ┌──────────────────────────────────────────────────────────┐  │    │
│  │  │  Streamlit UI (Pod)                                       │  │    │
│  │  │  - Port: 8501                                             │  │    │
│  │  │  - User Interface & Visualization                         │  │    │
│  │  └────────────────────────┬─────────────────────────────────┘  │    │
│  └───────────────────────────┼────────────────────────────────────┘    │
│                               │ HTTP/REST                               │
│  ┌───────────────────────────▼────────────────────────────────────┐    │
│  │                   Orchestration Layer                          │    │
│  │  ┌──────────────────────────────────────────────────────────┐  │    │
│  │  │  Coordinator Service (Pod)                                │  │    │
│  │  │  - Port: 8006                                             │  │    │
│  │  │  - Workflow Management                                    │  │    │
│  │  │  - Agent Communication                                    │  │    │
│  │  │  - Decision Logic                                         │  │    │
│  │  └────┬────────┬────────┬────────┬────────┬─────────────────┘  │    │
│  └───────┼────────┼────────┼────────┼────────┼────────────────────┘    │
│          │        │        │        │        │                         │
│          │ REST   │ REST   │ REST   │ REST   │ REST                    │
│          │        │        │        │        │                         │
│  ┌───────▼────────▼────────▼────────▼────────▼────────────────────┐    │
│  │                      Agent Layer                               │    │
│  │                                                                 │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐    │    │
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
│  │  └──────────────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

         External Services
         ┌─────────────────┐
         │  Google Gemini  │
         │  API (LLM)      │
         └────────▲────────┘
                  │
         All Agents use LLM
         for intelligence
```

### Agent Team

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

#### 🎭 **Chief Coordinator** (Port 8006)
- **Role**: Research Coordination Specialist
- **Expertise**: Managing multi-agent workflows and decision-making
- **Temperature**: 0.2 (Highly deterministic)
- **Responsibilities**:
  - Orchestrates the complete research workflow
  - Routes messages between agents
  - Makes decisions on research continuation
  - Manages task state and progress
  - Handles errors and retries

### Research Workflow

```
┌─────────┐
│  User   │
│ Input   │
└────┬────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Research Workflow                             │
│                                                                      │
│  1. Topic Refiner (🎯)                                              │
│     Input: Raw topic                                                │
│     Output: Refined, focused research topic                         │
│     └─────────────────────────────────────────────┐                 │
│                                                    ▼                 │
│  2. Question Architect (❓)                                         │
│     Input: Refined topic                                            │
│     Output: 3 specific research questions                           │
│     └─────────────────────────────────────────────┐                 │
│                                                    ▼                 │
│  3. Search Strategist (🔍)                                          │
│     Input: Research questions                                       │
│     Process: Optimize queries → Execute searches                    │
│     Output: Search results from DuckDuckGo                          │
│     └─────────────────────────────────────────────┐                 │
│                                                    ▼                 │
│  4. Data Analyst (📊)                                               │
│     Input: Search results                                           │
│     Process: Extract insights → Calculate quality                   │
│     Output: Key findings + quality score                            │
│     └─────────────────────────────────────────────┐                 │
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
│            └─────────────────────────▶ Output: Formatted report    │
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
- **Message Format**: Standardized JSON payload with task tracking

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
- **0.2-0.3**: Deterministic (Coordinator, Search Strategist)
- **0.4-0.5**: Analytical (Data Analyst, Topic Refiner)
- **0.6-0.7**: Balanced creativity (Report Writer, Question Architect)

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

## 🔄 Reusing Agents

The agents are designed as independent, reusable components that can be integrated into other applications!

### As Python Library

```python
from agents.topic_refiner_service import TopicRefinerAgent
from agents.question_architect_service import QuestionArchitectAgent

# Use agents directly in your code
refiner = TopicRefinerAgent()
architect = QuestionArchitectAgent()

refined_topic = refiner.refine_topic("machine learning")
questions = architect.generate_questions(refined_topic, 0)
```

### As REST API

```bash
# Deploy individual agents as APIs
docker run -p 8001:8001 -e GOOGLE_API_KEY="key" \
  multi-agent-research/topic-refiner:latest

# Call from any language
curl -X POST http://localhost:8001/process \
  -H "Content-Type: application/json" \
  -d '{"task_id": "123", "action": "refine_topic", ...}'
```

### Custom Workflows

Build your own workflows with any combination of agents:

```python
# Example: FAQ Generator
class FAQGenerator:
    def __init__(self):
        self.architect = QuestionArchitectAgent()
        self.searcher = SearchStrategistAgent()
    
    def generate_faq(self, topic: str):
        questions = self.architect.generate_questions(topic, 0)
        answers = [self.searcher.execute_search(q) for q in questions]
        return zip(questions, answers)
```

**📖 See [AGENT-REUSE.md](docs/agent-reuse.md) for detailed integration examples including:**
- Standalone Python usage
- REST API integration
- Message queue patterns
- Serverless deployment
- Node.js wrappers
- Custom workflow examples

**💡 Example Applications** (in `examples/` directory):
- **FAQ Generator** - Auto-generate FAQs for any topic
- **Content Writer** - Create articles with AI assistance
- **Search Assistant** - Enhanced search with analysis
- **FastAPI Service** - Expose agents as REST APIs
- **Flask Integration** - Web application examples
- **Jupyter Notebooks** - Interactive agent exploration

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