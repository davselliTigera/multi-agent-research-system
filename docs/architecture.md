# 🏗️ System Architecture

> **Multi-Agent Research System - Detailed Architecture Documentation**

## Overview

This document provides an in-depth explanation of the multi-agent research system's architecture, communication patterns, and data flow.

## Architecture Type

This is a **hub-and-spoke microservices architecture** where the Coordinator orchestrates all agent interactions through a centralized Redis state store.

### Key Architectural Principles

1. **Centralized Orchestration**: The Coordinator is the single point of workflow control
2. **Shared State Pattern**: All agents read/write to Redis for state management
3. **No Direct Agent-to-Agent Communication**: Agents never call each other directly
4. **Stateless Agents**: Each agent is independently scalable and stateless
5. **Sequential Workflow**: Coordinator calls agents in a defined sequence

## Detailed System Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Kubernetes Cluster                          │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                    Frontend Layer                          │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │  Streamlit UI (Pod: 8501)                            │  │   │
│  │  │  • User interface                                    │  │   │
│  │  │  • Real-time status updates                          │  │   │
│  │  │  • Report download                                   │  │   │
│  │  └────────────────┬─────────────────────────────────────┘  │   │
│  └───────────────────┼────────────────────────────────────────┘   │
│                      │ HTTP POST                                   │
│                      │ /start_research                             │
│                      ▼                                              │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │              Orchestration Layer (Hub)                       │ │
│  │  ┌────────────────────────────────────────────────────────┐  │ │
│  │  │  Coordinator Service (Pod: 8006)                       │  │ │
│  │  │  • Workflow orchestration                             │  │ │
│  │  │  • Sequential agent invocation                        │  │ │
│  │  │  • Decision logic (continue/finalize)                 │  │ │
│  │  │  • Error handling & retry                             │  │ │
│  │  └─────┬───────┬────────┬────────┬────────┬─────────────┘  │ │
│  └────────┼───────┼────────┼────────┼────────┼────────────────┘ │
│           │       │        │        │        │                   │
│           │ A2A   │ A2A    │ A2A    │ A2A    │ A2A               │
│           │ POST  │ POST   │ POST   │ POST   │ POST              │
│           ▼       ▼        ▼        ▼        ▼                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                  Agent Layer (Spokes)                      │ │
│  │                                                            │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                │ │
│  │  │ Topic    │  │ Question │  │ Search   │                │ │
│  │  │ Refiner  │  │ Architect│  │Strategist│                │ │
│  │  │ :8001    │  │ :8002    │  │ :8003    │                │ │
│  │  │          │  │          │  │          │                │ │
│  │  │ Temp:0.5 │  │ Temp:0.7 │  │ Temp:0.3 │                │ │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘                │ │
│  │       │             │             │                        │ │
│  │  ┌────┴─────┐  ┌───┴──────┐                               │ │
│  │  │ Data     │  │ Report   │                               │ │
│  │  │ Analyst  │  │ Writer   │                               │ │
│  │  │ :8004    │  │ :8005    │                               │ │
│  │  │          │  │          │                               │ │
│  │  │ Temp:0.4 │  │ Temp:0.6 │                               │ │
│  │  └────┬─────┘  └────┬─────┘                               │ │
│  │       │             │                                      │ │
│  │       │ Redis       │ Redis                                │ │
│  │       │ Read/Write  │ Read/Write                           │ │
│  │       ▼             ▼                                      │ │
│  └──────────────────────────────────────────────────────────┘ │
│           ▲             ▲                                       │
│           │             │                                       │
│           │   Redis     │                                       │
│           │   Protocol  │                                       │
│           │             │                                       │
│  ┌────────┴─────────────┴─────────────────────────────────┐   │
│  │                 State Layer (Shared)                    │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │  Redis (Pod: 6379)                               │   │   │
│  │  │  • Centralized state store                       │   │   │
│  │  │  • Task state (topic, questions, results, etc.)  │   │   │
│  │  │  • Agent logs and progress tracking              │   │   │
│  │  │  • Quality scores and iteration counters         │   │   │
│  │  │  Key format: task:{task_id}                      │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  External: Google Gemini API (LLM) ← All agents use this        │
└──────────────────────────────────────────────────────────────────┘

