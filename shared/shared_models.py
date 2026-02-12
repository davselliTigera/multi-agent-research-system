"""
shared_models.py
Shared data models and utilities for multi-agent system
"""

from typing import TypedDict, List, Optional
from datetime import datetime
from pydantic import BaseModel
import os

# Environment configuration
REDIS_HOST = os.getenv("REDIS_HOST", "redis-service")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# State models
class ResearchState(TypedDict):
    """Shared research state"""
    task_id: str
    original_topic: str
    topic: str
    research_questions: List[str]
    search_queries: List[str]
    search_results: List[str]
    key_findings: List[str]
    iteration: int
    max_iterations: int
    quality_score: float
    final_report: str
    status: str
    current_agent: str
    agent_logs: List[dict]
    error: Optional[str]

# Message models for inter-agent communication
class AgentMessage(BaseModel):
    """Message format for agent communication"""
    task_id: str
    agent_from: str
    agent_to: str
    action: str
    payload: dict
    timestamp: str = None
    
    def __init__(self, **data):
        if data.get('timestamp') is None:
            data['timestamp'] = datetime.now().isoformat()
        super().__init__(**data)

class AgentResponse(BaseModel):
    """Response format from agents"""
    task_id: str
    agent_name: str
    success: bool
    data: dict
    error: Optional[str] = None
    timestamp: str = None
    
    def __init__(self, **data):
        if data.get('timestamp') is None:
            data['timestamp'] = datetime.now().isoformat()
        super().__init__(**data)

# Agent registry
AGENTS = {
    "topic_refiner": "http://topic-refiner-service:8001",
    "question_architect": "http://question-architect-service:8002",
    "search_strategist": "http://search-strategist-service:8003",
    "data_analyst": "http://data-analyst-service:8004",
    "report_writer": "http://report-writer-service:8005",
    "coordinator": "http://coordinator-service:8006"
}

# Agent info for UI
AGENT_INFO = [
    {
        "key": "topic_refiner",
        "name": "Dr. Topic Refiner",
        "emoji": "🎯",
        "role": "Research Topic Specialist",
        "expertise": "Clarifying research objectives and scoping studies"
    },
    {
        "key": "question_architect",
        "name": "Prof. Question Architect",
        "emoji": "❓",
        "role": "Research Question Designer",
        "expertise": "Formulating precise, investigable research questions"
    },
    {
        "key": "search_strategist",
        "name": "Agent Search Strategist",
        "emoji": "🔍",
        "role": "Information Retrieval Specialist",
        "expertise": "Designing search strategies and executing queries"
    },
    {
        "key": "data_analyst",
        "name": "Dr. Data Analyst",
        "emoji": "📊",
        "role": "Research Data Analyst",
        "expertise": "Extracting insights and identifying patterns in research data"
    },
    {
        "key": "report_writer",
        "name": "Dr. Report Writer",
        "emoji": "📝",
        "role": "Research Report Specialist",
        "expertise": "Synthesizing findings into clear, structured reports"
    },
    {
        "key": "coordinator",
        "name": "Chief Coordinator",
        "emoji": "🎭",
        "role": "Research Coordination Specialist",
        "expertise": "Managing multi-agent workflows and decision-making"
    }
]
