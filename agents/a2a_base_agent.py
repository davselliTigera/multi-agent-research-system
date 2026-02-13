"""
a2a_base_agent.py
Base class for A2A-compliant agent microservices
"""

from fastapi import FastAPI, HTTPException
from langchain_google_genai import ChatGoogleGenerativeAI
from shared.a2a_models import (
    A2AMessage, A2AAgent, A2ACapability, A2AActionRequest, A2AActionResponse,
    A2ACapabilityRequest, A2ACapabilityResponse, MessageStatus,
    create_action_response, create_error_message, AGENT_URIS
)
from shared.shared_models import GOOGLE_API_KEY
from datetime import datetime
from typing import Dict, Any, List, Optional
from abc import abstractmethod
import redis
import json
import os
import uuid


class A2ABaseAgent:
    """Base class for all A2A-compliant agent microservices"""
    
    def __init__(
        self, 
        agent_id: str,
        name: str, 
        role: str, 
        expertise: str, 
        temperature: float = 0.7
    ):
        self.agent_id = agent_id
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
        
        # Define capabilities (to be overridden by subclasses)
        self.capabilities: List[A2ACapability] = []
        
    def _build_system_prompt(self) -> str:
        return f"""You are {self.name}, a specialized AI agent.
Role: {self.role}
Expertise: {self.expertise}

You work as part of a multi-agent research system using the A2A protocol. 
Focus on your specific role and provide high-quality output."""
    
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
    
    def invoke_llm(self, prompt: str) -> str:
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
    
    def get_state(self, task_id: str) -> Optional[dict]:
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
            "agent_id": self.agent_id,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            **data
        })
        state["agent_logs"] = logs
        self.redis_client.set(f"task:{task_id}", json.dumps(state))
    
    @abstractmethod
    def get_capabilities(self) -> List[A2ACapability]:
        """Return agent capabilities - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    async def handle_action(self, action: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle action request - must be implemented by subclasses"""
        pass
    
    async def process_message(self, message: A2AMessage) -> A2AMessage:
        """
        Process incoming A2A message
        This is the main entry point for A2A protocol communication
        """
        print(f"[{self.name}] Received message: {message.id} from {message.from_agent}")
        
        try:
            # Handle different content types
            if isinstance(message.content, A2ACapabilityRequest):
                return await self._handle_capability_request(message)
            
            elif isinstance(message.content, A2AActionRequest):
                return await self._handle_action_request(message)
            
            else:
                return create_error_message(
                    message_id=str(uuid.uuid4()),
                    to=message.from_agent,
                    from_agent=self.agent_id,
                    code="UNSUPPORTED_MESSAGE_TYPE",
                    message=f"Unsupported message content type: {type(message.content)}",
                    reply_to=message.id
                )
                
        except Exception as e:
            print(f"[{self.name}] Error processing message: {e}")
            return create_error_message(
                message_id=str(uuid.uuid4()),
                to=message.from_agent,
                from_agent=self.agent_id,
                code="PROCESSING_ERROR",
                message=str(e),
                reply_to=message.id
            )
    
    async def _handle_capability_request(self, message: A2AMessage) -> A2AMessage:
        """Handle capability request"""
        capabilities = self.get_capabilities()
        
        agent_info = A2AAgent(
            id=self.agent_id,
            name=self.name,
            version="1.0.0",
            capabilities=capabilities,
            metadata={
                "role": self.role,
                "expertise": self.expertise,
                "temperature": self.temperature
            }
        )
        
        return A2AMessage(
            id=str(uuid.uuid4()),
            to=message.from_agent,
            from_agent=self.agent_id,
            content=A2ACapabilityResponse(
                capabilities=capabilities,
                agent=agent_info
            ),
            reply_to=message.id
        )
    
    async def _handle_action_request(self, message: A2AMessage) -> A2AMessage:
        """Handle action request"""
        action_request = message.content
        
        try:
            # Execute the action
            result = await self.handle_action(
                action=action_request.action,
                parameters=action_request.parameters,
                context=action_request.context
            )
            
            # Create success response
            return create_action_response(
                message_id=str(uuid.uuid4()),
                to=message.from_agent,
                from_agent=self.agent_id,
                action=action_request.action,
                result=result,
                status=MessageStatus.COMPLETED,
                reply_to=message.id
            )
            
        except Exception as e:
            # Create error response
            return create_action_response(
                message_id=str(uuid.uuid4()),
                to=message.from_agent,
                from_agent=self.agent_id,
                action=action_request.action,
                result={},
                status=MessageStatus.FAILED,
                error=str(e),
                reply_to=message.id
            )
    
    def create_app(self) -> FastAPI:
        """Create FastAPI app for this agent with A2A endpoints"""
        app = FastAPI(
            title=f"{self.name} - A2A Agent",
            description=f"A2A-compliant agent: {self.expertise}"
        )
        
        @app.get("/")
        async def root():
            return {
                "agent": self.name,
                "agent_id": self.agent_id,
                "protocol": "A2A v1.0",
                "status": "online"
            }
        
        @app.get("/health")
        async def health():
            return {
                "status": "healthy", 
                "agent": self.name,
                "agent_id": self.agent_id
            }
        
        @app.post("/message", response_model=A2AMessage)
        async def receive_message(message: A2AMessage) -> A2AMessage:
            """
            A2A Protocol endpoint
            Receives A2A messages and returns A2A responses
            """
            response = await self.process_message(message)
            return response
        
        @app.get("/capabilities")
        async def get_capabilities():
            """Return agent capabilities"""
            capabilities = self.get_capabilities()
            return {
                "agent_id": self.agent_id,
                "name": self.name,
                "capabilities": [cap.dict() for cap in capabilities],
                "metadata": {
                    "role": self.role,
                    "expertise": self.expertise
                }
            }
        
        return app