Communication Flow:
┌────────────┐    POST      ┌─────────────┐
│ Streamlit  │─────────────→│ Coordinator │
└────────────┘              └──────┬──────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
            ┌──────────────┐ ┌──────────┐ ┌──────────┐
            │ Agent 1      │ │ Agent 2  │ │ Agent N  │
            │ (Refiner)    │ │(Architect)│ │ (Writer) │
            └──────┬───────┘ └────┬─────┘ └────┬─────┘
                   │              │            │
                   └──────────────┼────────────┘
                                  ▼
                           ┌────────────┐
                           │   Redis    │
                           │   State    │
                           └────────────┘
```

## How It Actually Works

### Step-by-Step Message Flow

Let's trace a research request for "Top 3 cars built in 2025":

```
1. USER → STREAMLIT
   POST /start_research?topic=Top+3+cars+built+in+2025&max_iterations=2
   
2. STREAMLIT → COORDINATOR
   POST http://coordinator-service:8006/start_research
   
3. COORDINATOR
   Creates task_id: abc-123
   Initializes Redis state:
   {
     "task_id": "abc-123",
     "topic": "Top 3 cars built in 2025",
     "status": "initialized",
     "research_questions": [],
     "search_results": [],
     "key_findings": []
   }
   
4. COORDINATOR → TOPIC REFINER
   POST http://topic-refiner-service:8001/message
   A2A Message:
   {
     "@type": "Message",
     "id": "msg-1",
     "to": "agent://topic-refiner",
     "from": "agent://coordinator",
     "content": {
       "@type": "ActionRequest",
       "action": "refine_topic",
       "parameters": {"task_id": "abc-123"}
     }
   }
   
5. TOPIC REFINER
   • Gets state from Redis: task:abc-123
   • Reads current topic: "Top 3 cars built in 2025"
   • Calls LLM to refine topic
   • Updates Redis state:
     {
       "task_id": "abc-123",
       "topic": "Top 3 production cars manufactured in 2025 by major automakers",
       "status": "topic_refined",
       "current_agent": "Dr. Topic Refiner"
     }
   • Returns A2A response to coordinator
   
6. COORDINATOR
   Receives success response, moves to next agent
   
7. COORDINATOR → QUESTION ARCHITECT
   POST http://question-architect-service:8002/message
   A2A Message with action: "generate_questions"
   
8. QUESTION ARCHITECT
   • Gets state from Redis: task:abc-123
   • Reads refined topic from state
   • Generates 3 research questions
   • Updates Redis state:
     {
       "research_questions": [
         "Which automakers released new models in 2025?",
         "What are the key features of top 2025 vehicles?",
         "What were the sales figures for 2025 models?"
       ]
     }
   • Returns success response
   
9. COORDINATOR → SEARCH STRATEGIST
   Similar pattern: reads questions from Redis, executes searches, updates results
   
10. COORDINATOR → DATA ANALYST
    Reads search results, analyzes, writes findings to Redis
    
11. COORDINATOR checks quality_score in Redis
    • If score < 0.8 and iteration < max_iterations: LOOP back to step 7
    • Otherwise: Continue to report generation
    
12. COORDINATOR → REPORT WRITER
    Reads all findings from Redis, generates final report
    
13. COORDINATOR updates Redis:
    {"status": "completed", "final_report": "..."}
    
14. STREAMLIT polls GET /task/abc-123
    Retrieves final state including report, displays to user
```

## Code References

### Coordinator Orchestration
**File**: `coordinator/coordinator_a2a.py`

```python
async def run_workflow(self, task_id: str):
    """Execute the complete A2A workflow"""
    
    # Step 1: Topic Refiner
    result = await self.call_agent_action(
        agent_uri=AGENT_URIS["topic_refiner"],
        action="refine_topic",
        parameters={"task_id": task_id}
    )
    
    # Step 2: Question Architect
    result = await self.call_agent_action(
        agent_uri=AGENT_URIS["question_architect"],
        action="generate_questions",
        parameters={"task_id": task_id}
    )
    
    # Step 3: Search Strategist
    result = await self.call_agent_action(
        agent_uri=AGENT_URIS["search_strategist"],
        action="execute_search",
        parameters={"task_id": task_id}
    )
    
    # Step 4: Data Analyst
    result = await self.call_agent_action(
        agent_uri=AGENT_URIS["data_analyst"],
        action="analyze_results",
        parameters={"task_id": task_id}
    )
    
    # Decision: Continue or Finalize?
    if await self.should_continue(task_id) == "continue":
        # Loop back to step 2
    else:
        # Step 5: Report Writer
        result = await self.call_agent_action(
            agent_uri=AGENT_URIS["report_writer"],
            action="generate_report",
            parameters={"task_id": task_id}
        )
