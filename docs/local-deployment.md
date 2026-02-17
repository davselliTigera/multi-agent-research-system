## 💻 Local Development (Without Kubernetes)

You can run the entire system locally on your machine for development and testing without needing Kubernetes.

### Prerequisites

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Redis** - For state management
  - macOS: `brew install redis`
  - Linux: `apt install redis-server`
  - Windows: [Download](https://redis.io/download)
- **Google API Key** - For Gemini LLM ([Get one here](https://makersuite.google.com/app/apikey))

### Quick Start (Automated)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/multi-agent-research-system.git
cd multi-agent-research-system

# 2. Set your Google API key
export GOOGLE_API_KEY='your-google-api-key-here'

# 3. Run the automated setup script
chmod +x scripts/run-local-simple.sh
./scripts/run-local-simple.sh
```

This script will:
- ✅ Create a Python virtual environment
- ✅ Install all dependencies
- ✅ Start Redis (if needed)
- ✅ Launch all 5 agents and the coordinator
- ✅ Verify all services are running

**Then in a new terminal:**

```bash
# 4. Start the Streamlit UI
source venv/bin/activate
export COORDINATOR_URL=http://localhost:8006
streamlit run frontend/streamlit_frontend.py
```

**Access the application**: Open http://localhost:8501 in your browser! 🎉

### Manual Setup (Step-by-Step)

If you prefer to start services manually or want more control:

#### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install fastapi uvicorn langchain-google-genai redis httpx pydantic duckduckgo-search streamlit
```

#### 3. Set Environment Variables

```bash
# Required
export GOOGLE_API_KEY='your-google-api-key-here'

# Optional (defaults are fine for local)
export REDIS_HOST=localhost
export REDIS_PORT=6379
export PYTHONPATH=$(pwd)
```

#### 4. Start Redis

```bash
# In a separate terminal
redis-server
```

#### 5. Start Services

Open **7 separate terminals** and run each service:

**Terminal 1 - Coordinator:**
```bash
cd multi-agent-research-system
source venv/bin/activate
export PYTHONPATH=$(pwd)
export REDIS_HOST=localhost
export REDIS_PORT=6379
export GOOGLE_API_KEY='your-key'
python coordinator/coordinator_a2a.py
```

**Terminal 2 - Topic Refiner:**
```bash
cd multi-agent-research-system
source venv/bin/activate
export PYTHONPATH=$(pwd)
export REDIS_HOST=localhost
export GOOGLE_API_KEY='your-key'
python agents/topic_refiner_a2a.py
```

**Terminal 3 - Question Architect:**
```bash
cd multi-agent-research-system
source venv/bin/activate
export PYTHONPATH=$(pwd)
export REDIS_HOST=localhost
export GOOGLE_API_KEY='your-key'
python agents/question_architect_a2a.py
```

**Terminal 4 - Search Strategist:**
```bash
cd multi-agent-research-system
source venv/bin/activate
export PYTHONPATH=$(pwd)
export REDIS_HOST=localhost
export GOOGLE_API_KEY='your-key'
python agents/search_strategist_a2a.py
```

**Terminal 5 - Data Analyst:**
```bash
cd multi-agent-research-system
source venv/bin/activate
export PYTHONPATH=$(pwd)
export REDIS_HOST=localhost
export GOOGLE_API_KEY='your-key'
python agents/data_analyst_a2a.py
```

**Terminal 6 - Report Writer:**
```bash
cd multi-agent-research-system
source venv/bin/activate
export PYTHONPATH=$(pwd)
export REDIS_HOST=localhost
export GOOGLE_API_KEY='your-key'
python agents/report_writer_a2a.py
```

**Terminal 7 - Streamlit UI:**
```bash
cd multi-agent-research-system
source venv/bin/activate
export PYTHONPATH=$(pwd)
export COORDINATOR_URL=http://localhost:8006
streamlit run frontend/streamlit_frontend.py
```

#### 6. Verify Services are Running

Open a new terminal and run:

```bash
# Check each service health
curl http://localhost:8006/health  # Coordinator
curl http://localhost:8001/health  # Topic Refiner
curl http://localhost:8002/health  # Question Architect
curl http://localhost:8003/health  # Search Strategist
curl http://localhost:8004/health  # Data Analyst
curl http://localhost:8005/health  # Report Writer
```

All should return: `{"status":"healthy",...}`

### Testing the System Locally

#### Test Individual Agents

```bash
# Test Topic Refiner capabilities
curl http://localhost:8001/capabilities | jq

# Test coordinator health
curl http://localhost:8006/health
```

#### Test Research Workflow

1. Open http://localhost:8501 in your browser
2. Enter a research topic (e.g., "Benefits of microservices")
3. Click "🚀 Deploy Agents"
4. Watch the agents collaborate in real-time
5. Download your research report!

#### Test via API (without UI)

```bash
# Start a research task
curl -X POST "http://localhost:8006/start_research?topic=quantum%20computing&max_iterations=1"

# Get task status (replace {task_id} with the ID from previous response)
curl http://localhost:8006/task/{task_id}
```

### Viewing Logs

If you used the automated script, logs are saved to `logs/` directory:

```bash
# View coordinator logs
tail -f logs/coordinator.log

# View topic-refiner logs
tail -f logs/topic-refiner.log

# View all logs
tail -f logs/*.log
```

For manual setup, logs appear directly in each terminal window.

### Stopping Services

#### If using automated script:

```bash
# Stop all services
pkill -f 'python.*_a2a.py'
pkill -f 'python.*coordinator'

# Stop Redis
redis-cli shutdown
```

#### If using tmux (from automated script):

```bash
# List sessions
tmux ls

# Kill the session
tmux kill-session -t multi-agent

# Stop Redis
redis-cli shutdown
```

#### If using manual terminals:

Press `Ctrl+C` in each terminal to stop each service.

### Troubleshooting Local Development

#### Issue: "ModuleNotFoundError: No module named 'shared'"

**Solution**: Set PYTHONPATH to the project root
```bash
export PYTHONPATH=$(pwd)
```

#### Issue: "Connection refused" or services can't connect

**Solution**: Ensure Redis is running
```bash
redis-cli ping  # Should return "PONG"

# If not running:
redis-server
```

#### Issue: "GOOGLE_API_KEY not set"

**Solution**: Export your API key
```bash
export GOOGLE_API_KEY='your-actual-key-here'
```

#### Issue: Port already in use

**Solution**: Kill the process using that port
```bash
# Find process on port 8001
lsof -i :8001

# Kill it
kill -9 <PID>
```

#### Issue: Agents returning errors

**Solution**: Check the logs
```bash
# If using automated script
tail -f logs/coordinator.log

# If using manual terminals
# Check the terminal output for that agent
```

### Development Tips

#### Hot Reload with Uvicorn

For faster development, use Uvicorn's reload flag:

```bash
uvicorn coordinator.coordinator_a2a:app --reload --host 0.0.0.0 --port 8006
```

#### Testing Changes

After making code changes:
1. Stop the affected service (Ctrl+C)
2. Restart it
3. Test your changes

No need to restart all services unless you modified shared code.

#### Debugging with Breakpoints

You can use Python debugger in any service:

```python
# Add this to your code
import pdb; pdb.set_trace()
```

Then run the service directly (not in background) to interact with the debugger.

#### Database Management

View Redis data:
```bash
# Connect to Redis CLI
redis-cli

# List all task keys
KEYS task:*

# View a specific task
GET task:abc-123

# Clear all data
FLUSHALL
```

### Switching Between Local and Kubernetes

The code automatically detects the environment:

- **Local**: When `REDIS_HOST=localhost`
- **Kubernetes**: When `REDIS_HOST=redis-service`

No code changes needed! The same codebase works in both environments.

### Performance Notes

**Local Development**:
- All services run on one machine
- Suitable for development and testing
- Performance depends on your machine specs

**Recommended Local Setup**:
- 8GB+ RAM
- 4+ CPU cores
- SSD storage

**For Production**: Use Kubernetes deployment for better scalability and reliability.

---

**Related Documentation**:
- [Architecture Details](docs/architecture.md) - How the system works
- [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions