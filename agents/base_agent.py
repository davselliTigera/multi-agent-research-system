"""
base_agent.py
Base class for agent microservices
"""

from fastapi import FastAPI, HTTPException
from langchain_google_genai import ChatGoogleGenerativeAI
from shared_models import AgentMessage, AgentResponse, GOOGLE_API_KEY
from datetime import datetime
from typing import Optional
import redis
import json
import os

class BaseAgent:
    """Base class for all agent microservices"""
    
    def __init__(self, name: str, role: str, expertise: str, temperature: float = 0.7):
        self.name = name
        self.role = role
        self.expertise = expertise
        self.temperature = temperature
        self.llm = None
        self.system_prompt = self._build_system_prompt()
        
        # Redis connection for state management
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis-service"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True
        )
        
    def _build_system_prompt(self) -> str:
        return f"""You are {self.name}, a specialized AI agent.
Role: {self.role}
Expertise: {self.expertise}

You work as part of a multi-agent research system. Focus on your specific role and provide high-quality output."""
    
    def _get_llm(self):
        """Lazily initialize LLM"""
        if self.llm is None:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-3-pro-preview",
                temperature=self.temperature,
                max_tokens=None,
                timeout=None,
                max_retries=2,
                google_api_key=GOOGLE_API_KEY
            )
        return self.llm
    
    def invoke(self, prompt: str) -> str:
        """Invoke the agent's LLM"""
        full_prompt = f"{self.system_prompt}\n\n{prompt}"
        llm = self._get_llm()
        response = llm.invoke(full_prompt)
        
        # Handle different response formats
        if isinstance(response.content, str):
            return response.content
        elif isinstance(response.content, list):
            text_parts = []
            for item in response.content:
                if isinstance(item, dict) and 'text' in item:
                    text_parts.append(item['text'])
                elif isinstance(item, str):
                    text_parts.append(item)
                elif hasattr(item, 'text'):
                    text_parts.append(item.text)
            return ''.join(text_parts)
        else:
            return str(response.content)
    
    def get_state(self, task_id: str) -> dict:
        """Get current state from Redis"""
        state_json = self.redis_client.get(f"task:{task_id}")
        if state_json:
            return json.loads(state_json)
        return None
    
    def update_state(self, task_id: str, updates: dict):
        """Update state in Redis"""
        state = self.get_state(task_id) or {}
        state.update(updates)
        self.redis_client.set(f"task:{task_id}", json.dumps(state))
    
    def add_log(self, task_id: str, action: str, data: dict):
        """Add log entry to state"""
        state = self.get_state(task_id) or {}
        logs = state.get("agent_logs", [])
        logs.append({
            "agent": self.name,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            **data
        })
        state["agent_logs"] = logs
        self.redis_client.set(f"task:{task_id}", json.dumps(state))
    
    def process(self, message: AgentMessage) -> AgentResponse:
        """Process message - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement process()")
    
    def create_app(self) -> FastAPI:
        """Create FastAPI app for this agent"""
        app = FastAPI(title=f"{self.name} Service")
        
        @app.get("/health")
        async def health():
            return {"status": "healthy", "agent": self.name}
        
        @app.post("/process")
        async def process_message(message: AgentMessage) -> AgentResponse:
            try:
                response = self.process(message)
                return response
            except Exception as e:
                return AgentResponse(
                    task_id=message.task_id,
                    agent_name=self.name,
                    success=False,
                    data={},
                    error=str(e)
                )
        
        return app