```

### Agent State Management
**File**: `agents/a2a_base_agent.py`

```python
def get_state(self, task_id: str) -> Optional[dict]:
    """Get current state from Redis"""
    state_json = self.redis_client.get(f"task:{task_id}")
    return json.loads(state_json) if state_json else None

def update_state(self, task_id: str, updates: dict):
    """Update state in Redis"""
    state = self.get_state(task_id) or {}
    state.update(updates)  # Merge updates
    self.redis_client.set(f"task:{task_id}", json.dumps(state))
```

### Example: Topic Refiner
**File**: `agents/topic_refiner_a2a.py`

```python
async def _refine_topic(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    task_id = parameters.get("task_id")
    
    # Read from Redis
    state = self.get_state(task_id)
    topic = state.get("topic", "")
    
    # Do work (call LLM)
    refined_topic = self.invoke_llm(prompt)
    
    # Write back to Redis
    self.update_state(task_id, {
        "topic": refined_topic,
        "status": "topic_refined",
        "current_agent": self.name
    })
    
    # Return result to coordinator
    return {"refined_topic": refined_topic}
```

## Research Workflow Diagram

```
┌──────────┐
│   User   │
│  Input   │
└────┬─────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Coordinator Orchestration                     │
│                                                                  │
│  ┌────────────────────────────────────────────────────┐         │
│  │ Initialize Redis State                             │         │
│  │ task:{task_id} = {topic, status, questions, ...}   │         │
│  └────────────────────┬───────────────────────────────┘         │
│                       │                                          │
│                       ▼                                          │
│  ┌────────────────────────────────────────────────────┐         │
│  │ 1. Call Topic Refiner (🎯)                         │         │
│  │    POST /message → agent://topic-refiner           │         │
│  │    Agent reads Redis, refines topic, writes back   │         │
│  │    Returns: {refined_topic: "..."}                 │         │
│  └────────────────────┬───────────────────────────────┘         │
│                       │                                          │
│         ┌─────────────┴────────────┐                            │
│         │    Iteration Loop        │                            │
│         │   (max_iterations times) │                            │
│         │                           │                            │
│         │  ┌─────────────────────────────────────┐              │
│         │  │ 2. Call Question Architect (❓)     │              │
│         │  │    Reads refined topic from Redis   │              │
│         │  │    Generates 3 questions            │              │
│         │  │    Writes questions to Redis        │              │
│         │  │    Returns: {questions: [...]}      │              │
│         │  └───────────┬─────────────────────────┘              │
│         │              │                                         │
│         │              ▼                                         │
│         │  ┌─────────────────────────────────────┐              │
│         │  │ 3. Call Search Strategist (🔍)      │              │
│         │  │    Reads questions from Redis       │              │
│         │  │    Executes DuckDuckGo searches     │              │
│         │  │    Writes results to Redis          │              │
│         │  │    Returns: {results_count: N}      │              │
│         │  └───────────┬─────────────────────────┘              │
│         │              │                                         │
│         │              ▼                                         │
│         │  ┌─────────────────────────────────────┐              │
│         │  │ 4. Call Data Analyst (📊)           │              │
│         │  │    Reads search results from Redis  │              │
│         │  │    Extracts 5 key findings          │              │
│         │  │    Calculates quality_score         │              │
│         │  │    Writes findings to Redis         │              │
│         │  │    Returns: {quality_score: 0.7}    │              │
│         │  └───────────┬─────────────────────────┘              │
│         │              │                                         │
│         │              ▼                                         │
│         │  ┌─────────────────────────────────────┐              │
│         │  │ Decision Point                      │              │
│         │  │ Check Redis state:                  │              │
│         │  │ - quality_score >= 0.8?             │              │
│         │  │ - iteration >= max_iterations?      │              │
│         │  │ - findings_count >= 10?             │              │
│         │  └───┬─────────────────────────────┬───┘              │
│         │      │                             │                  │
│         │     YES                           NO                  │
│         │      │                             │                  │
│         └──────┼─────────────────────────────┘                  │
│                │          Loop back to step 2                   │
│                │                                                 │
│                ▼                                                 │
│  ┌──────────────────────────────────────────────┐               │
│  │ 5. Call Report Writer (📝)                   │               │
│  │    Reads ALL data from Redis:                │               │
│  │    - refined topic                           │               │
│  │    - all questions                           │               │
│  │    - all findings                            │               │
│  │    - quality_score, iteration count          │               │
│  │    Generates formatted report                │               │
│  │    Writes final_report to Redis              │               │
│  │    Returns: {report_length: N}               │               │
│  └────────────────────┬─────────────────────────┘               │
│                       │                                          │
│                       ▼                                          │
│  ┌────────────────────────────────────────────────┐             │
│  │ Update Redis: status = "completed"             │             │
│  └────────────────────────────────────────────────┘             │
│                                                                  │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Streamlit UI   │
                  │  Polls for      │
                  │  /task/{id}     │
                  │  Displays Report│
                  └─────────────────┘
```

## Architectural Patterns

### 1. Hub-and-Spoke (Star Topology)
- **Hub**: Coordinator (single point of orchestration)
- **Spokes**: Agents (independent, scalable services)
- **Benefits**: Simple, centralized control; easy to debug; no agent coupling

### 2. Shared State Pattern
- **Store**: Redis with key format `task:{task_id}`
- **State Structure**:
  ```json
  {
    "task_id": "abc-123",
    "original_topic": "...",
    "topic": "...",
    "research_questions": [],
    "search_queries": [],
    "search_results": [],
    "key_findings": [],
    "iteration": 0,
    "quality_score": 0.0,
    "final_report": "",
    "status": "in_progress",
    "current_agent": "Dr. Topic Refiner",
    "agent_logs": []
  }
  ```

### 3. Sequential Workflow
- **Order**: Topic Refiner → Question Architect → Search Strategist → Data Analyst → (loop or finalize) → Report Writer
- **Coordination**: Coordinator maintains order
- **Benefits**: Predictable, testable, easy to add/remove steps

### 4. Stateless Agents
- **No memory**: Agents don't remember previous requests
- **State in Redis**: All context passed through shared state
- **Benefits**: Horizontal scaling, fault tolerance, simple deployment

## Redis State Management

### State Lifecycle

```
1. INITIALIZE
   task:abc-123 = {
     "status": "initialized",
     "topic": "User's raw input"
   }

2. TOPIC REFINEMENT
   task:abc-123 = {
     "status": "topic_refined",
     "topic": "Refined topic",
     "current_agent": "Dr. Topic Refiner"
   }

3. ITERATION N
   task:abc-123 = {
     "status": "analyzing",
     "research_questions": ["Q1", "Q2", "Q3"],
     "search_results": ["Result 1", "Result 2", ...],
     "key_findings": ["Finding 1", "Finding 2", ...],
     "iteration": 1,
     "quality_score": 0.65
   }

4. FINALIZE
   task:abc-123 = {
     "status": "completed",
     "final_report": "# Research Report\n\n...",
     "quality_score": 0.85
   }
```

### State Access Patterns

**Coordinator**:
- Initializes state
- Reads state to check progress
- Updates status and current_agent
- Makes continue/finalize decisions

**Agents**:
- Read state to get input (e.g., topic, questions)
- Process with LLM
- Write results back to state
- Update status and add logs

## Why This Architecture?

### Advantages
✅ **Simple mental model**: Clear hub-and-spoke  
✅ **Easy debugging**: Centralized logs and state  
✅ **Independent scaling**: Scale agents without affecting workflow  
✅ **Fault isolation**: Agent failure doesn't cascade  
✅ **Technology flexibility**: Each agent can use different tech  
✅ **Testability**: Easy to test individual agents in isolation  
✅ **Observability**: All communication goes through coordinator  

### Trade-offs
⚠️ Coordinator is a single point of failure (mitigated by K8s restart)  
⚠️ Redis is a single point of truth (mitigated by Redis clustering)  
⚠️ Sequential processing (could be parallelized for some steps)  
⚠️ Network overhead (multiple HTTP calls per workflow)  

## Comparison: What We DON'T Have

**Peer-to-Peer Architecture** (NOT implemented):
```
Topic Refiner → Question Architect → Search Strategist → Data Analyst → Report Writer
```

This would require:
- Each agent knows the next agent's URL
- Complex routing logic
- Harder to debug (distributed logs)
- Agent coupling (changes cascade)

**What We HAVE** (Hub-and-Spoke):
```
              ┌→ Topic Refiner →┐
Coordinator ──┼→ Question Arch →┼── Redis State
              └→ Search Strat  →┘
```

This prioritizes **simplicity, debuggability, and operational ease** over maximum parallelism.

## A2A Protocol Implementation

### Message Format

All agent communication uses the A2A (Agent-to-Agent) protocol standard:

```json
{
  "@type": "Message",
  "id": "unique-message-id",
  "to": "agent://target-agent",
  "from": "agent://source-agent",
  "content": {
    "@type": "ActionRequest",
    "action": "action_name",
    "parameters": {},
    "context": {}
  },
  "timestamp": "2024-02-16T12:00:00Z"
}
```

### Pydantic Serialization Workaround

**Issue**: Pydantic v2 has a bug where Union types only serialize the discriminator field.

**Solution**: Manual serialization in both coordinator and agents:

```python
# In coordinator (sending messages)
message_dict = {
    "@type": message.type,
    "id": message.id,
    "to": message.to,
    "from": message.from_agent,
    "content": json.loads(message.content.model_dump_json(by_alias=True)),
    "timestamp": message.timestamp,
    "metadata": message.metadata
}

# In agents (returning responses)
response_dict = {
    "@type": response.type,
    "id": response.id,
    "to": response.to,
    "from": response.from_agent,
    "content": json.loads(response.content.model_dump_json(by_alias=True)),
    "timestamp": response.timestamp,
    "metadata": response.metadata
}
```

This ensures all content fields are properly serialized, not just the `@type` discriminator.

## Scaling Considerations

### Horizontal Scaling

**Coordinator**:
- Can run multiple replicas with load balancer
- State is in Redis (shared), so replicas are stateless
- Each handles different user requests

**Agents**:
- Fully stateless, infinitely scalable
- Scale independently based on load
- Example: Scale search-strategist to 10 replicas during high load

**Redis**:
- Single instance for development
- Redis Cluster for production
- Redis Sentinel for high availability

### Vertical Scaling

Each agent has different resource needs:
- **Search Strategist**: Network I/O bound
- **Data Analyst**: CPU bound (LLM processing)
- **Report Writer**: Memory bound (large context)

Configure resources per agent in Kubernetes deployments.

## Error Handling

### Coordinator Error Handling

```python
try:
    result = await self.call_agent_action(...)
except Exception as e:
    # Log error
    # Update Redis state with error
    # Return failure response
    self.update_state(task_id, {
        "status": "failed",
        "error": str(e)
    })
```

### Agent Error Handling

```python
try:
    # Process request
    result = await self.handle_action(...)
except Exception as e:
    # Return A2A Error message
    return create_error_message(
        code="ACTION_EXECUTION_ERROR",
        message=str(e)
    )
```

Errors propagate back through the coordinator to the user.

## Future Enhancements

Potential architectural improvements:

1. **Parallel Execution**: Run independent agents concurrently
2. **Event-Driven**: Use message queue (RabbitMQ/Kafka) instead of HTTP
3. **Distributed Tracing**: Add OpenTelemetry for request tracing
4. **Circuit Breakers**: Add resilience patterns for external API calls
5. **Caching Layer**: Cache LLM responses to reduce costs
6. **Agent Mesh**: Implement service mesh (Istio) for advanced routing

---

**Related Documentation**:
- [REST vs A2A Comparison](REST-vs-A2A.md)
- [Deployment Guide](deployment.md)
- [Troubleshooting](troubleshooting.md)