# GitHub Repository Structure

```
multi-agent-research-system/
├── .gitignore
├── README.md
├── LICENSE
│
├── agents/
│   ├── __init__.py
│   ├── base_agent.py
│   ├── topic_refiner_service.py
│   ├── question_architect_service.py
│   ├── search_strategist_service.py
│   ├── data_analyst_service.py
│   └── report_writer_service.py
│
├── coordinator/
│   ├── __init__.py
│   └── coordinator_service.py
│
├── frontend/
│   ├── __init__.py
│   └── streamlit_frontend.py
│
├── shared/
│   ├── __init__.py
│   └── shared_models.py
│
├── docker/
│   ├── Dockerfile.agent
│   ├── Dockerfile.coordinator
│   └── Dockerfile.streamlit
│
├── kubernetes/
│   └── deployments.yaml
│
├── requirements/
│   ├── requirements-agent.txt
│   ├── requirements-coordinator.txt
│   └── requirements-streamlit.txt
│
├── scripts/
│   ├── create-requirements.sh
│   ├── setup-files.sh
│   ├── build-and-deploy.sh
│   ├── deploy-to-kind.sh
│   ├── cleanup.sh
│   └── debug-connectivity.sh
│
├── docs/
│   ├── architecture.md
│   ├── deployment.md
│   ├── troubleshooting.md
│   ├── contributing.md
│   └── agent-reuse.md
│
├── examples/
│   ├── sample-topics.md
│   ├── custom-workflows/
│   │   ├── faq_generator.py
│   │   ├── content_writer.py
│   │   └── search_assistant.py
│   ├── integrations/
│   │   ├── flask_example.py
│   │   ├── fastapi_example.py
│   │   └── nodejs_wrapper.ts
│   └── notebooks/
│       └── agent_playground.ipynb
```

## File Organization

### Root Files
- **README.md** - Main documentation (installation, quick start, features)
- **LICENSE** - MIT License
- **.gitignore** - Ignore patterns for Python, Docker, Kubernetes

### `/agents/` - Agent Microservices
All specialized AI agents that perform specific research tasks.

### `/coordinator/` - Workflow Orchestrator
Coordinator service that manages the multi-agent workflow.

### `/frontend/` - User Interface
Streamlit web application for user interaction.

### `/shared/` - Common Code
Shared models, configurations, and utilities used across services.

### `/docker/` - Docker Configuration
Dockerfiles for building container images.

### `/kubernetes/` - Kubernetes Manifests
YAML files for deploying to Kubernetes.

### `/requirements/` - Python Dependencies
Separate requirements files for each service type.

### `/scripts/` - Automation Scripts
Helper scripts for building, deploying, and managing the system.

### `/docs/` - Documentation
Detailed documentation split into focused topics.

### `/examples/` - Usage Examples
Sample topics and use cases for the research system.